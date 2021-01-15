import itertools
from django import forms
from contextlib import suppress
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field
from crispy_forms.bootstrap import FormActions, StrictButton

from .models import Paciente, Recepcion, Institucion, Clinica, Area, Departamento, Municipio, Prueba, EEID
from .models import Entomologia, ResponsableRecoleccion, LugarRecoleccion, InstitucionCitohistopatologia, EEDD
from .models import Citohistopatologia, InstitucionBancoSangre, BancoSangre, InstitucionEEDD, InstitucionEEID, Control
from .models import PruebasRealizadas, TipoMuestra, Programa, Muestra, ResultadoPrueba, TipoVigilancia
from .models import TipoEvento, TipoEnvase, ProgramaEvaluacionExterna, TipoEventoEvaluacionExterna, Temperatura
from .models import RegistroTemperaturaArea, NivelRiesgo
from administracion import models as admin_models
from common import forms as common_f
from . import models as m
from . import enums

__author__ = 'tania'


class RecepcionForm(forms.ModelForm):
    """Formulario para el manejo de los registros de recepción."""

    error_css_class = 'has-error'

    class Meta:
        model = Recepcion
        fields = ['fecha_recepcion']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['fecha_recepcion'].widget.attrs.update({'class': 'form-control'})
        self.confirmar = True if 'confirmado' in self.data else False

    def save(self, commit=True):
        if self.confirmar:
            self.instance.confirmada = True
            self.instance.confirmado_por = self.user
            self.instance.fecha_confirmacion = timezone.now()

        return super().save(commit)


class ActualizarRecepcionForm(RecepcionForm):
    """Formulario para actualizar los registros de recepción."""

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        if not user.has_perm('administracion.can_editar_ingresos'):
            self.fields['fecha_recepcion'].widget.attrs.update({'readonly': 'readonly'})


class EstadoIngresoForm(forms.ModelForm):
    """Formulario que permite definir el estado de recepción de una muestra que llega al laboratorio."""

    def __init__(self, *args, **kwargs):
        super(EstadoIngresoForm, self).__init__(*args, **kwargs)
        self.fields['motivo_rechazo'].widget.attrs.update({'class': 'rechazo_check'})
        self.fields['estado'].required = True
        self.fields['observaciones'].required = False

    def clean(self):
        cleaned_data = super(EstadoIngresoForm, self).clean()
        estado = cleaned_data.get('estado', None)
        motivo = cleaned_data['motivo_rechazo']
        observaciones = cleaned_data['observaciones']

        if estado == Recepcion.RECHAZADO:
            if not motivo:
                self.add_error('motivo_rechazo', 'Este campo es obligatorio.')

            if not observaciones:
                self.add_error('observaciones', 'Este campo es obligatorio.')

    class Meta:
        model = Recepcion
        fields = ['estado', 'motivo_rechazo', 'observaciones']
        widgets = {
            'motivo_rechazo': forms.CheckboxSelectMultiple()
        }


class EstadoIngresoAnalistaForm(forms.ModelForm):
    """Formulario que permite definir el estado de recepción de una muestra por parte del analista."""

    def __init__(self, *args, **kwargs):
        super(EstadoIngresoAnalistaForm, self).__init__(*args, **kwargs)
        self.fields['motivo_rechazo_analista'].widget.attrs.update({'class': 'rechazo_check'})
        self.fields['estado_analista'].required = True

    def clean(self):
        cleaned_data = super(EstadoIngresoAnalistaForm, self).clean()
        estado = cleaned_data.get('estado_analista', None)

        if estado == Recepcion.RECHAZADO:
            motivo = cleaned_data['motivo_rechazo_analista']
            observaciones = cleaned_data['observaciones_analista']

            if not motivo:
                self.add_error('motivo_rechazo_analista', 'Este campo es obligatorio.')

            if not observaciones:
                self.add_error('observaciones_analista', 'Este campo es obligatorio.')

    class Meta:
        model = Recepcion
        fields = ['estado_analista', 'motivo_rechazo_analista', 'observaciones_analista']
        widgets = {
            'motivo_rechazo_analista': forms.CheckboxSelectMultiple()
        }


class ObservacionSemaforoForm(forms.ModelForm):
    """Formulario para el manejo de las observaciones que desea poner el analista cuando el tiempo de desarrollo de
    una prueba ha sido mayor al tiempo normal de duración de esta."""

    def __init__(self, *args, **kwargs):
        super(ObservacionSemaforoForm, self).__init__(*args, **kwargs)
        self.fields['observacion_semaforo'].widget.attrs.update({'class': 'form-control input-sm'})
        self.fields['observacion_semaforo'].required = True

    class Meta:
        model = PruebasRealizadas
        fields = ['observacion_semaforo']


class ResultadoPruebaAnalisisForm(forms.ModelForm):
    """Formulario para el manejo del resultado de una prueba realizada por el analista a una muestra."""

    class Meta:
        model = PruebasRealizadas
        fields = ['resultados', 'resultado_numerico', 'metodo', 'concepto']

    def __init__(self, *args, **kwargs):
        super(ResultadoPruebaAnalisisForm, self).__init__(*args, **kwargs)
        self.fields['resultado_numerico'].label = 'Resultado'
        self.fields['resultado_numerico'].widget.attrs.update({'step': '0.01'})
        self.fields['metodo'].label = 'Metodo utilizado'

        self.fields['resultados'].queryset = self.instance.prueba.resultados.all()
        self.fields['metodo'].queryset = self.instance.prueba.metodos.all()
        self.fields['metodo'].required = True

        if self.instance.muestra.registro_recepcion.programa in Programa.objects.ambientes():
            if self.instance.muestra.registro_recepcion.programa == Programa.objects.bebidas_alcoholicas() and self.instance.prueba.area.oculto:
                self.fields['resultados'].required = True
            else:
                self.fields['resultado_numerico'].required = True
        else:
            self.fields['resultados'].required = True
    
    def save(self, commit=True):
        prueba = super().save(commit)
        prueba.actualizar_estado()

        return prueba

class ComentarioRecepcionistaForm(forms.ModelForm):
    """Formulario para el manejo del ingreso de la acción tomada por el recepcionista cuando un ingreso es rechazado
    por el analista."""

    error_css_class = 'has-error'

    def __init__(self, *args, **kwargs):
        super(ComentarioRecepcionistaForm, self).__init__(*args, **kwargs)
        self.fields['comentario'].required = True

    class Meta:
        model = Recepcion
        fields = ['comentario']


class PacienteForm(forms.ModelForm):
    """Formulario para el manejo de pacientes."""

    error_css_class = 'has-error'

    sin_identificacion = forms.BooleanField(required=False)

    class Meta:
        model = Paciente
        fields = ['sin_identificacion', 'tipo_identificacion', 'identificacion', 'nombre', 'apellido', 'edad',
                  'tipo_edad', 'direccion', 'eps', 'sexo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['identificacion'].widget = forms.NumberInput()
        self.fields['tipo_identificacion'].widget.attrs.update({'class': 'form-control'})
        self.fields['identificacion'].widget.attrs.update({'class': 'form-control'})
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['apellido'].widget.attrs.update({'class': 'form-control'})
        self.fields['edad'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_edad'].widget.attrs.update({'class': 'form-control'})
        self.fields['direccion'].widget.attrs.update({'class': 'form-control'})
        self.fields['eps'].widget.attrs.update({'class': 'form-control'})
        self.fields['sexo'].widget.attrs.update({'class': 'form-control'})


class InstitucionForm(forms.ModelForm):
    """Formulario para el manejo de instituciones."""

    error_css_class = 'has-error'

    institucion = forms.ModelChoiceField(
        required=False,
        empty_label='Nueva institución',
        queryset=Institucion.objects.select_related('municipio__departamento').all(),
    )
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super(InstitucionForm, self).__init__(*args, **kwargs)
        self.fields['institucion'].widget.attrs.update({'class': 'form-control'})
        self.fields['departamento'].widget.attrs.update({'class': 'form-control'})
        self.fields['municipio'].widget.attrs.update({'class': 'form-control'})
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})

        self.fields['nombre'].required = False
        self.fields['municipio'].required = False
        self.fields['departamento'].required = False

        if self.instance.pk:
            self.fields['institucion'].initial = self.instance

        try:
            id_departamento = int(self.data.get('institucion-departamento'))
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=id_departamento)
        except:
            self.fields['municipio'].queryset = Municipio.objects.none()

    def clean(self):
        cleaned_data = super(InstitucionForm, self).clean()
        institucion = cleaned_data['institucion']

        if not institucion:
            nombre = cleaned_data.get('nombre', None)
            municipio = cleaned_data.get('municipio', None)
            departamento = cleaned_data.get('departamento', None)

            if not nombre:
                self.add_error('nombre', 'Este campo es obligatorio.')

            if not municipio:
                self.add_error('municipio', 'Este campo es obligatorio.')

            if not departamento:
                self.add_error('departamento', 'Este campo es obligatorio.')

    def save(self, commit=True):
        if self.cleaned_data['institucion'] is None:
            self.instance.pk = None
            return super(InstitucionForm, self).save(commit)
        else:
            return self.cleaned_data['institucion']

    class Meta:
        model = Institucion
        fields = ['institucion', 'nombre', 'departamento', 'municipio']


class MuestraClinicaForm(forms.ModelForm):
    """Formulario para el manejo de las muestras clínicas."""

    error_css_class = 'has-error'

    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=True, label='Departamento')
    area = forms.ModelChoiceField(
        required=False,
        label='Area',
        queryset=Area.objects.filter(programa=Programa.objects.clinico()),
    )

    class Meta:
        model = Clinica
        fields = ['tipo_muestras', 'area', 'pruebas', 'municipio', 'barrio', 'embarazada', 'temp_ingreso']
        labels = {
            'pruebas': 'Pruebas solicitadas'
        }
        widgets = {
            'pruebas': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        confirmar = kwargs.pop('confirmar', None)
        super(MuestraClinicaForm, self).__init__(*args, **kwargs)
        self.fields['departamento'].widget.attrs.update({'class': 'form-control'})
        self.fields['municipio'].widget.attrs.update({'class': 'form-control'})
        self.fields['barrio'].widget.attrs.update({'class': 'form-control'})
        self.fields['embarazada'].widget.attrs.update({'class': 'form-control'})
        self.fields['temp_ingreso'].required = True
        self.fields['tipo_muestras'].required = True
        queryset = TipoMuestra.objects.by_programa(enums.ProgramaEnum.CLINICO.value).activos()
        self.fields['tipo_muestras'].queryset = queryset

        if self.is_bound:
            try:
                id_departamento = int(self.data.get('clinica-departamento'))
                self.fields['municipio'].queryset = Municipio.objects.filter(departamento=id_departamento)
            except:
                self.fields['municipio'].queryset = Municipio.objects.none()
        elif self.instance.pk:
            departamento = self.instance.municipio.departamento
            self.fields['departamento'].initial = departamento
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=departamento)

        if confirmar:
            self.fields['pruebas'].required = True
            self.fields['area'].required = True

        if self.instance.pk:
            area = self.instance.areas.first()
            self.fields['area'].initial = area

            if area is None:
                if self.data:
                    try:
                        id_area = int(self.data.get('clinica-area'))
                        self.fields['pruebas'].queryset = Prueba.objects.filter(area=id_area)

                    except:
                        self.fields['pruebas'].queryset = Prueba.objects.none()
                else:
                    self.fields['pruebas'].queryset = Prueba.objects.none()
            else:
                self.fields['pruebas'].queryset = area.pruebas.all()

            self.fields['pruebas'].initial = self.instance.pruebas
        else:
            if confirmar is None:
                self.fields['pruebas'].queryset = Prueba.objects.none()
            else:
                try:
                    id_area = int(self.data.get('clinica-area'))
                    self.fields['pruebas'].queryset = Prueba.objects.filter(area=id_area)
                except:
                    self.fields['pruebas'].queryset = Prueba.objects.none()


class InformacionAguaForm(common_f.RequireOnConfirmValidatableMixin, forms.ModelForm):
    """Formulario para el manejo de la información general que tienen las muestras de agua."""

    REQUIRED_ON_CONFIRM = [
        'municipio',
        'solicitante',
        'departamento',
        'responsable_toma',
        'fecha_recoleccion',
    ]

    nuevo_tipo_agua = forms.CharField(max_length=50, required=False)
    nueva_temperatura = forms.CharField(max_length=100, required=False)
    municipio = forms.ModelChoiceField(queryset=m.Municipio.objects.none())
    departamento = forms.ModelChoiceField(queryset=m.Departamento.objects.all())
    clase_tipo_agua = forms.ModelChoiceField(queryset=m.CategoriaAgua.objects.all(), required=False)

    class Meta:
        model = m.InformacionAgua
        fields = [
            'poblado',
            'municipio',
            'tipo_agua',
            'temperatura',
            'solicitante',
            'departamento',
            'clase_tipo_agua',
            'nuevo_tipo_agua',
            'responsable_toma',
            'fecha_recoleccion',
            'nueva_temperatura',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confirming = 'confirmado' in self.data
        self.fields['tipo_agua'].empty_label = 'Nuevo tipo de agua'
        self.fields['temperatura'].empty_label = 'Nueva temperatura'
        self.fields['solicitante'].queryset = m.Solicitante.objects.activos()
        self.fields['poblado'].queryset = m.Poblado.objects.none()

        if self.is_bound:
            with suppress(Exception):
                id_ = int(self.data.get('general-departamento'))
                self.fields['municipio'].queryset = m.Municipio.objects.filter(departamento=id_)
            
            with suppress(Exception):
                id_ = int(self.data.get('general-municipio'))
                self.fields['poblado'].queryset = m.Poblado.objects.filter(municipio=id_)
        elif self.instance.id and self.instance.poblado_id:
            municipio = self.instance.poblado.municipio
            departamento = self.instance.poblado.municipio.departamento

            self.fields['municipio'].queryset = m.Municipio.objects.filter(departamento=departamento)
            self.fields['poblado'].queryset = m.Poblado.objects.filter(municipio=self.instance.poblado.municipio)

            self.fields['municipio'].initial = municipio
            self.fields['departamento'].initial = departamento
    
    def clean(self):
        cleaned_data = super().clean()
        if not self.cleaned_data.get('tipo_agua') and self.confirming:
            if not self.cleaned_data.get('nuevo_tipo_agua'):
                self.add_error('nuevo_tipo_agua', 'Campo requerido')
            
            if not self.cleaned_data.get('clase_tipo_agua'):
                self.add_error('clase_tipo_agua', 'Campo requerido')
        
        if not self.cleaned_data.get('temperatura') and self.confirming:
            if not self.cleaned_data.get('nueva_temperatura'):
                self.add_error('nueva_temperatura', 'Campo requerido')

        return cleaned_data

    def save(self, user, commit=True):
        if self.cleaned_data['tipo_agua'] is None:
            if self.cleaned_data['clase_tipo_agua'] and self.cleaned_data['nuevo_tipo_agua']:
                nuevo_tipo = m.TipoAgua.objects.create(
                    categoria=self.cleaned_data['clase_tipo_agua'],
                    nombre=self.cleaned_data['nuevo_tipo_agua'],
                    modificado_por=user,
                )
                self.instance.tipo_agua = nuevo_tipo

        if self.cleaned_data['temperatura'] is None and self.cleaned_data['nueva_temperatura']:
            nueva_temperatura = m.Temperatura.objects.create(
                valor=self.cleaned_data['nueva_temperatura'],
                modificado_por=user,
            )
            self.instance.temperatura = nueva_temperatura

        return super().save(commit)

class MuestraAguaFormSet(forms.BaseModelFormSet):

    def save(self, user, ingreso, info, ingreso_nuevo=False):
        for form in self:
            form.user = user
            form.info = info
            form.ingreso = ingreso

        muestras = super().save()

        if not muestras and ingreso_nuevo:
            muestras.append(m.Agua.objects.create(registro_recepcion=ingreso, informacion_general=info))

        return muestras

class MuestraAguaForm(common_f.RequireOnConfirmValidatableMixin, forms.ModelForm):
    """Formulario para el manejo de las muestras de agua."""

    REQUIRED_ON_CONFIRM = [
        'areas',
        'hora_toma',
        'codigo_punto',
        'temp_ingreso',
    ]

    error_css_class = 'has-error'

    nuevo_motivo_analisis = forms.CharField(max_length=100, required=False)
    areas = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=m.Area.objects.filter(programa=m.Programa.objects.aguas()),
    )
    
    class Meta:
        model = m.Agua
        fields = [
            'areas',
            'hora_toma',
            'concertado',
            'temp_ingreso',
            'codigo_punto',
            'motivo_analisis',
            'nuevo_motivo_analisis',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confirming = 'confirmado' in self.data
        self.fields['hora_toma'].widget.attrs.update({'class': 'form-control input-hora-toma'})
        self.fields['codigo_punto'].widget.attrs.update({'class': 'form-control select-codigo-punto'})
        self.fields['concertado'].widget.attrs.update({'class': 'form-control select-concertado'})
        self.fields['motivo_analisis'].widget.attrs.update({'class': 'form-control select-motivo-analisis'})
        self.fields['nuevo_motivo_analisis'].widget.attrs.update({'class': 'form-control nuevo_motivo'})
        self.fields['codigo_punto'].queryset = m.CodigoPunto.objects.none()
        self.fields['motivo_analisis'].empty_label = 'Nuevo motivo de analisis'
        
        if self.is_bound:
            with suppress(Exception):
                id_ = int(self.data.get('general-poblado'))
                self.fields['codigo_punto'].queryset = m.CodigoPunto.objects.filter(poblado=id_).activos()
        elif self.instance.pk:
            self.fields['areas'].initial = [area.pk for area in self.instance.areas]
            poblado = self.instance.informacion_general.poblado
            self.fields['codigo_punto'].queryset = m.CodigoPunto.objects.filter(poblado=poblado).activos()

    def clean(self):
        cleaned_data = super().clean()
        motivo_analisis = cleaned_data['motivo_analisis']
        nuevo_motivo = cleaned_data['nuevo_motivo_analisis']

        if not motivo_analisis and not nuevo_motivo and self.confirming:
            self.add_error('nuevo_motivo_analisis', 'Este campo es obligatorio.')
        
        return cleaned_data

    def save(self, commit=True):
        if self.cleaned_data['motivo_analisis'] is None and self.cleaned_data['nuevo_motivo_analisis']:
            nueva_motivo = m.MotivoAnalisis.objects.create(
                nombre=self.cleaned_data['nuevo_motivo_analisis']
            )
            self.instance.motivo_analisis = nueva_motivo
        
        self.instance.informacion_general = self.info
        self.instance.registro_recepcion = self.ingreso        
        muestra = super().save(commit)
        
        muestra.pruebas.clear()
        for area in self.cleaned_data['areas']:
            for prueba in area.pruebas.activos():
                m.PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)
        
        return muestra


class ResponsableRecoleccionForm(forms.ModelForm):
    """Formulario para el manejo de los responsables de recolección de las muestras de entomologia."""

    error_css_class = 'has-error'

    responsable_recoleccion = forms.ModelChoiceField(queryset=ResponsableRecoleccion.objects.all(),
                                                     empty_label='Nuevo responsable de recolección', required=False)

    def __init__(self, *args, **kwargs):
        super(ResponsableRecoleccionForm, self).__init__(*args, **kwargs)

        self.fields['responsable_recoleccion'].widget.attrs.update({'class': 'form-control'})
        self.fields['nombres'].widget.attrs.update({'class': 'form-control'})
        self.fields['apellidos'].widget.attrs.update({'class': 'form-control'})

        self.fields['nombres'].required = False
        self.fields['apellidos'].required = False

        if self.instance.pk:
            self.fields['responsable_recoleccion'].initial = self.instance

    def clean(self):
        cleaned_data = super(ResponsableRecoleccionForm, self).clean()
        responsable_recoleccion = cleaned_data['responsable_recoleccion']

        if not responsable_recoleccion:
            nombres = cleaned_data.get('nombres', None)
            apellidos = cleaned_data.get('apellidos', None)

            if not nombres:
                self.add_error('nombres', 'Este campo es obligatorio.')

            if not apellidos:
                self.add_error('apellidos', 'Este campo es obligatorio.')

    def save(self, commit=True):
        if self.cleaned_data['responsable_recoleccion'] is None:
            self.instance.pk = None
            return super(ResponsableRecoleccionForm, self).save(commit)
        else:
            return self.cleaned_data['responsable_recoleccion']

    class Meta:
        model = ResponsableRecoleccion
        fields = ['responsable_recoleccion', 'nombres', 'apellidos']


class LugarRecoleccionForm(forms.ModelForm):
    """Formulario para el manejo de los lugares de recolección de las muestras de entomologia."""

    error_css_class = 'has-error'

    lugar_recoleccion = forms.ModelChoiceField(
        required=False,
        empty_label='Nuevo lugar de recolección',
        queryset=LugarRecoleccion.objects.select_related('municipio__departamento').all(),
    )
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super(LugarRecoleccionForm, self).__init__(*args, **kwargs)

        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['municipio'].widget.attrs.update({'class': 'form-control'})
        self.fields['departamento'].widget.attrs.update({'class': 'form-control'})
        self.fields['lugar_recoleccion'].widget.attrs.update({'class': 'form-control'})

        self.fields['nombre'].required = False
        self.fields['municipio'].required = False

        if self.instance.pk:
            self.fields['lugar_recoleccion'].initial = self.instance

        try:
            id_departamento = int(self.data.get('lugar-departamento'))
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=id_departamento)
        except:
            self.fields['municipio'].queryset = Municipio.objects.none()

    def clean(self):
        cleaned_data = super(LugarRecoleccionForm, self).clean()
        lugar = cleaned_data['lugar_recoleccion']

        if not lugar:
            nombre = cleaned_data.get('nombre', None)
            municipio = cleaned_data.get('municipio', None)
            departamento = cleaned_data.get('departamento', None)

            if not nombre:
                self.add_error('nombre', 'Este campo es obligatorio.')

            if not municipio:
                self.add_error('municipio', 'Este campo es obligatorio.')

            if not departamento:
                self.add_error('departamento', 'Este campo es obligatorio.')

    def save(self, commit=True):
        if self.cleaned_data['lugar_recoleccion'] is None:
            self.instance.pk = None
            return super(LugarRecoleccionForm, self).save(commit)
        else:
            return self.cleaned_data['lugar_recoleccion']

    class Meta:
        model = LugarRecoleccion
        fields = ['lugar_recoleccion', 'departamento', 'municipio', 'nombre']


class MuestraEntomologiaForm(forms.ModelForm):
    """Formulario para el manejo de las muestras de entomologia."""

    error_css_class = 'has-error'

    def __init__(self, *args, **kwargs):
        confirmar = kwargs.pop('confirmar', None)
        super(MuestraEntomologiaForm, self).__init__(*args, **kwargs)

        entomologia = Programa.objects.entomologia()
        areas = Area.objects.filter(programa=entomologia)
        queryset = TipoMuestra.objects.filter(programas=entomologia).activos()
        self.fields['tipo_muestra'].queryset = queryset
        self.fields['tipo_vigilancia'].queryset = TipoVigilancia.objects.activos()
        self.fields['pruebas'].queryset = Prueba.objects.filter(area__in=areas).activos()
        self.fields['temp_ingreso'].required = True

        if confirmar:
            self.fields['pruebas'].required = True

    class Meta:
        model = Entomologia
        fields = ['tipo_vigilancia', 'estado_desarrollo', 'tipo_muestra', 'pruebas', 'temp_ingreso']
        widgets = {
            'pruebas': forms.CheckboxSelectMultiple()
        }


class InstitucionCitohistopatologiaForm(forms.ModelForm):
    """Formulario para el manejo de los lugares de recolección de las muestras de citohistopatologia."""

    error_css_class = 'has-error'

    institucion = forms.ModelChoiceField(queryset=InstitucionCitohistopatologia.objects.all(),
                                         empty_label='Nueva institucion', required=False)
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())

    def __init__(self, *args, **kwargs):
        super(InstitucionCitohistopatologiaForm, self).__init__(*args, **kwargs)
        self.fields['institucion'].widget.attrs.update({'class': 'form-control'})
        self.fields['departamento'].widget.attrs.update({'class': 'form-control'})
        self.fields['municipio'].widget.attrs.update({'class': 'form-control'})
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['codigo'].widget.attrs.update({'class': 'form-control'})

        self.fields['nombre'].required = False
        self.fields['codigo'].required = False
        self.fields['municipio'].required = False
        self.fields['departamento'].required = False

        if self.instance.pk:
            self.fields['institucion'].initial = self.instance

        try:
            id_departamento = int(self.data.get('institucion-departamento'))
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=id_departamento)
        except:
            self.fields['municipio'].queryset = Municipio.objects.none()

    def clean(self):
        cleaned_data = super(InstitucionCitohistopatologiaForm, self).clean()
        institucion = cleaned_data['institucion']

        if not institucion:
            nombre = cleaned_data.get('nombre', None)
            municipio = cleaned_data.get('municipio', None)
            departamento = cleaned_data.get('departamento', None)
            codigo = cleaned_data.get('codigo', None)

            if not nombre:
                self.add_error('nombre', 'Este campo es obligatorio.')

            if not municipio:
                self.add_error('municipio', 'Este campo es obligatorio.')

            if not departamento:
                self.add_error('departamento', 'Este campo es obligatorio.')

            if not codigo:
                self.add_error('codigo', 'Este campo es obligatorio.')

    def save(self, commit=True):
        if self.cleaned_data['institucion'] is None:
            self.instance.pk = None
            return super(InstitucionCitohistopatologiaForm, self).save(commit)
        else:
            return self.cleaned_data['institucion']

    class Meta:
        model = InstitucionCitohistopatologia
        fields = ['institucion', 'departamento', 'municipio', 'nombre', 'codigo']


class MuestraCitohistopatologiaForm(forms.ModelForm):
    """Formulario para el manejo de las muestras de citohistopatologia."""

    error_css_class = 'has-error'

    def __init__(self, *args, **kwargs):
        confirmar = kwargs.pop('confirmar', None)
        super(MuestraCitohistopatologiaForm, self).__init__(*args, **kwargs)
        citohistopatologia = Programa.objects.citohistopatologia()
        areas = Area.objects.filter(programa=citohistopatologia)
        self.fields['control'].queryset = Control.objects.activos()
        self.fields['tipo_evento'].queryset = TipoEvento.objects.activos()
        self.fields['pruebas'].queryset = Prueba.objects.filter(area__in=areas).activos()
        queryset = TipoMuestra.objects.filter(programas=citohistopatologia).activos()
        self.fields['tipo_muestra'].queryset = queryset
        self.fields['temp_ingreso'].required = True

        if confirmar:
            self.fields['pruebas'].required = True

    class Meta:
        model = Citohistopatologia
        fields = ['control', 'tipo_evento', 'tipo_muestra', 'pruebas', 'temp_ingreso']
        widgets = {
            'pruebas': forms.CheckboxSelectMultiple()
        }


class InstitucionBancoSangreForm(forms.ModelForm):
    """Formulario para el manejo de los lugares de recolección de las muestras de banco de sangre."""

    error_css_class = 'has-error'

    institucion = forms.ModelChoiceField(queryset=InstitucionBancoSangre.objects.all(),
                                         empty_label='Nueva institución', required=False)
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())

    def __init__(self, *args, **kwargs):
        super(InstitucionBancoSangreForm, self).__init__(*args, **kwargs)
        self.fields['institucion'].widget.attrs.update({'class': 'form-control'})
        self.fields['departamento'].widget.attrs.update({'class': 'form-control'})
        self.fields['municipio'].widget.attrs.update({'class': 'form-control'})
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})

        self.fields['nombre'].required = False
        self.fields['municipio'].required = False
        self.fields['departamento'].required = False

        if self.instance.pk:
            self.fields['institucion'].initial = self.instance

        try:
            id_departamento = int(self.data.get('institucion-departamento'))
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=id_departamento)
        except:
            self.fields['municipio'].queryset = Municipio.objects.none()

    def clean(self):
        cleaned_data = super(InstitucionBancoSangreForm, self).clean()
        institucion = cleaned_data['institucion']

        if not institucion:
            nombre = cleaned_data.get('nombre', None)
            municipio = cleaned_data.get('municipio', None)
            departamento = cleaned_data.get('departamento', None)

            if not nombre:
                self.add_error('nombre', 'Este campo es obligatorio.')

            if not municipio:
                self.add_error('municipio', 'Este campo es obligatorio.')

            if not departamento:
                self.add_error('departamento', 'Este campo es obligatorio.')

    def save(self, commit=True):
        if self.cleaned_data['institucion'] is None:
            self.instance.pk = None
            return super(InstitucionBancoSangreForm, self).save(commit)
        else:
            return self.cleaned_data['institucion']

    class Meta:
        model = InstitucionBancoSangre
        fields = ['institucion', 'departamento', 'municipio', 'nombre']


class MuestraBancoSangreForm(forms.ModelForm):
    """Formulario para el manejo de las muestras de banco de sangre."""

    error_css_class = 'has-error'

    class Meta:
        model = BancoSangre
        fields = [
            'pruebas',
            'tipo_envase',
            'tipo_muestra',
            'temp_ingreso',
            'ficha_pacientes',
            'condensado_banco',
            'formatos_diligenciados',
        ]
        widgets = {
            'pruebas': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        confirmar = kwargs.pop('confirmar', None)
        super(MuestraBancoSangreForm, self).__init__(*args, **kwargs)
        self.fields['tipo_envase'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_muestra'].widget.attrs.update({'class': 'form-control'})
        self.fields['ficha_pacientes'].widget.attrs.update({'class': 'form-control'})
        self.fields['condensado_banco'].widget.attrs.update({'class': 'form-control'})
        self.fields['formatos_diligenciados'].widget.attrs.update({'class': 'form-control'})

        self.fields['temp_ingreso'].required = True
        self.fields['ficha_pacientes'].required = True
        self.fields['condensado_banco'].required = True
        self.fields['formatos_diligenciados'].required = True

        banco_sangre = Programa.objects.banco_sangre()
        areas = Area.objects.filter(programa=banco_sangre)
        self.fields['tipo_envase'].queryset = TipoEnvase.objects.activos()
        self.fields['pruebas'].queryset = Prueba.objects.filter(area__in=areas).activos()
        queryset = TipoMuestra.objects.filter(programas=banco_sangre).activos()
        self.fields['tipo_muestra'].queryset = queryset

        if confirmar:
            self.fields['pruebas'].required = True


class InstitucionEEDDForm(forms.ModelForm):
    """Formulario para el manejo del origen de la muestras de evaluación externa desempeño directo."""

    error_css_class = 'has-error'

    institucion = forms.ModelChoiceField(queryset=InstitucionEEDD.objects.all(),
                                         empty_label='Nueva institución', required=False)
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())

    def __init__(self, *args, **kwargs):
        super(InstitucionEEDDForm, self).__init__(*args, **kwargs)
        self.fields['institucion'].widget.attrs.update({'class': 'form-control'})
        self.fields['departamento'].widget.attrs.update({'class': 'form-control'})
        self.fields['municipio'].widget.attrs.update({'class': 'form-control'})
        self.fields['direccion'].widget.attrs.update({'class': 'form-control'})
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['nit'].widget.attrs.update({'class': 'form-control'})

        self.fields['nit'].required = False
        self.fields['nombre'].required = False
        self.fields['municipio'].required = False
        self.fields['direccion'].required = False
        self.fields['departamento'].required = False

        if self.instance.pk:
            self.fields['institucion'].initial = self.instance

        try:
            id_departamento = int(self.data.get('institucion-departamento'))
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=id_departamento)
        except:
            self.fields['municipio'].queryset = Municipio.objects.none()

    def clean(self):
        cleaned_data = super(InstitucionEEDDForm, self).clean()
        institucion = cleaned_data['institucion']

        if not institucion:
            nit = cleaned_data.get('nit', None)
            nombre = cleaned_data.get('nombre', None)
            direccion = cleaned_data.get('direccion', None)
            municipio = cleaned_data.get('municipio', None)
            departamento = cleaned_data.get('departamento', None)

            if not nit:
                self.add_error('nit', 'Este campo es obligatorio.')

            if not nombre:
                self.add_error('nombre', 'Este campo es obligatorio.')

            if not direccion:
                self.add_error('direccion', 'Este campo es obligatorio.')

            if not municipio:
                self.add_error('municipio', 'Este campo es obligatorio.')

            if not departamento:
                self.add_error('departamento', 'Este campo es obligatorio.')

    def save(self, commit=True):
        if self.cleaned_data['institucion'] is None:
            self.instance.pk = None
            return super(InstitucionEEDDForm, self).save(commit)
        else:
            return self.cleaned_data['institucion']

    class Meta:
        model = InstitucionEEDD
        fields = ['institucion', 'nombre', 'departamento', 'municipio', 'direccion', 'nit']


class MuestraEEDDForm(forms.ModelForm):
    """Formulario para el manejo de las muestras de evaluación externa de desempeño directo."""

    error_css_class = 'has-error'

    class Meta:
        model = EEDD
        fields = ['control', 'tipo_evento', 'tipo_muestra', 'pruebas', 'temp_ingreso']
        widgets = {
            'pruebas': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        confirmar = kwargs.pop('confirmar', None)
        super(MuestraEEDDForm, self).__init__(*args, **kwargs)
        self.fields['temp_ingreso'].required = True

        eedd = Programa.objects.eedd()
        areas = Area.objects.filter(programa=eedd)
        self.fields['control'].queryset = Control.objects.activos()
        self.fields['tipo_evento'].queryset = TipoEventoEvaluacionExterna.objects.activos()
        self.fields['pruebas'].queryset = Prueba.objects.filter(area__in=areas).activos()
        self.fields['tipo_muestra'].queryset = TipoMuestra.objects.filter(programas=eedd).activos()

        if confirmar:
            self.fields['pruebas'].required = True


class InstitucionEEIDForm(forms.ModelForm):
    """Formulario para el manejo del origen de la muestras de evaluación externa desempeño indirecto."""

    error_css_class = 'has-error'

    institucion = forms.ModelChoiceField(queryset=InstitucionEEID.objects.all(),
                                         empty_label='Nueva institución', required=False)
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())

    def __init__(self, *args, **kwargs):
        super(InstitucionEEIDForm, self).__init__(*args, **kwargs)
        self.fields['institucion'].widget.attrs.update({'class': 'form-control'})
        self.fields['departamento'].widget.attrs.update({'class': 'form-control'})
        self.fields['municipio'].widget.attrs.update({'class': 'form-control'})
        # self.fields['direccion'].widget.attrs.update({'class': 'form-control'})
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['codigo'].widget.attrs.update({'class': 'form-control'})
        # self.fields['nit'].widget.attrs.update({'class': 'form-control'})

        # self.fields['nit'].required = False
        self.fields['nombre'].required = False
        self.fields['codigo'].required = False
        # self.fields['direccion'].required = False
        self.fields['municipio'].required = False
        self.fields['departamento'].required = False

        if self.instance.pk:
            self.fields['institucion'].initial = self.instance

        try:
            id_departamento = int(self.data.get('institucion-departamento'))
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=id_departamento)
        except:
            self.fields['municipio'].queryset = Municipio.objects.none()

    def clean(self):
        cleaned_data = super(InstitucionEEIDForm, self).clean()
        institucion = cleaned_data['institucion']

        if not institucion:
            # nit = cleaned_data.get('nit', None)
            nombre = cleaned_data.get('nombre', None)
            codigo = cleaned_data.get('codigo', None)
            # direccion = cleaned_data.get('direccion', None)
            municipio = cleaned_data.get('municipio', None)
            departamento = cleaned_data.get('departamento', None)

            # if not nit:
            #     self.add_error('nit', 'Este campo es obligatorio.')

            if not nombre:
                self.add_error('nombre', 'Este campo es obligatorio.')

            if not codigo:
                self.add_error('codigo', 'Este campo es obligatorio.')

            # if not direccion:
            #     self.add_error('direccion', 'Este campo es obligatorio.')

            if not municipio:
                self.add_error('municipio', 'Este campo es obligatorio.')

            if not departamento:
                self.add_error('departamento', 'Este campo es obligatorio.')

    def save(self, commit=True):
        if self.cleaned_data['institucion'] is None:
            self.instance.pk = None
            return super(InstitucionEEIDForm, self).save(commit)
        else:
            return self.cleaned_data['institucion']

    class Meta:
        model = InstitucionEEID
        fields = ['institucion', 'nombre', 'codigo', 'departamento', 'municipio']  # , 'direccion', 'nit']


class MuestraEEIDForm(forms.ModelForm):
    """Formulario para el manejo de las muestras de evaluación externa de desempeño indirecto."""

    error_css_class = 'has-error'

    sin_identificacion = forms.BooleanField(required=False)

    class Meta:
        model = EEID
        fields = [
            'programado', 'control',
            'programa', 'tipo_evento',
            'tipo_muestra', 'pruebas',
            'nombre', 'identificacion',
            'tipo_identificacion', 'edad',
            'tipo_edad', 'sin_identificacion', 'temp_ingreso'
        ]
        widgets = {
            'pruebas': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        confirmar = kwargs.pop('confirmar', None)
        super(MuestraEEIDForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['identificacion'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_identificacion'].widget.attrs.update({'class': 'form-control'})
        self.fields['edad'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_edad'].widget.attrs.update({'class': 'form-control'})

        eeid = Programa.objects.eeid()
        areas = Area.objects.filter(programa=eeid)
        self.fields['control'].queryset = Control.objects.activos()
        self.fields['programa'].queryset = ProgramaEvaluacionExterna.objects.activos()
        self.fields['tipo_evento'].queryset = TipoEventoEvaluacionExterna.objects.activos()
        self.fields['pruebas'].queryset = Prueba.objects.filter(area__in=areas).activos()
        queryset = TipoMuestra.objects.filter(programas=eeid).activos()
        self.fields['tipo_muestra'].queryset = queryset
        self.fields['nombre'].required = False
        self.fields['temp_ingreso'].required = True

        if confirmar:
            self.fields['pruebas'].required = True

    def clean(self):
        cleaned_data = super(MuestraEEIDForm, self).clean()
        if cleaned_data['nombre'] is None or cleaned_data['nombre'] == '':
            if cleaned_data['sin_identificacion']:
                cleaned_data['nombre'] = 'NN'
            else:
                self.add_error('nombre', 'Este campo es obligatorio.')

# Formularios para reportes


class RangoFechasForm(forms.Form):
    """Formulario para consultas con un rango de fechas."""

    fecha_inicial = forms.DateField(required=True)
    fecha_final = forms.DateField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicial = cleaned_data.get('fecha_inicial')
        fecha_final = cleaned_data.get('fecha_final')

        if fecha_inicial and fecha_final:
            if fecha_inicial > fecha_final:
                self.add_error('fecha_final', 'La fecha final no puede ser menor a la fecha inicial')

        return cleaned_data

class ProductividadRecepcionForm(RangoFechasForm):
    
    def report_data(self):
        fi = self.cleaned_data['fecha_inicial']
        ff = self.cleaned_data['fecha_final']

        ingresos = (
            m.Ingreso.objects
                .confirmados()
                .by_fecha_recepcion(fi, ff)
                .select_related('confirmado_por', 'recepcionista')
        )

        list_ = []
        acumulado = 0
        grafico = [['Resultado', 'Frecuencia']]
        total = ingresos.count()
        grouped = itertools.groupby(ingresos, lambda i: i.digitado_por.id)
        for key, group in grouped:
            data = list(group)
            first = data[0]
            frecuencia = len(data)
            porcentaje = frecuencia / total * 100
            acumulado += porcentaje
            list_.append({
                'detalle': data,
                'acumulado': acumulado,
                'frecuencia': frecuencia,
                'porcentaje': porcentaje,
                'resultado': first.digitado_por.username,
            })
            grafico.append([first.digitado_por.username, frecuencia])
        
        return list_, total, grafico

class BuscadorForm(RangoFechasForm):
    """Formulario para realizar una busqueda de ingresos segun un rango de fechas, radicado o información del
    paciente."""

    # opciones
    RADICADO = 'R'
    PACIENTE = 'P'
    TIPOS = (
        (RADICADO, 'Radicado'),
        (PACIENTE, 'Paciente')
    )

    tipo = forms.ChoiceField(choices=TIPOS, required=False, label='Tipo de busqueda')
    busqueda = forms.CharField(required=False, label='Número de radicado (no incluir el año)',
                               help_text='Si escoge fechas este criterio es ignorado')

    def __init__(self, *args, **kwargs):
        super(BuscadorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = 'trazabilidad:buscar_radicado'
        self.helper.layout = Layout(
            Div(
                Div('fecha_inicial', css_class='col-md-2'),
                Div('fecha_final', css_class='col-md-2'),
                Div('tipo', css_class='col-md-2'),
                Div('busqueda', css_class='col-md-4'),
                Div(
                    StrictButton(
                        '<i class="glyphicon glyphicon-search"></i>  Buscar',
                        css_class='btn-primary btn-block',
                        type='submit'
                    ),
                    css_class='col-md-2'
                ),
                css_class='row'
            )
        )

        self.fields['fecha_inicial'].required = False
        self.fields['fecha_final'].required = False

    def clean(self):
        cleaned_data = super(BuscadorForm, self).clean()
        fecha_inicial = cleaned_data.get('fecha_inicial')
        fecha_final = cleaned_data.get('fecha_final')
        busqueda = cleaned_data.get('busqueda')

        if not busqueda and (not fecha_inicial or not fecha_final):
            raise forms.ValidationError(
                "Debe seleccionar algun criterio de busqueda: Rango de fechas o Numero de Radicado"
            )

    def resultados_busqueda(usuario):
        pass


class InformeForm(forms.ModelForm):
    """Formulario para el manejo de pacientes."""

    analista = forms.ModelChoiceField(queryset=admin_models.Empleado.objects.none())
    responsable_tecnico = forms.ModelChoiceField(queryset=admin_models.Empleado.objects.none())

    class Meta:
        model = m.Reporte
        fields = ['objeto']

    def __init__(self, ingreso, user, *args, **kwargs): 
        super().__init__(instance=ingreso.informe, *args, **kwargs)
        self.user = user
        areas = ingreso.areas
        self.ingreso = ingreso
        self.fields['objeto'].label = 'Propósito Géneral de la Prueba'
        self.fields['analista'].queryset = (
            admin_models.Empleado.objects
                .select_related('usuario')
                .by_areas(areas)
        )
        self.fields['responsable_tecnico'].queryset = (
            admin_models.Empleado.objects
                .select_related('usuario')
                .is_responsable_tecnico()
                .by_areas(areas)
        )

        self.no_debe_ingresar_analista = not user.has_perm('administracion.can_analizar_todos_programas')
        if self.no_debe_ingresar_analista:
            self.fields['analista'].initial = user.empleado
            self.fields['analista'].widget.attrs.update({'disabled': True})
        
        self.confirmando = 'confirmado' in self.data
        if self.instance.pk:
            self.fields['analista'].initial = ingreso.analista.empleado
            self.fields['responsable_tecnico'].initial = ingreso.responsable_tecnico.empleado
    
    def clean(self):
        if self.ingreso.cumplimiento < 100:
            self.add_error('', 'El ingreso no tiene el 100% de cumplimiento, por lo tanto no se puede crear el informe')
        return super().clean()

    def save(self, commit=True):
        now = timezone.now()
        self.instance.registro_recepcion = self.ingreso

        if self.confirmando:
            self.instance.confirmado = True
            self.instance.fecha = now

            if getattr(admin_models.ConfigGeneral.objects.first(), 'firma_automatica_reporte', False):
                self.instance.fecha_aprobacion = now
        
        analista = self.cleaned_data.get('analista', None)
        if self.no_debe_ingresar_analista:
            analista = self.user
        
        self.ingreso.responsable_tecnico = self.cleaned_data['responsable_tecnico'].usuario
        self.ingreso.analista = analista.usuario
        self.ingreso.save()

        return super().save(commit)

class MuestraForm(forms.ModelForm):
    """Formulario para agregar observaciones a una muestra, se usa en el informe."""

    irca = forms.FloatField(label='IRCA', required=False)

    class Meta:
        model = Muestra
        fields = ['irca', 'temp_procesamiento', 'observacion']

    def __init__(self, *args, **kwargs):
        super(MuestraForm, self).__init__(*args, **kwargs)
        self.fields['observacion'].widget.attrs.update({'rows': '4'})
        self.fields['temp_procesamiento'].required = True
        self.fields['observacion'].required = False
        self.helper = FormHelper()
        self.helper.form_tag = False

        if self.instance.pk:
            try:
                self.fields['irca'].initial = '{:.2f}'.format(self.instance.agua.calcular_irca()) if not self.instance.agua.irca else self.instance.agua.irca
                self.fields['irca'].required = True
            except:
                self.fields['irca'].widget = forms.HiddenInput()
        else:
            self.fields['irca'].widget = forms.HiddenInput()

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        irca = cleaned_data.get('irca', None)

        if irca is not None:
            if not NivelRiesgo.objects.filter(inicio__lte=irca, fin__gte=irca).exists():
                self.add_error('irca', 'No hay un nivel de riesgo definido para el porcentaje de IRCA que se há calculado.')

    def save(self, *args, **kwargs):
        if self.cleaned_data.get('irca', None) is not None:
            try:
                agua = self.instance.agua
                agua.irca = self.cleaned_data['irca']
                agua.save()
            except:
                pass
        super().save(*args, **kwargs)

class PruebasRealizadasForm(forms.ModelForm):
    """Formulario para el manejo de las muestras de agua."""

    error_css_class = 'has-error'

    def __init__(self, confirmar=None, *args, **kwargs):
        super(PruebasRealizadasForm, self).__init__(*args, **kwargs)
        self.fields['resultados'].widget.attrs.update({'class': 'form-control'})
        self.fields['metodo'].widget.attrs.update({'class': 'form-control'})
        self.fields['resultados'].queryset = self.instance.prueba.resultados.all()

    class Meta:
        model = PruebasRealizadas
        fields = ['resultados', 'metodo']


class fechaRangoForm(forms.Form):
    error_css_class = 'has-error'
    fechai = forms.DateField(label='Fecha Inicial', required=True)
    fechaf = forms.DateField(label='Fecha Final', required=True)

    def __init__(self, *args, **kwargs):
        super(fechaRangoForm, self).__init__(*args, **kwargs)
        self.fields['fechai'].widget.attrs.update({'class': 'form-control hidden-print', 'placeholder': 'aaaa-mm-dd'})
        self.fields['fechaf'].widget.attrs.update({'class': 'form-control hidden-print', 'placeholder': 'aaaa-mm-dd'})

        self.error_messages = {
            'Fecha Inicial': 'Hace falta ingresar una fecha inicial',
            'Fecha Final': 'Hace falta ingresar una fecha final',
        }


class ProgramaForm(forms.Form):
    error_css_class = 'has-error'
    programa = forms.ModelChoiceField(queryset=Programa.objects.all(), required=True)
    prueba = forms.ModelChoiceField(queryset=Prueba.objects.none(), required=True)

    def __init__(self, *args, **kwargs):
        super(ProgramaForm, self).__init__(*args, **kwargs)
        self.fields['programa'].widget.attrs.update({'class': 'form-control hidden-print'})
        self.fields['prueba'].widget.attrs.update({'class': 'form-control hidden-print'})

        try:
            id_programa = int(self.data.get('programa'))
            self.fields['prueba'].queryset = Prueba.objects.filter(area__programa=id_programa)
        except:
            self.fields['prueba'].queryset = Prueba.objects.none()


class UsuarioForm(forms.Form):
    error_css_class = 'has-error'
    usuario = forms.ModelChoiceField(queryset=User.objects.all())

    def __init__(self, *args, **kwargs):
        super(UsuarioForm, self).__init__(*args, **kwargs)
        self.fields['usuario'].widget.attrs.update({'class': 'form-control'})


class MulticonsultaForm(forms.Form):
    SEXO = (('A', 'Ambos'), ('M', 'Masculino'), ('F', 'Femenino'))
    SI = True
    NO = False

    EMBARAZADA = (
        (NO, 'NO'),
        (SI, 'SI')
    )
    error_css_class = 'has-error'
    fechai = forms.DateField(label='Fecha Inicial', required=True)
    fechaf = forms.DateField(label='Fecha Final', required=True)
    prueba = forms.ModelChoiceField(queryset=Prueba.objects.filter(area__programa=Programa.objects.clinico()))
    municipio = forms.ModelMultipleChoiceField(
        queryset=Municipio.objects.all(), widget=forms.SelectMultiple, required=True)
    resultado = forms.ModelChoiceField(queryset=ResultadoPrueba.objects.all())
    embarazada = forms.ChoiceField(choices=EMBARAZADA, required=False)
    sexo = forms.ChoiceField(choices=SEXO, required=False)
    edad1 = forms.IntegerField(required=False)
    edad2 = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super(MulticonsultaForm, self).__init__(*args, **kwargs)
        self.fields['fechai'].widget.attrs.update({'class': 'form-control hidden-print', 'placeholder': 'aaaa-mm-dd'})
        self.fields['fechaf'].widget.attrs.update({'class': 'form-control hidden-print', 'placeholder': 'aaaa-mm-dd'})

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('prueba', css_class='col-md-3'),
                Div('municipio', css_class='col-md-3'),
                Div('resultado', css_class='col-md-3'),
                Div('sexo', css_class='col-md-3'),
                css_class='row'
            ),
            Div(
                Div('embarazada', css_class='col-md-3 hidden', css_id="id_embarazada"),
                Div('fechai', css_class='col-md-3'),
                Div('fechaf', css_class='col-md-3'),
                Div('edad1', css_class='col-md-3'),
                Div('edad2', css_class='col-md-3'),
                css_class='row'
            ),

            FormActions(Submit('aceptar', 'Aceptar'))
        )


class MotivoRechazoForm(forms.Form):
    error_css_class = 'has-error'
    programa = forms.ModelChoiceField(queryset=Programa.objects.all(), required=True)
    prueba = forms.ModelChoiceField(queryset=Prueba.objects.none(), required=True)
    municipio = forms.ModelMultipleChoiceField(required=True, queryset=Municipio.objects.all())

    def __init__(self, *args, **kwargs):
        super(MotivoRechazoForm, self).__init__(*args, **kwargs)
        self.fields['programa'].widget.attrs.update({'class': 'form-control hidden-print'})
        self.fields['prueba'].widget.attrs.update({'class': 'form-control hidden-print'})
        self.fields['municipio'].widget.attrs.update({'class': 'form-control hidden-print'})
        # self.fields['solicitante'].widget.attrs.update({'class' : 'form-control hidden-print'})

        try:
            id_programa = int(self.data.get('programa'))
            self.fields['prueba'].queryset = Prueba.objects.filter(area__programa=id_programa)
        except:
            self.fields['prueba'].queryset = Prueba.objects.none()


class FormularioAgregarPruebas(forms.Form):
    """Formulario para agreagar las pruebas a una muestra especifica"""

    error_css_class = 'has-error'

    pruebas = forms.ModelMultipleChoiceField(queryset=Prueba.objects.none(), widget=forms.CheckboxSelectMultiple)
    muestra = forms.CharField(widget=forms.HiddenInput, max_length=255)

    def __init__(self, ingreso, *args, **kwargs):
        super(FormularioAgregarPruebas, self).__init__(*args, **kwargs)
        self.fields['pruebas'].queryset = Prueba.objects.filter(area__in=ingreso.areas)

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        muestra = cleaned_data.get('muestra', None)
        if muestra is not None:
            try:
                cleaned_data['muestra'] = Muestra.objects.get(id=muestra)
            except Muestra.DoesNotExist:
                self.add_error('muestra', 'Este campo es obligatorio')
        else:
            self.add_error('muestra', 'Este campo es obligatorio')

        return cleaned_data


class RegistroTemperaturaAreaForm(forms.ModelForm):
    """Formulario para el ingreso de la temperatura de las areas."""

    def __init__(self, *args, **kwargs):
        area = kwargs.pop('area')
        super(RegistroTemperaturaAreaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse_lazy('trazabilidad:registro_temperatura_area', args=(area.id, ))
        self.helper.layout = Layout(
            Div(
                Div(Field('fecha_registro', readonly=True), css_class='col-md-6'),
                css_class='row'
            ),
            Div(
                Div('temperatura', css_class='col-md-3'),
                Div('unidad', css_class='col-md-3'),
                Div('humedad', css_class='col-md-3'),
                css_class='row'
            ),
            Div(
                Div('observaciones', css_class='col-md-6'),
                css_class='row'
            ),
            FormActions(Submit('aceptar', 'Aceptar'))
        )

    class Meta:
        model = RegistroTemperaturaArea
        fields = ['fecha_registro', 'temperatura', 'humedad', 'unidad', 'observaciones']


class AreaTemperaturaForm(forms.Form):
    """Formulario que permite escoger un area para ver sus registro de temperatura"""

    area = forms.ModelChoiceField(queryset=Area.objects.all())
    temperatura_maxima = forms.CharField(max_length=100, required=False, label='Temperatura máxima (°C)')
    temperatura_minima = forms.CharField(max_length=100, required=False, label='Temperatura mínima (°C)')
    humedad_maxima = forms.CharField(max_length=100, required=False, label='Humedad máxima (°C)')
    humedad_minima = forms.CharField(max_length=100, required=False, label='Humedad mínima (°C)')
    fecha_inicial = forms.DateField()
    fecha_final = forms.DateField()
    unidad = forms.ChoiceField(choices=RegistroTemperaturaArea.UNIDADES)

    def __init__(self, *args, **kwargs):
        super(AreaTemperaturaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = 'trazabilidad:control_temperatura_area'
        self.helper.layout = Layout(
            Div(
                Div('area', css_class='col-md-3'),
                Div(Field('temperatura_minima', readonly=True), css_class='col-md-2'),
                Div(Field('temperatura_maxima', readonly=True), css_class='col-md-2'),
                Div(Field('humedad_minima', readonly=True), css_class='col-md-2'),
                Div(Field('humedad_maxima', readonly=True), css_class='col-md-2'),
                css_class='row'
            ),
            Div(
                Div('fecha_inicial', css_class='col-md-3'),
                Div('fecha_final', css_class='col-md-3'),
                Div('unidad', css_class='col-md-2'),
                css_class='row'
            ),
            FormActions(Submit('aceptar', 'Aceptar'))
        )
