from django.conf import settings
from django.db import models

from .managers import EstadoMixinQuerySet


class EstadoMixin(models.Model):
    """Modelo abstracto para manejar el campo estado."""

    # opciones
    ACTIVO = 'A'
    INACTIVO = 'I'
    ESTADOS = (
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
    )

    estado = models.CharField(max_length=1, choices=ESTADOS)

    # managers
    objects = EstadoMixinQuerySet.as_manager()

    class Meta:
        abstract = True


class UltimaModificacionMixin(models.Model):
    """Modelo abstracto que maneja la fecha de la ultima modificación y quien modifico un modelo."""

    ultima_modificacion = models.DateTimeField(auto_now=True)
    modificado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="%(app_label)s_%(class)s_set", on_delete=models.CASCADE)

    class Meta:
        abstract = True
