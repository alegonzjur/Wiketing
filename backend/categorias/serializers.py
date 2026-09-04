from rest_framework import serializers
from .models import Categoria


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion", "color", "activa", "fecha_creacion", "fecha_actualizacion"]
        read_only_fields = ["id", "fecha_creacion", "fecha_actualizacion"]