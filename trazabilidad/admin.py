from django.contrib import admin
from reversion.admin import VersionAdmin
from .models import Programa, Prueba, TipoMuestra, Institucion, Departamento, Municipio, Eps, Paciente
from .models import Muestra, Clinica, PruebasRealizadas, Epsa, FuenteAbastecimiento, Poblado
from .models import InformacionAgua, TipoAgua, Temperatura, CategoriaAgua, MotivoAnalisis, MotivoRechazo
from .models import TipoVigilancia, LugarRecoleccion, ResponsableRecoleccion, Entomologia, Citohistopatologia, Control
from .models import TipoEvento, BancoSangre, TipoEnvase, EEDD, TipoEventoEvaluacionExterna, EEID, Solicitante
from .models import ProgramaEvaluacionExterna, InstitucionEEID, InstitucionEEDD, InstitucionBancoSangre, Metodo
from .models import InstitucionCitohistopatologia, ResultadoPrueba, ObjetoPrueba, CodigoPunto, DescripcionPunto
from .models import PuntajeRiesgo, NivelRiesgo
from . import models as m


class PruebaAdmin(admin.ModelAdmin):

    list_display = ('id', 'nombre', 'duracion', 'area')
    list_filter = ('area', 'nombre')
    search_fields = ('nombre', 'area')  # Agrega un buscador


class MuestraAdmin(admin.ModelAdmin):

    list_display = ('id', 'registro_recepcion')


class PruebasRealizadasAdmin(admin.ModelAdmin):

    list_display = ('id', 'prueba', 'estado')
    list_filter = ('prueba', 'estado')


class ReporteInline(admin.StackedInline):
    extra = 0
    model = m.Reporte
    show_change_link = True

@admin.register(m.Recepcion)
class RecepcionAdmin(VersionAdmin):

    inlines = [ReporteInline]
    search_fields = ['id', 'indice_radicado']
    list_filter = ('fecha_radicado', 'estado', 'estado_analista')
    list_display = ('id', 'indice_radicado', 'fecha_radicado', 'fecha_recepcion', 'confirmada', 'estado', 'estado_analista', 'analista')

@admin.register(m.Reporte)
class ReporteAdmin(VersionAdmin):

    list_display = ('id', 'registro_recepcion', 'fecha', 'fecha_aprobacion', 'confirmado', 'objeto')
    list_filter = ('confirmado',)


class PruebasSolicitadasInline(admin.TabularInline):
    extra = 0
    model = m.PruebasRealizadas

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ('prueba', 'metodo', 'resultados'):
            # dirty trick so queryset is evaluated and cached in .choices
            formfield.choices = formfield.choices
        return formfield


class ClinicaAdmin(admin.ModelAdmin):
    """"""

    list_display = ('id', 'paciente', 'institucion', 'municipio', 'embarazada')
    inlines = [PruebasSolicitadasInline]

@admin.register(m.Agua)
class AguaAdmin(admin.ModelAdmin):
    ordering = ['-id']
    inlines = [PruebasSolicitadasInline]
    raw_id_fields = ['informacion_general']
    list_select_related = ['registro_recepcion']
    search_fields = ['id', 'registro_recepcion__indice_radicado']


class EntomologiaAdmin(admin.ModelAdmin):
    """"""

    inlines = [PruebasSolicitadasInline]


class CitohistopatologiaAdmin(admin.ModelAdmin):
    """"""

    inlines = [PruebasSolicitadasInline]


class BancoSangreAdmin(admin.ModelAdmin):
    """"""

    inlines = [PruebasSolicitadasInline]


class EEDDAdmin(admin.ModelAdmin):
    """"""

    inlines = [PruebasSolicitadasInline]


class EEIDAdmin(admin.ModelAdmin):
    """"""

    inlines = [PruebasSolicitadasInline]

@admin.register(m.Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'programa')

admin.site.register(Programa)
admin.site.register(ResultadoPrueba)
admin.site.register(Prueba, PruebaAdmin)
admin.site.register(TipoMuestra)
admin.site.register(Institucion)
admin.site.register(Departamento)
admin.site.register(Municipio)
admin.site.register(Poblado)
admin.site.register(Eps)
admin.site.register(Paciente)
admin.site.register(Muestra, MuestraAdmin)
admin.site.register(Clinica, ClinicaAdmin)
admin.site.register(Epsa)
admin.site.register(FuenteAbastecimiento)
admin.site.register(InformacionAgua)
admin.site.register(TipoAgua)
admin.site.register(Temperatura)
admin.site.register(CategoriaAgua)
admin.site.register(MotivoAnalisis)
admin.site.register(MotivoRechazo)
admin.site.register(PruebasRealizadas, PruebasRealizadasAdmin)
admin.site.register(TipoVigilancia)
admin.site.register(LugarRecoleccion)
admin.site.register(ResponsableRecoleccion)
admin.site.register(Entomologia, EntomologiaAdmin)
admin.site.register(Control)
admin.site.register(TipoEvento)
admin.site.register(InstitucionCitohistopatologia)
admin.site.register(Citohistopatologia, CitohistopatologiaAdmin)
admin.site.register(TipoEnvase)
admin.site.register(InstitucionBancoSangre)
admin.site.register(BancoSangre, BancoSangreAdmin)
admin.site.register(TipoEventoEvaluacionExterna)
admin.site.register(InstitucionEEDD)
admin.site.register(EEDD, EEDDAdmin)
admin.site.register(ProgramaEvaluacionExterna)
admin.site.register(InstitucionEEID)
admin.site.register(EEID, EEDDAdmin)
admin.site.register(ObjetoPrueba)
admin.site.register(CodigoPunto)
admin.site.register(DescripcionPunto)
admin.site.register(Solicitante)
admin.site.register(Metodo)
admin.site.register(PuntajeRiesgo)
admin.site.register(NivelRiesgo)
