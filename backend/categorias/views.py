from rest_framework import viewsets
from .models import Categoria
from .serializers import CategoriaSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    filterset_fields = ["activa"]
    search_fields = ["nombre"]

    def get_queryset(self):
        qs = super().get_queryset()
        # Por defecto solo categorías activas (para selects de creación de
        # tickets/guías). ?todas=true las incluye todas, útil para una
        # pantalla de administración de categorías.
        if self.request.query_params.get("todas") != "true":
            qs = qs.filter(activa=True)
        return qs

    def perform_destroy(self, instance):
        # Soft-delete: nunca se borra de verdad una categoría (podría tener
        # tickets/guías asociadas), se desactiva.
        instance.activa = False
        instance.save()