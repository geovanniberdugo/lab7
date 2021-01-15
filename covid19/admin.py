from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.contrib import admin
from . import models

class UpgdResource(resources.ModelResource):

    class Meta:
        use_bulk = True
        model = models.Upgd
        import_id_fields = ['codigo', 'subindice']
        fields = ['nombre', 'codigo', 'subindice', 'email']
    
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        self.user = kwargs.get('user')
    
    def before_save_instance(self, instance, using_transactions, dry_run):
        if not instance.email:
            instance.email = 'conf@mail.com'
            instance.modificado_por = self.user

@admin.register(models.Upgd)
class UpgdAdmin(ImportExportModelAdmin):
    resource_class = UpgdResource
    list_display = ['nombre', 'ultima_modificacion']


class OcupacionResource(resources.ModelResource):

    class Meta:
        use_bulk = True
        model = models.Ocupacion
        import_id_fields = ['codigo']
        fields = ['nombre', 'codigo']

@admin.register(models.Ocupacion)
class OcupacionAdmin(ImportExportModelAdmin):
    resource_class = OcupacionResource

@admin.register(models.InfoPaciente)
class InfoPacienteAdmin(admin.ModelAdmin):
    pass

@admin.register(models.InfoGeneral346)
class InfoGeneral346Admin(admin.ModelAdmin):
    list_display = ['id', 'upgd', 'municipio_upgd']
    list_select_related = ['upgd', 'municipio_upgd']

@admin.register(models.Muestra346)
class Muestra346Admin(admin.ModelAdmin):
    pass

@admin.register(models.InfoGeneral348)
class InfoGeneral348Admin(admin.ModelAdmin):
    list_display = ['id', 'upgd', 'municipio_upgd']
    list_select_related = ['upgd', 'municipio_upgd']

@admin.register(models.Muestra348)
class Muestra348Admin(admin.ModelAdmin):
    pass


@admin.register(models.Tipificacion)
class TipificacionAdmin(admin.ModelAdmin):
    pass

class EapbResource(resources.ModelResource):

    class Meta:
        model = models.Eapb
        import_id_fields = ['codigo']
        fields = ['nombre', 'codigo', 'email']
    
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        self.user = kwargs.get('user')
    
    def before_save_instance(self, instance, using_transactions, dry_run):
        if not instance.email:
            instance.email = 'conf@mail.com'
            instance.modificado_por = self.user

@admin.register(models.Eapb)
class EapbAdmin(ImportExportModelAdmin):
    resource_class = EapbResource
    list_display = ['nombre', 'ultima_modificacion']
