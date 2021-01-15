from django.contrib import admin
from trazabilidad.admin import PruebasSolicitadasInline
from .models import (
    BebidaAlcoholica, Institucion, InformacionBebidaAlcoholica, Grupo,
    Producto, Decreto, TipoEnvase, MotivoAnalisis
)


class BebidaAlcoholicaAdmin(admin.ModelAdmin):
    inlines = [PruebasSolicitadasInline]

admin.site.register(BebidaAlcoholica, BebidaAlcoholicaAdmin)
admin.site.register(Institucion)
admin.site.register(InformacionBebidaAlcoholica)
admin.site.register(Grupo)
admin.site.register(Producto)
admin.site.register(Decreto)
admin.site.register(TipoEnvase)
admin.site.register(MotivoAnalisis)
