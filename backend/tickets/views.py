from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncMonth
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

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


class DashboardResumenView(APIView):
    """
    Único endpoint de agregación para el dashboard: devuelve todos los
    números ya calculados (conteos, distribución, tendencia, tiempo medio
    de resolución) — el frontend no recalcula nada sobre datos crudos.

    Filtro opcional por rango de fechas (?fecha_desde=AAAA-MM-DD y/o
    ?fecha_hasta=AAAA-MM-DD), aplicado sobre fecha_creacion para el
    alcance general, y sobre fecha_resolucion para la serie de "resueltos"
    de la tendencia (tiene más sentido medir resueltos por cuándo se
    resolvieron, no por cuándo se crearon).
    """

    def get(self, request):
        fecha_desde = request.query_params.get("fecha_desde")
        fecha_hasta = request.query_params.get("fecha_hasta")

        qs = Ticket.objects.all()
        if fecha_desde:
            qs = qs.filter(fecha_creacion__date__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha_creacion__date__lte=fecha_hasta)

        # Todos los estados/prioridades se inicializan a 0 para que el
        # frontend no tenga que comprobar claves ausentes.
        por_estado = {estado: 0 for estado, _ in Ticket.Estado.choices}
        for fila in qs.values("estado").annotate(total=Count("id")):
            por_estado[fila["estado"]] = fila["total"]

        por_prioridad = {prioridad: 0 for prioridad, _ in Ticket.Prioridad.choices}
        for fila in qs.values("prioridad").annotate(total=Count("id")):
            por_prioridad[fila["prioridad"]] = fila["total"]

        por_categoria = [
            {
                "categoria": fila["categoria__nombre"],
                "color": fila["categoria__color"],
                "total": fila["total"],
            }
            for fila in qs.values("categoria__nombre", "categoria__color")
            .annotate(total=Count("id"))
            .order_by("-total")
        ]

        creados_por_mes = (
            qs.annotate(mes=TruncMonth("fecha_creacion"))
            .values("mes").annotate(total=Count("id")).order_by("mes")
        )

        resueltos_qs = Ticket.objects.filter(fecha_resolucion__isnull=False)
        if fecha_desde:
            resueltos_qs = resueltos_qs.filter(fecha_resolucion__date__gte=fecha_desde)
        if fecha_hasta:
            resueltos_qs = resueltos_qs.filter(fecha_resolucion__date__lte=fecha_hasta)
        resueltos_por_mes = (
            resueltos_qs.annotate(mes=TruncMonth("fecha_resolucion"))
            .values("mes").annotate(total=Count("id")).order_by("mes")
        )

        tendencia = {}
        for fila in creados_por_mes:
            clave = fila["mes"].strftime("%Y-%m")
            tendencia.setdefault(clave, {"periodo": clave, "creados": 0, "resueltos": 0})
            tendencia[clave]["creados"] = fila["total"]
        for fila in resueltos_por_mes:
            clave = fila["mes"].strftime("%Y-%m")
            tendencia.setdefault(clave, {"periodo": clave, "creados": 0, "resueltos": 0})
            tendencia[clave]["resueltos"] = fila["total"]
        tendencia = [tendencia[clave] for clave in sorted(tendencia.keys())]

        duracion_expr = ExpressionWrapper(
            F("fecha_resolucion") - F("fecha_creacion"), output_field=DurationField()
        )
        promedio = resueltos_qs.annotate(duracion=duracion_expr).aggregate(
            promedio=Avg("duracion")
        )["promedio"]
        tiempo_medio_resolucion_horas = (
            round(promedio.total_seconds() / 3600, 1) if promedio else None
        )

        return Response({
            "total_tickets": qs.count(),
            "por_estado": por_estado,
            "por_prioridad": por_prioridad,
            "por_categoria": por_categoria,
            "tendencia": tendencia,
            "tiempo_medio_resolucion_horas": tiempo_medio_resolucion_horas,
        })