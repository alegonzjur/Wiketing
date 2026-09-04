"""
Signals de auditoría para Ticket.

Decisión de diseño: la auditoría vive aquí (a nivel de modelo) y no en las
vistas, para que sea imposible olvidarse de registrar un cambio — cualquier
código que guarde un Ticket (API, admin, shell, comando de management)
queda auditado por igual.

Limitación conocida y documentada (no oculta): el modelo no tiene acceso a
`request.user`. Quien guarde el ticket debe asignar
`ticket._usuario_modificacion = request.user` ANTES de llamar a `.save()`
si quiere que el historial refleje quién hizo el cambio. Si no se asigna,
el historial queda con `usuario=None`, que es el comportamiento correcto
para cambios automáticos (p.ej. el futuro cron de abandono).
"""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Ticket, HistorialCambios, Comentario

CAMPOS_AUDITADOS = ["estado", "prioridad", "asignado_a"]


@receiver(pre_save, sender=Ticket)
def cachear_valores_previos(sender, instance, **kwargs):
    """Guarda el estado del ticket en BD antes de esta escritura, para
    poder compararlo en post_save. En creación (sin pk todavía) no hay
    nada que comparar."""
    if instance.pk:
        try:
            instance._valores_previos = Ticket.objects.get(pk=instance.pk)
        except Ticket.DoesNotExist:
            instance._valores_previos = None
    else:
        instance._valores_previos = None


@receiver(post_save, sender=Ticket)
def registrar_historial_y_actividad(sender, instance, created, **kwargs):
    if created:
        return  # la creación no es un "cambio", no genera historial

    anterior = getattr(instance, "_valores_previos", None)
    if anterior is None:
        return

    usuario_modificacion = getattr(instance, "_usuario_modificacion", None)
    hubo_cambio_relevante = False

    for campo in CAMPOS_AUDITADOS:
        valor_anterior = getattr(anterior, campo)
        valor_nuevo = getattr(instance, campo)
        if valor_anterior != valor_nuevo:
            HistorialCambios.objects.create(
                ticket=instance,
                campo_modificado=campo,
                valor_anterior=str(valor_anterior) if valor_anterior is not None else "",
                valor_nuevo=str(valor_nuevo) if valor_nuevo is not None else "",
                usuario=usuario_modificacion,
            )
            hubo_cambio_relevante = True

    if not hubo_cambio_relevante:
        return

    # No refrescar fecha_ultima_actividad cuando el cambio ES el propio
    # marcado automático de abandono: haría que el ticket nunca pudiera
    # marcarse como abandonado (el cron reiniciaría su propio contador).
    es_abandono_automatico = (
        instance.estado == Ticket.Estado.ABANDONADO
        and instance.abandono_origen == Ticket.AbandonoOrigen.AUTOMATICO
    )
    if not es_abandono_automatico:
        # .update() en vez de .save() para no volver a disparar estos
        # mismos signals (evita recursión).
        Ticket.objects.filter(pk=instance.pk).update(fecha_ultima_actividad=timezone.now())


@receiver(post_save, sender=Comentario)
def actividad_por_comentario(sender, instance, created, **kwargs):
    """Un comentario nuevo también cuenta como actividad del ticket."""
    if created:
        Ticket.objects.filter(pk=instance.ticket_id).update(
            fecha_ultima_actividad=timezone.now()
        )