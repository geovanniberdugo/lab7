# Generated by Django 2.2.13 on 2020-07-07 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trazabilidad', '0003_recepcion_responsable_tecnico'),
        ('administracion', '0003_auto_20200703_1236'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='empleado',
            options={'permissions': [('can_see_analisis', 'Puede ver pagina de analisis'), ('can_ingresar_muestras_covid', 'Puede ingresar muestras de covid19'), ('can_analizar_todos_programas', 'Puede ingresar analisis de todos los programas')], 'verbose_name': 'empleado', 'verbose_name_plural': 'empleados'},
        ),
        migrations.AddField(
            model_name='empleado',
            name='areas',
            field=models.ManyToManyField(to='trazabilidad.Area'),
        ),
        migrations.AddField(
            model_name='empleado',
            name='codigo',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='empleado',
            name='responsable_tecnico',
            field=models.BooleanField(default=False),
        ),
    ]
