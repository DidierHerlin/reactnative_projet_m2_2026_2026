from django.contrib import admin
from .models import Materiel


@admin.register(Materiel)
class MaterielAdmin(admin.ModelAdmin):
    list_display = ['numero_materiel', 'design', 'etat', 'quantite', 'date_ajout']
    list_filter = ['etat']
    search_fields = ['numero_materiel', 'design']
    ordering = ['-date_ajout']
    readonly_fields = ['date_ajout', 'date_modification']
