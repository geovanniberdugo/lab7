from django.db import models
from trazabilidad.models import Muestra
from common.models import UltimaModificacionMixin, EstadoMixin


class Solicitante(UltimaModificacionMixin):
    """Modelo usado para guardar los solicitantes de tomas de muestras de alimentos."""

    nombre = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'solicitante'
        verbose_name_plural = 'solicitantes'

    def __str__(self):
        return self.nombre.capitalize()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(Solicitante, self).save(*args, **kwargs)


class InformacionAlimento(models.Model):
    """Modelo usado para guardar la información común que manejan las muestras de alimentos."""

    solicitante = models.ForeignKey(Solicitante, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=100, verbose_name='dirección')
    responsable = models.CharField(max_length=200)
    cargo = models.CharField(max_length=100)
    poblado = models.ForeignKey('trazabilidad.Poblado', on_delete=models.CASCADE)
    sitio_toma = models.CharField(max_length=100, verbose_name='sitio de la toma')
    direccion_recoleccion = models.CharField(max_length=100, verbose_name='dirección')
    fecha = models.DateTimeField()

    class Meta:
        verbose_name = 'información general de las muestras de alimento'
        verbose_name_plural = 'información general de las muestras de alimento'

    def __str__(self):
        return self.solicitante.nombre

    def save(self, *args, **kwargs):
        self.direccion = self.direccion.lower()
        self.responsable = self.responsable.lower()
        self.cargo = self.cargo.lower()
        super(InformacionAlimento, self).save(*args, **kwargs)


class Grupo(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los grupos de alimento."""

    codigo = models.IntegerField()
    descripcion = models.CharField(max_length=250, verbose_name='descripción')

    class Meta:
        verbose_name = 'grupo de alimento'
        verbose_name_plural = 'grupos de alimentos'

    def __str__(self):
        return "{0} - {1}".format(self.codigo, self.descripcion)

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.lower()
        super(Grupo, self).save(*args, **kwargs)


class Categoria(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar las categorias de los alimentos."""

    codigo = models.IntegerField()
    descripcion = models.CharField(max_length=200, verbose_name='descripción')
    grupo = models.ForeignKey(Grupo, related_name='categorias', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'categoría de alimento'
        verbose_name_plural = 'categorías de alimentos'

    def __str__(self):
        return "{0}.{1} - {2}".format(self.grupo.codigo, self.codigo, self.descripcion)

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.lower()
        super(Categoria, self).save(*args, **kwargs)


class Subcategoria(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar las subcategorias de los alimentos."""

    codigo = models.IntegerField()
    descripcion = models.CharField(max_length=200, verbose_name='descripción')
    categoria = models.ForeignKey(Categoria, related_name='subcategorias', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'subcategoría de alimento'
        verbose_name_plural = 'subcategorías de alimentos'

    def __str__(self):
        return "{0}.{1}.{2} - {3}".format(self.categoria.grupo.codigo,
                                          self.categoria.codigo,
                                          self.codigo,
                                          self.descripcion)

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.lower()
        super(Subcategoria, self).save(*args, **kwargs)


class Fabricante(UltimaModificacionMixin):
    """Modelo usado para guardar los fabricantes de las muestras de alimentos."""

    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'fabricante'
        verbose_name_plural = 'fabricantes'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(Fabricante, self).save(*args, **kwargs)


class Distribuidor(UltimaModificacionMixin):
    """Modelo usado para guardar los distribuidor de las muestras de alimentos."""

    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'distribuidor'
        verbose_name_plural = 'distribuidores'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        super(Distribuidor, self).save(*args, **kwargs)


class Decreto(EstadoMixin, UltimaModificacionMixin):
    """Modelo de decreto de normatividad para las pruebas de alimentos."""

    nombre = models.CharField(max_length=255, verbose_name='nombre')
    tipo = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    area = models.ForeignKey('trazabilidad.Area', on_delete=models.CASCADE)
    pruebas = models.ManyToManyField('trazabilidad.Prueba', related_name='pruebas_alimentos')

    def __str__(self):
        return self.nombre.title()


class Alimento(Muestra):
    """Modelo usado para guardar las muestras de alimentos ingresadas a un laboratorio.

    El modelo extiende de Muestra."""

    # opciones
    SI = True
    NO = False
    NO_APLICA = None
    SI_NO_OPCIONES = (
        (SI, 'Si'),
        (NO, 'No'),
        (NO_APLICA, 'No Aplica'),
    )

    informacion_general = models.ForeignKey(InformacionAlimento, on_delete=models.CASCADE)
    unidad_muestra = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        blank=True,
        null=True,
        verbose_name='n. unidad de muestra'
    )
    contenido_neto = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='contenido neto por unidad de muestra'
    )
    unidad_contramuestra = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        blank=True,
        null=True,
        verbose_name='n. unidad de contramuestra'
    )
    tipo = models.ForeignKey(Categoria, blank=True, null=True, verbose_name='tipo de alimento', on_delete=models.SET_NULL)
    subcategoria = models.ForeignKey(Subcategoria, blank=True, null=True, verbose_name="sub-categoria", on_delete=models.SET_NULL)
    descripcion = models.CharField(max_length=200, blank=True, verbose_name='descripción del producto según el rótulo')
    registro_sanitario = models.CharField(max_length=200, blank=True)
    lote = models.CharField(max_length=200, blank=True)
    ano_vencimiento = models.PositiveIntegerField(blank=True, null=True)
    mes_vencimiento = models.PositiveIntegerField(blank=True, null=True)
    dia_vencimiento = models.PositiveIntegerField(blank=True, null=True)
    propietario = models.CharField(max_length=200, blank=True)
    fabricante = models.ForeignKey(Fabricante, blank=True, null=True, on_delete=models.SET_NULL)
    distribuidor = models.ForeignKey(Distribuidor, blank=True, null=True, on_delete=models.SET_NULL)
    importador = models.CharField(max_length=100, blank=True)
    direccion_importador = models.CharField(max_length=130, blank=True)
    responsable_entrega = models.CharField(max_length=100, blank=True, verbose_name='responsable de la entrega')
    temperatura = models.CharField(max_length=100, blank=True)
    temperatura_recoleccion = models.CharField(max_length=100, blank=True)
    cumple = models.NullBooleanField(choices=SI_NO_OPCIONES, verbose_name='cumple con criterios de aceptación')
    cadena_custodia = models.NullBooleanField(choices=SI_NO_OPCIONES, verbose_name='cadena de custodia')
    constancia_pago = models.NullBooleanField(choices=SI_NO_OPCIONES, verbose_name='constancia de pago')
    decretos = models.ManyToManyField(Decreto, blank=True, related_name='muestras_alimento')
    motivo_analisis = models.ForeignKey(
        'trazabilidad.MotivoAnalisis',
        verbose_name='motivo del analisis',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = 'muestra de alimento'
        verbose_name_plural = 'muestras de alimento'

    @property
    def solicitante(self):
        return self.informacion_general.solicitante
