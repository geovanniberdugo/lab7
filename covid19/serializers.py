from django.db.models import OuterRef, Subquery, Exists, Prefetch
from rest_framework import serializers
from cie10_django.models import CIE10
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.core import mail

from trazabilidad import services as trazabilidad_services
from trazabilidad import serializers as trazabilidad_se
from trazabilidad import models as trazabilidad_m
from . import models as m

class InfoPacienteSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.InfoPaciente
        fields = [
            'id',
            'paciente',
            'tipificacion',
            'telefono',
            # 'nacionalidad',
            # 'pais_ocurrencia',
            'municipio_ocurrencia',
            'area_ocurrencia',
            'localidad_ocurrencia',
            'barrio_ocurrencia',
            'lugar_ocurrencia',
            'vereda_zona',
            'ocupacion',
            'tipo_regimen',
            'eapb',
            'pertenencia_etnica',
            'grupo_etnico',
            'estrato',
            'grupos_poblacionales',
            'semanas_gestacion',
        ]

class PacienteSerializer(trazabilidad_se.PacienteSerializer):
    """Serializer para el modelo Paciente."""

    infos_covid19 = InfoPacienteSerializer(many=True)

    class Meta(trazabilidad_se.PacienteSerializer.Meta):
        fields = trazabilidad_se.PacienteSerializer.Meta.fields + ['email', 'infos_covid19', 'fecha_nacimiento']

class Cie10Serializer(serializers.ModelSerializer):

    text = serializers.SerializerMethodField()

    class Meta:
        model = CIE10
        fields = ['id', 'code', 'description', 'text']
    
    def get_text(self, obj):
        return '{} - {}'.format(obj.code, obj.description)

class UpgdSerializer(serializers.ModelSerializer):

    text = serializers.SerializerMethodField()

    class Meta:
        model = m.Upgd
        fields = ['id', 'nombre', 'codigo', 'text']
    
    def get_text(self, obj):
        return obj.nombre


class SendResultsEmailSerializer(serializers.Serializer):

    ingresos = serializers.ListField(
        allow_empty=False,
        child=serializers.IntegerField(),
    )

    @transaction.atomic
    def send(self, request):
        ingresos = (
            trazabilidad_m.Ingreso.objects
                .select_related('programa', 'analista__empleado', 'responsable_tecnico__empleado')
                .prefetch_related(
                    'reportes__objeto',
                    'muestras__tipo_muestra',
                    'muestras__informacion_general__upgd',
                    'muestras__pruebasrealizadas_set__metodo',
                    'muestras__pruebasrealizadas_set__prueba',
                    'muestras__pruebasrealizadas_set__resultados',
                    'muestras__informacion_general__info_paciente__paciente',
                    'muestras__informacion_general__municipio_upgd__departamento',
                    'muestras__informacion_general__info_paciente__municipio_ocurrencia__departamento',
                )
                .filter(id__in=self.validated_data['ingresos'])
        )

        def create_email(ingreso):
            data = trazabilidad_services.data_informe_resultados(ingreso, ingreso.muestras.all())
            pdf = trazabilidad_services.generate_results_pdf(request, data)

            subject, body = self.msg_text(self.is_positivo(ingreso))
            return mail.EmailMessage(
                body=body,
                subject=subject,
                to=self.recipients(ingreso),
                attachments=[('resultados.pdf', pdf, 'application/pdf')],
            )
        
        connection = mail.get_connection()
        connection.send_messages(map(lambda o: create_email(o), ingresos))

        ingresos.update(fecha_envio_resultados=timezone.now())
    
    def is_positivo(self, ingreso):
        query = trazabilidad_m.PruebasRealizadas.objects.filter(muestra=OuterRef('pk')).positivos()
        return any(ingreso.muestras.annotate(is_positivo=Exists(query)).values_list('is_positivo', flat=True))
    
    def msg_text(self, is_positivo):
        if is_positivo:
            return (
                'Resultados SARS-CoV-2 Positivos',
                ' Buen día, \n\n\n Estamos enviando en pdf resultados positivos para SARS-CoV-2 procesados en el Laboratorio Departamental de Salud Pública. \n\n Atentamente, \n\n\n ELCY SIBAJA ALEAN \n Coordinadora LDSP \n\n'
            )

        return (
            'Resultados SARS-CoV-2',
            ' Buen día, \n\n\n Estamos enviando en pdf resultados para SARS-CoV-2 procesados en el Laboratorio Departamental de Salud Pública. \n\n Atentamente, \n\n\n ELCY SIBAJA ALEAN \n Coordinadora LDSP \n\n'
        )

    def recipients(self, ingreso):
        muestra = ingreso.muestra

        mails = [
            # 'maillaboratorio@gmail.com',
            # muestra.solicitante.email,
            muestra.municipio_upgd.email,
        ]

        if muestra.paciente().email:
            mails.append(muestra.paciente().email)
        
        # if getattr(muestra.informacion_general.info_paciente.eapb, 'email', None):
        #     mails.append(muestra.informacion_general.info_paciente.eapb.email)

        return mails
