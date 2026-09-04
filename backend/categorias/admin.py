from django.contrib import admin
from .models import Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "color", "activa", "fecha_actualizacion")
    list_filter = ("activa",)
    search_fields = ("nombre",)