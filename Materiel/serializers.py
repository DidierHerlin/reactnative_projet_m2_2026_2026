from rest_framework import serializers
from .models import Materiel


class MaterielSerializer(serializers.ModelSerializer):
    etat_display = serializers.CharField(source='get_etat_display', read_only=True)

    class Meta:
        model = Materiel
        fields = [
            'id',
            'numero_materiel',
            'design',
            'etat',
            'etat_display',
            'quantite',
            'date_ajout',
            'date_modification',
        ]
        read_only_fields = ['id', 'etat_display', 'date_ajout', 'date_modification']

    def validate_numero_materiel(self, value):
        """Unicité du numéro matériel (ignore l'instance actuelle en cas de mise à jour)."""
        instance = self.instance
        qs = Materiel.objects.filter(numero_materiel=value)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ce numéro de matériel existe déjà.")
        return value

    def validate_quantite(self, value):
        if value < 0:
            raise serializers.ValidationError("La quantité ne peut pas être négative.")
        return value
