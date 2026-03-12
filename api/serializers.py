# api/serializers.py

from rest_framework import serializers
from api.models import User, Employe, Administrateur
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.hashers import make_password, check_password


# ===================================================================
# 1. USER SERIALIZER (avec photo et validation améliorée)
# ===================================================================
class UserSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'id', 
            'email', 
            'nom', 
            'prenoms', 
            'role', 
            'photo_profil',  # Champ pour l'upload
            'photo_url',     # URL pour l'affichage
            'is_active',
            'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'photo_profil': {'required': False},
            'role': {'required': False},
            'email': {'required': True},
            'nom': {'required': True},
            'prenoms': {'required': True},
        }

    def get_photo_url(self, obj):
        """
        Retourne l'URL complète de la photo de profil
        """
        request = self.context.get('request')
        if obj.photo_profil:
            if request:
                return request.build_absolute_uri(obj.photo_profil.url)
            return obj.photo_profil.url
        return None

    def validate_password(self, value):
        """Valider le mot de passe avec les validateurs Django"""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


# ===================================================================
# 2. EMPLOYE SERIALIZER (avec validation et mise à jour)
# ===================================================================
class EmployeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    # Champs pour la création/écriture
    email = serializers.EmailField(write_only=True)
    nom = serializers.CharField(write_only=True)
    prenoms = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    photo_profil = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = Employe
        fields = [
            'id',
            'user',
            'cin',
            'contact',
            'departement',
            # Champs pour la création
            'email',
            'nom',
            'prenoms',
            'password',
            'photo_profil'
        ]

    def validate_cin(self, value):
        """Valider le CIN"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Le CIN ne peut pas être vide.")
        return value.strip()
    
    def validate_contact(self, value):
        """Valider le contact"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Le contact ne peut pas être vide.")
        return value.strip()

    def create(self, validated_data):
        # Extraire les données utilisateur
        email = validated_data.pop('email')
        nom = validated_data.pop('nom')
        prenoms = validated_data.pop('prenoms')
        password = validated_data.pop('password')
        photo_profil = validated_data.pop('photo_profil', None)

        # Créer l'utilisateur
        user = User.objects.create_user(
            email=email,
            password=password,
            nom=nom,
            prenoms=prenoms,
            role='employe',
            photo_profil=photo_profil
        )

        # Créer le profil employé
        employe = Employe.objects.create(user=user, **validated_data)
        return employe

    def update(self, instance, validated_data):
        """Mettre à jour un employé"""
        # Champs directs de l'employé
        instance.cin = validated_data.get('cin', instance.cin)
        instance.contact = validated_data.get('contact', instance.contact)
        instance.departement = validated_data.get('departement', instance.departement)
        instance.save()
        
        # Mettre à jour l'utilisateur si des données sont fournies
        user = instance.user
        user.nom = validated_data.get('nom', user.nom)
        user.prenoms = validated_data.get('prenoms', user.prenoms)
        user.email = validated_data.get('email', user.email)
        
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
        
        if 'photo_profil' in validated_data:
            user.photo_profil = validated_data['photo_profil']
        
        user.save()
        
        return instance


# ===================================================================
# 3. ADMINISTRATEUR SERIALIZER (avec validation et mise à jour)
# ===================================================================
class AdministrateurSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    # Champs pour la création/écriture
    email = serializers.EmailField(write_only=True)
    nom = serializers.CharField(write_only=True)
    prenoms = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    photo_profil = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = Administrateur
        fields = [
            'id',
            'user',
            'fonction',
            # Champs pour la création
            'email',
            'nom',
            'prenoms',
            'password',
            'photo_profil'
        ]

    def create(self, validated_data):
        # Extraire les données utilisateur
        email = validated_data.pop('email')
        nom = validated_data.pop('nom')
        prenoms = validated_data.pop('prenoms')
        password = validated_data.pop('password')
        photo_profil = validated_data.pop('photo_profil', None)

        # Créer l'utilisateur
        user = User.objects.create_user(
            email=email,
            password=password,
            nom=nom,
            prenoms=prenoms,
            role='admin',
            photo_profil=photo_profil
        )

        # Créer le profil administrateur
        administrateur = Administrateur.objects.create(user=user, **validated_data)
        return administrateur


# ===================================================================
# 4. UPDATE PROFILE PHOTO (dédié à la photo uniquement)
# ===================================================================
class UpdateProfilePhotoSerializer(serializers.Serializer):
    """
    Serializer dédié pour la mise à jour de la photo de profil uniquement
    """
    photo_profil = serializers.ImageField(required=True)

    def validate_photo_profil(self, value):
        """
        Validation personnalisée de l'image
        """
        # Vérifier la taille (5 MB max)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("La taille de l'image ne doit pas dépasser 5 MB")
        
        # Vérifier le type de fichier
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Format d'image non supporté. Utilisez JPG, PNG ou GIF")
        
        return value


# ===================================================================
# 5. UPDATE USER (avec changement de mot de passe sécurisé)
# ===================================================================
class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour du profil utilisateur
    Permet de changer :
    - Nom, prénom, email
    - Photo de profil
    - Mot de passe (avec vérification de l'ancien)
    """
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False, min_length=8)
    photo_profil = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'nom', 
            'prenoms', 
            'email', 
            'photo_profil', 
            'current_password', 
            'new_password'
        ]

    def validate(self, data):
        """Validation globale"""
        user = self.instance
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        # Si changement de mot de passe demandé
        if new_password:
            # Vérifier que le mot de passe actuel est fourni
            if not current_password:
                raise serializers.ValidationError({
                    "current_password": "Vous devez fournir le mot de passe actuel pour changer de mot de passe."
                })
            
            # Vérifier que le mot de passe actuel est correct
            if not check_password(current_password, user.password):
                raise serializers.ValidationError({
                    "current_password": "Le mot de passe actuel est incorrect."
                })
            
            # Valider le nouveau mot de passe
            try:
                validate_password(new_password, user)
            except DjangoValidationError as e:
                raise serializers.ValidationError({
                    "new_password": list(e.messages)
                })
            
            # Hasher le nouveau mot de passe
            data['password'] = make_password(new_password)

        return data

    def update(self, instance, validated_data):
        """Mise à jour de l'utilisateur"""
        # Retirer les champs temporaires
        validated_data.pop('current_password', None)
        validated_data.pop('new_password', None)

        # Mise à jour du mot de passe si présent
        password = validated_data.pop('password', None)
        if password:
            instance.password = password

        # Mise à jour des autres champs
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


# ===================================================================
# 6. PASSWORD RESET (réinitialisation par email)
# ===================================================================
class PasswordResetRequestSerializer(serializers.Serializer):
    """Demande de réinitialisation par email"""
    email = serializers.EmailField()

    def validate_email(self, value):
        """Vérifier que l'email existe"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Aucun compte trouvé avec cet email.")
        return value


class PasswordResetCodeVerificationSerializer(serializers.Serializer):
    """Vérification du code de réinitialisation"""
    email = serializers.EmailField()
    code = serializers.CharField(max_length=100)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Confirmation du nouveau mot de passe"""
    email = serializers.EmailField()
    code = serializers.CharField(max_length=100)
    new_password = serializers.CharField(min_length=8)

    def validate_new_password(self, value):
        """Valider le nouveau mot de passe"""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value


# ===================================================================
# 7. SERIALIZERS SIMPLIFIÉS (lecture seule)
# ===================================================================
class UserSimpleSerializer(serializers.ModelSerializer):
    """Version simplifiée pour les listes"""
    photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'nom', 'prenoms', 'role', 'photo_url']
    
    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo_profil:
            if request:
                return request.build_absolute_uri(obj.photo_profil.url)
            return obj.photo_profil.url
        return None


class EmployeSimpleSerializer(serializers.ModelSerializer):
    """Version simplifiée pour les listes d'employés"""
    user = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = Employe
        fields = ['id', 'user', 'cin', 'contact', 'departement']