# Generated by Django 2.2.13 on 2020-07-21 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('covid19', '0007_auto_20200721_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='infogeneral348',
            name='otros_antecedentes_clinicos',
            field=models.CharField(blank=True, max_length=200, verbose_name='¿cuáles otros?'),
        ),
    ]