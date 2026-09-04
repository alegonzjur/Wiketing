from django.db import models


class Categoria(models.Model):
    """
    Categoría compartida por Ticket y Guia (misma taxonomía para ambos,
    para poder relacionar guías con incidencias de la misma categoría).

    Gestionable desde la propia app (CRUD vía API) — sin fixtures ni
    choices fijas hardcodeadas, tal y como se pidió.
    """

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    color = models.CharField(
        max_length=7,
        default="#3B82F6",
        help_text="Color hexadecimal para la etiqueta visual (p.ej. #3B82F6).",
    )
    # Soft-delete: nunca se borra una categoría con tickets/guías asociadas,
    # se desactiva. Evita romper integridad referencial y conserva histórico.
    activa = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre