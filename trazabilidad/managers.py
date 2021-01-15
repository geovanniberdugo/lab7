from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta
from django.db import models
from . import enums

from common.managers import EstadoMixinQuerySet

__author__ = 'tania'


class ProgramaManager(models.Manager):
    """Manager para el modelo programa."""

    def clinico(self):
        """Devuelve el programa clinico o None si no existe."""

        try:
            return self.get(codigo=enums.ProgramaEnum.CLINICO.value)
        except ObjectDoesNotExist:
            return None
    
    def covid19(self):
        """Devuelve el programa covid19 o None si no existe."""

        try:
            return self.get(codigo=enums.ProgramaEnum.COVID19.value)
        except ObjectDoesNotExist:
            return None

    def entomologia(self):
        """Devuelve el programa entomologia o None si no existe."""

        try:
            return self.get(codigo='entomologia')
        except ObjectDoesNotExist:
            return None

    def citohistopatologia(self):
        """Devuelve el programa citohistopatologia o None si no existe."""

        try:
            return self.get(codigo='citohistopatologia')
        except ObjectDoesNotExist:
            return None

    def banco_sangre(self):
        """Devuelve el programa banco de sangre o None si no existe."""

        try:
            return self.get(codigo='banco_sangre')
        except ObjectDoesNotExist:
            return None

    def eedd(self):
        """Devuelve el programa evaluación externa de desempeño directo o None si no existe."""

        try:
            return self.get(codigo='eedd')
        except ObjectDoesNotExist:
            return None

    def eeid(self):
        """Devuelve el programa evaluación externa de desempeño indirecto o None si no existe."""

        try:
            return self.get(codigo='eeid')
        except ObjectDoesNotExist:
            return None

    def aguas(self):
        """Devuelve el programa de aguas o None si no existe."""

        try:
            return self.get(codigo='aguas')
        except ObjectDoesNotExist:
            return None

    def alimentos(self):
        """Devuelve el programa de alimentos o None si no existe."""

        try:
            return self.get(codigo='alimentos')
        except ObjectDoesNotExist:
            return None

    def bebidas_alcoholicas(self):
        """Devuelve el programa de bebidas alcoholicas o None si no existe."""

        try:
            return self.get(codigo='bebidas_alcoholicas')
        except ObjectDoesNotExist:
            return None

    def ambientes(self):
        """Retorna los programas ambientales."""
        return list(filter(lambda x: x is not None, [self.aguas(), self.alimentos(), self.bebidas_alcoholicas()]))

class RecepcionQuerySet(models.QuerySet):
    """QuerySet para el modelo Recepción."""

    def ultimos_treinta_dias(self):
        """Devuelve un queryset con los ingresos recepcionados en los ultimos quince dias."""

        hoy = timezone.now().date()
        hace_treinta_dias = hoy - timedelta(days=90)
        manana = hoy + timedelta(days=1)

        return self.filter(fecha_recepcion__range=(hace_treinta_dias, manana))

    def parciales(self):
        """Devuelve un queryset con los ingresos parciales."""

        return self.filter(confirmada=False)

    def confirmados(self):
        """Devuelve un queryset con los ingresos comfirmados."""

        return self.filter(confirmada=True)

    def by_programas(self, codigos):
        return self.filter(programa__codigo__in=codigos)
    
    def exclude_programas(self, codigos):
        return self.exclude(programa__codigo__in=codigos)
    
    def by_programa_covid(self):
        return self.by_programas(codigos=[enums.ProgramaEnum.COVID19.value])
    
    def exclude_programa_covid(self):
        return self.exclude_programas(codigos=[enums.ProgramaEnum.COVID19.value])

    def exclude_programa_ambientes(self):
        return self.exclude_programas(codigos=[
            enums.ProgramaEnum.AGUAS.value,
            enums.ProgramaEnum.ALIMENTOS.value,
            enums.ProgramaEnum.ENTOMOLOGIA.value,
            enums.ProgramaEnum.BEBIDAS_ALCOHOLICAS.value,
        ])

    def exclude_programa_clinicos(self):
        return self.exclude_programas(codigos=[
            enums.ProgramaEnum.EEDD.value,
            enums.ProgramaEnum.EEID.value,
            enums.ProgramaEnum.COVID19.value,
            enums.ProgramaEnum.CLINICO.value,
            enums.ProgramaEnum.BANCO_SANGRE.value,
            enums.ProgramaEnum.CITOHISTOPATOLOGIA.value,
        ])

    def no_rechazados_recepcionista(self):
        return self.exclude(estado=self.model.RECHAZADO)

    def aceptados_recepcionista(self):
        return self.filter(estado=self.model.ACEPTADO)
    
    def rechazados_recepcionista(self):
        return self.filter(estado=self.model.RECHAZADO)

    def aceptados_analista(self):
        return self.filter(estado_analista=self.model.ACEPTADO)
    
    def rechazados_analista(self):
        return self.filter(estado_analista=self.model.RECHAZADO)

    def no_rechazados_analista(self):
        """"Devuelve un queryset con los ingresos que no han sido rechazados por el analista."""

        return self.exclude(estado_analista=self.model.RECHAZADO)

    def estado_analista_sin_llenar(self):
        return self.filter(estado_analista='')

    def by_area(self, area):
        """Filtra los ingresos por area."""

        return self.filter(muestras__pruebas__area=area).distinct()
    
    def by_areas(self, areas):
        return self.filter(muestras__pruebas__area__in=areas).distinct()
    
    def con_informe_confirmado(self):
        return self.filter(reportes__confirmado=True).distinct()
    
    def con_informe_aprobado(self):
        return self.filter(reportes__fecha_aprobacion__isnull=False).distinct()
    
    def con_informe_no_aprobado(self):
        return self.filter(reportes__fecha_aprobacion__isnull=True).distinct()
    
    def by_fecha_informe(self, desde, hasta):
        return self.filter(reportes__fecha__date__range=(desde, hasta))
    
    def by_fecha_recepcion(self, desde, hasta):
        return self.filter(fecha_recepcion__date__range=(desde, hasta))

class RecepcionManager(models.Manager.from_queryset(RecepcionQuerySet)):
    """Manager para los Querysets del modelo de Recepcion."""

    def get_queryset(self):
        return super().get_queryset().order_by('-fecha_recepcion', '-indice_radicado')

class PruebaQuerySet(EstadoMixinQuerySet):
    """QuerySet para el modelo Prueba."""

    def tipo_alimento(self, tipo):
        """Filtra las pruebas según un tipo de alimento."""

        return self.filter(subcategoria=tipo)

    def areas(self, areas):
        """Filtra las pruebas según las areas especificadas."""

        return self.filter(area__in=areas)
    
    def programa_covid19(self):
        return self.filter(area__programa__codigo=enums.ProgramaEnum.COVID19.value)

class ReporteQuerySet(models.QuerySet):

    def confirmados(self):
        return self.filter(confirmado=True)
    
    def aprobados(self):
        return self.filter(fecha_aprobacion__isnull=False)
    
    def no_aprobados(self):
        return self.filter(fecha_aprobacion__isnull=True)
    
    def by_ingresos(self, ingresos):
        return self.filter(registro_recepcion__in=ingresos)

class ReporteManager(models.Manager.from_queryset(ReporteQuerySet)):
    pass

class TipoMuestraQuerySet(EstadoMixinQuerySet):

    def by_programa(self, codigo):
        return self.filter(programas__codigo=codigo)

class TipoMuestraManager(models.Manager.from_queryset(TipoMuestraQuerySet)):
    pass

class PacienteQuerySet(EstadoMixinQuerySet):

    def by_identificacion(self, identificacion):
        return self.filter(identificacion=identificacion)

class PacienteManager(models.Manager.from_queryset(PacienteQuerySet)):
    pass

class PruebasRealizadasQuerySet(models.QuerySet):

    def positivos(self):
        return self.filter(resultados__id=1)
    
    def negativos(self):
        return self.filter(resultados__id=2)

class PruebasRealizadasManager(models.Manager.from_queryset(PruebasRealizadasQuerySet)):
    pass

