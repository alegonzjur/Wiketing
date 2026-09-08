from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from categorias.serializers import CategoriaSerializer
from .models import Ticket, HistorialCambios, Comentario

Usuario = get_user_model()


class UsuarioResumenSerializer(serializers.ModelSerializer):
    """Versión mínima de Usuario para anidar en tickets/comentarios/historial
    — nunca se expone la lista completa de campos del usuario aquí."""

    class Meta:
        model = Usuario
        fields = ["id", "username", "first_name", "last_name"]


class HistorialCambiosSerializer(serializers.ModelSerializer):
    usuario = UsuarioResumenSerializer(read_only=True)

    class Meta:
        model = HistorialCambios
        fields = ["id", "campo_modificado", "valor_anterior", "valor_nuevo", "usuario", "fecha"]


class ComentarioSerializer(serializers.ModelSerializer):
    usuario = UsuarioResumenSerializer(read_only=True)

    class Meta:
        model = Comentario
        fields = ["id", "ticket", "usuario", "texto", "fecha"]
        read_only_fields = ["id", "usuario", "fecha"]


class TicketListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados (tabla de tickets, dashboard) — sin
    historial ni comentarios completos, que solo hacen falta en detalle."""

    categoria = CategoriaSerializer(read_only=True)
    creado_por = UsuarioResumenSerializer(read_only=True)
    asignado_a = UsuarioResumenSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id", "titulo", "tipo", "estado", "prioridad", "categoria",
            "creado_por", "asignado_a", "fecha_creacion",
            "fecha_ultima_actividad", "fecha_resolucion",
        ]


class TicketDetailSerializer(serializers.ModelSerializer):
    """Serializer de lectura para el detalle: categoría y usuarios
    anidados completos, más historial y comentarios."""

    categoria = CategoriaSerializer(read_only=True)
    creado_por = UsuarioResumenSerializer(read_only=True)
    asignado_a = UsuarioResumenSerializer(read_only=True)
    historial = HistorialCambiosSerializer(many=True, read_only=True)
    comentarios = ComentarioSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id", "titulo", "descripcion", "tipo", "estado", "prioridad",
            "categoria", "creado_por", "asignado_a",
            "fecha_creacion", "fecha_actualizacion", "fecha_resolucion",
            "fecha_ultima_actividad", "abandono_origen",
            "tiempo_estimado", "tiempo_real",
            "historial", "comentarios",
        ]


class TicketWriteSerializer(serializers.ModelSerializer):
    """Serializer de escritura: solo espera IDs (categoria, asignado_a),
    nunca objetos anidados. `creado_por` nunca se acepta desde fuera —
    lo asigna la vista a partir de request.user (ver tickets/views.py)."""

    class Meta:
        model = Ticket
        fields = [
            "id", "titulo", "descripcion", "tipo", "estado", "prioridad",
            "categoria", "asignado_a", "fecha_resolucion",
            "abandono_origen", "tiempo_estimado", "tiempo_real",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        estado_nuevo = attrs.get("estado", getattr(self.instance, "estado", None))
        estado_anterior = getattr(self.instance, "estado", None) if self.instance else None

        # abandono_origen nunca lo manda el cliente a mano: si marca
        # estado=abandonado por la API, SIEMPRE es manual (el marcado
        # automático lo hace el comando de la Fase 8 directamente sobre
        # el modelo, sin pasar por este serializer). Así evitamos que
        # alguien falsifique un abandono como "automatico" desde fuera.
        if estado_nuevo == Ticket.Estado.ABANDONADO:
            attrs["abandono_origen"] = Ticket.AbandonoOrigen.MANUAL
        elif estado_nuevo is not None and estado_nuevo != Ticket.Estado.ABANDONADO:
            attrs["abandono_origen"] = None

        # fecha_resolucion: se fija sola al entrar en "resuelto" (si el
        # cliente no la manda explícitamente) y se limpia al salir de ese
        # estado. Sin esto, el tiempo medio de resolución del dashboard
        # (Fase 6) no tendría datos con los que calcularse.
        if estado_nuevo == Ticket.Estado.RESUELTO and estado_anterior != Ticket.Estado.RESUELTO:
            attrs.setdefault("fecha_resolucion", timezone.now())
        elif estado_anterior == Ticket.Estado.RESUELTO and estado_nuevo != Ticket.Estado.RESUELTO:
            attrs["fecha_resolucion"] = None

        return attrs