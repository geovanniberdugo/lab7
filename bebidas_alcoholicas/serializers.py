from rest_framework import serializers
from .models import Producto


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo de Producto."""

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'grupo']
