from rest_framework import serializers
from django.db import transaction
from django.utils import timezone

from trazabilidad.models import Epsa, Municipio, Poblado, Prueba, Area
from .models import Paciente, CodigoPunto
from . import models

__author__ = 'tania'


class PruebaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Prueba."""

    class Meta:
        model = Prueba
        fields = ['id', 'nombre', 'area', 'duracion', 'resultados', 'metodos', 'valores_referencia']


class AreaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Prueba."""

    class Meta:
        model = Area
        fields = ['id', 'nombre', 'programa', 'temperatura_minima', 'temperatura_maxima', 'humedad_minima', 'humedad_maxima', 'oculto']


class MunicipioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Municipio."""

    class Meta:
        model = Municipio
        fields = ['id', 'nombre', 'departamento', 'codigo']


class PobladoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Poblado."""

    class Meta:
        model = Poblado
        fields = ['id', 'nombre', 'municipio', 'codigo', 'epsa']


class PacienteSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Paciente."""

    class Meta:
        model = Paciente
        fields = ['id', 'nombre', 'apellido', 'direccion', 'identificacion', 'tipo_identificacion', 'edad', 'tipo_edad', 'eps', 'sexo']


class CodigoPuntoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Codigo Punto."""

    punto_intradomiciliario = serializers.SerializerMethodField()

    class Meta:
        depth = 1
        model = CodigoPunto
        fields = ['id', 'codigo', 'direccion', 'lugar_toma', 'descripcion', 'fuente_abastecimiento', 'punto_intradomiciliario', 'poblado']

    def get_punto_intradomiciliario(self, obj):
        return obj.get_punto_intradomiciliario_display()


class EpsaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Epsa."""

    class Meta:
        model = Epsa
        fields = ['id', 'nombre', 'direccion', 'rup', 'nit', 'tipo']

class ProgramaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Programa
        fields = ['id', 'nombre']

class RecepcionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Recepción."""

    programa = ProgramaSerializer()
    areas = serializers.SerializerMethodField()
    solicitante = serializers.SerializerMethodField()
    estado_display = serializers.SerializerMethodField()

    class Meta:
        model = models.Recepcion
        fields = [
            'id',
            'areas',
            'estado',
            'programa',
            'radicado',
            'confirmada',
            'comentario',
            'solicitante',
            'cumplimiento',
            'estado_display',
            'fecha_recepcion',
            'url_editar_ingreso',
            'url_estado_ingreso',
            'url_radicado_ingreso',
        ]
    
    def get_areas(self, obj):
        return ' - '.join(map(lambda o: str(o), obj.areas)).title()
    
    def get_solicitante(self, obj):
        return str(obj.solicitante).title()
    
    def get_estado_display(self, obj):
        return obj.get_estado_display()


class AprobarInformeResultadosSerializer(serializers.Serializer):

    ingresos = serializers.ListField(
        allow_empty=False,
        child=serializers.IntegerField(),
    )

    @transaction.atomic
    def aprove(self):
        (
            models.Reporte.objects
                .no_aprobados()
                .by_ingresos(self.validated_data['ingresos'])
        ).update(fecha_aprobacion=timezone.now())
