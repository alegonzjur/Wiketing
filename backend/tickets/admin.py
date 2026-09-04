from django.contrib import admin
from .models import Ticket, HistorialCambios, Comentario


class HistorialCambiosInline(admin.TabularInline):
    model = HistorialCambios
    extra = 0
    readonly_fields = ("campo_modificado", "valor_anterior", "valor_nuevo", "usuario", "fecha")
    can_delete = False


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    readonly_fields = ("usuario", "fecha")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id", "titulo", "tipo", "estado", "prioridad", "categoria",
        "asignado_a", "fecha_ultima_actividad",
    )
    list_filter = ("tipo", "estado", "prioridad", "categoria")
    search_fields = ("titulo", "descripcion")
    inlines = [ComentarioInline, HistorialCambiosInline]
    readonly_fields = ("fecha_creacion", "fecha_actualizacion", "fecha_ultima_actividad")


@admin.register(HistorialCambios)
class HistorialCambiosAdmin(admin.ModelAdmin):
    list_display = ("ticket", "campo_modificado", "valor_anterior", "valor_nuevo", "usuario", "fecha")
    list_filter = ("campo_modificado",)