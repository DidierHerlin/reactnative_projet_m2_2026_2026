from django.db import models


class Materiel(models.Model):
    ETAT_CHOICES = [
        ('bon', 'Bon État'),
        ('mauvais', 'Mauvais'),
        ('abime', 'Abimé'),
    ]

    numero_materiel = models.CharField(max_length=100, unique=True, verbose_name="Numéro Matériel")
    design = models.CharField(max_length=255, verbose_name="Désignation")
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='bon', verbose_name="État")
    quantite = models.PositiveIntegerField(default=1, verbose_name="Quantité")
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Matériel"
        verbose_name_plural = "Matériels"
        ordering = ['-date_ajout']

    def __str__(self):
        return f"{self.numero_materiel} - {self.design} ({self.get_etat_display()})"
