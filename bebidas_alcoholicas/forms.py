from django import forms

from .models import (
    BebidaAlcoholica, Grupo, Producto, TipoEnvase,
    MotivoAnalisis, InformacionBebidaAlcoholica, Institucion,
    Decreto
)
from trazabilidad.models import Area, Departamento, Municipio, Poblado, Programa, PruebasRealizadas

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field


class MuestraBebidaAlcoholicaFormSet(forms.BaseModelFormSet):
    """ModelFormSet para las muestras de bebidas alcoholicas."""

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        self.nueva = kwargs.pop('nueva', None)
        super().__init__(*args, **kwargs)

        for form in self:
            form.usuario = self.usuario

    def save(self, ingreso=None, general=None):
        for form in self:
            form.ingreso = ingreso
            form.general = general

        muestras = super().save()

        if not muestras and self.nueva:
            muestra = BebidaAlcoholica()
            muestra.registro_recepcion = ingreso
            muestra.informacion_general = general
            muestra.save()

            muestras.append(muestra)

        return muestras


class MuestraBebidaAlcoholicaForm(forms.ModelForm):
    """Formulario para el manejo de las muestras de alimento."""

    error_css_class = 'has-error'

    CHOICES = (
        (True, 'Si'),
        (False, 'No'),
    )
    no_aplica_vencimiento = forms.ChoiceField(choices=CHOICES, widget=forms.CheckboxInput)
    grupo = forms.ModelChoiceField(queryset=Grupo.objects.activos(), required=False, label='Grupo de bebida alcohólica')
    nuevo_motivo_analisis = forms.CharField(max_length=100, required=False)
    areas = forms.ModelMultipleChoiceField(
        queryset=Area.objects.filter(
            programa=Programa.objects.bebidas_alcoholicas(),
            oculto=False
        ),
        widget=forms.CheckboxSelectMultiple, required=False, label='Analisis solicitado'
    )

    def __init__(self, *args, **kwargs):
        super(MuestraBebidaAlcoholicaForm, self).__init__(*args, **kwargs)
        self.fields['temp_ingreso'].required = True
        self.fields['numero_lote'].label = 'Lote'
        self.fields['temperatura'].label = 'Temperatura de Ingreso'
        # self.fields['tipo'].label = 'Sub-Categoria'
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.render_hidden_fields = True
        self.helper.layout = Layout(
            Div(
                Div('temp_ingreso', css_class='col-md-3'),
                Div('temperatura', css_class='col-md-3'),
                Div(
                    Field('grupo', css_class='select-grupo'),
                    css_class='col-md-3 grupo'
                ),
                Div(
                    Field('producto', css_class='select-producto'),
                    css_class='col-md-3 producto'
                ),
                Div('registro_sanitario', css_class='col-md-4'),
                Div('numero_lote', css_class='col-md-4'),
                Div('grado', css_class='col-md-4'),
                Div(
                    Field('ano_vencimiento', css_class='input-año'),
                    css_class='col-md-2 f-ano'
                ),
                Div(
                    Field('mes_vencimiento', css_class='input-mes'),
                    css_class='col-md-2 f-mes'
                ),
                Div(
                    Field('dia_vencimiento', css_class='input-dia'),
                    css_class='col-md-2 f-dia'
                ),
                Div('no_aplica_vencimiento', css_class='col-md-2 no-aplica'),
                Div('fabricante', css_class='col-md-4'),
                Div('direccion_fabricante', css_class='col-md-4'),
                Div('contenido', css_class='col-md-4'),
                Div(
                    Field('tipo_envase', css_class='select-tipo'),
                    css_class='col-md-4 tipo'
                ),
                Div('aspecto_externo', css_class='col-md-4'),
                Div('aspecto_interno', css_class='col-md-4'),
                Div('hermeticidad', css_class='col-md-4'),
                Div(
                    Field('motivo_analisis', css_class='select-motivo-analisis'),
                    css_class='col-md-4 motivo-analisis'
                ),
                Div('nuevo_motivo_analisis', css_class='col-md-3 nuevo-motivo-analisis'),
                Div('areas', css_class='col-md-4'),
                css_class='row'
            )
        )

        self.confirmar = True if 'confirmado' in self.data else False

        self.fields['motivo_analisis'].empty_label = 'Nuevo motivo de analisis'
        # self.fields['tipo_envase'].empty_label = 'Nuevo tipo de envase'
        # self.fields['producto'].empty_label = 'Nuevo producto'

        if self.is_bound:
            valor_grupo = self['grupo'].data
            if valor_grupo:
                self.fields['producto'].queryset = Producto.objects.filter(grupo_id=valor_grupo)
            else:
                self.fields['producto'].queryset = Producto.objects.none()

            if self['motivo_analisis'].data:
                self.helper.layout[0][18].css_class += ' hidden'

            # if self['distribuidor'].data:
            #     self.helper.layout[0][17].css_class += ' hidden'
        elif self.instance.pk:
            self.fields['areas'].initial = [area.pk for area in self.instance.areas]
            if self.instance.producto:
                # self.fields['grupo'].queryset = Grupo.objects.filter(grupo=categoria.grupo)
                self.fields['grupo'].initial = self.instance.producto.grupo

            if self.instance.motivo_analisis:
                self.helper.layout[0][18].css_class += ' hidden'

            # if self.instance.fabricante:
            #     self.helper.layout[0][15].css_class += ' hidden'

            # if self.instance.distribuidor:
            #     self.helper.layout[0][17].css_class += ' hidden'
        else:
            self.fields['producto'].queryset = Producto.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        motivo_analisis = cleaned_data['motivo_analisis']
        nuevo_motivo = cleaned_data['nuevo_motivo_analisis']

        if not motivo_analisis and not nuevo_motivo and self.confirmar:
            self.add_error('nuevo_motivo_analisis', 'Este campo es obligatorio.')

        grado = cleaned_data['grado']

        if not grado and self.confirmar:
            self.add_error('grado', 'Este campo es obligatorio.')

        fabricante = cleaned_data['fabricante']

        if not fabricante and self.confirmar:
            self.add_error('fabricante', 'Este campo es obligatorio.')

        direccion_fabricante = cleaned_data['direccion_fabricante']

        if not direccion_fabricante and self.confirmar:
            self.add_error('direccion_fabricante', 'Este campo es obligatorio.')

        producto = cleaned_data.get('producto', None)

        if not producto and self.confirmar:
            self.add_error('producto', 'Este campo es obligatorio.')

        contenido = cleaned_data.get('contenido', None)

        if not contenido and self.confirmar:
            self.add_error('contenido', 'Este campo es obligatorio.')

        grupo = cleaned_data['grupo']

        if grupo is None and self.confirmar:
            self.add_error('grupo', 'Este campo es obligatorio.')

        tipo = cleaned_data['tipo_envase']

        if tipo is None and self.confirmar:
            self.add_error('tipo_envase', 'Este campo es obligatorio.')

        registro_sanitario = cleaned_data['registro_sanitario']

        if registro_sanitario is "" and self.confirmar:
            self.add_error('registro_sanitario', 'Este campo es obligatorio.')

        numero_lote = cleaned_data['numero_lote']

        if numero_lote is "" and self.confirmar:
            self.add_error('numero_lote', 'Este campo es obligatorio.')

        ano_vencimiento = cleaned_data.get('ano_vencimiento', None) or None
        no_aplica = cleaned_data['no_aplica_vencimiento']
        operators = {'True': True, 'False': False}

        if not operators[no_aplica] and self.confirmar:
            if ano_vencimiento is None:
                self.add_error('ano_vencimiento', 'Este campo es obligatorio.')

        temperatura = cleaned_data['temperatura']

        if temperatura is "" and self.confirmar:
            self.add_error('temperatura', 'Este campo es obligatorio.')

        areas = cleaned_data['areas']

        if not areas and self.confirmar:
            self.add_error('areas', 'Este campo es obligatorio.')

        externo = cleaned_data['aspecto_externo']

        if externo is None and self.confirmar:
            self.add_error('aspecto_externo', 'Este campo es obligatorio.')

        interno = cleaned_data['aspecto_interno']

        if interno is None and self.confirmar:
            self.add_error('aspecto_interno', 'Este campo es obligatorio.')

        hermeticidad = cleaned_data['hermeticidad']

        if hermeticidad is None and self.confirmar:
            self.add_error('hermeticidad', 'Este campo es obligatorio.')

    def save(self, commit=True):
        if self.cleaned_data['motivo_analisis'] is None:
            if self.cleaned_data['nuevo_motivo_analisis']:
                nueva_motivo = MotivoAnalisis()
                nueva_motivo.motivo = self.cleaned_data['nuevo_motivo_analisis']
                nueva_motivo.modificado_por = self.usuario
                nueva_motivo.save()
                self.instance.motivo_analisis = nueva_motivo

        self.instance.registro_recepcion = self.ingreso
        self.instance.informacion_general = self.general

        muestra = super().save(commit)

        if self.cleaned_data['areas']:
            muestra.pruebas.clear()
            for area in self.cleaned_data['areas']:
                for prueba in area.pruebas.activos():
                    PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)

        return muestra

    class Meta:
        model = BebidaAlcoholica
        fields = [
            'temperatura', 'producto', 'registro_sanitario',
            'numero_lote', 'ano_vencimiento', 'mes_vencimiento',
            'dia_vencimiento', 'no_aplica_vencimiento', 'fabricante',
            'direccion_fabricante', 'grado', 'contenido',
            'tipo_envase', 'aspecto_externo', 'aspecto_interno',
            'hermeticidad', 'motivo_analisis', 'temp_ingreso'
        ]


class InformacionBebidaAlcoholicaForm(forms.ModelForm):
    """Formulario para el manejo de la información general que tienen las muestras de bebidas alcoholicas."""

    error_css_class = 'has-error'

    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.none())
    nueva_institucion = forms.CharField(max_length=255, required=False)
    nueva_direccion_institucion = forms.CharField(max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        self.fields['responsable_entrega'].widget.attrs.update({'class': 'form-control'})
        self.fields['institucion'].widget.attrs.update({'class': 'form-control'})
        self.fields['cargo'].widget.attrs.update({'class': 'form-control'})
        self.fields['numero_caso'].widget.attrs.update({'class': 'form-control'})
        self.fields['numero_oficio'].widget.attrs.update({'class': 'form-control'})
        self.fields['poblado'].widget.attrs.update({'class': 'form-control'})
        self.fields['sitio_toma'].widget.attrs.update({'class': 'form-control'})
        self.fields['propietario'].widget.attrs.update({'class': 'form-control'})
        self.fields['direccion'].widget.attrs.update({'class': 'form-control'})
        self.fields['fecha'].widget.attrs.update({'class': 'form-control'})
        self.fields['departamento'].widget.attrs.update({'class': 'form-control'})
        self.fields['municipio'].widget.attrs.update({'class': 'form-control'})
        self.fields['nueva_institucion'].widget.attrs.update({'class': 'form-control'})
        self.fields['nueva_direccion_institucion'].widget.attrs.update({'class': 'form-control'})

        self.fields['institucion'].empty_label = 'Nueva institución'

        self.confirmar = True if 'confirmado' in self.data else False

        if self.is_bound:
            if self['institucion'].data:
                self.fields['nueva_institucion'].widget.attrs.update({'class': 'form-control', 'readonly': 'true'})
                self.fields['nueva_direccion_institucion'].widget.attrs.update({'class': 'form-control', 'readonly': 'true'})

            if self.data.get('general-institucion', None) is not None:
                self.fields['institucion'].required = False
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

            if self.instance.institucion:
                self.fields['nueva_institucion'].widget.attrs.update({'class': 'form-control', 'readonly': 'true'})
                self.fields['nueva_direccion_institucion'].widget.attrs.update({'class': 'form-control', 'readonly': 'true'})

            departamento = self.instance.poblado.municipio.departamento
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=departamento)
            self.fields['poblado'].queryset = Poblado.objects.filter(municipio=self.instance.poblado.municipio)

            self.fields['municipio'].initial = self.instance.poblado.municipio
            self.fields['departamento'].initial = self.instance.poblado.municipio.departamento
        else:
            self.fields['poblado'].queryset = Poblado.objects.none()

    def clean(self):
        cleaned_data = super().clean()

        institucion = cleaned_data['institucion']
        nueva_institucion = cleaned_data['nueva_institucion']

        if not institucion and not nueva_institucion and self.confirmar:
            self.add_error('nueva_institucion', 'Este campo es obligatorio.')
            self.add_error('nueva_direccion_institucion', 'Este campo es obligatorio.')

        poblado = cleaned_data['poblado']

        if not poblado and self.confirmar:
            self.add_error('poblado', 'Este campo es obligatorio.')

        sitio_toma = cleaned_data['sitio_toma']

        if not sitio_toma and self.confirmar:
            self.add_error('sitio_toma', 'Este campo es obligatorio.')

        propietario = cleaned_data['propietario']

        if not propietario and self.confirmar:
            self.add_error('propietario', 'Este campo es obligatorio.')

        direccion = cleaned_data['direccion']

        if not direccion and self.confirmar:
            self.add_error('direccion', 'Este campo es obligatorio.')

        fecha = cleaned_data['fecha']

        if not fecha and self.confirmar:
            self.add_error('fecha', 'Este campo es obligatorio.')

    def save(self, commit=True):
        if self.cleaned_data['institucion'] is None:
            if self.cleaned_data['nueva_institucion']:
                nueva_institucion = Institucion()
                nueva_institucion.nombre = self.cleaned_data['nueva_institucion']
                nueva_institucion.direccion = self.cleaned_data['nueva_direccion_institucion'] or ''
                nueva_institucion.modificado_por = self.usuario
                nueva_institucion.save()
                self.instance.institucion = nueva_institucion
        return super().save(commit=commit)

    class Meta:
        model = InformacionBebidaAlcoholica
        fields = [
            'institucion', 'responsable_entrega', 'cargo',
            'numero_caso', 'numero_oficio', 'poblado',
            'sitio_toma', 'propietario', 'direccion',
            'fecha'
        ]


class MuestraDecretoForm(forms.ModelForm):
    """Formulario para añadirle un decreto a una muestra de bebida alcoholica."""

    class Meta:
        model = BebidaAlcoholica
        fields = ('decreto', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['decreto'].widget.attrs.update({'class': 'form-control'})
        self.fields['decreto'].required = True

        if self.instance.pk:
            self.fields['decreto'].queryset = Decreto.objects.filter(grupo_id=self.instance.producto.grupo_id)

    def save(self, commit=True):
        muestra = super().save(commit)
        # decreto = self.cleaned_data.get('decreto')
        muestra.pruebas.clear()
        for prueba in muestra.decreto.pruebas.activos():
            PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)
        # se agregan las pruebas de el area oculta, si falla, es que no se ha creado el area oculta
        q = Area.objects.get(oculto=True, programa_id=Programa.objects.bebidas_alcoholicas().id)
        for prueba in q.pruebas.activos():
            p = PruebasRealizadas.objects.create(muestra=muestra, prueba=prueba)
            p.actualizar_estado()
            p.actualizar_estado()

        return muestra

