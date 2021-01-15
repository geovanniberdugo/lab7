# Generated by Django 2.2.13 on 2020-07-07 03:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trazabilidad', '0002_auto_20200703_1236'),
    ]

    operations = [
        migrations.AddField(
            model_name='recepcion',
            name='responsable_tecnico',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ingresos_responsable_tecnico', to=settings.AUTH_USER_MODEL),
        ),
    ]