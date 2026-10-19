import django_filters
from .models import Ticket


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    """Permite filtrar por una lista separada por comas (?estado=abierto,en_progreso)
    en vez de un único valor exacto, sin tocar el modelo ni añadir un estado nuevo."""
    pass


class TicketFilter(django_filters.FilterSet):
    estado = CharInFilter(field_name="estado", lookup_expr="in")
    fecha_creacion_desde = django_filters.DateTimeFilter(field_name="fecha_creacion", lookup_expr="gte")
    fecha_creacion_hasta = django_filters.DateTimeFilter(field_name="fecha_creacion", lookup_expr="lte")

    class Meta:
        model = Ticket
        fields = ["estado", "tipo", "categoria", "prioridad", "asignado_a"]