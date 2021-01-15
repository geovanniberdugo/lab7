# Generated by Django 2.2.14 on 2020-08-21 00:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0011_configgeneral'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='empleado',
            options={'permissions': [('can_see_analisis', 'Puede ver pagina de analisis'), ('can_aprobar_informes', 'Puede aprobar informes de resultado'), ('can_consultar_resultados_covid', 'Puede consultar resultados de covid'), ('can_exportar_ficha_excel', 'Puede exportar a excel las fichas de covid'), ('can_mail_resultados_covid', 'Puede enviar resultados de covid por mail'), ('can_see_ingresos_recepcionados', 'Puede ver pagina de ingresos recepcionados'), ('can_analizar_todos_programas', 'Puede ingresar analisis de todos los programas'), ('can_ingresar_muestras_programas_clinicos', 'Puede ingresar muestras de programas clinicos'), ('can_ingresar_muestras_programas_ambientes', 'Puede ingresar muestras de programas de ambientes')], 'verbose_name': 'empleado', 'verbose_name_plural': 'empleados'},
        ),
    ]
