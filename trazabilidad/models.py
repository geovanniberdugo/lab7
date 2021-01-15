import re
import barcode
import logging
import operator
from django.core.files.storage import default_storage
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from contextlib import suppress
from django.urls import reverse
from django.db.models import Q
from django.db import models
from polymorphic.models import PolymorphicModel

from common.models import EstadoMixin, UltimaModificacionMixin
from .managers import ProgramaManager, PruebaQuerySet
from .utils import nuevo_radicado
from . import managers
from . import enums

logger = logging.getLogger(__name__)


class Programa(models.Model):
    """Modelo usado para guardar los programas que existen en un laboratorio."""

    nombre = models.CharField(max_length=100)
    codigo = models.CharField('código', max_length=100)

    # managers
    objects = ProgramaManager()

    class Meta:
        verbose_name = 'programa'
        verbose_name_plural = 'programas'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        self.codigo = self.codigo.lower()
        super(Programa, self).save(*args, **kwargs)


class Area(models.Model):
    """Modelo usado para guardar las áreas que de cada programa."""

    nombre = models.CharField(max_length=100)
    programa = models.ForeignKey(Programa, related_name='areas', on_delete=models.CASCADE)
    temperatura_minima = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    temperatura_maxima = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    humedad_minima = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    humedad_maxima = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    oculto = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'area'
        verbose_name_plural = 'areas'

    def __str__(self):
        return self.nombre.title()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(Area, self).save(*args, **kwargs)


class RegistroTemperaturaArea(models.Model):
    """Modelo usado para registrar las temperaturas diarias de las areas."""

    # opciones
    CENTIGRADOS = 'C'
    FARHENHEIT = 'F'
    UNIDADES = (
        (CENTIGRADOS, 'Celsius'),
        (FARHENHEIT, 'Farhenheit'),
    )

    area = models.ForeignKey(Area, related_name='registros', on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField()
    temperatura = models.DecimalField(max_digits=7, decimal_places=3)
    humedad = models.DecimalField(max_digits=7, decimal_places=3)
    unidad = models.CharField(max_length=1, choices=UNIDADES)
    observaciones = models.TextField()
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = 'registro de temperatura area'
        verbose_name_plural = 'registros de temperatura area'

    def __str__(self):
        return 'Registro de %(temperatura)f°%(unidad)s y %(humedad)f de Humedad para %(area)s' % {
            'temperatura': self.temperatura, 'unidad': self.unidad,
            'area': self.area.nombre, 'humedad': self.humedad
        }

    def save(self, *args, **kwargs):
        self.observaciones = self.observaciones.lower()
        super(RegistroTemperaturaArea, self).save(*args, **kwargs)

    def alerta(self):
        """Retorna Verdadero si se paso de el rango"""
        if self.unidad == self.CENTIGRADOS:
            temperatura = self.temperatura
        else:
            from equipos.utils import convertidor_unidad_temperatura
            temperatura = convertidor_unidad_temperatura(self.temperatura, self.unidad, self.CENTIGRADOS)

        if temperatura > self.area.temperatura_maxima or temperatura < self.area.temperatura_minima:
            return True
        elif self.humedad > self.area.humedad_maxima or self.humedad < self.area.humedad_minima:
            return True
        return False


class ResultadoPrueba(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los resultados posibles de las pruebas que se hacen en el laboratorio."""

    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'resultado'
        verbose_name_plural = 'resultados'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(ResultadoPrueba, self).save(*args, **kwargs)


class Metodo(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los métodos usados en las pruebas."""

    nombre = models.CharField(max_length=100)
    objeto = models.CharField(max_length=200)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'metodo'
        verbose_name_plural = 'metodos'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        self.objeto = self.objeto.lower()
        super(Metodo, self).save(*args, **kwargs)


class Prueba(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar las pruebas que se realizan en cada área."""

    nombre = models.CharField(max_length=100)
    area = models.ForeignKey(Area, related_name='pruebas', on_delete=models.CASCADE)
    duracion = models.DurationField('duración')
    resultados = models.ManyToManyField(ResultadoPrueba, related_name='pruebas')
    metodos = models.ManyToManyField(Metodo, related_name='pruebas')
    valores_referencia = models.CharField(max_length=100, verbose_name='valores de referencia', blank=True)

    # managers
    objects = PruebaQuerySet.as_manager()

    class Meta:
        ordering = ['nombre']
        verbose_name = 'prueba'
        verbose_name_plural = 'pruebas'

    def __str__(self):
        return self.nombre.upper()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(Prueba, self).save(*args, **kwargs)

        aguas = Programa.objects.aguas()
        if self.area.programa == aguas:
            if self.estado == EstadoMixin.INACTIVO:
                pruebas = PruebasRealizadas.objects.filter(estado=PruebasRealizadas.CONSERVACION, prueba=self)
                pruebas.delete()
            else:
                ingresos = Recepcion.objects.filter(programa=aguas)
                ingresos = ingresos.exclude(Q(estado=Recepcion.RECHAZADO) | Q(estado_analista=Recepcion.RECHAZADO))
                ingresos = ingresos.exclude(reportes__confirmado=True)
                ingresos = ingresos.exclude(muestras__pruebas=self)

                for ingreso in ingresos:
                    if ingreso.cumplimiento < 100:
                        for muestra in ingreso.muestras.non_polymorphic().all():
                            if muestra.areas.filter(id=self.area.id).exists():
                                PruebasRealizadas.objects.create(muestra=muestra, prueba=self)


class MotivoRechazo(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los motivos por el cual se puede rechazar una muestra que llega al laboratorio."""

    motivo = models.CharField(max_length=250)

    class Meta:
        verbose_name = 'motivo de rechazo'
        verbose_name_plural = 'motivos de rechazo'

    def __str__(self):
        return self.motivo.capitalize()

    def save(self, *args, **kwargs):
        self.motivo = self.motivo.lower()
        super(MotivoRechazo, self).save(*args, **kwargs)


class Recepcion(models.Model):
    """Modelo usado para guardar los registros de recepción de las muestras que llegan a un laboratorio."""

    # opciones
    ACEPTADO = 'A'
    RECHAZADO = 'R'
    ESTADOS_RECEPCIONISTA = (
        (ACEPTADO, 'Aceptado para verificación'),
        (RECHAZADO, 'Rechazado'),
    )

    ESTADOS_ANALISTA = (
        (ACEPTADO, 'Aceptado'),
        (RECHAZADO, 'Rechazado'),
    )

    programa = models.ForeignKey(Programa, on_delete=models.CASCADE)
    indice_radicado = models.BigIntegerField()
    fecha_radicado = models.DateTimeField('fecha de radicación', auto_now_add=True)
    fecha_recepcion = models.DateTimeField('fecha de recepción')
    recepcionista = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='ingresos_recepcionista', on_delete=models.CASCADE)
    estado = models.CharField(max_length=1, blank=True, choices=ESTADOS_RECEPCIONISTA)
    observaciones = models.TextField(blank=True)
    motivo_rechazo = models.ManyToManyField(MotivoRechazo, verbose_name='motivos de rechazo', blank=True, related_name='rechazos_recepcionista')
    confirmada = models.BooleanField(default=False)
    fecha_confirmacion = models.DateTimeField('fecha de confirmación', blank=True, null=True)
    confirmado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', on_delete=models.SET_NULL, blank=True, null=True)
    comentario = models.CharField(max_length=300, blank=True,
                                  help_text='Por favor indique que acción tomo con el ingreso respecto al rechazo del analista.')

    # Confirmacion analista
    estado_analista = models.CharField('estado', max_length=1, blank=True, choices=ESTADOS_ANALISTA)
    observaciones_analista = models.TextField('observaciones', blank=True)
    motivo_rechazo_analista = models.ManyToManyField(MotivoRechazo, verbose_name='motivos de rechazo', blank=True,
                                                     related_name='rechazos_analista')
    fecha_estado_analista = models.DateTimeField('fecha de estado', blank=True, null=True)
    analista = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='ingresos_analista', on_delete=models.SET_NULL)
    responsable_tecnico = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='ingresos_responsable_tecnico', on_delete=models.SET_NULL)
    fecha_envio_resultados = models.DateTimeField(blank=True, null=True)

    # managers
    objects = managers.RecepcionManager()

    class Meta:
        ordering = ['-indice_radicado']
        verbose_name = 'recepción'
        verbose_name_plural = 'recepciones'

    def __str__(self):
        return self.radicado

    def save(self, *args, **kwargs):
        if self.observaciones:
            self.observaciones = self.observaciones.lower()

        if self.comentario:
            self.comentario = self.comentario.lower()

        if self.observaciones_analista:
            self.observaciones_analista = self.observaciones_analista.lower()

        if not self.id:
            with transaction.atomic():
                self.indice_radicado = nuevo_radicado(alternativo=self.usar_radicado_alternativo)
                super(Recepcion, self).save(*args, **kwargs)
        else:
            super(Recepcion, self).save(*args, **kwargs)

        logger.debug(default_storage.location)
        if not default_storage.exists('barcode/' + self.radicado + '.svg'):
            logger.debug('no existe')
            Code39 = barcode.get_barcode_class('code39')
            codigo = Code39(str(self.id), add_checksum=False)
            codigo.save(
                settings.MEDIA_ROOT + '/barcode/' + self.radicado,
                options={'module_width': 0.5, 'module_height': 17, 'text': self.radicado, 'write_text': False}
            )

    @property
    def digitado_por(self):
        return self.confirmado_por or self.recepcionista

    @property
    def aceptado_analista(self):
        return self.estado_analista == self.ACEPTADO

    @property
    def radicado(self):
        return '{0}-{1}'.format(self.fecha_recepcion.year, self.indice_radicado)

    @property
    def usar_radicado_alternativo(self):
        """Devuelve True si el ingreso hace parte de los programas EEID, EEDD o Citohistopatologia de lo
        contrario devuelve False."""

        return self.programa.codigo in [enums.ProgramaEnum.EEDD.value, enums.ProgramaEnum.EEID.value, enums.ProgramaEnum.CITOHISTOPATOLOGIA.value]

    @property
    def usa_resultado_numerico(self):
        return self.is_programa_ambientes
    
    @property
    def has_concepto(self):
        return self.is_programa_ambientes
    
    @property
    def has_valores_referencia(self):
        return self.is_programa_ambientes
    
    @property
    def can_actualizar_estado_todas_pruebas(self):
        return self.is_programa_ambientes
    
    @property
    def is_programa_ambientes(self):
        return self.programa.codigo in [enums.ProgramaEnum.AGUAS.value, enums.ProgramaEnum.ALIMENTOS.value, enums.ProgramaEnum.BEBIDAS_ALCOHOLICAS.value]

    @property
    def tipo(self):
        muestra = self.muestras.first()

        with suppress(Exception):
            return muestra.tipo

        try:
            muestra.agua
            return 'agua'
        except Agua.DoesNotExist:
            pass

        try:
            muestra.entomologia
            return 'entomologia'
        except Entomologia.DoesNotExist:
            pass

        try:
            muestra.eedd
            return 'evaluacion externa desempeño directo'
        except EEDD.DoesNotExist:
            pass

        try:
            muestra.eeid
            return 'evaluacion externa desempeño indirecto'
        except EEID.DoesNotExist:
            pass

        try:
            muestra.bebidaalcoholica
            return 'bebidas_alcoholicas'
        except:
            pass

        try:
            muestra.alimento
            return 'alimentos'
        except:
            pass

    @property
    def areas(self):
        pruebas = Prueba.objects.filter(muestra__in=self.muestras.non_polymorphic().all())
        # para resultado_emitido
        return Area.objects.filter(pruebas__in=pruebas, oculto=False).distinct()

    @property
    def muestra(self):
        return self.muestras.first()

    @property
    def solicitante(self):
        muestra = self.muestras.first()
        return muestra.solicitante

    @property
    def informe(self):
        return self.reportes.first()
    
    @property
    def fecha_proceso(self):
        return self.fecha_estado_analista

    @property
    def cumplimiento(self):
        """El cumplimiento es calculado mediante el promedio aritmetico de los cumplimientos de las pruebas
        realizadas."""

        muestras = self.muestras.non_polymorphic().all()
        pruebas = PruebasRealizadas.objects.filter(muestra__in=muestras)

        cumplimiento = 0
        for prueba in pruebas:
            cumplimiento += prueba.cumplimiento

        try:
            cumplimiento = round(cumplimiento / pruebas.count(), 2)
        except ZeroDivisionError:
            cumplimiento = 0

        return cumplimiento

    @property
    def estado_(self):
        """
        Retorna el estado de el ingreso, de acuerdo a donde se encuentre la recepcion en el momento
        de la trazabilidad
        """

        if self.reportes.aprobados().exists() and self.confirmada:
            return enums.EstadoIngresoEnum.RESULTADO.value
        if self.reportes.no_aprobados().exists() and self.confirmada:
            return enums.EstadoIngresoEnum.EN_APROBACION.value
        elif self.estado == self.ACEPTADO and self.estado_analista == self.ACEPTADO:
            return enums.EstadoIngresoEnum.EN_CURSO.value
        elif self.estado == self.ACEPTADO and self.estado_analista == '':
            return enums.EstadoIngresoEnum.PENDIENTE.value

        return enums.EstadoIngresoEnum.RECHAZADA.value

    @property
    def estado_resultado(self):
        """Indica el estado de los resultados. Sin resultado, Resultado no enviado, Resultado y enviado."""

        if self.estado_ == enums.EstadoIngresoEnum.RESULTADO.value:
            if not self.fecha_envio_resultados:
                return enums.EstadoResultadoEnum.RESULTADO_NO_ENVIADO
            else:
                return enums.EstadoResultadoEnum.RESULTADO_ENVIADO

        return enums.EstadoResultadoEnum.SIN_RESULTADO

    @property
    def url_estado_ingreso(self):
        """Devuelve la URL en la cual se define el estado de un ingreso."""

        if self.programa.codigo == enums.ProgramaEnum.CLINICO.value:
            return reverse('trazabilidad:estado_muestra_clinica', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.COVID19.value:
            return reverse('covid19:estado_muestra', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.AGUAS.value:
            return reverse('trazabilidad:estado_muestra_agua', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.ENTOMOLOGIA.value:
            return reverse('trazabilidad:estado_muestra_entomologia', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.CITOHISTOPATOLOGIA.value:
            return reverse('trazabilidad:estado_muestra_citohistopatologia', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.BANCO_SANGRE.value:
            return reverse('trazabilidad:estado_muestra_banco_sangre', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.EEDD.value:
            return reverse('trazabilidad:estado_muestra_eedd', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.EEID.value:
            return reverse('trazabilidad:estado_muestra_eeid', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.ALIMENTOS.value:
            return reverse('alimentos:estado_muestra', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.BEBIDAS_ALCOHOLICAS.value:
            return reverse('bebidas_alcoholicas:estado_muestra', args=(self.id, ))

    @property
    def url_editar_ingreso(self):
        """Devuelve la URL en la cual se edita la información de un ingreso."""

        if self.programa.codigo == enums.ProgramaEnum.CLINICO.value:
            return reverse('trazabilidad:actualizar_muestra_clinica', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.COVID19.value:
            return reverse('covid19:actualizar_muestra', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.AGUAS.value:
            return reverse('trazabilidad:actualizar_muestra_agua', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.ENTOMOLOGIA.value:
            return reverse('trazabilidad:actualizar_muestra_entomologia', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.CITOHISTOPATOLOGIA.value:
            return reverse('trazabilidad:actualizar_muestra_citohistopatologia', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.BANCO_SANGRE.value:
            return reverse('trazabilidad:actualizar_muestra_banco_sangre', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.EEDD.value:
            return reverse('trazabilidad:actualizar_muestra_eedd', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.EEID.value:
            return reverse('trazabilidad:actualizar_muestra_eeid', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.ALIMENTOS.value:
            return reverse('alimentos:actualizar_muestra', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.BEBIDAS_ALCOHOLICAS.value:
            return reverse('bebidas_alcoholicas:actualizar_muestra', args=(self.id, ))

    @property
    def url_radicado_ingreso(self):
        """Devuelve la URL en la cual se edita la información de un ingreso."""

        if self.programa.codigo == enums.ProgramaEnum.CLINICO.value:
            return reverse('trazabilidad:radicado_muestra_clinica', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.COVID19.value:
            return reverse('covid19:radicado_muestra', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.AGUAS.value:
            return reverse('trazabilidad:radicado_muestra_agua', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.ENTOMOLOGIA.value:
            return reverse('trazabilidad:radicado_muestra_entomologia', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.CITOHISTOPATOLOGIA.value:
            return reverse('trazabilidad:radicado_muestra_citohistopatologia', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.BANCO_SANGRE.value:
            return reverse('trazabilidad:radicado_muestra_banco_sangre', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.EEDD.value:
            return reverse('trazabilidad:radicado_muestra_eedd', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.EEID.value:
            return reverse('trazabilidad:radicado_muestra_eeid', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.ALIMENTOS.value:
            return reverse('alimentos:radicado_muestra', args=(self.id,))
        elif self.programa.codigo == enums.ProgramaEnum.BEBIDAS_ALCOHOLICAS.value:
            return reverse('bebidas_alcoholicas:radicado_muestra', args=(self.id, ))

    def crear_codigos_muestra(self):
        """Crea los codigos de barra para cada muestra."""

        muestras = self.muestras.non_polymorphic().all()
        for index, muestra in enumerate(muestras):
            i = index + 1
            if default_storage.exists('barcode/{0}.svg'.format(muestra)):
                logger.debug('existe')
            else:
                logger.debug('no existe')
                if self.programa in Programa.objects.ambientes():
                    texto = '{0}-{1}'.format(self.radicado, i)
                else:
                    texto = '{0}'.format(self.radicado)

                Code39 = barcode.get_barcode_class('code39')
                codigo = Code39(str(muestra.id), add_checksum=False)
                options = {'module_width': 0.5, 'module_height': 17, 'text': texto, 'write_text': False}
                codigo.save('{0}/barcode/{1}'.format(settings.MEDIA_ROOT, muestra), options=options)

Ingreso = Recepcion

class Muestra(PolymorphicModel):
    """Modelo usado para guardar las muestras ingresadas en un laboratorio."""

    registro_recepcion = models.ForeignKey(Recepcion, verbose_name='ingreso', related_name='muestras', on_delete=models.CASCADE)
    pruebas = models.ManyToManyField(Prueba, through='PruebasRealizadas', blank=True)
    observacion = models.TextField('Observacion', max_length=500)

    temp_ingreso = models.FloatField(blank=True, null=True, verbose_name='temperatura de muestra ºC')
    temp_procesamiento = models.FloatField(blank=True, null=True, verbose_name='temperatura de procesamiento ºC')

    class Meta:
        ordering = ['id']
        verbose_name = 'muestra'
        verbose_name_plural = 'muestras'

    def __str__(self):
        return '{0}-{1}'.format(self.registro_recepcion.radicado, self.id)

    @property
    def areas(self):
        return Area.objects.filter(pruebas__in=self.pruebas.all(), oculto=False).distinct()

    @property
    def solicitante(self):
        raise NotImplementedError
    
    @property
    def tipo(self):
        raise NotImplementedError


class PruebasRealizadas(models.Model):
    """Modelo usado para guardar la pruebas que se le realizan a una muestra."""

    # opciones
    CONSERVACION = 'C'
    PRE_ANALISIS = 'P'
    ANALISIS = 'A'
    RESULTADO = 'R'
    ESTADOS = (
        (CONSERVACION, 'Conservación'),
        (PRE_ANALISIS, 'Pre-Analisis'),
        (ANALISIS, 'Analisis'),
        (RESULTADO, 'Prueba finalizada'),
    )

    muestra = models.ForeignKey(Muestra, on_delete=models.CASCADE)
    prueba = models.ForeignKey(Prueba, on_delete=models.CASCADE)
    estado = models.CharField(max_length=1, choices=ESTADOS, default=CONSERVACION)
    fecha_pre_analisis = models.DateTimeField(blank=True, null=True)
    ultima_modificacion = models.DateTimeField(blank=True, null=True)
    observacion_semaforo = models.CharField(
        'observaciones', 
        max_length=200, 
        blank=True,
        help_text='Indique porque ha durado mas tiempo del establecido para terminar la prueba.'
    )
    resultados = models.ManyToManyField(ResultadoPrueba, blank=True, related_name='resultados')
    resultado_numerico = models.CharField(verbose_name='resultado numerico', max_length=150, blank=True)
    metodo = models.ForeignKey(Metodo, blank=True, null=True, on_delete=models.SET_NULL)
    concepto = models.CharField('concepto', max_length=255, blank=True)

    objects = managers.PruebasRealizadasManager()

    class Meta:
        ordering = ['prueba']
        verbose_name = 'prueba realizada'
        verbose_name_plural = 'pruebas realizadas'
        unique_together = ('muestra', 'prueba')

    @property
    def cumplimiento(self):
        """El cumplimiento se mide según el estado en que se encuentra la prueba.

        Conservación --> 0%
        Pre-Analisis --> 33%
        Analisis     --> 66%
        Resultado    --> 100%
        """

        if self.estado == self.CONSERVACION:
            cumplimiento = 0
        elif self.estado == self.PRE_ANALISIS:
            cumplimiento = 33
        elif self.estado == self.ANALISIS:
            cumplimiento = 66
        elif self.estado == self.RESULTADO:
            cumplimiento = 100

        return cumplimiento

    @property
    def color_semaforo(self):
        """El color del semáforo es calculado según el tiempo de duración de la prueba y el tiempo que ha pasado desde
        que fue iniciado el pre-analisis.

        rojo --> tiempo del proceso lleva mas de la duración la prueba.
        amarillo --> tiempo del proceso lleva 2/3 de la duración de la prueba.
        verde  --> tiempo del proceso lleva 1/3 de la duración de la prueba.
        """

        if self.estado != self.CONSERVACION:

            if self.estado == self.RESULTADO:
                ahora = self.ultima_modificacion
            else:
                ahora = timezone.now()

            delta = ahora - self.fecha_pre_analisis
            dos_tecios_duracion = self.prueba.duracion * (2 / 3)

            if delta > self.prueba.duracion:
                return 'rojo'
            elif delta >= dos_tecios_duracion:
                return 'amarillo'
            else:
                return 'verde'
        else:
            return None

    @property
    def con_resultado(self):
        return self.estado == self.RESULTADO
    
    @property
    def en_analisis(self):
        return self.estado == self.ANALISIS

    def actualizar_estado(self):
        """Actualiza el estado de una prueba."""

        if self.estado == self.CONSERVACION:
            self.estado = self.PRE_ANALISIS
            self.fecha_pre_analisis = timezone.now()
        elif self.estado == self.PRE_ANALISIS:
            self.estado = self.ANALISIS
        elif self.estado == self.ANALISIS:
            self.estado = self.RESULTADO
            self.ultima_modificacion = timezone.now()

        self.save()


class Eps(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar las eps a la cual se puede asociar un paciente."""

    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'eps'
        verbose_name_plural = 'eps'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(Eps, self).save(*args, **kwargs)


class Paciente(UltimaModificacionMixin):
    """Modelo usado para guardar los pacientes a los cuales se les han recogido muestras."""

    # opciones
    HORAS = 'H'
    MESES = 'M'
    DIAS = 'D'
    ANOS = 'A'
    UNIDADES_MEDIDA = (
        (ANOS, 'Años'),
        (MESES, 'Meses'),
        (DIAS, 'Dias'),
        (HORAS, 'Horas'),
    )

    CEDULA_EXTRANJERIA = 'CE'
    TARJETA_IDENTIDAD = 'TI'
    REGISTRO_CIVIL = 'RC'
    PASAPORTE = 'P'
    CEDULA = 'CC'
    CODIGO = 'CO'
    CEDULACOD = 'CD'
    SIN_IDENTIFICACION = 'NN'
    TIPO_IDENTIFICACION = (
        (CEDULA, 'CC'),
        (TARJETA_IDENTIDAD, 'TI'),
        (REGISTRO_CIVIL, 'RC'),
        (PASAPORTE, 'P'),
        (CEDULA_EXTRANJERIA, 'CE'),
        (CODIGO, 'COD'),
        (CEDULACOD, 'CC/COD'),
        (SIN_IDENTIFICACION, 'SIN DATOS'),
    )

    FEMENINO = 'F'
    MASCULINO = 'M'
    GENEROS = (
        (FEMENINO, 'Femenino'),
        (MASCULINO, 'Masculino'),
    )

    email = models.EmailField(blank=True)
    nombre = models.CharField('nombres', max_length=100, blank=True)
    apellido = models.CharField('apellidos', max_length=100, blank=True)
    direccion = models.CharField('dirección', max_length=100, blank=True)
    identificacion = models.CharField('documento id', max_length=50)
    tipo_identificacion = models.CharField(max_length=2, choices=TIPO_IDENTIFICACION)
    edad = models.IntegerField(blank=True, null=True)
    tipo_edad = models.CharField(max_length=1, choices=UNIDADES_MEDIDA, blank=True)
    fecha_nacimiento = models.DateField(verbose_name='fecha de nacimiento', blank=True, null=True)
    eps = models.ForeignKey(Eps, verbose_name='eps-plan', related_name='pacientes', on_delete=models.CASCADE, blank=True, null=True)
    sexo = models.CharField(max_length=1, choices=GENEROS, blank=True)

    objects = managers.PacienteManager()

    class Meta:
        verbose_name = 'paciente'
        verbose_name_plural = 'pacientes'

    def __str__(self):
        return '{0} {1}'.format(self.nombre.title(), self.apellido.title())

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        self.apellido = self.apellido.lower()
        self.direccion = self.direccion.lower()
        super(Paciente, self).save(*args, **kwargs)


class Epsa(UltimaModificacionMixin):
    """Modelo usado para guardar las empresas de suministro de agua."""

    # opciones
    EPSA = 'EP'
    ACUEDUCTO_VEREDAL = 'AV'
    NO_EPSA = 'NE'
    EPSA_SIN_REGISTRO = 'ES'
    TIPOS = (
        (EPSA, 'Empresa prestadora de servicio de acueducto'),
        (ACUEDUCTO_VEREDAL, 'Acueducto veredal'),
        (NO_EPSA, 'No tiene EPSA'),
        (EPSA_SIN_REGISTRO, 'EPSA sin registro conocido'),
    )

    nombre = models.CharField('nombre epsa', max_length=100)
    direccion = models.CharField('dirección', max_length=100)
    rup = models.CharField('n. rup', max_length=50)
    nit = models.CharField('n. nit', max_length=50)
    tipo = models.CharField('tipo de epsa', max_length=2, choices=TIPOS)

    class Meta:
        verbose_name = 'epsa'
        verbose_name_plural = 'epsas'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        self.direccion = self.direccion.lower()
        super(Epsa, self).save(*args, **kwargs)


class Departamento(UltimaModificacionMixin):
    """Modelo usado para guardar los datos de los departamentos."""

    nombre = models.CharField(max_length=100)
    codigo = models.IntegerField()

    class Meta:
        verbose_name = 'departamento'
        verbose_name_plural = 'departamentos'

    def __str__(self):
        return self.nombre.title()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(Departamento, self).save(*args, **kwargs)


class Municipio(UltimaModificacionMixin):
    """Modelo usado para guardar los municipios de un departamento."""

    nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, related_name='municipios', on_delete=models.CASCADE)
    codigo = models.IntegerField()
    email = models.EmailField()

    class Meta:
        verbose_name = 'municipio'
        verbose_name_plural = 'municipios'

    def __str__(self):
        return self.nombre.title()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(Municipio, self).save(*args, **kwargs)


class Poblado(UltimaModificacionMixin):
    """Modelo usado para guardar los poblados de un municipio."""

    nombre = models.CharField(max_length=100)
    municipio = models.ForeignKey(Municipio, related_name='poblados', on_delete=models.CASCADE)
    codigo = models.IntegerField()
    epsa = models.ForeignKey(Epsa, related_name='poblados', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'poblado'
        verbose_name_plural = 'poblados'

    def __str__(self):
        return self.nombre.title()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(Poblado, self).save(*args, **kwargs)


class Institucion(UltimaModificacionMixin):
    """Modelo usado para guardar las instituciones en donde se recolecta una muestra."""

    nombre = models.CharField(max_length=100)
    municipio = models.ForeignKey(Municipio, related_name='instituciones', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'institución'
        verbose_name_plural = 'instituciones'

    def __str__(self):
        return '{0} ({1}-{2})'.format(self.nombre.capitalize(), self.municipio.departamento, self.municipio)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(Institucion, self).save(*args, **kwargs)


class TipoMuestra(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los tipos de muestra que llegan al laboratorio."""

    nombre = models.CharField(max_length=50)
    programas = models.ManyToManyField(Programa)

    objects = managers.TipoMuestraManager()

    class Meta:
        verbose_name = 'tipo de muestra'
        verbose_name_plural = 'tipos de muestra'

    def __str__(self):
        return self.nombre.upper()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(TipoMuestra, self).save(*args, **kwargs)


class Clinica(Muestra):
    """Modelo usado para guardar las muestras clinicas ingresadas a un laboratorio.

    El modelo extiende de Muestra."""

    # opciones
    SI = True
    NO = False
    SI_NO_OPCIONES = (
        (SI, 'Si'),
        (NO, 'No'),
    )

    paciente = models.ForeignKey(Paciente, related_name='muestras', on_delete=models.CASCADE)
    tipo_muestras = models.ManyToManyField(TipoMuestra, verbose_name='tipo de muestra', blank=True, related_name='tipos_muestra')
    institucion = models.ForeignKey(Institucion, blank=True, null=True, on_delete=models.SET_NULL)
    municipio = models.ForeignKey(Municipio, related_name='muestras_clinicas', on_delete=models.CASCADE)
    barrio = models.CharField(max_length=100)
    embarazada = models.BooleanField(default=False, choices=SI_NO_OPCIONES)

    class Meta:
        verbose_name = 'muestra clinica'
        verbose_name_plural = 'muestras clinicas'

    @property
    def solicitante(self):
        return self.institucion
    
    @property
    def tipo(self):
        return enums.TipoMuestraEnum.CLINICA.value


class CategoriaAgua(UltimaModificacionMixin):
    """Modelo usado para guardar las distintas categorias de agua."""

    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'categoria de agua'
        verbose_name_plural = 'categorias de agua'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(CategoriaAgua, self).save(*args, **kwargs)


class TipoAgua(UltimaModificacionMixin):
    """Modelo usado para guardar los tipo de agua de las muestras de agua."""

    nombre = models.CharField(max_length=50)
    categoria = models.ForeignKey(CategoriaAgua, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'tipo de agua'
        verbose_name_plural = 'tipos de agua'

    def __str__(self):
        return "{0} - {1}".format(self.nombre.capitalize(), self.categoria.nombre)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(TipoAgua, self).save(*args, **kwargs)


class Temperatura(UltimaModificacionMixin):
    """Modelo usado para guardar las temperaturas posibles que tienen las muestras de agua."""

    valor = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'temperatura'
        verbose_name_plural = 'temperaturas'

    def __str__(self):
        return self.valor.capitalize()

    def save(self, *args, **kwargs):
        self.valor = self.valor.lower()
        super(Temperatura, self).save(*args, **kwargs)


class Solicitante(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los solicitantes de toma de muestras de agua."""

    nombre = models.CharField(max_length=200)
    direccion = models.CharField('dirección', max_length=100)
    telefono = models.IntegerField()

    class Meta:
        verbose_name = 'solicitante'
        verbose_name_plural = 'solicitantes'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(Solicitante, self).save(*args, **kwargs)


class InformacionAgua(models.Model):
    """Modelo usado para guardar la información común que manejan las muestras de aguas."""

    poblado = models.ForeignKey(Poblado, on_delete=models.CASCADE)
    fecha_recoleccion = models.DateField('fecha de recolección', blank=True, null=True)
    tipo_agua = models.ForeignKey(TipoAgua, verbose_name='tipo de agua', blank=True, null=True, on_delete=models.SET_NULL)
    responsable_toma = models.CharField('responsable de la toma', max_length=100, blank=True)
    temperatura = models.ForeignKey(Temperatura, blank=True, null=True, on_delete=models.SET_NULL)
    solicitante = models.ForeignKey(Solicitante, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'información general de las muestras de agua'
        verbose_name_plural = 'información general de las muestras de agua'

    def __str__(self):
        return self.poblado.epsa.nombre

    def save(self, *args, **kwargs):
        if self.responsable_toma:
            self.responsable_toma = self.responsable_toma.lower()
        super(InformacionAgua, self).save(*args, **kwargs)


class MotivoAnalisis(models.Model):
    """Modelo usado para guardar los motivos que se tienen para analizar una muestra de agua."""

    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'motivo de analisis'
        verbose_name_plural = 'motivos de analisis'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(MotivoAnalisis, self).save(*args, **kwargs)


class DescripcionPunto(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar las descripciones de los puntos de toma de las muestras de agua."""

    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'descripción del punto de toma'
        verbose_name_plural = 'descripciónes de los puntos de toma'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(DescripcionPunto, self).save(*args, **kwargs)


class FuenteAbastecimiento(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar las fuentes de abastecimiento de las muestras de agua."""

    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'fuente de abastecimiento'
        verbose_name_plural = 'fuentes de abastecimiento'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(FuenteAbastecimiento, self).save(*args, **kwargs)


class LugarPunto(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los lugares del punto de toma en donde se recogen las muestras de agua."""

    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'lugar del punto de toma'
        verbose_name_plural = 'lugares de los puntos de toma'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(LugarPunto, self).save(*args, **kwargs)


class CodigoPunto(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los códigos de los punto de los poblados en donde se recogen las muestras de agua."""

    # opciones
    SI = True
    NO = False
    SI_NO_OPCIONES = (
        (SI, 'Si'),
        (NO, 'No'),
    )

    codigo = models.CharField('código', max_length=20)
    direccion = models.CharField('dirección', max_length=100)
    lugar_toma = models.ForeignKey(LugarPunto, verbose_name='lugar del punto de toma', on_delete=models.CASCADE)
    descripcion = models.ForeignKey(DescripcionPunto, verbose_name='descripción punto de toma', on_delete=models.CASCADE)
    fuente_abastecimiento = models.ForeignKey(FuenteAbastecimiento, verbose_name='fuente de abastecimiento', on_delete=models.CASCADE)
    punto_intradomiciliario = models.BooleanField(choices=SI_NO_OPCIONES)
    poblado = models.ForeignKey(Poblado, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'codigo del punto'
        verbose_name_plural = 'codigos de los puntos'

    def __str__(self):
        return self.codigo.lower()

    def save(self, *args, **kwargs):
        self.codigo = self.codigo.lower()
        self.direccion = self.direccion.lower()
        super(CodigoPunto, self).save(*args, **kwargs)


class PuntajeRiesgo(UltimaModificacionMixin):
    """
    Modelo para guardar los puntajes de riesgo de cada prueba, siempre y cuando esta sea de aguas,
    para calcular el IRCA.
    """

    prueba = models.OneToOneField(Prueba, related_name='puntaje_riesgo', on_delete=models.CASCADE)
    puntaje = models.FloatField()

    class Meta:
        verbose_name = 'Puntaje Riesgo'
        verbose_name_plural = 'Puntajes de Riesgo'

    def __str__(self):
        return 'Puntaje IRCA {:.2f} para {}'.format(self.puntaje, self.prueba)

    def save(self, *args, **kwargs):
        if self.prueba.area.programa != Programa.objects.aguas():
            from django.db import IntegrityError
            raise IntegrityError('Prueba debe ser de Aguas, pero es de {}'.format(self.prueba.area.programa))
        super().save(*args, **kwargs)


class NivelRiesgo(UltimaModificacionMixin):
    """
    Modelo para guardar los niveles de riesgo segun el IRCA.
    """

    inicio = models.FloatField()
    fin = models.FloatField()
    nivel = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Nivel de Riesgo'
        verbose_name_plural = 'Niveles de Riesgo'

    def __str__(self):
        return '{self.nivel}: de {self.inicio:.2f} a {self.fin:.2f}'.format(self=self)

    def save(self, *args, **kwargs):
        self.nivel = self.nivel.upper()
        super().save(*args, **kwargs)


class Agua(Muestra):
    """Modelo usado para guardar las muestras de agua ingresadas a un laboratorio.

    El modelo extiende de Muestra."""

    # opciones
    SI = True
    NO = False
    SI_NO_OPCIONES = (
        (SI, 'Si'),
        (NO, 'No'),
    )

    informacion_general = models.ForeignKey(InformacionAgua, on_delete=models.CASCADE)
    motivo_analisis = models.ForeignKey(MotivoAnalisis, verbose_name='motivo del analisis', blank=True, null=True, on_delete=models.SET_NULL)
    hora_toma = models.TimeField('hora de toma', blank=True, null=True)
    codigo_punto = models.ForeignKey(CodigoPunto, verbose_name='cod. del punto', blank=True, null=True, on_delete=models.SET_NULL)
    concertado = models.NullBooleanField('concertado')
    irca = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = 'muestra de agua'
        verbose_name_plural = 'muestras de agua'

    @property
    def solicitante(self):
        return self.informacion_general.solicitante

    def calcular_irca(self):
        """Metodo para calcular el IRCA."""

        _table = {
            '>': operator.ge, '<': operator.le, '<=': operator.le,
            '>=': operator.ge, '=<': operator.le, '=>': operator.ge
        }
        pruebas = self.pruebasrealizadas_set.filter(
            prueba__in=PuntajeRiesgo.objects.all().values_list('prueba__id', flat=1)
        )
        digit = lambda rg, gr='digit': float(rg.group(gr).replace(r',', '.'))
        irca = 0
        total = pruebas.aggregate(suma=models.Sum('prueba__puntaje_riesgo__puntaje'))['suma'] or 0

        regex = re.compile(r'(?P<operator>=?(<|>)=?\s*)?(?P<digit>\d+(,|\.)?\d*)\w*(\s*-\s*(?P<range_to>\d+(,|\.)?\d*))?|(?P<organoleptico>[nN]{1}[oO]{1}\s*[a-zA-Z]*)')

        for prueba in pruebas:
            resultado = prueba.resultado_numerico
            referencia = prueba.prueba.valores_referencia

            match_resultado = regex.match(resultado)
            match_referencia = regex.match(referencia)

            if not match_referencia:
                if match_resultado and match_resultado.group('organoleptico') is not None:
                    irca += prueba.prueba.puntaje_riesgo.puntaje
                else:
                    regex_aceptable = re.compile(r'[aA]{1}[cC]{1}[eE]{1}[pP]{1}[tT]{1}[aA]{1}[bB]{1}[lL]{1}[eE]{1}')
                    if regex_aceptable.match(referencia) is None:
                        print('No se calcula el IRCA para: {}({}) con el resultado: {}'.format(prueba.prueba, referencia, resultado))
                continue

            groups = match_referencia.groupdict()
            valor_referencia = digit(match_referencia) if match_referencia.group('digit') else 0
            result = digit(match_resultado) if match_resultado else None

            if not result:
                continue

            if groups.get('operator') is not None:
                function = _table[groups.get('operator').strip()]
                if not function(result, valor_referencia):
                    irca += prueba.prueba.puntaje_riesgo.puntaje
            elif groups.get('range_to') is not None:
                _range = (valor_referencia, digit(match_referencia, 'range_to'))
                if result > _range[1] or result < _range[0]:
                    irca += prueba.prueba.puntaje_riesgo.puntaje
            elif groups.get('digit') is not None:
                if result >= valor_referencia:
                    irca += prueba.prueba.puntaje_riesgo.puntaje
            else:
                print("No matches found for '{}'".format(referencia))

        try:
            return (irca / total) * 100
        except ZeroDivisionError:
            return 0

    def get_clasificacion_irca(self):
        """Retorna la clasificacion de la muestra de acuerdo al IRCA."""

        irca = self.irca if self.irca is not None else self.calcular_irca()

        try:
            return NivelRiesgo.objects.get(inicio__lte=irca, fin__gte=irca).nivel
        except NivelRiesgo.DoesNotExist:
            raise NotImplementedError('Nivel de riesgo para IRCA en rango de "{}" no fue encontrado.'.format(irca))


class ResponsableRecoleccion(UltimaModificacionMixin):
    """Modelo usado para guardar los responsables de recolección de las muestras de entomologia."""

    nombres = models.CharField(max_length=200)
    apellidos = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'responsable de recolección'
        verbose_name_plural = 'responsables de recolección'

    def __str__(self):
        return '{0} {1}'.format(self.nombres.title(), self.apellidos.title())

    def save(self, *args, **kwargs):
        self.nombres = self.nombres.lower()
        self.apellidos = self.apellidos.lower()
        super(ResponsableRecoleccion, self).save(*args, **kwargs)


class LugarRecoleccion(UltimaModificacionMixin):
    """Modelo usado para guardar los lugares de recolección para las muestras de entomologia."""

    nombre = models.CharField(max_length=250)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'lugar de recolección'
        verbose_name_plural = 'lugares de recolección'

    def __str__(self):
        return '{0} ({1} - {2})'.format(self.nombre.title(), self.municipio.departamento, self.municipio)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(LugarRecoleccion, self).save(*args, **kwargs)


class TipoVigilancia(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los tipos de vigilancia."""

    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'tipo de vigilancia'
        verbose_name_plural = 'tipos de vigilancia'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(TipoVigilancia, self).save(*args, **kwargs)


class Entomologia(Muestra):
    """Modelo usado para guardar las muestras de entomologia ingresadas a un laboratorio.

    El modelo extiende de muestra."""

    # opciones
    PUPA = 'P'
    NINFA = 'N'
    HUEVO = 'H'
    LARVAS = 'L'
    ADULTO = 'A'
    INDETERMINADO = 'I'
    ESTADOS = (
        (HUEVO, 'Huevo'),
        (LARVAS, 'Larvas'),
        (PUPA, 'Pupa'),
        (NINFA, 'Ninfa'),
        (ADULTO, 'Adulto'),
        (INDETERMINADO, 'Indeterminado'),
    )

    responsable_recoleccion = models.ForeignKey(ResponsableRecoleccion, verbose_name='responsable de recolección', on_delete=models.CASCADE)
    lugar_recoleccion = models.ForeignKey(LugarRecoleccion, verbose_name='lugar de recolección', on_delete=models.CASCADE)
    tipo_vigilancia = models.ForeignKey(TipoVigilancia, verbose_name='tipo de vigilancia', on_delete=models.CASCADE)
    estado_desarrollo = models.CharField('estado de desarrollo', max_length=1, choices=ESTADOS)
    tipo_muestra = models.ForeignKey(TipoMuestra, related_name='muestras_entomologia', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'muestra de entomologia'
        verbose_name_plural = 'muestras de entomologia'

    @property
    def solicitante(self):
        return self.lugar_recoleccion


class ObjetoPrueba(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los strings de cada Objeto de Prueba."""

    nombre = models.CharField(max_length=300)

    class Meta:
        verbose_name = 'proposito general de la prueba'
        verbose_name_plural = 'propositos generales de la prueba'

    def __str__(self):
        return self.nombre.title()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(ObjetoPrueba, self).save(*args, **kwargs)


class Reporte(models.Model):
    """Modelo usado para guardar los informes de Laboratorio."""

    registro_recepcion = models.ForeignKey(Recepcion, related_name='reportes', on_delete=models.CASCADE)
    confirmado = models.BooleanField(default=False)
    objeto = models.ForeignKey(ObjetoPrueba, verbose_name='Objeto de la Prueba', related_name='objeto_prueba_reporte', on_delete=models.CASCADE)
    fecha = models.DateTimeField('fecha de reporte', blank=True, null=True)
    fecha_aprobacion = models.DateTimeField('fecha de aprobación', blank=True, null=True)

    objects = managers.ReporteManager()

    class Meta:
        verbose_name = 'reporte'
        verbose_name_plural = 'reportes'
        permissions = [
            ('can_generar_informe', 'Puede generar nuevo informe de resultado'),
            ('can_see_informe_resultados', 'Puede ver informe de resultado regenerado'),
        ]


class TipoEnvase(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los tipos de envase usados en una muestra de banco de sangre."""

    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'tipo de envase'
        verbose_name_plural = 'tipos de envase'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(TipoEnvase, self).save(*args, **kwargs)


class InstitucionBancoSangre(UltimaModificacionMixin):
    """Modelo usado para guardar las instituciones en donde se recolecta una muestra."""

    nombre = models.CharField(max_length=100)
    municipio = models.ForeignKey(Municipio, related_name='instituciones_banco_sangre', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'institución banco de sangre'
        verbose_name_plural = 'instituciónes banco de sangre'

    def __str__(self):
        return '{0} ({1}-{2})'.format(self.nombre.capitalize(), self.municipio.departamento, self.municipio)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(InstitucionBancoSangre, self).save(*args, **kwargs)


class BancoSangre(Muestra):
    """Modelo usado para guardar las muestras de Banco de Sangre ingresadas a un laboratorio.

    El modelo extiende de Muestra."""

    # opciones
    SI = True
    NO = False
    SI_NO_OPCIONES = (
        (SI, 'Si'),
        (NO, 'No'),
    )

    paciente = models.ForeignKey(Paciente, related_name='muestras_banco_sangre', on_delete=models.CASCADE)
    tipo_muestra = models.ForeignKey(TipoMuestra, related_name='muestras_banco_sangre', on_delete=models.CASCADE)
    institucion = models.ForeignKey(InstitucionBancoSangre, related_name='muestras_banco_sangre', on_delete=models.CASCADE)
    tipo_envase = models.ForeignKey(TipoEnvase, verbose_name='tipo de envase', on_delete=models.CASCADE)
    formatos_diligenciados = models.BooleanField(choices=SI_NO_OPCIONES)
    ficha_pacientes = models.BooleanField('ficha de pacientes', choices=SI_NO_OPCIONES)
    condensado_banco = models.BooleanField(choices=SI_NO_OPCIONES)

    class Meta:
        verbose_name = 'muestra de banco de sangre'
        verbose_name_plural = 'muestras de banco de sangre'

    @property
    def solicitante(self):
        return self.institucion
    
    @property
    def tipo(self):
        return enums.TipoMuestraEnum.BANCO_SANGRE.value


class InstitucionCitohistopatologia(UltimaModificacionMixin):
    """Modelo usado para guardar las instituciones en donde se recolecta una muestra."""

    nombre = models.CharField(max_length=100)
    municipio = models.ForeignKey(Municipio, related_name='instituciones_citohistopatologia', on_delete=models.CASCADE)
    codigo = models.BigIntegerField()

    class Meta:
        verbose_name = 'institución de citohistopatologia'
        verbose_name_plural = 'instituciónes de citohistopatologia'

    def __str__(self):
        return '{0} ({1}-{2})'.format(self.nombre.capitalize(), self.municipio.departamento, self.municipio)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(InstitucionCitohistopatologia, self).save(*args, **kwargs)


class Control(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los tipos de controles."""

    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'control'
        verbose_name_plural = 'controles'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(Control, self).save(*args, **kwargs)


class TipoEvento(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los tipos de eventos."""

    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'tipo de evento'
        verbose_name_plural = 'tipos de eventos'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(TipoEvento, self).save(*args, **kwargs)


class Citohistopatologia(Muestra):
    """Modelo usado para guardar las muestras de citohistopatologia ingresadas a un laboratorio.

    El modelo extiende de Muestra."""

    paciente = models.ForeignKey(Paciente, related_name='muestras_citohistopatologia', on_delete=models.CASCADE)
    institucion = models.ForeignKey(InstitucionCitohistopatologia, on_delete=models.CASCADE)
    control = models.ForeignKey(Control, on_delete=models.CASCADE)
    tipo_evento = models.ForeignKey(TipoEvento, on_delete=models.CASCADE)
    tipo_muestra = models.ForeignKey(TipoMuestra, related_name='muestras_citohistopatologia', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'muestra de citohistopatologia'
        verbose_name_plural = 'muestras de citohistopatologia'

    @property
    def solicitante(self):
        return self.institucion
    
    @property
    def tipo(self):
        return enums.TipoMuestraEnum.CITOHISTOPATOLOGIA.value


class ProgramaEvaluacionExterna(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los programas para las muestras de evaluación externa."""

    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'programa de evaluación externa'
        verbose_name_plural = 'programas de evaluación externa'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(ProgramaEvaluacionExterna, self).save(*args, **kwargs)


class TipoEventoEvaluacionExterna(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los tipos de evento para los programas de evaluación externa"""

    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'tipo de evento de evaluación externa'
        verbose_name_plural = 'tipos de eventos de evaluación externa'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(TipoEventoEvaluacionExterna, self).save(*args, **kwargs)


class InstitucionEEDD(UltimaModificacionMixin):
    """Modelo usado para guardar las instituciones para la evaluación externa desempeño directo."""

    nombre = models.CharField(max_length=100)
    direccion = models.CharField('dirección', max_length=100)
    nit = models.CharField('n. nit', max_length=50)
    municipio = models.ForeignKey(Municipio, related_name='instituciones_eedd', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'institución EEDD'
        verbose_name_plural = 'instituciones EEDD'

    def __str__(self):
        return '{0} ({1}-{2})'.format(self.nombre.capitalize(), self.municipio.departamento, self.municipio)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        self.direccion = self.direccion.lower()
        super(InstitucionEEDD, self).save(*args, **kwargs)


class EEDD(Muestra):
    """Modelo usado para guardar las muestras de evaluación externa de desempeño directo ingresadas a un laboratorio.

    El modelo extiende de Muestra."""

    institucion = models.ForeignKey(InstitucionEEDD, on_delete=models.CASCADE)
    control = models.ForeignKey(Control, related_name='muestras_eedd', on_delete=models.CASCADE)
    tipo_evento = models.ForeignKey(TipoEventoEvaluacionExterna, related_name='muestras_eedd', on_delete=models.CASCADE)
    tipo_muestra = models.ForeignKey(TipoMuestra, related_name='muestras_eedd', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'muestra EEDD'
        verbose_name_plural = 'muestras EEDD'

    @property
    def solicitante(self):
        return self.institucion


class InstitucionEEID(UltimaModificacionMixin):
    """Modelo usado para guardar las instituciones para la evaluación externa desempeño indirecto."""

    nombre = models.CharField(max_length=100)
    municipio = models.ForeignKey(Municipio, related_name='instituciones_eeid', on_delete=models.CASCADE)
    codigo = models.IntegerField()

    class Meta:
        verbose_name = 'institución EEID'
        verbose_name_plural = 'instituciones EEID'

    def __str__(self):
        return '{0} ({1}-{2})'.format(self.nombre.capitalize(), self.municipio.departamento, self.municipio)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        # self.direccion = self.direccion.lower()
        super(InstitucionEEID, self).save(*args, **kwargs)


class EEID(Muestra):
    """Modelo usado para guardar las muestras de evaluación externa de desempeño indirecto ingresadas a un laboratorio.

    El modelo extiende de Muestra."""

    # opciones
    SI = True
    NO = False
    SI_NO_OPCIONES = (
        (SI, 'Si'),
        (NO, 'No'),
    )

    CEDULA = 'CC'
    CODIGO = 'CO'
    PASAPORTE = 'P'
    CEDULACOD = 'CD'
    REGISTRO_CIVIL = 'RC'
    TARJETA_IDENTIDAD = 'TI'
    CEDULA_EXTRANJERIA = 'CE'
    SIN_IDENTIFICACION = 'NN'
    TIPOS_IDENTIFICACION = (
        (CEDULA, 'CC'),
        (TARJETA_IDENTIDAD, 'TI'),
        (REGISTRO_CIVIL, 'RC'),
        (PASAPORTE, 'P'),
        (CEDULA_EXTRANJERIA, 'CE'),
        (CODIGO, 'COD'),
        (CEDULACOD, 'CC/COD'),
        (SIN_IDENTIFICACION, 'SIN DATOS'),
    )

    HORAS = 'H'
    MESES = 'M'
    DIAS = 'D'
    ANOS = 'A'
    UNIDADES_MEDIDA = (
        (ANOS, 'Años'),
        (MESES, 'Meses'),
        (DIAS, 'Dias'),
        (HORAS, 'Horas'),
    )

    nombre = models.CharField('nombres', max_length=100)
    identificacion = models.CharField('documento id', max_length=50)
    tipo_identificacion = models.CharField(max_length=2, choices=TIPOS_IDENTIFICACION)
    edad = models.IntegerField()
    tipo_edad = models.CharField(max_length=1, choices=UNIDADES_MEDIDA)

    institucion = models.ForeignKey(InstitucionEEID, related_name='muestras_eeid', on_delete=models.CASCADE)
    programado = models.BooleanField(choices=SI_NO_OPCIONES)
    control = models.ForeignKey(Control, related_name='muestras_eeid', on_delete=models.CASCADE)
    programa = models.ForeignKey(ProgramaEvaluacionExterna, related_name='muestras_eeid', on_delete=models.CASCADE)
    tipo_evento = models.ForeignKey(TipoEventoEvaluacionExterna, related_name='muestras_eeid', on_delete=models.CASCADE)
    tipo_muestra = models.ForeignKey(TipoMuestra, related_name='muestras_eeid', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'muestra EEID'
        verbose_name_plural = 'muestras EEID'

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(EEID, self).save(*args, **kwargs)

    @property
    def solicitante(self):
        return self.institucion
