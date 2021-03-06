# Generated by Django 2.2.14 on 2020-07-09 20:17

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cie10_django', '0001_initial'),
        ('trazabilidad', '0002_auto_20200703_1236'),
        ('covid19', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InfoGeneral348',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evento', models.CharField(blank=True, choices=[('346', 'COVID-19'), ('345', 'ESI/IRAG'), ('348', 'IRAG INSITADO')], max_length=4)),
                ('fecha_notificacion', models.DateField(blank=True, null=True, verbose_name='fecha de la notificación')),
                ('fuente', models.CharField(blank=True, choices=[('5', 'Investigaciones'), ('2', 'Busqueda activa ins.'), ('4', 'Busqueda activa com.'), ('3', 'Vigilancia intensificada'), ('1', 'Notificacion rutinaria')], max_length=2, null=True)),
                ('pais_residencia', django_countries.fields.CountryField(default='CO', max_length=2, verbose_name='pais de residencia')),
                ('direccion', models.CharField(blank=True, max_length=150, verbose_name='dirección de residencia')),
                ('fecha_consulta', models.DateField(blank=True, null=True, verbose_name='fecha de consulta')),
                ('fecha_inicio_sintomas', models.DateField(blank=True, null=True, verbose_name='fecha de inicio de sintomas')),
                ('clasificacion_inicial_caso', models.CharField(blank=True, choices=[('2', 'Probable'), ('1', 'Sospechoso'), ('5', 'Conf. clinica'), ('4', 'Conf. por laboratorio'), ('3', 'Conf. nexo epidemiologico')], max_length=2, verbose_name='clasificación inicial de caso')),
                ('hospitalizado', models.CharField(blank=True, choices=[('SI', 'Si'), ('NO', 'No')], max_length=2)),
                ('fecha_hospitalizacion', models.DateField(blank=True, null=True, verbose_name='fecha de hospitalización')),
                ('condicion_final', models.CharField(blank=True, choices=[('1', 'Vivo'), ('2', 'Muerto'), ('0', 'No sabe, no responde')], max_length=2)),
                ('fecha_defuncion', models.DateField(blank=True, null=True, verbose_name='fecha de defunción')),
                ('certificado_defuncion', models.CharField(blank=True, max_length=100, verbose_name='número de certificado de defunción')),
                ('profesional_diligenciante', models.CharField(blank=True, max_length=200, verbose_name='nombre del profesional que diligencio la ficha')),
                ('telefono', models.CharField(blank=True, max_length=15)),
                ('fecha_ajuste', models.DateField(blank=True, null=True, verbose_name='fecha de ajuste')),
                ('clasificacion_final_caso', models.CharField(blank=True, choices=[('0', 'No aplica'), ('6', 'Descartado'), ('5', 'Conf. clinica'), ('7', 'Otra actualización'), ('4', 'Conf. por laboratorio'), ('3', 'Conf. nexo epidemiologico'), ('D', 'Descartado por error de digitación')], max_length=2, verbose_name='seguimiento y clasificación final de caso')),
                ('seleccione_opciones', models.CharField(blank=True, choices=[('TS', 'Es trabajador del área de la salud'), ('DC', 'Presenta deterioro clínico sin etiología determinada, con evolución rápida (con necesidad de vasopresores y/o ventilación mecánica) desde el inicio de síntomas'), ('CA', 'Caso asociado a un brote o conglomerado'), ('VI', 'Viajó'), ('CC', 'Tuvo contacto con aves o cerdos enfermos o muertos durante 14 días previos al inicio de los síntomas'), ('CP', 'Tuvo contacto estrecho con personas enfermas o que hallan fallecido de IRAG durante los 14 días previos a los síntomas')], max_length=2, verbose_name='Seleccione una o varias de las siguientes opciones')),
                ('viaje_nacional', models.CharField(blank=True, choices=[('SI', 'Si'), ('NO', 'No')], max_length=2, verbose_name='¿El Viaje fue en territorio nacional?')),
                ('viaje_internacional', models.CharField(blank=True, choices=[('SI', 'Si'), ('NO', 'No')], max_length=2, verbose_name='¿El Viaje fue internacional?')),
                ('pais_viaje_iternacional', django_countries.fields.CountryField(blank=True, max_length=2, verbose_name='¿donde?')),
                ('caso_irag', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('TOS', 'Paciente con Tos'), ('FI', 'Paciente con Fiebre')], max_length=4), blank=True, null=True, size=None)),
                ('neumococo', models.CharField(blank=True, choices=[('SI', 'Si'), ('NO', 'No'), ('DE', 'Desconocido')], max_length=2, verbose_name='Streptococcus pneumoniae (neumococo)')),
                ('dosis_neumococo', models.CharField(blank=True, max_length=10, verbose_name='dosis')),
                ('influenza_estacional', models.CharField(blank=True, choices=[('SI', 'Si'), ('NO', 'No'), ('DE', 'Desconocido')], max_length=2)),
                ('dosis_influenza_estacional', models.CharField(blank=True, max_length=10, verbose_name='dosis')),
                ('antecedentes_clinicos', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('VIH', 'VIH'), ('EP', 'EPOC'), ('AS', 'Asma'), ('OT', 'Otros'), ('CA', 'Cancer'), ('FU', 'Fumador'), ('OB', 'Obesidad'), ('DI', 'Diabetes'), ('DE', 'Desnutrición'), ('TU', 'Tuberculosis'), ('EC', 'Enfermedad cardiaca'), ('IR', 'Insuficiencia renal'), ('MI', 'Toma medicamentos inmusupresores')], max_length=3), blank=True, null=True, size=None)),
                ('otros_antecedentes_clinicos', models.CharField(blank=True, max_length=3, verbose_name='¿cuáles otros?')),
                ('radiografia_torax', models.CharField(blank=True, choices=[('3', 'Ninguno'), ('1', 'Infiltrado alveolar o neumonía'), ('2', 'Infiltrados intersticiales')], max_length=2)),
                ('antibiotico_ultimas_semanas', models.CharField(blank=True, choices=[('SI', 'Si'), ('NO', 'No')], max_length=2)),
                ('uso_antivirales', models.CharField(blank=True, choices=[('SI', 'Si'), ('NO', 'No')], max_length=2, verbose_name='¡Usó antivirales en la última semana?')),
                ('fecha_antiviral', models.DateField(verbose_name='¿Fecha de inicio de antiviral?')),
                ('servicio_hospitalizo', models.CharField(blank=True, choices=[('HG', 'Hospitalización General'), ('UCI', 'UCI')], max_length=3, verbose_name='Servicio en el que se hospitalizó')),
                ('fecha_ingreso_uci', models.DateField(verbose_name='Fecha de Ingreso a UCI')),
                ('complicaciones', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('DP', 'Derrame Pleural'), ('PE', 'Derrame Pericárdico'), ('MI', 'Miocarditis'), ('SE', 'Septicemia'), ('FR', 'Falla Respiratoria'), ('OT', 'Otro')], max_length=3), blank=True, null=True, size=None, verbose_name='Si hubo complicaciones, ¿Cuáles se presentaron?')),
                ('causa_muerte', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='cie10_django.CIE10', verbose_name='causa básica de muerte')),
                ('info_paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='covid19.InfoPaciente')),
                ('municipio_residencia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='trazabilidad.Municipio', verbose_name='municipio de residencia')),
                ('municipio_upgd', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='trazabilidad.Municipio')),
                ('municipio_viaje_nacional', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='trazabilidad.Municipio', verbose_name='¿Donde?')),
                ('upgd', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='covid19.Upgd')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='infogeneral346',
            name='info_paciente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='covid19.InfoPaciente'),
        ),
        migrations.CreateModel(
            name='Muestra348',
            fields=[
                ('muestra_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='trazabilidad.Muestra')),
                ('fecha_toma', models.DateField()),
                ('informacion_general', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='covid19.InfoGeneral348')),
                ('tipo_muestra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='muestras_348', to='trazabilidad.TipoMuestra')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('trazabilidad.muestra',),
        ),
    ]
