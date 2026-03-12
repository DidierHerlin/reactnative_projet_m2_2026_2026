from django.urls import path
from .views import (
    MaterielListCreateView,
    MaterielDetailView,
    MaterielStatistiquesView,
)

urlpatterns = [
    # ── CRUD Matériel ──────────────────────────────────────────────
    path('', MaterielListCreateView.as_view(), name='materiels-list-create'),
    path('<int:pk>/', MaterielDetailView.as_view(), name='materiels-detail'),

    # ── Statistiques ───────────────────────────────────────────────
    path('stats/', MaterielStatistiquesView.as_view(), name='materiels-stats'),
]
