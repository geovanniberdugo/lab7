# Generated by Django 2.2.13 on 2020-07-14 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trazabilidad', '0006_auto_20200714_1049'),
    ]

    operations = [
        migrations.AddField(
            model_name='paciente',
            name='fecha_nacimiento',
            field=models.DateField(blank=True, null=True, verbose_name='fecha de nacimiento'),
        ),
    ]
