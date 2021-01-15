from django.contrib import admin
from . import models as m


@admin.register(m.ConfigGeneral)
class ConfigGeneralAdmin(admin.ModelAdmin):
    list_display = ['id', 'firma_automatica_reporte']

@admin.register(m.Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_select_related = ['usuario']
    list_display = ['usuario', '__str__']

