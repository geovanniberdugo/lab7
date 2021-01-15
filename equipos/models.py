from django.conf import settings
from django.db import models
from common.models import EstadoMixin, UltimaModificacionMixin


class Equipo(EstadoMixin, UltimaModificacionMixin):
    """Modelo usado para guardar los equipos usados en el laboratorio."""

    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=100)
    temperatura_minima = models.DecimalField(max_digits=7, decimal_places=2)
    temperatura_maxima = models.DecimalField(max_digits=7, decimal_places=2)
    area = models.ForeignKey('trazabilidad.Area', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'equipo'
        verbose_name_plural = 'equipos'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        self.codigo = self.codigo.lower()
        super(Equipo, self).save(*args, **kwargs)


class RegistroTemperatura(models.Model):
    """Modelo usado para registrar las temperaturas diarias de los equipos usados en el laboratorio."""

    # opciones
    CENTIGRADOS = 'C'
    FARHENHEIT = 'F'
    UNIDADES = (
        (CENTIGRADOS, 'Celsius'),
        (FARHENHEIT, 'Farhenheit'),
    )

    equipo = models.ForeignKey(Equipo, related_name='registros', on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField()
    temperatura = models.DecimalField(max_digits=7, decimal_places=3)
    unidad = models.CharField(max_length=1, choices=UNIDADES)
    observaciones = models.TextField()
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = 'registro de temperatura'
        verbose_name_plural = 'registros de temperatura'

    def __str__(self):
        return self.equipo

    def save(self, *args, **kwargs):
        self.observaciones = self.observaciones.lower()
        super(RegistroTemperatura, self).save(*args, **kwargs)

    def alerta(self):
        """Retorna Verdadero si se paso de el rango"""
        if self.unidad == self.CENTIGRADOS:
            temperatura = self.temperatura
        else:
            from .utils import convertidor_unidad_temperatura
            temperatura = convertidor_unidad_temperatura(self.temperatura, self.unidad, self.CENTIGRADOS)

        if temperatura > self.equipo.temperatura_maxima or temperatura < self.equipo.temperatura_minima:
            return True
        return False
