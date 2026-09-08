from rest_framework import viewsets
from .models import Categoria
from .serializers import CategoriaSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    filterset_fields = ["activa"]
    search_fields = ["nombre"]
    # Sin paginación: es una tabla de referencia pequeña usada como
    # desplegable en el frontend, no una lista que crece sin límite como
    # los tickets. Con paginación, un desplegable con más categorías que
    # el page_size dejaría de mostrar las últimas sin que se note por qué.
    pagination_class = None

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