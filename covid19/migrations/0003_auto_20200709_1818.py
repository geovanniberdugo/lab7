# Generated by Django 2.2.14 on 2020-07-09 23:18

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('covid19', '0002_auto_20200709_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='infogeneral348',
            name='fecha_antiviral',
            field=models.DateField(blank=True, null=True, verbose_name='¿Fecha de inicio de antiviral?'),
        ),
        migrations.AlterField(
            model_name='infogeneral348',
            name='fecha_ingreso_uci',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha de Ingreso a UCI'),
        ),
        migrations.AlterField(
            model_name='infogeneral348',
            name='seleccione_opciones',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('TS', 'Es trabajador del área de la salud'), ('DC', 'Presenta deterioro clínico sin etiología determinada, con evolución rápida (con necesidad de vasopresores y/o ventilación mecánica) desde el inicio de síntomas'), ('CA', 'Caso asociado a un brote o conglomerado'), ('VI', 'Viajó'), ('CC', 'Tuvo contacto con aves o cerdos enfermos o muertos durante 14 días previos al inicio de los síntomas'), ('CP', 'Tuvo contacto estrecho con personas enfermas o que hallan fallecido de IRAG durante los 14 días previos a los síntomas')], max_length=2), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='infogeneral348',
            name='uso_antivirales',
            field=models.CharField(blank=True, choices=[('SI', 'Si'), ('NO', 'No')], max_length=2, verbose_name='¿Usó antivirales en la última semana?'),
        ),
    ]
