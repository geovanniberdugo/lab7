from rest_framework import serializers
from .models import Subcategoria, Categoria


class SubcategoriaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Subcategoria."""

    class Meta:
        model = Subcategoria
        fields = ['id', 'codigo', 'descripcion', 'categoria']


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo de Categoria."""

    class Meta:
        model = Categoria
        fields = ['id', 'codigo', 'descripcion', 'grupo']
