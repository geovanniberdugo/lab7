from django.urls import reverse
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Field
from django import forms
from .models import RegistroTemperatura, Equipo
from trazabilidad.models import Area
from administracion.models import Empleado

__author__ = 'tania'


class EquiposAreaForm(forms.Form):
    """Formulario que permite escoger un equipo de un area."""

    areas = forms.ModelChoiceField(queryset=Area.objects.all())
    equipos = forms.ModelChoiceField(queryset=Equipo.objects.none())
    codigo = forms.CharField(max_length=100, required=False)
    temperatura_maxima = forms.CharField(max_length=100, required=False, label='Temperatura máxima (ºC)')
    temperatura_minima = forms.CharField(max_length=100, required=False, label='Temperatura mínima (ºC)')
    fecha_inicial = forms.DateField(required=True)
    fecha_final = forms.DateField(required=True)
    unidad = forms.ChoiceField(choices=RegistroTemperatura.UNIDADES)

    def __init__(self, *args, **kwargs):
        super(EquiposAreaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = 'equipos:control_temperatura'
        self.helper.layout = Layout(
            Div(
                Div('areas', css_class='col-md-3'),
                Div('equipos', css_class='col-md-3'),
                Div(Field('codigo', readonly=True), css_class='col-md-2'),
                Div(Field('temperatura_minima', readonly=True), css_class='col-md-2'),
                Div(Field('temperatura_maxima', readonly=True), css_class='col-md-2'),
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

        if self.is_bound:
            try:
                area = int(self.data.get('areas'))
                self.fields['equipos'].queryset = Equipo.objects.filter(area=area)
            except:
                pass


class EquiposForm(forms.Form):
    """Formulario que permite escoger un equipo del laboratorio para mostrar sus registros de tempertura."""

    equipos = forms.ModelChoiceField(queryset=Equipo.objects.none())
    codigo = forms.CharField(max_length=100, required=False)
    temperatura_maxima = forms.CharField(max_length=100, required=False, label='Temperatura máxima (ºC)')
    temperatura_minima = forms.CharField(max_length=100, required=False, label='Temperatura mínima (ºC)')
    fecha_inicial = forms.DateField(required=True)
    fecha_final = forms.DateField(required=True)
    unidad = forms.ChoiceField(choices=RegistroTemperatura.UNIDADES)

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario')
        super(EquiposForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = 'equipos:control_temperatura'
        self.helper.layout = Layout(
            Div(
                Div('equipos', css_class='col-md-3'),
                Div(Field('codigo', readonly=True), css_class='col-md-2'),
                Div(Field('temperatura_minima', readonly=True), css_class='col-md-3'),
                Div(Field('temperatura_maxima', readonly=True), css_class='col-md-3'),
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

        try:
            self.fields['equipos'].queryset = Equipo.objects.filter(area__in=usuario.empleado.areas.all())
        except Empleado.DoesNotExist:
            pass


class RegistroTemperaturaForm(forms.ModelForm):
    """Formulario para el ingreso de la temperatura de los equipos usados en el laboratorio."""

    def __init__(self, *args, **kwargs):
        equipo = kwargs.pop('equipo')
        super(RegistroTemperaturaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('equipos:registro_temperatura_equipo', args=(equipo.id,))
        self.helper.layout = Layout(
            Div(
                Div(Field('fecha_registro', readonly=True), css_class='col-md-6'),
                css_class='row'
            ),
            Div(
                Div('temperatura', css_class='col-md-3'),
                Div('unidad', css_class='col-md-3'),
                css_class='row'
            ),
            Div(
                Div('observaciones', css_class='col-md-6'),
                css_class='row'
            ),

            FormActions(Submit('aceptar', 'Aceptar'))
        )

    class Meta:
        model = RegistroTemperatura
        fields = ['fecha_registro', 'temperatura', 'unidad', 'observaciones']
