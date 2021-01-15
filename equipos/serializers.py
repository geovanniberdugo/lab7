from rest_framework import serializers
from .models import Equipo

__author__ = 'tania'

class EquipoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Equipo."""

    class Meta:
        model = Equipo
        fields = ['id', 'nombre', 'codigo', 'temperatura_minima', 'temperatura_maxima', 'area']
