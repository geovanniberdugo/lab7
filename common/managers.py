from django.db import models


class EstadoMixinQuerySet(models.QuerySet):
    """QuerySet para el modelo abstracto EstadoMixin."""

    def inactivos(self):
        """Devuelve los registros con estado inactivo."""

        from .models import EstadoMixin
        return self.filter(estado=EstadoMixin.INACTIVO)

    def activos(self):
        """Devuelve los registros con estado activo."""

        from .models import EstadoMixin
        return self.filter(estado=EstadoMixin.ACTIVO)
