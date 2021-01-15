import logging
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from trazabilidad.models import Departamento, Municipio, Poblado, Area, Programa, MotivoAnalisis, PruebasRealizadas
from trazabilidad.models import Prueba
from .models import InformacionAlimento, Alimento, Grupo, Subcategoria, Fabricante, Distribuidor, Categoria, Decreto

logger = logging.getLogger(__name__)


class InformacionAlimentoForm(forms.ModelForm):
    """Formulario para el manejo de la información general que tienen las muestras de alimento."""

    error_css_class = 'has-error'

    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.none())

    def __init__(self, *args, **kwargs):
        super(InformacionAlimentoForm, self).__init__(*args, **kwargs)
        self.fields['direccion_recoleccion'].widget.attrs.update({'class': 'form-control'})
        self.fields['departamento'].widget.attrs.update({'class': 'form-control'})
        self.fields['solicitante'].widget.attrs.update({'class': 'form-control'})
        self.fields['responsable'].widget.attrs.update({'class': 'form-control'})
        self.fields['sitio_toma'].widget.attrs.update({'class': 'form-control'})
        self.fields['direccion'].widget.attrs.update({'class': 'form-control'})
        self.fields['municipio'].widget.attrs.update({'class': 'form-control'})
        self.fields['poblado'].widget.attrs.update({'class': 'form-control'})
        self.fields['fecha'].widget.attrs.update({'class': 'form-control'})
        self.fields['cargo'].widget.attrs.update({'class': 'form-control'})

        if self.is_bound:
            try:
                id_departamento = int(self.data.get('general-departamento'))
                self.fields['municipio'].queryset = Municipio.objects.filter(departamento=id_departamento)
            except:
                self.fields['municipio'].queryset = Municipio.objects.none()

            try:
                id_municipio = int(self.data.get('general-municipio'))
                self.fields['poblado'].queryset = Poblado.objects.filter(municipio=id_municipio)
            except:
                self.fields['poblado'].queryset = Poblado.objects.none()
        elif self.instance.pk:
            departamento = self.instance.poblado.municipio.departamento
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=departamento)
            self.fields['poblado'].queryset = Poblado.objects.filter(municipio=self.instance.poblado.municipio)

            self.fields['municipio'].initial = self.instance.poblado.municipio
            self.fields['departamento'].initial = self.instance.poblado.municipio.departamento
        else:
            self.fields['poblado'].queryset = Poblado.objects.none()

    class Meta:
        model = InformacionAlimento
        fields = ['solicitante', 'direccion', 'responsable', 'cargo', 'departamento',
                  'municipio', 'poblado', 'sitio_toma', 'direccion_recoleccion', 'fecha']


class MuestraAlimentoFormSet(forms.BaseModelFormSet):
    """Model formset para las muestras de alimento."""

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        self.nueva = kwargs.pop('nueva', None)
        super(MuestraAlimentoFormSet, self).__init__(*args, **kwargs)

        for form in self:
            form.usuario = self.usuario

    def save(self, ingreso=None, general=None):
        for form in self:
            form.ingreso = ingreso
            form.general = general

        muestras = super(MuestraAlimentoFormSet, self).save()

        if not muestras and self.nueva:
            muestra = Alimento()
            muestra.registro_recepcion = ingreso
            muestra.informacion_general = general
            muestra.save()

            muestras.append(muestra)

        return muestras


class MuestraAlimentoForm(forms.ModelForm):
    """Formulario para el manejo de las muestras de alimento."""

    error_css_class = 'has-error'

    CHOICES = (
        (True, 'Si'),
        (False, 'No'),
    )
    no_aplica_vencimiento = forms.ChoiceField(choices=CHOICES, widget=forms.CheckboxInput)
    nuevo_fabricante = forms.CharField(max_length=100, required=False)
    nuevo_distribuidor = forms.CharField(max_length=100, required=False)
    grupo = forms.ModelChoiceField(queryset=Grupo.objects.activos(), required=False, label='Grupo de alimento')
    nuevo_motivo_analisis = forms.CharField(max_length=100, required=False)
    areas = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(programa=Programa.objects.alimentos()),
                                           widget=forms.CheckboxSelectMultiple, required=False,
                                           label='Analisis solicitado')

    class Meta:
        model = Alimento
        fields = ['unidad_muestra', 'contenido_neto', 'unidad_contramuestra', 'grupo', 'tipo',
                  'descripcion', 'registro_sanitario', 'lote', 'ano_vencimiento', 'mes_vencimiento',
                  'dia_vencimiento', 'propietario', 'fabricante', 'nuevo_fabricante', 'distribuidor',
                  'nuevo_distribuidor', 'importador', 'responsable_entrega', 'temperatura', 'cumple',
                  'cadena_custodia', 'constancia_pago', 'motivo_analisis', 'nuevo_motivo_analisis', 'areas',
                  'subcategoria', 'direccion_importador', 'temperatura_recoleccion', 'temp_ingreso']

    def __init__(self, *args, **kwargs):
        super(MuestraAlimentoForm, self).__init__(*args, **kwargs)
        self.fields['lote'].label = 'Lote'
        self.fields['temp_ingreso'].required = True
        self.fields['temperatura'].label = 'Temperatura de Ingreso'
        self.fields['temperatura_recoleccion'].label = 'Temperatura en sitio de toma'
        # self.fields['tipo'].label = 'Sub-Categoria'
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.render_hidden_fields = True
        self.helper.layout = Layout(
            Div(
                Div('temp_ingreso', css_class='col-md-3'),
                Div('unidad_muestra', css_class='col-md-3'),
                Div('contenido_neto', css_class='col-md-3'),
                Div('unidad_contramuestra', css_class='col-md-3'),
                Div(
                    Field('grupo', css_class='select-grupo'),
                    css_class='col-md-4 grupo'
                ),
                Div(
                    Field('tipo', css_class='select-tipo'),
                    css_class='col-md-4 tipo'
                ),
                Div(
                    Field('subcategoria', css_class='select-subcategoria'),
                    css_class='col-md-4 subcategoria'
                ),
                Div('descripcion', css_class='col-md-4'),
                Div('registro_sanitario', css_class='col-md-4'),
                Div('lote', css_class='col-md-4'),
                Div('propietario', css_class='col-md-3'),
                Div('importador', css_class='col-md-3'),
                Div('direccion_importador', css_class='col-md-3'),
                Div(
                    Field('ano_vencimiento', css_class='input-año'),
                    css_class='col-md-3 f-ano'
                ),
                Div(
                    Field('mes_vencimiento', css_class='input-mes'),
                    css_class='col-md-3 f-mes'
                ),
                Div(
                    Field('dia_vencimiento', css_class='input-dia'),
                    css_class='col-md-3 f-dia'
                ),
                Div('no_aplica_vencimiento', css_class='col-md-3 no-aplica'),
                Div('responsable_entrega', css_class='col-md-3'),
                Div(
                    Field('fabricante', css_class='select-fabricante'),
                    css_class='col-md-3 fabricante'
                ),
                Div('nuevo_fabricante', css_class='col-md-3 nuevo-fabricante'),
                Div(
                    Field('distribuidor', css_class='select-distribuidor'),
                    css_class='col-md-3 distribuidor'
                ),
                Div('nuevo_distribuidor', css_class='col-md-3 nuevo-distribuidor'),
                Div('temperatura', css_class='col-md-3'),
                Div('temperatura_recoleccion', css_class='col-md-3'),
                Div('cumple', css_class='col-md-3'),
                Div('cadena_custodia', css_class='col-md-3'),
                Div('constancia_pago', css_class='col-md-3'),
                Div(
                    Field('motivo_analisis', css_class='select-motivo-analisis'),
                    css_class='col-md-3 motivo-analisis'
                ),
                Div('nuevo_motivo_analisis', css_class='col-md-3 nuevo-motivo-analisis'),
                Div('areas', css_class='col-md-3'),
                css_class='row'
            )
        )

        self.confirmar = True if 'confirmado' in self.data else False

        self.fields['motivo_analisis'].empty_label = 'Nuevo motivo de analisis'
        self.fields['distribuidor'].empty_label = 'Nuevo distribuidor'
        self.fields['fabricante'].empty_label = 'Nuevo fabricante'

        if self.is_bound:
            if not self['ano_vencimiento'].data:
                self.fields['no_aplica_vencimiento'].initial = True
            valor_grupo = self['grupo'].data
            if valor_grupo:
                self.fields['tipo'].queryset = Categoria.objects.filter(grupo__id=valor_grupo)
                valor_tipo = self['tipo'].data
                if valor_tipo:
                    self.fields['subcategoria'].queryset = Subcategoria.objects.filter(categoria__id=valor_tipo)
                else:
                    self.fields['subcategoria'].queryset = Subcategoria.objects.none()
            else:
                self.fields['tipo'].queryset = Categoria.objects.none()
                self.fields['subcategoria'].queryset = Subcategoria.objects.none()

            if self['fabricante'].data:
                self.helper.layout[0][18].css_class += ' hidden'

            if self['distribuidor'].data:
                self.helper.layout[0][20].css_class += ' hidden'
        elif self.instance.pk:
            if not self.instance.ano_vencimiento:
                self.fields['no_aplica_vencimiento'].initial = True
            self.fields['areas'].initial = [area.pk for area in self.instance.areas]
            if self.instance.tipo:
                categoria = self.instance.tipo
                self.fields['grupo'].initial = categoria.grupo
                self.fields['tipo'].queryset = Categoria.objects.filter(grupo=categoria.grupo)
                self.fields['tipo'].initial = categoria
                self.fields['subcategoria'].queryset = Subcategoria.objects.filter(categoria=categoria)
            else:
                self.fields['subcategoria'].queryset = Subcategoria.objects.none()
                self.fields['tipo'].queryset = Categoria.objects.none()

            if self.instance.fabricante:
                self.helper.layout[0][18].css_class += ' hidden'

            if self.instance.distribuidor:
                self.helper.layout[0][20].css_class += ' hidden'
        else:
            self.fields['subcategoria'].queryset = Subcategoria.objects.none()
            self.fields['tipo'].queryset = Categoria.objects.none()

    def clean(self):
        cleaned_data = super(MuestraAlimentoForm, self).clean()
        motivo_analisis = cleaned_data['motivo_analisis']
        nuevo_motivo = cleaned_data['nuevo_motivo_analisis']

        if not motivo_analisis and not nuevo_motivo and self.confirmar:
            self.add_error('nuevo_motivo_analisis', 'Este campo es obligatorio.')

        fabricante = cleaned_data['fabricante']
        nuevo_fabricante = cleaned_data['nuevo_fabricante']

        if not fabricante and not nuevo_fabricante and self.confirmar:
            self.add_error('nuevo_fabricante', 'Este campo es obligatorio.')

        distribuidor = cleaned_data['distribuidor']
        nuevo_distribuidor = cleaned_data['nuevo_distribuidor']

        if not distribuidor and not nuevo_distribuidor and self.confirmar:
            self.add_error('nuevo_distribuidor', 'Este campo es obligatorio.')

        unidad_muestra = cleaned_data.get('unidad_muestra', None)

        if not unidad_muestra and self.confirmar:
            self.add_error('unidad_muestra', 'Este campo es obligatorio.')

        contenido_neto = cleaned_data.get('contenido_neto', None)

        if not contenido_neto and self.confirmar:
            self.add_error('contenido_neto', 'Este campo es obligatorio.')

        unidad_contramuestra = cleaned_data['unidad_contramuestra']

        if unidad_contramuestra is None and self.confirmar:
            self.add_error('unidad_contramuestra', 'Este campo es obligatorio.')

        grupo = cleaned_data['grupo']

        if grupo is None and self.confirmar:
            self.add_error('grupo', 'Este campo es obligatorio.')

        tipo = cleaned_data['tipo']

        if tipo is None and self.confirmar:
            self.add_error('tipo', 'Este campo es obligatorio.')

        subcategoria = cleaned_data['subcategoria']

        if subcategoria is None and self.confirmar:
            self.add_error('subcategoria', 'Este campo es obligatorio.')

        descripcion = cleaned_data['descripcion']

        if descripcion is "" and self.confirmar:
            self.add_error('descripcion', 'Este campo es obligatorio.')

        registro_sanitario = cleaned_data['registro_sanitario']

        if registro_sanitario is "" and self.confirmar:
            self.add_error('registro_sanitario', 'Este campo es obligatorio.')

        lote = cleaned_data['lote']

        if lote is "" and self.confirmar:
            self.add_error('lote', 'Este campo es obligatorio.')

        ano_vencimiento = cleaned_data['ano_vencimiento']
        no_aplica_vencimiento = cleaned_data.get('no_aplica_vencimiento', False)

        if ano_vencimiento is None and self.confirmar and not no_aplica_vencimiento:
            self.add_error('ano_vencimiento', 'Este campo es obligatorio.')

        propietario = cleaned_data['propietario']

        if propietario is "" and self.confirmar:
            self.add_error('propietario', 'Este campo es obligatorio.')

        importador = cleaned_data['importador']

        if importador is "" and self.confirmar:
            self.add_error('importador', 'Este campo es obligatorio.')

        direccion_importador = cleaned_data['direccion_importador']

        if direccion_importador is "" and self.confirmar:
            self.add_error('direccion_importador', 'Este campo es obligatorio.')

        responsable_entrega = cleaned_data['responsable_entrega']

        if responsable_entrega is "" and self.confirmar:
            self.add_error('responsable_entrega', 'Este campo es obligatorio.')

        temperatura = cleaned_data['temperatura']

        if temperatura is "" and self.confirmar:
            self.add_error('temperatura', 'Este campo es obligatorio.')

        temperatura_recoleccion = cleaned_data['temperatura_recoleccion']

        if temperatura_recoleccion is "" and self.confirmar:
            self.add_error('temperatura_recoleccion', 'Este campo es obligatorio.')

        areas = cleaned_data['areas']

        if not areas and self.confirmar:
            self.add_error('areas', 'Este campo es obligatorio.')

        if subcategoria is not None and areas:
            if Prueba.objects.areas(areas).activos().count() == 0:
                self.add_error('areas', 'No se encontraron pruebas en las areas escogidas.')

    def save(self, commit=True):
        if self.cleaned_data['motivo_analisis'] is None:
            if self.cleaned_data['nuevo_motivo_analisis']:
                nueva_motivo = MotivoAnalisis()
                nueva_motivo.nombre = self.cleaned_data['nuevo_motivo_analisis']
                nueva_motivo.save()
                self.instance.motivo_analisis = nueva_motivo

        if self.cleaned_data['fabricante'] is None:
            if self.cleaned_data['nuevo_fabricante']:
                nuevo_fabricante = Fabricante()
                nuevo_fabricante.nombre = self.cleaned_data['nuevo_fabricante']
                nuevo_fabricante.modificado_por = self.usuario
                nuevo_fabricante.save()
                self.instance.fabricante = nuevo_fabricante

        if self.cleaned_data['distribuidor'] is None:
            if self.cleaned_data['nuevo_distribuidor']:
                nuevo_distribuidor = Distribuidor()
                nuevo_distribuidor.nombre = self.cleaned_data['nuevo_distribuidor']
                nuevo_distribuidor.modificado_por = self.usuario
                nuevo_distribuidor.save()
                self.instance.distribuidor = nuevo_distribuidor

        self.instance.registro_recepcion = self.ingreso
        self.instance.informacion_general = self.general

        muestra = super(MuestraAlimentoForm, self).save(commit)

        if self.cleaned_data['areas'] and self.cleaned_data['subcategoria']:
            muestra.pruebas.clear()
            for area in self.cleaned_data['areas']:
                for prueba in area.pruebas.activos():
                    PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)

        return muestra


class MuestraDecretoForm(forms.ModelForm):
    """Formulario para añadirle un decreto a una muestra de alimentos."""

    area = forms.ModelChoiceField(queryset=Area.objects.filter(programa=Programa.objects.alimentos()))

    class Meta:
        model = Alimento
        fields = ('decretos', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['decretos'].widget.attrs.update({'class': 'form-control'})
        self.fields['decretos'].required = True

    def save(self, commit=True):
        muestra = self.instance
        decreto = self.cleaned_data.get('decretos')[0]
        muestra.decretos.add(decreto)
        area = self.cleaned_data.get('area')
        muestra.pruebasrealizadas_set.filter(prueba__area=area).delete()

        for prueba in decreto.pruebas.filter(area=area).activos():
            PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)
        return muestra
