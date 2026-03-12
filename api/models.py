# api/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator
import os


# ====================== FONCTION POUR LE CHEMIN DE L'IMAGE ======================
def user_profile_image_path(instance, filename):
    """
    Génère un chemin personnalisé pour les photos de profil
    Exemple: profile_photos/user_123/photo.jpg
    """
    ext = filename.split('.')[-1]
    filename = f"photo_{instance.id}.{ext}"
    return os.path.join('profile_photos', f'user_{instance.id}', filename)


# ====================== USER MANAGER ======================
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        return self.create_user(email, password, **extra_fields)


# ====================== USER MODEL ======================
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('employe', 'Employé'),
        ('admin', 'Administrateur'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employe')
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=150)

    # ============ PHOTO DE PROFIL ============
    photo_profil = models.ImageField(
        upload_to=user_profile_image_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])],
        help_text="Photo de profil (optionnel). Formats acceptés: JPG, PNG, GIF"
    )
    # =========================================

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # ============ CHAMPS POUR LA RÉINITIALISATION ============
    reset_token = models.CharField(max_length=10, blank=True, null=True)
    reset_token_expiration = models.DateTimeField(blank=True, null=True)
    # =========================================================

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nom", "prenoms", "role"]

    objects = UserManager()

    def __str__(self):
        return f"{self.nom} {self.prenoms} ({self.get_role_display()})"

    def get_photo_url(self):
        """
        Retourne l'URL de la photo de profil ou None si pas de photo
        """
        if self.photo_profil:
            return self.photo_profil.url
        return None

    def has_photo(self):
        """
        Vérifie si l'utilisateur a une photo de profil
        """
        return bool(self.photo_profil)


# ====================== SIGNALS ======================
@receiver(pre_save, sender=User)
def rendre_admin_complet(sender, instance, **kwargs):
    """Seuls les comptes 'admin' ont les droits admin Django"""
    if instance.role == 'admin':
        instance.is_staff = True
        instance.is_superuser = True
    else:
        instance.is_staff = False
        instance.is_superuser = False


@receiver(post_save, sender=User)
def log_creation_admin(sender, instance, created, **kwargs):
    if created and instance.role == 'admin':
        print(f"\n✅ ADMIN CRÉÉ → {instance.email} | Accès admin activé !\n")


# ====================== SIGNAL POUR SUPPRIMER L'ANCIENNE PHOTO ======================
@receiver(pre_save, sender=User)
def delete_old_profile_photo(sender, instance, **kwargs):
    """
    Supprime l'ancienne photo de profil lorsqu'une nouvelle est uploadée
    """
    if not instance.pk:
        return False

    try:
        old_user = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return False

    # Si l'ancienne photo existe et qu'elle est différente de la nouvelle
    if old_user.photo_profil and old_user.photo_profil != instance.photo_profil:
        # Supprimer l'ancien fichier du système de fichiers
        if os.path.isfile(old_user.photo_profil.path):
            os.remove(old_user.photo_profil.path)


# ====================== PROFIL EMPLOYE ======================
class Employe(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_employe')
    cin = models.CharField(max_length=50, unique=True)
    contact = models.CharField(max_length=20)
    departement = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.cin} - {self.user.nom} {self.user.prenoms}"

    def get_photo_url(self):
        """Raccourci pour accéder à la photo via le profil employé"""
        return self.user.get_photo_url()


# ====================== PROFIL ADMIN ======================
class Administrateur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_admin')
    fonction = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Admin - {self.user.nom} {self.user.prenoms}"

    def get_photo_url(self):
        """Raccourci pour accéder à la photo via le profil admin"""
        return self.user.get_photo_url()