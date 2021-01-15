from django.db import models

class EmpleadoQuerySet(models.QuerySet):
    
    def is_responsable_tecnico(self):
        return self.filter(responsable_tecnico=True)
    
    def by_areas(self, areas):
        return self.filter(areas__in=areas).distinct()

class EmpleadoManager(models.Manager.from_queryset(EmpleadoQuerySet)):
    pass