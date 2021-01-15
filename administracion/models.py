from django.conf import settings
from django.db import models
from . import managers

class Empleado(models.Model):
    """Modelo usado para guardar la informacion de los empleados del laboratorio."""

    # opciones
    PLANTA = 'P'
    CONTRATISTA = 'C'
    OPCIONES_TIPO_EMPLEADO = (
        (PLANTA, 'PLANTA'),
        (CONTRATISTA, 'CONTRATISTA'),
    )

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='empleado', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1, choices=OPCIONES_TIPO_EMPLEADO)
    areas = models.ManyToManyField('trazabilidad.Area')
    responsable_tecnico = models.BooleanField(default=False)
    codigo = models.CharField(max_length=150, blank=True)

    objects = managers.EmpleadoManager()

    class Meta:
        verbose_name = 'empleado'
        verbose_name_plural = 'empleados'
        permissions = [
            ('can_buscar_ingresos', 'Puede buscar ingresos'),
            ('can_editar_ingresos', 'Puede editar ingresos'),
            ('can_see_analisis', 'Puede ver pagina de analisis'),
            ('can_aprobar_informes', 'Puede aprobar informes de resultado'),
            ('can_devolver_ingreso_analisis', 'Puede devolver ingresos a anlisis'),
            ('can_consultar_resultados_covid', 'Puede consultar resultados de covid'),
            ('can_exportar_ficha_excel', 'Puede exportar a excel las fichas de covid'),
            ('can_mail_resultados_covid', 'Puede enviar resultados de covid por mail'),
            ('can_see_ingresos_recepcionados', 'Puede ver pagina de ingresos recepcionados'),
            ('can_see_ingresos_todos_programas', 'Puede ver ingresos de todos los programas'),
            ('can_analizar_todos_programas', 'Puede ingresar analisis de todos los programas'),
            ('can_imprimir_lote_fichas_covid', 'Puede imprimir en lote las fichas y resultados de covid'),
            ('can_ingresar_muestras_programas_clinicos', 'Puede ingresar muestras de programas clinicos'),
            ('can_ingresar_muestras_programas_ambientes', 'Puede ingresar muestras de programas de ambientes'),
        ]

    def __str__(self):
        return '{} {}'.format(self.usuario.first_name, self.usuario.last_name)

class ConfigGeneral(models.Model):
    
    firma_automatica_reporte = models.BooleanField(default=False, verbose_name='Firma de reporte automatica')
