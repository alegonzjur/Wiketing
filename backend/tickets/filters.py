import django_filters
from .models import Ticket


class TicketFilter(django_filters.FilterSet):
    fecha_creacion_desde = django_filters.DateTimeFilter(field_name="fecha_creacion", lookup_expr="gte")
    fecha_creacion_hasta = django_filters.DateTimeFilter(field_name="fecha_creacion", lookup_expr="lte")

    class Meta:
        model = Ticket
        fields = ["estado", "tipo", "categoria", "prioridad", "asignado_a"]