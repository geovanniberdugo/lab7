# Generated by Django 2.2.13 on 2020-07-16 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trazabilidad', '0007_paciente_fecha_nacimiento'),
    ]

    operations = [
        migrations.AddField(
            model_name='recepcion',
            name='fecha_envio_resultados',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]