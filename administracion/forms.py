from django import forms
from contextlib import suppress
from django.urls import reverse
from django.db import transaction
from crispy_forms.helper import FormHelper
from braces.forms import UserKwargModelFormMixin
from django.contrib.auth.models import User, Group
from crispy_forms.layout import Layout, Div, Submit
from equipos.models import Equipo
from .models import Empleado
from trazabilidad.models import Prueba, Metodo, MotivoRechazo, Departamento, Municipio, Poblado, MotivoAnalisis, Eps
from trazabilidad.models import ObjetoPrueba, TipoMuestra, ResultadoPrueba, Epsa, CategoriaAgua, TipoAgua, Temperatura
from trazabilidad.models import Solicitante, DescripcionPunto, FuenteAbastecimiento, LugarPunto, CodigoPunto, Paciente
from trazabilidad.models import Institucion, ResponsableRecoleccion, LugarRecoleccion, TipoVigilancia, TipoEnvase
from trazabilidad.models import InstitucionBancoSangre, ProgramaEvaluacionExterna, TipoEventoEvaluacionExterna, Area
from trazabilidad.models import InstitucionEEDD, InstitucionEEID, TipoEvento, Control, InstitucionCitohistopatologia
from trazabilidad.models import Programa
from alimentos.models import Solicitante as SolicitanteAlimento, Grupo, Categoria, Subcategoria
from alimentos.models import Distribuidor, Fabricante, Decreto as Normatividad
from bebidas_alcoholicas.models import (
    Grupo as GrupoBebidaAlcoholica, Producto, Decreto, TipoEnvase as TipoEnvaseBebidaAlcoholica
)
from covid19 import models as covid_models
from . import models as m

__author__ = 'tania'


class ActualizarAreaForm(UserKwargModelFormMixin, forms.ModelForm):
    """
    Formulario para actualizar los valores de temperatura y humedad de las áreas
    """

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:actualizar_area', args=(self.instance.id, ))
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = Area
        fields = ('temperatura_maxima', 'temperatura_minima', 'humedad_maxima', 'humedad_minima', )


class NuevaPruebaForm(UserKwargModelFormMixin, forms.ModelForm):
    """Formulario para creación de la pruebas en el sistema."""
    programa = forms.ModelChoiceField(queryset=Programa.objects.all())
    area = forms.ModelChoiceField(queryset=Area.objects.none())

    def __init__(self, *args, **kwargs):
        super(NuevaPruebaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nueva_prueba')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

        if self.is_bound:
            try:
                programa_id = self.data.get('programa')
                self.fields['area'].queryset = Area.objects.filter(programa=programa_id)
            except:
                self.fields['area'].queryset = Area.objects.none()

    class Meta:
        model = Prueba
        fields = ['nombre', 'programa', 'area', 'duracion', 'resultados', 'metodos', 'estado', 'valores_referencia']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevaPruebaForm, self).save(commit)


class ActualizarPruebaForm(NuevaPruebaForm):
    """Formulario para la actualización de una prueba en el sistema."""

    def __init__(self, *args, **kwargs):
        super(ActualizarPruebaForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_prueba', args=(self.instance.id,))
        self.fields['programa'].initial = self.instance.area.programa
        self.fields['area'].queryset = Area.objects.filter(programa=self.instance.area.programa)
        self.fields['area'].initial = self.instance.area


class NuevoMetodoForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoMetodoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_metodo')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = Metodo
        fields = ['estado', 'nombre', 'objeto']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoMetodoForm, self).save(commit)


class ActualizarMetodoForm(NuevoMetodoForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarMetodoForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_metodo', args=(self.instance.id,))


class NuevoMotivoRechazoForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoMotivoRechazoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_motivo_rechazo')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = MotivoRechazo
        fields = ['motivo', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoMotivoRechazoForm, self).save(commit)


class ActualizarMotivoRechazoForm(NuevoMotivoRechazoForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarMotivoRechazoForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_motivo_rechazo', args=(self.instance.id,))


class NuevoDepartamentoForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoDepartamentoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_departamento')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = Departamento
        fields = ['nombre', 'codigo']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoDepartamentoForm, self).save(commit)


class ActualizarDepartamentoForm(NuevoDepartamentoForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarDepartamentoForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_departamento', args=(self.instance.id,))


class NuevoMunicipioForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoMunicipioForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_municipio')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = Municipio
        fields = ['nombre', 'departamento', 'codigo', 'email']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoMunicipioForm, self).save(commit)


class ActualizarMunicipioForm(NuevoMunicipioForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarMunicipioForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_municipio', args=(self.instance.id,))


class NuevoPobladoForm(UserKwargModelFormMixin, forms.ModelForm):
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.none())

    def __init__(self, *args, **kwargs):
        super(NuevoPobladoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_poblado')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

        if self.is_bound:
            try:
                id_departamento = int(self.data.get('departamento'))
                self.fields['municipio'].queryset = Municipio.objects.filter(departamento=id_departamento)
            except:
                self.fields['municipio'].queryset = Municipio.objects.none()

    class Meta:
        model = Poblado
        fields = ['nombre', 'departamento', 'municipio', 'codigo', 'epsa']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoPobladoForm, self).save(commit)


class ActualizarPobladoForm(NuevoPobladoForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarPobladoForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_poblado', args=(self.instance.id,))

        if not self.is_bound:
            departamento = self.instance.municipio.departamento
            self.fields['departamento'].initial = departamento
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=departamento)
            self.fields['municipio'].initial = self.instance.municipio


class NuevoMotivoAnalisisForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoMotivoAnalisisForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_motivo_analisis')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = MotivoAnalisis
        fields = ['nombre']


class ActualizarMotivoAnalisisForm(NuevoMotivoAnalisisForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarMotivoAnalisisForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_motivo_analisis', args=(self.instance.id,))


class NuevoObjetoPruebaForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoObjetoPruebaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_objeto_general_prueba')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = ObjetoPrueba
        fields = ['nombre', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoObjetoPruebaForm, self).save(commit)


class ActualizarObjetoPruebaForm(NuevoObjetoPruebaForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarObjetoPruebaForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_objeto_general_prueba', args=(self.instance.id,))


class NuevoResultadoPruebaForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoResultadoPruebaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_resultado_prueba')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = ResultadoPrueba
        fields = ['nombre', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoResultadoPruebaForm, self).save(commit)


class ActualizarResultadoPruebaForm(NuevoResultadoPruebaForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarResultadoPruebaForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_resultado_prueba', args=(self.instance.id,))


class NuevoTipoMuestraForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoTipoMuestraForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_tipo_muestra')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = TipoMuestra
        fields = ['nombre', 'programas', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoTipoMuestraForm, self).save(commit)


class ActualizarTipoMuestraForm(NuevoTipoMuestraForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarTipoMuestraForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_tipo_muestra', args=(self.instance.id,))


class NuevoPacienteForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoPacienteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_paciente')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'direccion', 'identificacion',
                  'tipo_identificacion', 'edad', 'tipo_edad', 'eps', 'sexo']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoPacienteForm, self).save(commit)


class ActualizarPacienteForm(NuevoPacienteForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarPacienteForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_paciente', args=(self.instance.id,))


class NuevoEpsaForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoEpsaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_epsa')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = Epsa
        fields = ['nombre', 'direccion', 'rup', 'nit', 'tipo']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoEpsaForm, self).save(commit)


class ActualizarEpsaForm(NuevoEpsaForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarEpsaForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_epsa', args=(self.instance.id,))


class NuevoCategoriaAguaForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoCategoriaAguaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_categoria_agua')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = CategoriaAgua
        fields = ['nombre']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoCategoriaAguaForm, self).save(commit)


class ActualizarCategoriaAguaForm(NuevoCategoriaAguaForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarCategoriaAguaForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_categoria_agua', args=(self.instance.id,))


class NuevoTipoAguaForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoTipoAguaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_tipo_agua')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = TipoAgua
        fields = ['nombre', 'categoria']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoTipoAguaForm, self).save(commit)


class ActualizarTipoAguaForm(NuevoTipoAguaForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarTipoAguaForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_tipo_agua', args=(self.instance.id,))


class NuevoTemperaturaForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoTemperaturaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_temperatura')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = Temperatura
        fields = ['valor']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoTemperaturaForm, self).save(commit)


class ActualizarTemperaturaForm(NuevoTemperaturaForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarTemperaturaForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_temperatura', args=(self.instance.id,))


class NuevoSolicitanteForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoSolicitanteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_solicitante')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = Solicitante
        fields = ['nombre', 'direccion', 'telefono', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoSolicitanteForm, self).save(commit)


class ActualizarSolicitanteForm(NuevoSolicitanteForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarSolicitanteForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_solicitante', args=(self.instance.id,))


class NuevoDescripcionPuntoForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoDescripcionPuntoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_descripcion_punto')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = DescripcionPunto
        fields = ['nombre', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoDescripcionPuntoForm, self).save(commit)


class ActualizarDescripcionPuntoForm(NuevoDescripcionPuntoForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarDescripcionPuntoForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_descripcion_punto', args=(self.instance.id,))


class NuevoFuenteAbastecimientoForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoFuenteAbastecimientoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_fuente_abastecimiento')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = FuenteAbastecimiento
        fields = ['nombre', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoFuenteAbastecimientoForm, self).save(commit)


class ActualizarFuenteAbastecimientoForm(NuevoFuenteAbastecimientoForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarFuenteAbastecimientoForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_fuente_abastecimiento', args=(self.instance.id,))


class NuevoLugarPuntoForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoLugarPuntoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_lugar_punto')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = LugarPunto
        fields = ['nombre', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoLugarPuntoForm, self).save(commit)


class ActualizarLugarPuntoForm(NuevoLugarPuntoForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarLugarPuntoForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_lugar_punto', args=(self.instance.id,))


class NuevoCodigoPuntoForm(UserKwargModelFormMixin, forms.ModelForm):
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.none())
    poblado = forms.ModelChoiceField(queryset=Poblado.objects.none())

    def __init__(self, *args, **kwargs):
        super(NuevoCodigoPuntoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_codigo_punto')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

        if self.is_bound:
            try:
                departamento_id = self.data.get('departamento')
                self.fields['municipio'].queryset = Municipio.objects.filter(departamento=departamento_id)
                try:
                    municipio_id = self.data.get('municipio')
                    self.fields['poblado'].queryset = Poblado.objects.filter(municipio=municipio_id)
                except:
                    self.fields['poblado'].queryset = Poblado.objects.none()
            except:
                self.fields['municipio'].queryset = Municipio.objects.none()

    class Meta:
        model = CodigoPunto
        fields = ['codigo', 'direccion', 'lugar_toma', 'descripcion',
                  'fuente_abastecimiento', 'punto_intradomiciliario', 'departamento', 'municipio', 'poblado', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoCodigoPuntoForm, self).save(commit)


class ActualizarCodigoPuntoForm(NuevoCodigoPuntoForm):
    def __init__(self, *args, **kwargs):
        super(ActualizarCodigoPuntoForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_codigo_punto', args=(self.instance.id,))

        if not self.is_bound:
            self.fields['departamento'].initial = self.instance.poblado.municipio.departamento
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=self.instance.poblado.municipio.departamento)
            self.fields['municipio'].initial = self.instance.poblado.municipio
            self.fields['poblado'].queryset = Poblado.objects.filter(municipio=self.instance.poblado.municipio)
            self.fields['poblado'].initial = self.instance.poblado


class NuevaEpsForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevaEpsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nueva_eps')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = Eps
        fields = ['nombre', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevaEpsForm, self).save(commit)


class ActualizarEpsForm(NuevaEpsForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarEpsForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_eps', args=(self.instance.id,))


class NuevaInstitucionForm(UserKwargModelFormMixin, forms.ModelForm):
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.none())

    def __init__(self, *args, **kwargs):
        super(NuevaInstitucionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nueva_institucion')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

        if self.is_bound:
            try:
                id_departamento = self.data.get('departamento')
                self.fields['municipio'].queryset = Municipio.objects.filter(departamento=id_departamento)
            except:
                self.fields['municipio'].queryset = Municipio.objects.none()

    class Meta:
        model = Institucion
        fields = ['nombre', 'departamento', 'municipio']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevaInstitucionForm, self).save(commit)


class ActualizarInstitucionForm(NuevaInstitucionForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarInstitucionForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_institucion', args=(self.instance.id,))

        if not self.is_bound:
            self.fields['departamento'].initial = self.instance.municipio.departamento
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=self.instance.municipio.departamento)
            self.fields['municipio'].initial = self.instance.municipio


class NuevoResponsableRecoleccionForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoResponsableRecoleccionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_responsable_recoleccion')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = ResponsableRecoleccion
        fields = ['nombres', 'apellidos']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoResponsableRecoleccionForm, self).save(commit)


class ActualizarResponsableRecoleccionForm(NuevoResponsableRecoleccionForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarResponsableRecoleccionForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_responsable_recoleccion', args=(self.instance.id,))


class NuevoLugarRecoleccionForm(UserKwargModelFormMixin, forms.ModelForm):
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.none())

    def __init__(self, *args, **kwargs):
        super(NuevoLugarRecoleccionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_lugar_recoleccion')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

        if self.is_bound:
            try:
                self.fields['municipio'].queryset = Municipio.objects.filter(departamento=int(self.data.get('departamento')))
            except:
                self.fields['municipio'].queryset = Municipio.objects.none()

    class Meta:
        model = LugarRecoleccion
        fields = ['nombre', 'departamento', 'municipio']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoLugarRecoleccionForm, self).save(commit)


class ActualizarLugarRecoleccionForm(NuevoLugarRecoleccionForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarLugarRecoleccionForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_lugar_recoleccion', args=(self.instance.id,))

        if not self.is_bound:
            self.fields['departamento'].initial = self.instance.municipio.departamento
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=self.instance.municipio.departamento)
            self.fields['municipio'].initial = self.instance.municipio


class NuevoTipoVigilanciaForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoTipoVigilanciaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_tipo_vigilancia')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = TipoVigilancia
        fields = ['nombre', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoTipoVigilanciaForm, self).save(commit)


class ActualizarTipoVigilanciaForm(NuevoTipoVigilanciaForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarTipoVigilanciaForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_tipo_vigilancia', args=(self.instance.id,))


class NuevoTipoEnvaseForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoTipoEnvaseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_tipo_envase')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = TipoEnvase
        fields = ['nombre', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoTipoEnvaseForm, self).save(commit)


class ActualizarTipoEnvaseForm(NuevoTipoEnvaseForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarTipoEnvaseForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_tipo_envase', args=(self.instance.id,))


class NuevoInstitucionBancoSangreForm(UserKwargModelFormMixin, forms.ModelForm):
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.none())

    def __init__(self, *args, **kwargs):
        super(NuevoInstitucionBancoSangreForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_institucion_banco_sangre')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

        if self.is_bound:
            try:
                departamento = int(self.data.get('departamento'))
                self.fields['municipio'].queryset = Municipio.objects.filter(departamento=departamento)
            except:
                self.fields['municipio'].queryset = Municipio.objects.none()

    class Meta:
        model = InstitucionBancoSangre
        fields = ['nombre', 'departamento', 'municipio']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoInstitucionBancoSangreForm, self).save(commit)


class ActualizarInstitucionBancoSangreForm(NuevoInstitucionBancoSangreForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarInstitucionBancoSangreForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_institucion_banco_sangre', args=(self.instance.id,))

        if not self.is_bound:
            self.fields['departamento'].initial = self.instance.municipio.departamento
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=self.instance.municipio.departamento)
            self.fields['municipio'].initial = self.instance.municipio


class NuevoProgramaEvaluacionExternaForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoProgramaEvaluacionExternaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_programa_evaluacion_externa')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = ProgramaEvaluacionExterna
        fields = ['nombre', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoProgramaEvaluacionExternaForm, self).save(commit)


class ActualizarProgramaEvaluacionExternaForm(NuevoProgramaEvaluacionExternaForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarProgramaEvaluacionExternaForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_programa_evaluacion_externa', args=(self.instance.id,))


class NuevoTipoEventoEvaluacionExternaForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoTipoEventoEvaluacionExternaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_tipo_evento_evaluacion_externa')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = TipoEventoEvaluacionExterna
        fields = ['nombre', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoTipoEventoEvaluacionExternaForm, self).save(commit)


class ActualizarTipoEventoEvaluacionExternaForm(NuevoTipoEventoEvaluacionExternaForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarTipoEventoEvaluacionExternaForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_tipo_evento_evaluacion_externa', args=(self.instance.id,))


class NuevoInstitucionEEDDForm(UserKwargModelFormMixin, forms.ModelForm):
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.none())

    def __init__(self, *args, **kwargs):
        super(NuevoInstitucionEEDDForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_institucion_eedd')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

        if self.is_bound:
            try:
                departamento = int(self.data.get('departamento'))
                self.fields['municipio'].queryset = Municipio.objects.filter(departamento=departamento)
            except:
                self.fields['municipio'].queryset = Municipio.objects.none()

    class Meta:
        model = InstitucionEEDD
        fields = ['nombre', 'direccion', 'nit', 'departamento', 'municipio']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoInstitucionEEDDForm, self).save(commit)


class ActualizarInstitucionEEDDForm(NuevoInstitucionEEDDForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarInstitucionEEDDForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_institucion_eedd', args=(self.instance.id,))

        if not self.is_bound:
            self.fields['departamento'].initial = self.instance.municipio.departamento
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=self.instance.municipio.departamento)
            self.fields['municipio'].initial = self.instance.municipio


class NuevoInstitucionEEIDForm(UserKwargModelFormMixin, forms.ModelForm):
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.none())

    def __init__(self, *args, **kwargs):
        super(NuevoInstitucionEEIDForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_institucion_eeid')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

        if self.is_bound:
            try:
                departamento = int(self.data.get('departamento'))
                self.fields['municipio'].queryset = Municipio.objects.filter(departamento=departamento)
            except:
                self.fields['municipio'].queryset = Municipio.objects.none()

    class Meta:
        model = InstitucionEEID
        fields = ['nombre', 'departamento', 'municipio', 'codigo']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoInstitucionEEIDForm, self).save(commit)


class ActualizarInstitucionEEIDForm(NuevoInstitucionEEIDForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarInstitucionEEIDForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_institucion_eeid', args=(self.instance.id,))

        if not self.is_bound:
            self.fields['departamento'].initial = self.instance.municipio.departamento
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=self.instance.municipio.departamento)
            self.fields['municipio'].initial = self.instance.municipio


class NuevoInstitucionCitohistopatologiaForm(UserKwargModelFormMixin, forms.ModelForm):
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.none())

    def __init__(self, *args, **kwargs):
        super(NuevoInstitucionCitohistopatologiaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_institucion_citohistopatologia')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

        if self.is_bound:
            try:
                departamento_id = int(self.data.get('departamento'))
                self.fields['municipio'].queryset = Municipio.objects.filter(departamento=departamento_id)
            except:
                self.fields['municipio'].queryset = Municipio.objects.none()

    class Meta:
        model = InstitucionCitohistopatologia
        fields = ['nombre', 'departamento', 'municipio', 'codigo']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoInstitucionCitohistopatologiaForm, self).save(commit)


class ActualizarInstitucionCitohistopatologiaForm(NuevoInstitucionCitohistopatologiaForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarInstitucionCitohistopatologiaForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_institucion_citohistopatologia', args=(self.instance.id,))

        if not self.is_bound:
            self.fields['departamento'].initial = self.instance.municipio.departamento
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=self.instance.municipio.departamento)
            self.fields['municipio'].initial = self.instance.municipio


class NuevoControlForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoControlForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_control')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = Control
        fields = ['nombre', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoControlForm, self).save(commit)


class ActualizarControlForm(NuevoControlForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarControlForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_control', args=(self.instance.id,))


class NuevoTipoEventoForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoTipoEventoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_tipo_evento')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = TipoEvento
        fields = ['nombre', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoTipoEventoForm, self).save(commit)


class ActualizarTipoEventoForm(NuevoTipoEventoForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarTipoEventoForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_tipo_evento', args=(self.instance.id,))


class NuevoUsuarioForm(UserKwargModelFormMixin, forms.ModelForm):

    OPCIONES_TIPO_EMPLEADO = (
        ('P', 'PLANTA'),
        ('C', 'CONTRATISTA'),
    )

    first_name = forms.CharField(label='Nombres', max_length=100, required=False)
    confirm_pass = forms.CharField(label='Repita contraseña', max_length=100, required=True, widget=forms.PasswordInput)
    password1 = forms.CharField(label='Contraseña', max_length=100, required=True, widget=forms.PasswordInput)
    grupos = forms.ModelMultipleChoiceField(label='Perfil', queryset=Group.objects.all())
    empleado = forms.BooleanField(label='Empleado?', required=False)
    areas = forms.ModelMultipleChoiceField(queryset=Area.objects.all(), required=False)
    tipo_empleado = forms.ChoiceField(label='Tipo Empleado', choices=OPCIONES_TIPO_EMPLEADO, required=False)
    codigo = forms.CharField(max_length=100, required=False)
    responsable_tecnico = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = [
            'email',
            'grupos',
            'areas',
            'codigo',
            'username',
            'password1',
            'is_active',
            'last_name',
            'first_name',
            'confirm_pass',
            'tipo_empleado',
            'responsable_tecnico',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

        self.fields['username'].widget.attrs.update({'autofocus': ''})
        self.fields['confirm_pass'].widget.attrs.update({'type': 'password'})
        self.fields['password1'].widget.attrs.update({'type': 'password'})
        self.fields['is_active'].help_text = None

        self.helper.layout = Layout(
            Div(
                Div('username', css_class='col-md-4'),
                Div('password1', css_class='col-md-4'),
                Div('confirm_pass', css_class='col-md-4'),
                css_class='row'
            ),
            Div(
                Div('first_name', css_class='col-md-4'),
                Div('last_name', css_class='col-md-4'),
                Div('email', css_class='col-md-4'),
                css_class='row'
            ),
            Div(
                Div('grupos', css_class='col-md-4'),
                Div('is_active', css_class='col-md-4'),
                Div('empleado', css_class='col-md-4'),
                css_class='row'
            ),
            Div(
                Div('areas', css_class='col-md-3'),
                Div('codigo', css_class='col-md-3'),
                Div('tipo_empleado', css_class='col-md-3'),
                Div('responsable_tecnico', css_class='col-md-3'),
                css_class='row info-empleado'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        pass1 = cleaned_data.get('password1', None)
        pass2 = cleaned_data.get('confirm_pass', None)

        if pass1 != pass2:
            self.add_error('confirm_pass', 'Contraseñas no coinciden')
        
        if cleaned_data.get('empleado', False):
            for f in ['tipo_empleado', 'areas', 'codigo']:
                if not cleaned_data.get(f, None):
                    self.add_error(f, 'Campo requerido')

        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit)

        user.groups.set(self.cleaned_data['grupos'])        
        self.set_password(user)

        if self.cleaned_data.get('empleado', False):
            emp, _ = Empleado.objects.update_or_create(
                usuario=user,
                defaults={
                    'codigo': self.cleaned_data['codigo'],
                    'tipo': self.cleaned_data['tipo_empleado'],
                    'responsable_tecnico': self.cleaned_data.get('responsable_tecnico', False),
                }
            )
            emp.areas.set(self.cleaned_data['areas'])


        return user
    
    def set_password(self, user):
        user.set_password(self.cleaned_data['password1'])
        user.save()

class ActualizarUsuarioForm(NuevoUsuarioForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_usuario', args=(self.instance.id,))
        self.fields['password1'].required = False
        self.fields['confirm_pass'].required = False
        self.fields['grupos'].initial = self.instance.groups.all()
        
        with suppress(Exception):
            empleado = self.instance.empleado
            self.fields['empleado'].disabled = True
            self.fields['empleado'].initial = True
            self.fields['codigo'].initial = empleado.codigo
            self.fields['tipo_empleado'].initial = empleado.tipo
            self.fields['areas'].initial = empleado.areas.all()
            self.fields['responsable_tecnico'].initial = empleado.responsable_tecnico
        
    def set_password(self, user):
        if self.cleaned_data.get('password1', None):
            user.set_password(self.cleaned_data['password1'])
            user.save()


class NuevoEmpleadoForm(UserKwargModelFormMixin, forms.ModelForm):

    usuario = forms.ModelChoiceField(queryset=User.objects.none())

    class Meta:
        model = Empleado
        fields = ['usuario', 'codigo', 'areas', 'tipo', 'responsable_tecnico']

    def __init__(self, *args, **kwargs):
        super(NuevoEmpleadoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('aceptar', 'Aceptar'))
        self.fields['usuario'].queryset = User.objects.exclude(id__in=Empleado.objects.values_list('usuario', flat=True))


class ActualizarEmpleadoForm(NuevoEmpleadoForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarEmpleadoForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_empleado', args=(self.instance.id,))

        empleado = User.objects.filter(id=self.instance.usuario.id)
        self.fields['usuario'].queryset = self.fields['usuario'].queryset | empleado


class NuevoEquipoForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoEquipoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_equipo')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = Equipo
        fields = ['nombre', 'codigo', 'temperatura_minima', 'temperatura_maxima', 'area', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoEquipoForm, self).save(commit)


class ActualizarEquipoForm(NuevoEquipoForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarEquipoForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_equipo', args=(self.instance.id,))


class NuevoSolicitanteAlimentoForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoSolicitanteAlimentoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_solicitante_alimento')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = SolicitanteAlimento
        fields = ['nombre']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoSolicitanteAlimentoForm, self).save(commit)


class ActualizarSolicitanteAlimentoForm(NuevoSolicitanteAlimentoForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarSolicitanteAlimentoForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_solicitante_alimento', args=(self.instance.id,))


class NuevoGrupoForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoGrupoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_grupo')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = Grupo
        fields = ['codigo', 'descripcion', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoGrupoForm, self).save(commit)


class ActualizarGrupoForm(NuevoGrupoForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarGrupoForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_grupo', args=(self.instance.id,))


class NuevoCategoriaForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoCategoriaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_categoria')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = Categoria
        fields = ['codigo', 'descripcion', 'grupo', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoCategoriaForm, self).save(commit)


class ActualizarCategoriaForm(NuevoCategoriaForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarCategoriaForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_categoria', args=(self.instance.id,))


class NuevoSubcategoriaForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoSubcategoriaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_sub_categoria')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))
        # queryset = Programa.objects.get(nombre__iexact='alimentos')
        # self.fields['pruebas'].queryset = Prueba.objects.filter(area__programa=queryset)

    class Meta:
        model = Subcategoria
        fields = ['codigo', 'descripcion', 'categoria', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoSubcategoriaForm, self).save(commit)


class ActualizarSubcategoriaForm(NuevoSubcategoriaForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarSubcategoriaForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_sub_categoria', args=(self.instance.id,))


class NuevoFabricanteForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoFabricanteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_fabricante')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = Fabricante
        fields = ['nombre']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoFabricanteForm, self).save(commit)


class ActualizarFabricanteForm(NuevoFabricanteForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarFabricanteForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_fabricante', args=(self.instance.id,))


class NuevoDistribuidorForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoDistribuidorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_distribuidor')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = Distribuidor
        fields = ['nombre']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoDistribuidorForm, self).save(commit)


class ActualizarDistribuidorForm(NuevoDistribuidorForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarDistribuidorForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_distribuidor', args=(self.instance.id,))


class NuevoGrupoBebidaAlcoholicaForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoGrupoBebidaAlcoholicaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_grupo_bebida_alcoholica')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = GrupoBebidaAlcoholica
        fields = ['nombre', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoGrupoBebidaAlcoholicaForm, self).save(commit)


class ActualizarGrupoBebidaAlcoholicaForm(NuevoGrupoBebidaAlcoholicaForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarGrupoBebidaAlcoholicaForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_grupo_bebida_alcoholica', args=(self.instance.id,))


class NuevoProductoForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoProductoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_producto')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = Producto
        fields = ['nombre', 'grupo', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoProductoForm, self).save(commit)


class ActualizarProductoForm(NuevoProductoForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarProductoForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_producto', args=(self.instance.id,))


class NuevoDecretoForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoDecretoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_decreto')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))
        self.fields['pruebas'].queryset = Prueba.objects.filter(
            area__programa=Programa.objects.bebidas_alcoholicas(),
            area__oculto=False
        )

    class Meta:
        model = Decreto
        fields = ['nombre', 'grupo', 'pruebas', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoDecretoForm, self).save(commit)


class ActualizarDecretoForm(NuevoDecretoForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarDecretoForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_decreto', args=(self.instance.id,))


class NuevoTipoEnvaseBebidaAlcoholicaForm(UserKwargModelFormMixin, forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(NuevoTipoEnvaseBebidaAlcoholicaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_tipo_envase_bebida_alcoholica')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = TipoEnvaseBebidaAlcoholica
        fields = ['nombre']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoTipoEnvaseBebidaAlcoholicaForm, self).save(commit)


class ActualizarTipoEnvaseBebidaAlcoholicaForm(NuevoTipoEnvaseBebidaAlcoholicaForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarTipoEnvaseBebidaAlcoholicaForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_tipo_envase_bebida_alcoholica', args=(self.instance.id,))


class NuevoNormatividadForm(UserKwargModelFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuevoNormatividadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_normatividad')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))
        self.fields['area'].queryset = Area.objects.filter(programa=Programa.objects.alimentos())
        self.fields['pruebas'].queryset = Prueba.objects.none()
        self.fields['pruebas'].required = True

        if self.is_bound:
            area = self.data.get('area', None) or None
            if area is not None:
                self.fields['pruebas'].queryset = Prueba.objects.filter(
                    area__programa=Programa.objects.alimentos(),
                    area_id=area
                )
        elif self.instance.pk:
            self.fields['pruebas'].queryset = self.instance.pruebas.all()
            # self.fields['pruebas'].initial = self.instance.pruebas.all()

    class Meta:
        model = Normatividad
        fields = ['nombre', 'area', 'pruebas', 'tipo', 'estado']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super(NuevoNormatividadForm, self).save(commit)


class ActualizarNormatividadForm(NuevoNormatividadForm):

    def __init__(self, *args, **kwargs):
        super(ActualizarNormatividadForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_normatividad', args=(self.instance.id,))


class NuevoUpgdForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_upgd')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = covid_models.Upgd
        fields = ['nombre', 'codigo', 'subindice', 'email']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super().save(commit)

class ActualizarUpgdForm(NuevoUpgdForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_upgd', args=(self.instance.id,))


class NuevoEapbForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_eapb')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = covid_models.Eapb
        fields = ['nombre', 'codigo', 'email']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super().save(commit)

class ActualizarEapbForm(NuevoEapbForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_eapb', args=(self.instance.id,))


class NuevoTipificacionForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_tipificacion')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = covid_models.Tipificacion
        fields = ['nombre']

    def save(self, commit=True):
        self.instance.modificado_por = self.user
        return super().save(commit)

class ActualizarTipificacionForm(NuevoTipificacionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_tipificacion', args=(self.instance.id,))


class NuevoOcupacionForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:nuevo_ocupacion')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))

    class Meta:
        model = covid_models.Ocupacion
        fields = ['nombre', 'codigo']

class ActualizarOcupacionForm(NuevoOcupacionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse('administracion:actualizar_ocupacion', args=(self.instance.id,))

class ConfigGeneralForm(forms.ModelForm):

    class Meta:
        model = m.ConfigGeneral
        fields = ['firma_automatica_reporte']
    
    def __init__(self, *args, **kwargs):
        super().__init__(instance=m.ConfigGeneral.objects.first(), * args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('administracion:config_general')
        self.helper.add_input(Submit('aceptar', 'Aceptar'))
