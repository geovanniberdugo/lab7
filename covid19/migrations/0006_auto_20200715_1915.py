# Generated by Django 2.2.13 on 2020-07-16 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('covid19', '0005_auto_20200714_1850'),
    ]

    operations = [
        migrations.AlterField(
            model_name='infogeneral346',
            name='otros_antecedentes_clinicos',
            field=models.CharField(blank=True, max_length=200, verbose_name='¿cuáles otros?'),
        ),
    ]
