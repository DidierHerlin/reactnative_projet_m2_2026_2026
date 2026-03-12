from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count

from .models import Materiel
from .serializers import MaterielSerializer


# ====================== LISTE ET CRÉATION ======================
class MaterielListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retourne la liste de tous les matériels."""
        materiels = Materiel.objects.all()
        serializer = MaterielSerializer(materiels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Crée un nouveau matériel (employé ou admin)."""
        serializer = MaterielSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ====================== DÉTAIL, MODIFICATION ET SUPPRESSION ======================
class MaterielDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Materiel.objects.get(pk=pk)
        except Materiel.DoesNotExist:
            return None

    def get(self, request, pk):
        """Retourne le détail d'un matériel."""
        materiel = self.get_object(pk)
        if not materiel:
            return Response({'error': 'Matériel introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MaterielSerializer(materiel)
        return Response(serializer.data)

    def put(self, request, pk):
        """Mise à jour complète d'un matériel."""
        materiel = self.get_object(pk)
        if not materiel:
            return Response({'error': 'Matériel introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MaterielSerializer(materiel, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        """Mise à jour partielle d'un matériel."""
        materiel = self.get_object(pk)
        if not materiel:
            return Response({'error': 'Matériel introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MaterielSerializer(materiel, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        """Supprime un matériel."""
        materiel = self.get_object(pk)
        if not materiel:
            return Response({'error': 'Matériel introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        materiel.delete()
        return Response({'message': 'Matériel supprimé avec succès.'}, status=status.HTTP_204_NO_CONTENT)


# ====================== STATISTIQUES ======================
class MaterielStatistiquesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retourne les statistiques agrégées :
        - quantite_totale : somme de toutes les quantités
        - nombre_total : nombre de lignes (références) matériels
        - par_etat : {bon, mauvais, abime} → { nombre, quantite }
        """
        total_quantite = Materiel.objects.aggregate(total=Sum('quantite'))['total'] or 0
        total_nombre = Materiel.objects.count()

        etats = ['bon', 'mauvais', 'abime']
        par_etat = {}
        for etat in etats:
            agg = Materiel.objects.filter(etat=etat).aggregate(
                nombre=Count('id'),
                quantite=Sum('quantite')
            )
            par_etat[etat] = {
                'nombre': agg['nombre'] or 0,
                'quantite': agg['quantite'] or 0,
                'label': dict(Materiel.ETAT_CHOICES).get(etat, etat),
            }

        return Response({
            'quantite_totale': total_quantite,
            'nombre_total': total_nombre,
            'par_etat': par_etat,
        }, status=status.HTTP_200_OK)
