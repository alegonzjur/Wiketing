from rest_framework import viewsets

from .models import Ticket, Comentario
from .serializers import (
    TicketListSerializer,
    TicketDetailSerializer,
    TicketWriteSerializer,
    ComentarioSerializer,
)
from .filters import TicketFilter


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related(
        "categoria", "creado_por", "asignado_a"
    ).prefetch_related("historial__usuario", "comentarios__usuario")
    filterset_class = TicketFilter
    search_fields = ["titulo", "descripcion"]

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        if self.action in ("create", "update", "partial_update"):
            return TicketWriteSerializer
        return TicketDetailSerializer

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

    def perform_update(self, serializer):
        # Necesario para que el signal de auditoría (tickets/signals.py)
        # sepa qué usuario hizo el cambio, en vez de registrarlo como
        # automático (usuario=None). Mismo objeto en memoria que usará
        # el signal post_save.
        serializer.instance._usuario_modificacion = self.request.user
        serializer.save()


class ComentarioViewSet(viewsets.ModelViewSet):
    queryset = Comentario.objects.select_related("usuario", "ticket")
    serializer_class = ComentarioSerializer
    filterset_fields = ["ticket"]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)