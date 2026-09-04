from django.conf import settings
from django.db import models


class Ticket(models.Model):
    """
    Entidad única para incidencias y tareas (campo `tipo`), en vez de dos
    modelos separados: el dashboard, los estados y el flujo de seguimiento
    son los mismos para ambos casos — separar solo duplicaría lógica.
    """

    class Tipo(models.TextChoices):
        INCIDENCIA = "incidencia", "Incidencia"
        TAREA = "tarea", "Tarea"

    class Estado(models.TextChoices):
        ABIERTO = "abierto", "Abierto"
        EN_PROGRESO = "en_progreso", "En progreso"
        RESUELTO = "resuelto", "Resuelto"
        ABANDONADO = "abandonado", "Abandonado"
        CERRADO = "cerrado", "Cerrado"

    class Prioridad(models.TextChoices):
        BAJA = "baja", "Baja"
        MEDIA = "media", "Media"
        ALTA = "alta", "Alta"
        CRITICA = "critica", "Crítica"

    class AbandonoOrigen(models.TextChoices):
        AUTOMATICO = "automatico", "Automático (30 días sin actividad)"
        MANUAL = "manual", "Manual"

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.INCIDENCIA)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ABIERTO)
    prioridad = models.CharField(max_length=20, choices=Prioridad.choices, default=Prioridad.MEDIA)

    categoria = models.ForeignKey(
        "categorias.Categoria",
        on_delete=models.PROTECT,  # nunca se borra una categoría con tickets asociados
        related_name="tickets",
    )

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tickets_creados",
    )
    asignado_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="tickets_asignados",
        null=True,
        blank=True,
        help_text="Vacío en uso single-user; preparado para asignación cuando haya más usuarios.",
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    # Campo clave para la regla de abandono automático (Fase 8): el comando
    # programado compara esta fecha con "ahora - 30 días". Se actualiza
    # automáticamente vía signals (ver tickets/signals.py) en cada cambio
    # relevante o comentario nuevo — NUNCA cuando el propio cambio es el
    # marcado automático de abandono (ver razón en signals.py).
    fecha_ultima_actividad = models.DateTimeField(auto_now_add=True)

    abandono_origen = models.CharField(
        max_length=20,
        choices=AbandonoOrigen.choices,
        null=True,
        blank=True,
        help_text="Solo relevante cuando estado='abandonado'.",
    )

    tiempo_estimado = models.DurationField(null=True, blank=True)
    tiempo_real = models.DurationField(null=True, blank=True)

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ["-fecha_creacion"]
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["fecha_ultima_actividad"]),
        ]

    def __str__(self):
        return f"#{self.pk} — {self.titulo}"


class HistorialCambios(models.Model):
    """
    Auditoría de cambios sobre un Ticket. Se rellena automáticamente vía
    signals (tickets/signals.py) — ninguna vista debe crear entradas aquí
    a mano, para no tener rutas de cambio sin auditar.
    """

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="historial")
    campo_modificado = models.CharField(max_length=50)
    valor_anterior = models.TextField(blank=True)
    valor_nuevo = models.TextField(blank=True)
    # null=True es intencional: un cambio con usuario=None es un cambio
    # automático (p.ej. el cron de abandono), no un usuario sin asignar.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historial de cambio"
        verbose_name_plural = "Historial de cambios"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Ticket #{self.ticket_id}: {self.campo_modificado} → {self.valor_nuevo}"


class Comentario(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comentarios")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ["fecha"]

    def __str__(self):
        return f"Comentario de {self.usuario} en Ticket #{self.ticket_id}"