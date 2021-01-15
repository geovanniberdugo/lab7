# Generated by Django 2.2.13 on 2020-07-29 17:22

from django.db import migrations
from django.db.models import F

def update_fecha_aprobacion(apps, schema_editor):
    Reporte = apps.get_model('trazabilidad', 'Reporte')

    (
        Reporte.objects
            .filter(fecha_aprobacion__isnull=True, confirmado=True, registro_recepcion__fecha_recepcion__year__lte=2019)
            .update(fecha_aprobacion=F('fecha'))
    )

def update_fecha_aprobacion_to_null(apps, schema_editor):
    Reporte = apps.get_model('trazabilidad', 'Reporte')

    (
        Reporte.objects
            .filter(fecha_aprobacion__isnull=True, confirmado=True, registro_recepcion__fecha_recepcion__year__lte=2019)
            .update(fecha_aprobacion=None)
    )


class Migration(migrations.Migration):

    dependencies = [
        ('trazabilidad', '0010_reporte_fecha_aprobacion'),
    ]

    operations = [
        migrations.RunPython(update_fecha_aprobacion, reverse_code=update_fecha_aprobacion_to_null),
    ]
