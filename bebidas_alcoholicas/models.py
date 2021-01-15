from django.db import models
from trazabilidad.models import Muestra
from common.models import UltimaModificacionMixin, EstadoMixin


class Institucion(UltimaModificacionMixin):
    """Modelo usado para guardar las instituciones remitentes de muestras de bebidas alcoholicas."""

    nombre = models.CharField(max_length=200, verbose_name='nombre remitente')
    direccion = models.CharField(max_length=100, verbose_name='dirección remitente', blank=True)

    class Meta:
        verbose_name = 'institución'
        verbose_name_plural = 'instituciones'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(Institucion, self).save(*args, **kwargs)


class InformacionBebidaAlcoholica(models.Model):
    """Modelo usado para guardar la información común que manejan las muestras de bebidas alcoholicas."""

    institucion = models.ForeignKey(Institucion, verbose_name='institución', on_delete=models.CASCADE)
    responsable_entrega = models.CharField(max_length=200, verbose_name='nombre responsable de entrega')
    cargo = models.CharField(max_length=100)
    numero_caso = models.CharField(max_length=100, verbose_name='n. de caso')
    numero_oficio = models.CharField(max_length=100, verbose_name='n. de oficio')
    poblado = models.ForeignKey('trazabilidad.Poblado', blank=True, null=True, on_delete=models.SET_NULL)
    sitio_toma = models.CharField(max_length=100, verbose_name='sitio de la toma', blank=True)
    propietario = models.CharField(max_length=100, verbose_name='propietario del producto', blank=True)
    direccion = models.CharField(max_length=100, verbose_name='dirección', blank=True)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'información general de las muestras de bebidas alcoholicas'
        verbose_name_plural = 'información general de las muestras de bebidas alcoholicas'

    def __str__(self):
        return self.institucion.nombre

    def save(self, *args, **kwargs):
        self.cargo = self.cargo.lower()
        self.numero_caso = self.numero_caso.lower()
        self.numero_oficio = self.numero_oficio.lower()
        self.responsable_entrega = self.responsable_entrega.lower()

        if self.direccion:
            self.direccion = self.direccion.lower()

        if self.sitio_toma:
            self.sitio_toma = self.sitio_toma.lower()

        if self.propietario:
            self.propietario = self.propietario.lower()

        super(InformacionBebidaAlcoholica, self).save(*args, **kwargs)


class Grupo(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los grupos de bebida alcoholicas."""

    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'grupo'
        verbose_name_plural = 'grupos'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(Grupo, self).save(*args, **kwargs)


class Producto(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los productos de bebidas alcoholicas."""

    nombre = models.CharField(max_length=200)
    grupo = models.ForeignKey(Grupo, related_name='productos', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(Producto, self).save(*args, **kwargs)


class Decreto(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los decretos."""

    nombre = models.CharField(max_length=100)
    grupo = models.ForeignKey(Grupo, related_name='decretos', on_delete=models.CASCADE)
    pruebas = models.ManyToManyField('trazabilidad.Prueba')

    class Meta:
        verbose_name = 'decreto'
        verbose_name_plural = 'decretos'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(Decreto, self).save(*args, **kwargs)


class TipoEnvase(UltimaModificacionMixin):
    """Modelo usado para guardar la información del tipo de envase."""

    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'tipo de envase'
        verbose_name_plural = 'tipos de envase'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(TipoEnvase, self).save(*args, **kwargs)


class MotivoAnalisis(UltimaModificacionMixin):
    """Modelo usado para guardar los motivos de analisis."""

    motivo = models.CharField(max_length=200, verbose_name='nombre del motivo')

    class Meta:
        verbose_name = 'motivo de analisis'
        verbose_name_plural = 'motivos de analisis'

    def __str__(self):
        return self.motivo.capitalize()

    def save(self, *args, **kwargs):
        self.motivo = self.motivo.lower()
        super(MotivoAnalisis, self).save(*args, **kwargs)


class BebidaAlcoholica(Muestra):
    """Modelo usado para guardar las muestras de bebidas alcoholicas ingresadas en un laboratorio.

    El modelo extiende Muestra."""

    # opciones
    BUENO = True
    MALO = False
    BUENO_MALO_OPCIONES = (
        (BUENO, 'BUENO'),
        (MALO, 'MALO'),
    )

    informacion_general = models.ForeignKey(InformacionBebidaAlcoholica, on_delete=models.CASCADE)
    temperatura = models.CharField(max_length=100, verbose_name='temperatura de ingreso', blank=True)
    producto = models.ForeignKey(Producto, verbose_name='nombre comercial del producto', blank=True, null=True, on_delete=models.SET_NULL)
    registro_sanitario = models.CharField(max_length=150, verbose_name='registro sanitario', blank=True)
    numero_lote = models.CharField(max_length=100, verbose_name='n. lote', blank=True)
    ano_vencimiento = models.PositiveIntegerField(blank=True, null=True)
    mes_vencimiento = models.PositiveIntegerField(blank=True, null=True)
    dia_vencimiento = models.PositiveIntegerField(blank=True, null=True)
    no_aplica_vencimiento = models.NullBooleanField()
    fabricante = models.CharField(max_length=150, verbose_name='empresa fabricante', blank=True)
    direccion_fabricante = models.CharField(max_length=100, verbose_name='dirección fabricante', blank=True)
    grado = models.CharField(max_length=100, verbose_name='grado alcoholimetrico declarado', blank=True)
    contenido = models.CharField(max_length=200, verbose_name='contenido declarado', blank=True)
    tipo_envase = models.ForeignKey(TipoEnvase, verbose_name='tipo de envase', blank=True, null=True, on_delete=models.SET_NULL)
    aspecto_externo = models.NullBooleanField(choices=BUENO_MALO_OPCIONES)
    aspecto_interno = models.NullBooleanField(choices=BUENO_MALO_OPCIONES)
    hermeticidad = models.NullBooleanField(choices=BUENO_MALO_OPCIONES)
    motivo_analisis = models.ForeignKey(MotivoAnalisis, verbose_name='motivo del analisis', blank=True, null=True, on_delete=models.SET_NULL)
    decreto = models.ForeignKey(Decreto, verbose_name='decreto', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'muestra de bebida alcoholica'
        verbose_name_plural = 'muestras de bebidas alcoholicas'

    @property
    def solicitante(self):
        return self.informacion_general.institucion
