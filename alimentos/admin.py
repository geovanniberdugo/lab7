from django.contrib import admin
from trazabilidad.admin import PruebasSolicitadasInline
from .models import Grupo, Categoria, Subcategoria, Alimento, Solicitante, InformacionAlimento
from .models import Fabricante, Distribuidor


class AlimentoAdmin(admin.ModelAdmin):

    inlines = [PruebasSolicitadasInline]


admin.site.register(Grupo)
admin.site.register(Categoria)
admin.site.register(Fabricante)
admin.site.register(Solicitante)
admin.site.register(Distribuidor)
admin.site.register(Subcategoria)
admin.site.register(InformacionAlimento)
admin.site.register(Alimento, AlimentoAdmin)
