import operator
from django.db.models import Q, Exists, OuterRef
from import_export.fields import Field
from cie10_django.models import CIE10
from import_export import resources
from django.utils import timezone
from contextlib import suppress
from functools import reduce
from django import forms

from trazabilidad.models import Departamento, Municipio, TipoMuestra, Prueba, Recepcion, Reporte, Muestra, PruebasRealizadas
from trazabilidad import models as trazabilidad_models
from trazabilidad import forms as trazabilidad_forms
from common import forms as common_f
from trazabilidad import enums
from . import services as s
from . import models


class PacienteForm(common_f.RequireOnConfirmValidatableMixin, trazabilidad_forms.PacienteForm):

    REQUIRED_ON_CONFIRM = [
        'nombre',
        'apellido',
    ]

    class Meta(trazabilidad_forms.PacienteForm.Meta):
        fields = ['email', 'fecha_nacimiento'] + trazabilidad_forms.PacienteForm.Meta.fields
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confirming = 'confirmado' in self.data

        if 'paciente-sin_identificacion' in self.data:
            self.fields['identificacion'].required = False
            self.fields['tipo_identificacion'].required = False

        if self.instance.id and self.instance.tipo_identificacion == 'NN':
            self.fields['sin_identificacion'].initial = True
    
    def save(self, user, commit=True):
        self.instance.modificado_por = user

        if self.cleaned_data.get('sin_identificacion', False):
            self.instance.identificacion = '-------'
            self.instance.tipo_identificacion = 'NN'

        return super().save(commit)

class InfoPacienteForm(forms.ModelForm):

    departamento_ocurrencia = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False)
    grupos_poblacionales = forms.MultipleChoiceField(
        required=False,
        choices=models.GRUPOS_POBLACIONALES,
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = models.InfoPaciente
        fields = [
            'eapb',
            'estrato',
            'telefono',
            'ocupacion',
            'vereda_zona',
            'tipificacion',
            'tipo_regimen',
            'grupo_etnico',
            'nacionalidad',
            'area_ocurrencia',
            'pais_ocurrencia',
            'lugar_ocurrencia',
            'barrio_ocurrencia',
            'semanas_gestacion',
            'pertenencia_etnica',
            'municipio_ocurrencia',
            'grupos_poblacionales',
            'localidad_ocurrencia',
        ]
        widgets = {
            'telefono': forms.NumberInput()
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['municipio_ocurrencia'].queryset = Municipio.objects.none()
        self.fields['nacionalidad'].initial = 'CO'

        if self.is_bound:
            with suppress(Exception):
                id_departamento = int(self.data.get('info_paciente-departamento_ocurrencia'))
                self.fields['municipio_ocurrencia'].queryset = Municipio.objects.filter(departamento=id_departamento)
        elif self.instance.id:
            if self.instance.municipio_ocurrencia_id:
                departamento = self.instance.municipio_ocurrencia.departamento_id
                self.fields['municipio_ocurrencia'].queryset = Municipio.objects.filter(departamento=departamento)
                self.fields['departamento_ocurrencia'].initial = departamento

    def clean(self):
        cleaned_data = super().clean()

        pert_etnica = cleaned_data.get('pertenencia_etnica', None)
        if pert_etnica and pert_etnica == models.INDIGENA:
            if not cleaned_data.get('grupo_etnico', None):
                self.add_error('grupo_etnico', 'Campo requerido')
        
        grupo_pob = cleaned_data.get('grupos_poblacionales', None)
        if grupo_pob and grupo_pob == models.SI:
            if not cleaned_data.get('semanas_gestacion', None):
                self.add_error('semanas_gestacion', 'Campo requerido')

        return cleaned_data

    def save(self, user, paciente, commit=True):
        self.instance.modificado_por = user
        self.instance.paciente = paciente
        return super().save(commit)

class InfoGeneralMixin(forms.ModelForm):

    REQUIRED_ON_CONFIRM = [
        'upgd',
        'municipio_upgd',
        'departamento_upgd',
    ]

    departamento_upgd = forms.ModelChoiceField(
        required=False,
        label='Departamento UPGD',
        queryset=Departamento.objects.all(),
    )

    class Meta:
        fields = [
            'upgd',
            'evento',
            'municipio_upgd',
            'fecha_notificacion',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['municipio_upgd'].queryset = Municipio.objects.none()
        self.fields['municipio_upgd'].label = 'Municipio UPGD'
        self.fields['upgd'].queryset = models.Upgd.objects.none()
        self.fields['upgd'].label = 'UPGD'

        if self.is_bound:
            with suppress(Exception):
                id_departamento = int(self.data.get('general-departamento_upgd'))
                self.fields['municipio_upgd'].queryset = Municipio.objects.filter(departamento=id_departamento)
            
            with suppress(Exception):
                upgd = int(self.data.get('general-upgd'))
                self.fields['upgd'].queryset = models.Upgd.objects.filter(id=upgd)
        elif self.instance.id:
            if self.instance.municipio_upgd_id:
                departamento = self.instance.municipio_upgd.departamento_id
                self.fields['municipio_upgd'].queryset = Municipio.objects.filter(departamento=departamento)
                self.fields['departamento_upgd'].initial = departamento

            self.fields['upgd'].queryset = models.Upgd.objects.filter(id=self.instance.upgd_id)

class NotificacionMixin(forms.ModelForm):
    
    REQUIRED_ON_CONFIRM = [
        'pais_residencia',
        'municipio_residencia',
        'departamento_residencia',
    ]

    departamento_residencia = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False)

    class Meta:
        fields = [
            'fuente',
            'telefono',
            'direccion',
            'causa_muerte',
            'hospitalizado',
            'fecha_consulta',
            'pais_residencia',
            'condicion_final',
            'fecha_defuncion',
            'municipio_residencia',
            'certificado_defuncion',
            'fecha_hospitalizacion',
            'fecha_inicio_sintomas',
            'profesional_diligenciante',
            'clasificacion_inicial_caso',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['causa_muerte'].queryset = CIE10.objects.none()
        self.fields['municipio_residencia'].queryset = Municipio.objects.none()
        self.fields['causa_muerte'].label_from_instance = lambda o: '{code} - {des}'.format(code=o.code, des=o.description)
        self.fields['telefono'].widget = forms.NumberInput()

        if self.is_bound:
            with suppress(Exception):
                id_departamento = int(self.data.get('general-departamento_residencia'))
                self.fields['municipio_residencia'].queryset = Municipio.objects.filter(departamento=id_departamento)
            
            with suppress(Exception):
                causa_muerte = int(self.data.get('general-causa_muerte'))
                self.fields['causa_muerte'].queryset = CIE10.objects.filter(id=causa_muerte)
        elif self.instance.id:
            if self.instance.municipio_residencia_id:
                departamento = self.instance.municipio_residencia.departamento_id
                self.fields['municipio_residencia'].queryset = Municipio.objects.filter(departamento=departamento)
                self.fields['departamento_residencia'].initial = departamento

            if self.instance.causa_muerte_id:
                self.fields['causa_muerte'].queryset = CIE10.objects.filter(id=self.instance.causa_muerte_id)

    def clean(self):
        cleaned_data = super().clean()

        hosp = cleaned_data.get('hospitalizado', None)
        if hosp and hosp == models.SI and not cleaned_data.get('fecha_hospitalizacion', None):
            self.add_error('fecha_hospitalizacion', 'Campo requerido')
        
        con_final = cleaned_data.get('condicion_final', None)
        if con_final and con_final == models.MUERTO:
            if not cleaned_data.get('fecha_defuncion', None):
                self.add_error('fecha_defuncion', 'Campo requerido')
            
            if not cleaned_data.get('certificado_defuncion', None):
                self.add_error('certificado_defuncion', 'Campo requerido')
            
            if not cleaned_data.get('causa_muerte', None):
                self.add_error('causa_muerte', 'Campo requerido')

        return cleaned_data

class EnteMixin(forms.ModelForm):

    class Meta:
        fields = ['fecha_ajuste', 'clasificacion_final_caso']

INFO_FIELDS_346 = [
    'sintomas',
    'viaje_nacional',
    'trabajador_salud',
    'radiografia_torax',
    'viaje_internacional',
    'influenza_estacional',
    'viajo_area_con_virus',
    'antecedentes_clinicos',
    'pais_viaje_iternacional',
    'municipio_viaje_nacional',
    'contacto_caso_confirmado',
    'dosis_influenza_estacional',
    'otros_antecedentes_clinicos',
    'antibiotico_ultimas_semanas',
]

class InfoGeneral346Form(InfoGeneralMixin, NotificacionMixin, EnteMixin, common_f.RequireOnConfirmValidatableMixin, forms.ModelForm):

    REQUIRED_ON_CONFIRM = InfoGeneralMixin.REQUIRED_ON_CONFIRM + NotificacionMixin.REQUIRED_ON_CONFIRM

    departamento_viaje_nacional = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False)
    sintomas = forms.MultipleChoiceField(
        required=False,
        choices=models.OPCIONES_SINTOMAS,
        widget=forms.CheckboxSelectMultiple(),
    )
    antecedentes_clinicos = forms.MultipleChoiceField(
        required=False,
        choices=models.ANTECEDENTES_CLINICOS,
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = models.InfoGeneral346
        fields = INFO_FIELDS_346 + InfoGeneralMixin.Meta.fields + NotificacionMixin.Meta.fields + EnteMixin.Meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confirming = 'confirmado' in self.data
        self.fields['municipio_viaje_nacional'].queryset = Municipio.objects.none()
        self.fields['municipio_viaje_nacional'].label = 'Municipio viaje nacional'
        self.fields['pais_viaje_iternacional'].label = 'Pais viaje internacional'
        
        if self.is_bound:
            with suppress(Exception):
                id_departamento = int(self.data.get('general-departamento_viaje_nacional'))
                self.fields['municipio_viaje_nacional'].queryset = Municipio.objects.filter(departamento=id_departamento)
        elif self.instance.id:
            if self.instance.municipio_viaje_nacional_id:
                departamento = self.instance.municipio_viaje_nacional.departamento_id
                self.fields['municipio_viaje_nacional'].queryset = Municipio.objects.filter(departamento=departamento)
                self.fields['departamento_viaje_nacional'].initial = departamento

    def clean(self):
        cleaned_data = super().clean()

        viaje_nal = cleaned_data.get('viaje_nacional', None)
        if viaje_nal and viaje_nal == models.SI:
            if not cleaned_data.get('municipio_viaje_nacional', None):
                self.add_error('municipio_viaje_nacional', 'Campo requerido')
            
            if not cleaned_data.get('departamento_viaje_nacional', None):
                self.add_error('departamento_viaje_nacional', 'Campo requerido')
        
        viaje_intnal = cleaned_data.get('viaje_internacional', None)
        if viaje_intnal and viaje_intnal == models.SI:
            if not cleaned_data.get('pais_viaje_internacional', None):
                self.add_error('pais_viaje_internacional', 'Campo requerido')

        return cleaned_data

    def save(self, info_paciente, commit=True):
        self.instance.info_paciente = info_paciente
        return super().save(commit)

class Muestra346FormSet(forms.BaseModelFormSet):
    
    def save(self, user, ingreso, info, ingreso_nuevo=False):
        for form in self:
            form.user = user
            form.info = info
            form.ingreso = ingreso
        
        muestras = super().save()

        if not muestras and ingreso_nuevo:
            muestras.append(models.Muestra346.objects.create(registro_recepcion=ingreso, informacion_general=info))

        return muestras

class Muestra346Form(common_f.RequireOnConfirmValidatableMixin, forms.ModelForm):

    REQUIRED_ON_CONFIRM = [
        'pruebas',
        'fecha_toma',
        'tipo_muestra',
        'temp_ingreso',
    ]

    class Meta:
        model = models.Muestra346
        fields = [
            'fecha_toma',
            'tipo_muestra',
            'pruebas',
            'temp_ingreso',
        ]
        widgets = {
            'pruebas': forms.CheckboxSelectMultiple()
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confirming = 'confirmado' in self.data
        self.fields['tipo_muestra'].queryset = TipoMuestra.objects.by_programa(enums.ProgramaEnum.COVID19.value).activos()
        self.fields['pruebas'].queryset = Prueba.objects.programa_covid19()
        # self.fields['temp_ingreso'].required = True
        # self.fields['pruebas'].required = True
        self.fields['fecha_toma'].widget.attrs.update({'class': 'date-toma'})
    
    def save(self, commit=True):
        self.instance.informacion_general = self.info
        self.instance.registro_recepcion = self.ingreso
        return super().save(commit)

INFO_FIELDS_348 = [
    'seleccione_opciones',
    'viaje_nacional',
    'municipio_viaje_nacional',
    'viaje_internacional',
    'pais_viaje_iternacional',
    'caso_irag',
    'neumococo',
    'dosis_neumococo',
    'influenza_estacional',
    'dosis_influenza_estacional',
    'antecedentes_clinicos',
    'otros_antecedentes_clinicos',
    'radiografia_torax',
    'antibiotico_ultimas_semanas',
    'uso_antivirales',
    'fecha_antiviral',
    'servicio_hospitalizo',
    'fecha_ingreso_uci',
    'complicaciones',
]

class InfoGeneral348Form(InfoGeneralMixin, NotificacionMixin, EnteMixin, common_f.RequireOnConfirmValidatableMixin, forms.ModelForm):

    REQUIRED_ON_CONFIRM = InfoGeneralMixin.REQUIRED_ON_CONFIRM + NotificacionMixin.REQUIRED_ON_CONFIRM

    seleccione_opciones = forms.MultipleChoiceField(
        required=False,
        choices=models.SELECCIONE_OPCIONES,
        widget=forms.CheckboxSelectMultiple(),
    )

    departamento_viaje_nacional = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False)


    caso_irag = forms.MultipleChoiceField(
        required=False,
        choices=models.OPCIONES_IRAG,
        widget=forms.CheckboxSelectMultiple(),
    )

    antecedentes_clinicos = forms.MultipleChoiceField(
        required=False,
        choices=models.ANTECEDENTES_CLINICOS,
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = models.InfoGeneral348
        fields = INFO_FIELDS_348 + InfoGeneralMixin.Meta.fields + NotificacionMixin.Meta.fields + EnteMixin.Meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confirming = 'confirmado' in self.data
        self.fields['municipio_viaje_nacional'].queryset = Municipio.objects.none()
        self.fields['municipio_viaje_nacional'].label = 'Municipio viaje nacional'
        self.fields['pais_viaje_iternacional'].label = 'Pais viaje internacional'
        
        if self.is_bound:
            with suppress(Exception):
                id_departamento = int(self.data.get('general-departamento_viaje_nacional'))
                self.fields['municipio_viaje_nacional'].queryset = Municipio.objects.filter(departamento=id_departamento)
        elif self.instance.id:
            if self.instance.municipio_viaje_nacional_id:
                departamento = self.instance.municipio_viaje_nacional.departamento_id
                self.fields['municipio_viaje_nacional'].queryset = Municipio.objects.filter(departamento=departamento)
                self.fields['departamento_viaje_nacional'].initial = departamento

    def clean(self):
        cleaned_data = super().clean()

        viaje_nal = cleaned_data.get('viaje_nacional', None)
        if viaje_nal and viaje_nal == models.SI:
            if not cleaned_data.get('municipio_viaje_nacional', None):
                self.add_error('municipio_viaje_nacional', 'Campo requerido')
            
            if not cleaned_data.get('departamento_viaje_nacional', None):
                self.add_error('departamento_viaje_nacional', 'Campo requerido')
        
        viaje_intnal = cleaned_data.get('viaje_internacional', None)
        if viaje_intnal and viaje_intnal == models.SI:
            if not cleaned_data.get('pais_viaje_iternacional', None):
                self.add_error('pais_viaje_internacional', 'Campo requerido')

        return cleaned_data

    def save(self, info_paciente, commit=True):
        self.instance.info_paciente = info_paciente
        return super().save(commit)

class Muestra348FormSet(forms.BaseModelFormSet):
    
    def save(self, user, ingreso, info, ingreso_nuevo=False):
        for form in self:
            form.user = user
            form.info = info
            form.ingreso = ingreso
        
        muestras = super().save()

        if not muestras and ingreso_nuevo:
            muestras.append(models.Muestra348.objects.create(registro_recepcion=ingreso, informacion_general=info))

        return muestras

class Muestra348Form(common_f.RequireOnConfirmValidatableMixin, forms.ModelForm):

    REQUIRED_ON_CONFIRM = [
        'pruebas',
        'fecha_toma',
        'tipo_muestra',
        'temp_ingreso',
    ]

    class Meta:
        model = models.Muestra348
        fields = [
            'fecha_toma',
            'tipo_muestra',
            'pruebas',
            'temp_ingreso',
        ]
        widgets = {
            'pruebas': forms.CheckboxSelectMultiple()
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confirming = 'confirmado' in self.data
        self.fields['tipo_muestra'].queryset = TipoMuestra.objects.by_programa(enums.ProgramaEnum.COVID19.value).activos()
        self.fields['pruebas'].queryset = Prueba.objects.programa_covid19()
        # self.fields['temp_ingreso'].required = True
        # self.fields['pruebas'].required = True
        self.fields['fecha_toma'].widget.attrs.update({'class': 'date-toma'})
    
    def save(self, commit=True):
        self.instance.informacion_general = self.info
        self.instance.registro_recepcion = self.ingreso
        return super().save(commit)

class EnvioMasivoResultadosForm(trazabilidad_forms.RangoFechasForm):

    upgd = forms.ModelChoiceField(queryset=models.Upgd.objects.all(), required=False, label='UPGD')
    municipio_upgd = forms.ModelChoiceField(queryset=Municipio.objects.all(), required=False, label='Municipio UPGD')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_inicial'].label = 'Fecha inicial informe'
        self.fields['fecha_final'].label = 'Fecha final informe'
    
    def resultados(self):
        desde = self.cleaned_data.get('fecha_inicial')
        hasta = self.cleaned_data.get('fecha_final')
        ingresos = (
            trazabilidad_models.Ingreso.objects
                .confirmados()
                .by_programa_covid()
                .con_informe_aprobado()
                .by_fecha_informe(desde, hasta)
                .prefetch_related('muestras__informacion_general__upgd', 'muestras__informacion_general__info_paciente__paciente', 'muestras__informacion_general__municipio_upgd')
        )

        query = Q(instance_of=models.Muestra346) | Q(instance_of=models.Muestra348)        
        upgd = self.cleaned_data.get('upgd')
        if upgd:
            query = (
                query &
                (Q(Muestra346___informacion_general__upgd=upgd) | 
                Q(Muestra348___informacion_general__upgd=upgd))
            )
        
        municipio_upgd = self.cleaned_data.get('municipio_upgd')
        if municipio_upgd:
            query = (
                query &
                (Q(Muestra346___informacion_general__municipio_upgd=municipio_upgd) | 
                Q(Muestra348___informacion_general__municipio_upgd=municipio_upgd))
            )

        return ingresos.filter(muestras__in=Muestra.objects.filter(query)).distinct()

class ConsultaResultadosForm(trazabilidad_forms.RangoFechasForm):

    nombres = forms.CharField(label='Nombres paciente', required=False)
    identificacion = forms.IntegerField(label='Identificación paciente', required=False)
    upgd = forms.ModelChoiceField(queryset=models.Upgd.objects.all(), required=False, label='UPGD')
    municipio_upgd = forms.ModelChoiceField(queryset=Municipio.objects.all(), required=False, label='Municipio UPGD')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_inicial'].label = 'Fecha inicial recepción'
        self.fields['fecha_final'].label = 'Fecha final recepción'
    
    def resultados(self):
        desde = self.cleaned_data.get('fecha_inicial')
        hasta = self.cleaned_data.get('fecha_final')
        ingresos = (
            Recepcion.objects
                .by_programa_covid()
                .by_fecha_recepcion(desde, hasta)
                .prefetch_related('muestras__informacion_general__upgd', 'muestras__informacion_general__info_paciente__paciente')
        )

        query = Q(instance_of=models.Muestra346) | Q(instance_of=models.Muestra348)        
        upgd = self.cleaned_data.get('upgd')
        if upgd:
            query = (
                query &
                (Q(Muestra346___informacion_general__upgd=upgd) | 
                Q(Muestra348___informacion_general__upgd=upgd))
            )
        
        municipio_upgd = self.cleaned_data.get('municipio_upgd')
        if municipio_upgd:
            query = (
                query &
                (Q(Muestra346___informacion_general__municipio_upgd=municipio_upgd) | 
                Q(Muestra348___informacion_general__municipio_upgd=municipio_upgd))
            )
        
        identificacion = self.cleaned_data.get('identificacion')
        if identificacion:
            query = (
                query &
                (Q(Muestra346___informacion_general__info_paciente__paciente__identificacion__exact=identificacion) |
                Q(Muestra348___informacion_general__info_paciente__paciente__identificacion__exact=identificacion))
            )
        
        nombres = self.cleaned_data.get('nombres')
        if nombres:
            query = (
                query &
                (self.paciente_search(nombres, 'Muestra346') | self.paciente_search(nombres, 'Muestra348'))
            )

        return ingresos.filter(muestras__in=Muestra.objects.filter(query)).distinct()
    
    def paciente_search(self, term, muestra):
        words = term.split()
        orm_lookups = ['{}___informacion_general__info_paciente__paciente__{}__icontains'.format(muestra, search_field) for search_field in ['nombre', 'apellido']]

        conditions = []
        for word in words:
            queries = [Q(**{orm_lookup: word}) for orm_lookup in orm_lookups]
            conditions.append(reduce(operator.or_, queries))
        
        return reduce(operator.and_, conditions)

class ExportacionExcelFichaForm(trazabilidad_forms.RangoFechasForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_inicial'].label = 'Fecha inicial recepción'
        self.fields['fecha_final'].label = 'Fecha final recepción'
    
    def data_exportar(self):
        desde = self.cleaned_data.get('fecha_inicial')
        hasta = self.cleaned_data.get('fecha_final')

        ingresos = (
            Recepcion.objects
                .by_programa_covid()
                .by_fecha_recepcion(desde, hasta)
        )

        # TODO intentar sacar los ingresos y transformarlos en lista de muestras
        query = PruebasRealizadas.objects.filter(muestra=OuterRef('pk')).positivos()
        dataset = MuestraCovidResource().export(
            Muestra.objects
                .non_polymorphic()
                .filter(registro_recepcion__in=ingresos)
                .annotate(is_positivo=Exists(query))
                .select_related(
                    'registro_recepcion',
                    # 'muestra346__tipo_muestra',
                    # 'muestra346__informacion_general__upgd',
                    # 'muestra346__informacion_general__info_paciente__paciente',
                    # 'muestra346__informacion_general__info_paciente__ocupacion',
                    # 'muestra346__informacion_general__municipio_residencia__departamento',
                    # 'muestra348__tipo_muestra',
                    # 'muestra348__informacion_general__upgd',
                    # 'muestra348__informacion_general__info_paciente__paciente',
                    # 'muestra348__informacion_general__info_paciente__ocupacion',
                    # 'muestra348__informacion_general__municipio_residencia__departamento',
                )
                .order_by('-registro_recepcion__indice_radicado')
        )
        return dataset, f'{desde} - {hasta}'

class MuestraCovidResource(resources.Resource):

    SIN_DATOS = 'Sin datos'

    ficha = Field()
    radicado = Field(attribute='registro_recepcion__radicado')
    fecha_recepcion = Field()
    estado = Field(attribute='registro_recepcion__estado_resultado__value')
    resultado = Field()
    tipo_muestra = Field()
    fecha_toma = Field(attribute='mues__fecha_toma')
    temperatura_procesamiento = Field(attribute='temp_procesamiento')
    codigo_analista = Field()
    codigo_responsable_tecnico = Field()
    codigo_digitador = Field()
    fecha_procesamiento = Field()
    hora_procesamiento = Field()
    fecha_informe = Field()
    metodo_utilizado = Field()
    municipio_upgd = Field(attribute='mues__informacion_general__municipio_upgd')
    upgd = Field(attribute='mues__informacion_general__upgd')
    evento = Field(attribute='mues__informacion_general__evento')
    fecha_notificacion = Field(attribute='mues__informacion_general__fecha_notificacion')
    identificacion = Field()
    paciente = Field(attribute='mues__informacion_general__info_paciente__paciente')
    telefono = Field()
    fecha_nacimiento = Field()
    edad = Field()
    sexo = Field()
    nacionalidad = Field()
    pais_ocurrencia = Field()
    departamento_ocurrencia = Field()
    municipio_ocurrencia = Field()
    area_ocurrencia = Field()
    localidad_ocurrencia = Field()
    barrio_ocurrencia = Field()
    lugar_ocurrencia = Field()
    vereda_zona = Field()
    ocupacion = Field()
    tipo_regimen = Field()
    eapb = Field()
    pertenencia_etnica = Field()
    grupo_etnico = Field()
    estrato = Field()
    grupos_poblacionales = Field()
    semanas_gestacion = Field()
    fuente = Field()
    pais_residencia = Field()
    departamento_residencia = Field()
    municipio_residencia = Field()
    direccion_residencia = Field()
    fecha_consulta = Field()
    fecha_inicio_sintomas = Field()
    clasificacion_inicial_caso = Field()
    hospitalizado = Field()
    fecha_hospitalizacion = Field()
    condicion_final = Field()
    fecha_defuncion = Field()
    certificado_defuncion = Field()
    causa_muerte = Field()
    profesional_diligenciante = Field()
    telefono_profesional = Field()
    clasificacion_final_caso = Field()
    fecha_ajuste = Field()

    # 346
    trabajador_salud = Field()
    viajo_area_con_virus = Field()
    viaje_nacional = Field()
    departamento_viaje_nacional = Field()
    municipio_viaje_nacional = Field()
    viaje_internacional = Field()
    pais_viaje_iternacional = Field()
    contacto_caso_confirmado = Field()
    sintomas = Field()
    influenza_estacional = Field()
    dosis_influenza_estacional = Field()
    antecedentes_clinicos = Field()
    otros_antecedentes_clinicos = Field()
    radiografia_torax = Field()
    antibiotico_ultimas_semanas = Field()

    # 348
    seleccione_opciones = Field()
    caso_irag = Field()
    neumococo = Field()
    dosis_neumococo = Field()
    uso_antivirales = Field()
    fecha_antiviral = Field()
    servicio_hospitalizo = Field()
    fecha_ingreso_uci = Field()
    complicaciones = Field()
    
    observaciones = Field(attribute='registro_recepcion__observaciones')

    # def iter_queryset(self, queryset):
    #     return queryset

    def export_resource(self, obj):
        obj.mues = self.muestra(obj)
        return super().export_resource(obj)

    def muestra(self, obj):
        with suppress(Exception):
            return obj.muestra346
        
        with suppress(Exception):
            return obj.muestra348
    
    def dehydrate_fecha_recepcion(self, obj):
        fecha = obj.registro_recepcion.fecha_recepcion
        return fecha.date()

    def dehydrate_ficha(self, obj):
        return obj.mues.tipo
    
    def dehydrate_resultado(self, obj):
        if obj.registro_recepcion.estado_resultado == enums.EstadoResultadoEnum.SIN_RESULTADO:
            return None
        
        return 'Positivo' if obj.is_positivo else 'Negativo'
    
    def dehydrate_tipo_muestra(self, obj):
        return obj.mues.tipo_muestra
    
    def dehydrate_codigo_analista(self, obj):
        if not obj.registro_recepcion.analista_id:
            return None

        return obj.registro_recepcion.analista.empleado.codigo
    
    def dehydrate_codigo_responsable_tecnico(self, obj):
        if not obj.registro_recepcion.responsable_tecnico_id:
            return None

        return obj.registro_recepcion.responsable_tecnico.empleado.codigo
    
    def dehydrate_codigo_digitador(self, obj):
        if not obj.registro_recepcion.digitado_por:
            return None

        return obj.registro_recepcion.digitado_por.empleado.codigo
    
    def dehydrate_fecha_procesamiento(self, obj):
        fecha = obj.registro_recepcion.fecha_estado_analista
        return fecha and fecha.date()
    
    def dehydrate_hora_procesamiento(self, obj):
        fecha = obj.registro_recepcion.fecha_estado_analista
        return fecha and timezone.localtime(fecha).strftime('%I:%M %p')
    
    def dehydrate_fecha_informe(self, obj):
        fecha = getattr(obj.registro_recepcion.informe, 'fecha_aprobacion', None)
        return fecha and fecha.date()
    
    def dehydrate_metodo_utilizado(self, obj):
        return getattr(obj.pruebasrealizadas_set.first(), 'metodo', None)
    
    def dehydrate_identificacion(self, obj):
        paciente = obj.mues.informacion_general.info_paciente.paciente
        return f'{paciente.get_tipo_identificacion_display()} {paciente.identificacion}'
    
    def dehydrate_telefono(self, obj):
        return obj.mues.informacion_general.info_paciente.telefono or self.SIN_DATOS
    
    def dehydrate_fecha_nacimiento(self, obj):
        return obj.mues.informacion_general.info_paciente.paciente.fecha_nacimiento or self.SIN_DATOS
    
    def dehydrate_edad(self, obj):
        paciente = obj.mues.informacion_general.info_paciente.paciente
        if not paciente.edad:
            return self.SIN_DATOS

        return f'{paciente.edad} {paciente.get_tipo_edad_display()}'
    
    def dehydrate_sexo(self, obj):
        paciente = obj.mues.informacion_general.info_paciente.paciente
        if not paciente.sexo:
            return self.SIN_DATOS

        return paciente.get_sexo_display()
    
    def dehydrate_nacionalidad(self, obj):
        return obj.mues.informacion_general.info_paciente.nacionalidad or self.SIN_DATOS
    
    def dehydrate_pais_ocurrencia(self, obj):
        return obj.mues.informacion_general.info_paciente.pais_ocurrencia or self.SIN_DATOS
    
    def dehydrate_departamento_ocurrencia(self, obj):
        if not obj.mues.informacion_general.info_paciente.municipio_ocurrencia_id:
            return self.SIN_DATOS

        return obj.mues.informacion_general.info_paciente.municipio_ocurrencia.departamento
    
    def dehydrate_municipio_ocurrencia(self, obj):
        return obj.mues.informacion_general.info_paciente.municipio_ocurrencia or self.SIN_DATOS
    
    def dehydrate_area_ocurrencia(self, obj):
        return obj.mues.informacion_general.info_paciente.get_area_ocurrencia_display() or self.SIN_DATOS
    
    def dehydrate_localidad_ocurrencia(self, obj):
        return obj.mues.informacion_general.info_paciente.localidad_ocurrencia or self.SIN_DATOS
    
    def dehydrate_barrio_ocurrencia(self, obj):
        return obj.mues.informacion_general.info_paciente.barrio_ocurrencia or self.SIN_DATOS
    
    def dehydrate_lugar_ocurrencia(self, obj):
        return obj.mues.informacion_general.info_paciente.lugar_ocurrencia or self.SIN_DATOS
    
    def dehydrate_vereda_zona(self, obj):
        return obj.mues.informacion_general.info_paciente.vereda_zona or self.SIN_DATOS
    
    def dehydrate_ocupacion(self, obj):
        return obj.mues.informacion_general.info_paciente.ocupacion or self.SIN_DATOS
    
    def dehydrate_tipo_regimen(self, obj):
        return obj.mues.informacion_general.info_paciente.get_tipo_regimen_display() or self.SIN_DATOS
    
    def dehydrate_eapb(self, obj):
        return obj.mues.informacion_general.info_paciente.eapb or self.SIN_DATOS
    
    def dehydrate_pertenencia_etnica(self, obj):
        return obj.mues.informacion_general.info_paciente.get_pertenencia_etnica_display() or self.SIN_DATOS

    def dehydrate_grupo_etnico(self, obj):
        return obj.mues.informacion_general.info_paciente.grupo_etnico or self.SIN_DATOS

    def dehydrate_estrato(self, obj):
        return obj.mues.informacion_general.info_paciente.get_estrato_display() or self.SIN_DATOS
    
    def dehydrate_grupos_poblacionales(self, obj):
        return obj.mues.informacion_general.info_paciente.grupos_poblacionales or self.SIN_DATOS
    
    def dehydrate_semanas_gestacion(self, obj):
        return obj.mues.informacion_general.info_paciente.semanas_gestacion or self.SIN_DATOS

    def dehydrate_fuente(self, obj):
        return obj.mues.informacion_general.get_fuente_display() or self.SIN_DATOS

    def dehydrate_pais_residencia(self, obj):
        return obj.mues.informacion_general.pais_residencia or self.SIN_DATOS
    
    def dehydrate_departamento_residencia(self, obj):
        if not obj.mues.informacion_general.municipio_residencia_id:
            return self.SIN_DATOS

        return obj.mues.informacion_general.municipio_residencia.departamento
    
    def dehydrate_municipio_residencia(self, obj):
        return obj.mues.informacion_general.municipio_residencia or self.SIN_DATOS
    
    def dehydrate_direccion_residencia(self, obj):
        return obj.mues.informacion_general.direccion or self.SIN_DATOS
    
    def dehydrate_fecha_consulta(self, obj):
        return obj.mues.informacion_general.fecha_consulta or self.SIN_DATOS
    
    def dehydrate_fecha_inicio_sintomas(self, obj):
        return obj.mues.informacion_general.fecha_inicio_sintomas or self.SIN_DATOS
    
    def dehydrate_clasificacion_inicial_caso(self, obj):
        return obj.mues.informacion_general.get_clasificacion_inicial_caso_display() or self.SIN_DATOS
    
    def dehydrate_hospitalizado(self, obj):
        return obj.mues.informacion_general.get_hospitalizado_display() or self.SIN_DATOS
    
    def dehydrate_fecha_hospitalizacion(self, obj):
        return obj.mues.informacion_general.fecha_hospitalizacion or self.SIN_DATOS

    def dehydrate_condicion_final(self, obj):
        return obj.mues.informacion_general.get_condicion_final_display() or self.SIN_DATOS
    
    def dehydrate_fecha_defuncion(self, obj):
        return obj.mues.informacion_general.fecha_defuncion or self.SIN_DATOS
    
    def dehydrate_certificado_defuncion(self, obj):
        return obj.mues.informacion_general.certificado_defuncion or self.SIN_DATOS
    
    def dehydrate_causa_muerte(self, obj):
        return obj.mues.informacion_general.causa_muerte or self.SIN_DATOS
    
    def dehydrate_profesional_diligenciante(self, obj):
        return obj.mues.informacion_general.profesional_diligenciante or self.SIN_DATOS
    
    def dehydrate_telefono_profesional(self, obj):
        return obj.mues.informacion_general.telefono or self.SIN_DATOS
    
    def dehydrate_clasificacion_final_caso(self, obj):
        return obj.mues.informacion_general.get_clasificacion_final_caso_display() or self.SIN_DATOS
    
    def dehydrate_fecha_ajuste(self, obj):
        return obj.mues.informacion_general.fecha_ajuste or self.SIN_DATOS
    
    def dehydrate_trabajador_salud(self, obj):
        if not obj.mues.tipo == enums.TipoMuestraEnum.COVID346.value:
            return None
        return obj.mues.informacion_general.get_trabajador_salud_display() or self.SIN_DATOS
    
    def dehydrate_viajo_area_con_virus(self, obj):
        if not obj.mues.tipo == enums.TipoMuestraEnum.COVID346.value:
            return None
        return obj.mues.informacion_general.get_viajo_area_con_virus_display() or self.SIN_DATOS
    
    def dehydrate_viaje_nacional(self, obj):
        return obj.mues.informacion_general.get_viaje_nacional_display() or self.SIN_DATOS
    
    def dehydrate_departamento_viaje_nacional(self, obj):
        if not obj.mues.informacion_general.municipio_viaje_nacional_id:
            return self.SIN_DATOS

        return obj.mues.informacion_general.municipio_viaje_nacional.departamento
    
    def dehydrate_municipio_viaje_nacional(self, obj):
        return obj.mues.informacion_general.municipio_viaje_nacional or self.SIN_DATOS
    
    def dehydrate_viaje_internacional(self, obj):
        return obj.mues.informacion_general.get_viaje_internacional_display() or self.SIN_DATOS
    
    def dehydrate_pais_viaje_iternacional(self, obj):
        return obj.mues.informacion_general.pais_viaje_iternacional or self.SIN_DATOS
    
    def dehydrate_contacto_caso_confirmado(self, obj):
        if not obj.mues.tipo == enums.TipoMuestraEnum.COVID346.value:
            return None
        return obj.mues.informacion_general.get_contacto_caso_confirmado_display() or self.SIN_DATOS
    
    def dehydrate_sintomas(self, obj):
        if not obj.mues.tipo == enums.TipoMuestraEnum.COVID346.value:
            return None
        return obj.mues.informacion_general.sintomas or self.SIN_DATOS
    
    def dehydrate_influenza_estacional(self, obj):
        return obj.mues.informacion_general.get_influenza_estacional_display() or self.SIN_DATOS
    
    def dehydrate_dosis_influenza_estacional(self, obj):
        return obj.mues.informacion_general.dosis_influenza_estacional or self.SIN_DATOS
    
    def dehydrate_antecedentes_clinicos(self, obj):
        return obj.mues.informacion_general.antecedentes_clinicos or self.SIN_DATOS
    
    def dehydrate_otros_antecedentes_clinicos(self, obj):
        return obj.mues.informacion_general.otros_antecedentes_clinicos or self.SIN_DATOS
    
    def dehydrate_radiografia_torax(self, obj):
        return obj.mues.informacion_general.get_radiografia_torax_display() or self.SIN_DATOS
    
    def dehydrate_antibiotico_ultimas_semanas(self, obj):
        return obj.mues.informacion_general.get_antibiotico_ultimas_semanas_display() or self.SIN_DATOS

    def dehydrate_seleccione_opciones(self, obj):
        if not obj.mues.tipo == enums.TipoMuestraEnum.COVID348.value:
            return None
        return obj.mues.informacion_general.seleccione_opciones or self.SIN_DATOS
    
    def dehydrate_caso_irag(self, obj):
        if not obj.mues.tipo == enums.TipoMuestraEnum.COVID348.value:
            return None
        return obj.mues.informacion_general.caso_irag or self.SIN_DATOS
    
    def dehydrate_neumococo(self, obj):
        if not obj.mues.tipo == enums.TipoMuestraEnum.COVID348.value:
            return None
        return obj.mues.informacion_general.get_neumococo_display() or self.SIN_DATOS
    
    def dehydrate_dosis_neumococo(self, obj):
        if not obj.mues.tipo == enums.TipoMuestraEnum.COVID348.value:
            return None
        return obj.mues.informacion_general.dosis_neumococo or self.SIN_DATOS
    
    def dehydrate_uso_antivirales(self, obj):
        if not obj.mues.tipo == enums.TipoMuestraEnum.COVID348.value:
            return None
        return obj.mues.informacion_general.get_uso_antivirales_display() or self.SIN_DATOS
    
    def dehydrate_fecha_antiviral(self, obj):
        if not obj.mues.tipo == enums.TipoMuestraEnum.COVID348.value:
            return None
        return obj.mues.informacion_general.fecha_antiviral or self.SIN_DATOS
    
    def dehydrate_servicio_hospitalizo(self, obj):
        if not obj.mues.tipo == enums.TipoMuestraEnum.COVID348.value:
            return None
        return obj.mues.informacion_general.get_servicio_hospitalizo_display() or self.SIN_DATOS
    
    def dehydrate_fecha_ingreso_uci(self, obj):
        if not obj.mues.tipo == enums.TipoMuestraEnum.COVID348.value:
            return None
        return obj.mues.informacion_general.fecha_ingreso_uci or self.SIN_DATOS
    
    def dehydrate_complicaciones(self, obj):
        if not obj.mues.tipo == enums.TipoMuestraEnum.COVID348.value:
            return None
        return obj.mues.informacion_general.complicaciones or self.SIN_DATOS

class ImpresionLoteFichaForm(trazabilidad_forms.RangoFechasForm):
    
    FECHA_INFORME = 'I'
    FECHA_RECEPCION = 'R'
    TIPOS = (
        (FECHA_RECEPCION, 'Fecha de recepción'),
        (FECHA_INFORME, 'Fecha de informe'),
    )

    TODOS = 'T'
    POSITIVO = 'P'
    NEGATIVO = 'N'
    RESULTADOS = (
        (TODOS, 'Todos'),
        (POSITIVO, 'Positivos'),
        (NEGATIVO, 'Negativos'),
    )

    tipo_fecha = forms.ChoiceField(choices=TIPOS, required=True)
    por_resultado = forms.ChoiceField(choices=RESULTADOS, required=True)

    def generar_zip(self, request):
        tipo = self.cleaned_data.get('tipo_fecha')
        desde = self.cleaned_data.get('fecha_inicial')
        hasta = self.cleaned_data.get('fecha_final')
        por_resultado = self.cleaned_data.get('por_resultado')

        ingresos = (
            trazabilidad_models.Ingreso.objects
                .by_programa_covid()
                .con_informe_aprobado()
        )
        if tipo == self.FECHA_RECEPCION:
            ingresos = ingresos.by_fecha_recepcion(desde, hasta)
        else:
            ingresos = ingresos.by_fecha_informe(desde, hasta)

        if por_resultado != self.TODOS:
            query = trazabilidad_models.PruebasRealizadas.objects.filter(muestra__registro_recepcion=OuterRef('pk'))
            if por_resultado == self.POSITIVO:
                query = query.positivos()
            else:
                query = query.negativos()
            
            ingresos = ingresos.annotate(is_filtered=Exists(query)).filter(is_filtered=True)

        mem_file = s.generate_zip_fichas_covid(request=request, ingresos=ingresos)
        return mem_file, f'{desde} - {hasta}'

