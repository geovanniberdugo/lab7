from common.models import EstadoMixin, UltimaModificacionMixin
from django.contrib.postgres.fields import ArrayField
from django_countries.fields import CountryField
from trazabilidad.models import Muestra
from trazabilidad import enums
from django.db import models
from django import forms

RURAL_DISPERSO = 'RD'
CENTRO_POBLADO = 'CP'
CABECERA_MUNICIPAL = 'CB'
AREAS_OCURRENCIA = (
    (RURAL_DISPERSO, 'Rural disperso'),
    (CENTRO_POBLADO, 'centro poblado'),
    (CABECERA_MUNICIPAL, 'Cabecera municipal'),
)

ESPECIAL = 'E'
EXCEPCION = 'P'
SUBSIDIADO = 'S'
NO_ASEGURADO = 'N'
CONTRIBUTIVO = 'C'
INDETERMINADO = 'I'
TIPOS_REGIMEN = (
    (ESPECIAL, 'Especial'),
    (EXCEPCION, 'Excepción'),
    (SUBSIDIADO, 'Subsidiado'),
    (NO_ASEGURADO, 'No asegurado'),
    (CONTRIBUTIVO, 'Contributivo'),
    (INDETERMINADO, 'Indeterminado/Pendiente'),
)

OTRO = 'O'
NEGRO = 'N'
GITANO = 'G'
RAIZAL = 'R'
INDIGENA = 'I'
PALENQUERO = 'P'
PERTENENCIAS_ETNICAS = (
    (OTRO, 'Otro'),
    (RAIZAL, 'Raizal'),
    (INDIGENA, 'Indígena'),
    (GITANO, 'Rom, Gitano'),
    (PALENQUERO, 'Palenquero'),
    (NEGRO, 'Negro, mulato afro colombiano'),
)

ALTO = '6'
BAJO = '2'
MEDIO = '4'
BAJO_BAJO = '1'
MEDIO_BAJO = '3'
MEDIO_ALTO = '5'
ESTRATOS = (
    (BAJO_BAJO, 'Bajo-Bajo'),
    (BAJO, 'Bajo'),
    (MEDIO_BAJO, 'Medio-Bajo'),
    (MEDIO, 'Medio'),
    (MEDIO_ALTO, 'Medio-Alto'),
    (ALTO, 'Alto'),
)

OTROS = 'O'
INFANTIL = 'PI'
GESTANTES = 'GE'
MIGRANTES = 'MI'
INDIGENTES = 'IN'
CARCELARIOS = 'CA'
DESPLAZADOS = 'DE'
DISCAPACITADOS = 'DI'
DESMOVILIZADOS = 'DES'
MADRES_COMUNITARIAS = 'MC'
VICTIMAS_VIOLENCIA = 'VVA'
CENTROS_PSIQUIATRICOS = 'CP'
GRUPOS_POBLACIONALES = (
    (DISCAPACITADOS, 'Discapacitados'),
    (DESPLAZADOS, 'Desplazados'),
    (MIGRANTES, 'Migrantes'),
    (CARCELARIOS, 'Carcelarios'),
    (GESTANTES, 'Gestantes'),
    (INDIGENTES, 'Indigentes'),
    (INFANTIL, 'Poblacion infantil a cargo del ICBF'),
    (MADRES_COMUNITARIAS, 'Madres comunitarias'),
    (DESMOVILIZADOS, 'Desmovilizados'),
    (CENTROS_PSIQUIATRICOS, 'Centros psiquiátricos'),
    (VICTIMAS_VIOLENCIA, 'Victimas de violencia armada'),
    (OTROS, 'Otros grupos poblacionales'),
)

INVESTIGACIONES = '5'
BUSQ_ACTIVA_IN = '2'
BUSQ_ACTIVA_COM = '4'
VIGIL_INTESIFICADA = '3'
NOTIFICACION_RUTINARIA = '1'
FUENTES = (
    (INVESTIGACIONES, 'Investigaciones'),
    (BUSQ_ACTIVA_IN, 'Busqueda activa ins.'),
    (BUSQ_ACTIVA_COM, 'Busqueda activa com.'),
    (VIGIL_INTESIFICADA, 'Vigilancia intensificada'),
    (NOTIFICACION_RUTINARIA, 'Notificacion rutinaria'),
)

PROBABLE = '2'
NO_APLICA = '0'
DESCARTADO = '6'
SOSPECHOSO = '1'
CONF_CLINICA = '4'
ACTUALIZACION = '7'
CONF_NEXO_EPI = '5'
CONF_LABORATORIO = '3'
DESCARTADO_DIGITACION = 'D'
CLASIFICACIONES_INICIALES_CASO = (
    (PROBABLE, 'Probable'),
    (SOSPECHOSO, 'Sospechoso'),
    (CONF_NEXO_EPI, 'Conf. clinica'),
    (CONF_CLINICA, 'Conf. por laboratorio'),
    (CONF_LABORATORIO, 'Conf. nexo epidemiologico'),
)

CLASIFICACIONES_FINALES_CASO = (
    (NO_APLICA, 'No aplica'),
    (DESCARTADO, 'Descartado'),
    (CONF_NEXO_EPI, 'Conf. clinica'),
    (ACTUALIZACION, 'Otra actualización'),
    (CONF_CLINICA, 'Conf. por laboratorio'),
    (CONF_LABORATORIO, 'Conf. nexo epidemiologico'),
    (DESCARTADO_DIGITACION, 'Descartado por error de digitación'),
)

SI = 'SI'
NO = 'NO'
DESCONOCIDO = 'DE'
SI_NO_OPCIONES = (
    (SI, 'Si'),
    (NO, 'No'),
)

SI_NO_DES_OPCIONES = (
    (SI, 'Si'),
    (NO, 'No'),
    (DESCONOCIDO, 'Desconocido'),
)

VIVO = '1'
MUERTO = '2'
NO_SABE = '0'
CONDICIONES_FINALES = (
    (VIVO, 'Vivo'),
    (MUERTO, 'Muerto'),
    (NO_SABE, 'No sabe, no responde'),
)

VIH = 'VIH'
EPOC = 'EP'
ASMA = 'AS'
CANCER = 'CA'
FUMADOR = 'FU'
OBESIDAD = 'OB'
DIABETES = 'DI'
DESNUTRICION = 'DE'
TUBERCULOSIS = 'TU'
ENFERMEDAD_CARDIACA = 'EC'
INSUFICIENCIA_RENAL = 'IR'
MED_INMUNOSUPRESORES = 'MI'
OTROS = 'OT'
ANTECEDENTES_CLINICOS = (
    (ASMA, 'Asma'),
    (OBESIDAD, 'Obesidad'),
    (EPOC, 'EPOC'),
    (INSUFICIENCIA_RENAL, 'Insuficiencia renal'),
    (DIABETES, 'Diabetes'),
    (MED_INMUNOSUPRESORES, 'Toma medicamentos inmusupresores'),
    (VIH, 'VIH'),
    (FUMADOR, 'Fumador'),
    (ENFERMEDAD_CARDIACA, 'Enfermedad cardiaca'),
    (TUBERCULOSIS, 'Tuberculosis'),
    (CANCER, 'Cancer'),
    (DESNUTRICION, 'Desnutrición'),
    (OTROS, 'Otros'),
)

TOS = 'TOS'
FIEBRE = 'FI'
FATIGA = 'FA'
ODINOFAGIA = 'OD'
DIF_RESPIRATORIA = 'DR'
OPCIONES_SINTOMAS = (
    (TOS, 'Tos'),
    (FIEBRE, 'Fiebre'),
    (ODINOFAGIA, 'Odinofagia'),
    (DIF_RESPIRATORIA, 'Dificulta respiratoria'),
    (FATIGA, 'Fatiga o adinamia'),
)

NINGUNO = '3'
IN_ALVEOLAR = '1'
IN_INTERSTICIALES = '2'
HALLAZGOS_RADIOGRAFIA = (
    (NINGUNO, 'Ninguno'),
    (IN_ALVEOLAR, 'Infiltrado alveolar o neumonía'),
    (IN_INTERSTICIALES, 'Infiltrados intersticiales'),
)

IRAG = '348'
COVID19 = '346'
ESI_IRAG = '345'
EVENTOS = (
    (COVID19, 'COVID-19'),
    (ESI_IRAG, 'ESI/IRAG'),
    (IRAG, 'IRAG INSITADO'),
)

TRABAJADOR_SALUD = 'TS'
DETERIORO_CLINICO = 'DC'
CASO_ASOCIADO = 'CA'
VIAJO = 'VI'
CONTACTO_AVE_CERDO = 'CC'
CONTACTO_PERSONAS = 'CP'
SELECCIONE_OPCIONES = (
    (TRABAJADOR_SALUD, 'Es trabajador del área de la salud'),
    (DETERIORO_CLINICO, 'Presenta deterioro clínico sin etiología determinada, con evolución rápida (con necesidad de vasopresores y/o ventilación mecánica) desde el inicio de síntomas'),
    (CASO_ASOCIADO, 'Caso asociado a un brote o conglomerado'),
    (VIAJO, 'Viajó'),
    (CONTACTO_AVE_CERDO, 'Tuvo contacto con aves o cerdos enfermos o muertos durante 14 días previos al inicio de los síntomas'),
    (CONTACTO_PERSONAS, 'Tuvo contacto estrecho con personas enfermas o que hallan fallecido de IRAG durante los 14 días previos a los síntomas'),
)

OPCIONES_IRAG = (
    (TOS, 'Paciente con Tos'),
    (FIEBRE, 'Paciente con Fiebre'),
)

HOSPITALIZACION_GENERAL = 'HG'
UCI = 'UCI'
SERVICIO_HOSPITALIZO = (
    (HOSPITALIZACION_GENERAL, 'Hospitalización General'),
    (UCI, 'UCI'),
)

DERRAME_PLEURAL = 'DP'
DERRAME_PERICARDICO = 'PE'
MIOCARDITIS = 'MI'
SEPTICEMIA = 'SE'
FALLA_RESPIRATORIA = 'FR'
OTRO = 'OT'
COMPLICACIONES = (
    (DERRAME_PLEURAL, 'Derrame Pleural'),
    (DERRAME_PERICARDICO, 'Derrame Pericárdico'),
    (MIOCARDITIS, 'Miocarditis'),
    (SEPTICEMIA, 'Septicemia'),
    (FALLA_RESPIRATORIA, 'Falla Respiratoria'),
    (OTRO, 'Otro'),
)

def label_from(options, value):
    return next(item[1] for item in options if item[0] == value)

class Ocupacion(models.Model):

    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre.title()

class Tipificacion(UltimaModificacionMixin):

    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre.title()

class Upgd(UltimaModificacionMixin):
    """Unidad primaria generadora del dato"""

    nombre = models.CharField(max_length=400)
    codigo = models.CharField(max_length=100)
    subindice = models.CharField(max_length=10)
    email = models.EmailField()

    def __str__(self):
        return self.nombre

class Eapb(UltimaModificacionMixin):
    """Entidad administradora de planes de beneficios"""

    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.nombre

class InfoPaciente(UltimaModificacionMixin):

    paciente = models.ForeignKey('trazabilidad.Paciente', related_name='infos_covid19', on_delete=models.CASCADE)

    tipificacion = models.ForeignKey(Tipificacion, related_name='+', verbose_name='tipificación paciente', on_delete=models.CASCADE, blank=True, null=True)
    telefono = models.CharField(max_length=15, verbose_name='teléfono', blank=True)
    nacionalidad = CountryField(verbose_name='nacionalidad', blank=True)
    # Ocurrencia del caso
    pais_ocurrencia = CountryField(verbose_name='pais de ocurrencia del caso', default='CO', blank=True)
    municipio_ocurrencia = models.ForeignKey('trazabilidad.Municipio', related_name='+', verbose_name='municipio de procedencia/ocurrencia', on_delete=models.CASCADE, blank=True, null=True)
    area_ocurrencia = models.CharField(max_length=3, choices=AREAS_OCURRENCIA, verbose_name='área de ocurrencia del caso', blank=True)
    localidad_ocurrencia = models.CharField(max_length=200, verbose_name='localidad de ocurrencia del caso', blank=True)
    barrio_ocurrencia = models.CharField(max_length=200, verbose_name='barrio de ocurrencia del caso', blank=True)
    lugar_ocurrencia = models.CharField(max_length=200, verbose_name='cabecera municipal/centro poblado/rural disperso', blank=True)
    vereda_zona = models.CharField(max_length=200, verbose_name='vereda/zona', blank=True)

    ocupacion = models.ForeignKey(Ocupacion, related_name='+', on_delete=models.CASCADE, blank=True, null=True)
    tipo_regimen = models.CharField(max_length=1, choices=TIPOS_REGIMEN, verbose_name='tipo de régimen en salud', blank=True)
    eapb = models.ForeignKey(Eapb, related_name='+', verbose_name='nombre de la administradora de Planes de beneficios', on_delete=models.CASCADE, blank=True, null=True)
    pertenencia_etnica = models.CharField(max_length=1, choices=PERTENENCIAS_ETNICAS, blank=True)
    grupo_etnico = models.CharField(max_length=200, blank=True)
    estrato = models.CharField(max_length=1, choices=ESTRATOS, blank=True)
    grupos_poblacionales = ArrayField(models.CharField(max_length=4, choices=GRUPOS_POBLACIONALES), blank=True, null=True)
    semanas_gestacion = models.CharField(max_length=100, blank=True, verbose_name='sem. de gestación')

    def __str__(self):
        return str(self.paciente)
    
    def get_grupos_poblacionales_display(self):
        return [label_from(GRUPOS_POBLACIONALES, grupo) for grupo in self.grupos_poblacionales]

class InfoGeneralMixin(models.Model):
    upgd = models.ForeignKey(Upgd, related_name='+', on_delete=models.CASCADE, blank=True, null=True)
    municipio_upgd = models.ForeignKey('trazabilidad.Municipio', related_name='+', on_delete=models.CASCADE, blank=True, null=True)
    info_paciente = models.ForeignKey(InfoPaciente, related_name='+', on_delete=models.CASCADE)
    evento = models.CharField(max_length=4, choices=EVENTOS, blank=True)
    fecha_notificacion = models.DateField(verbose_name='fecha de la notificación', blank=True, null=True)

    class Meta:
        abstract = True

class NotificacionMixin(models.Model):

    fuente = models.CharField(max_length=2, choices=FUENTES, blank=True, null=True)
    pais_residencia = CountryField(verbose_name='pais de residencia', default='CO', blank=True, null=True)
    municipio_residencia = models.ForeignKey('trazabilidad.Municipio', related_name='+', verbose_name='municipio de residencia', on_delete=models.CASCADE, blank=True, null=True)
    direccion = models.CharField(max_length=150, verbose_name='dirección de residencia', blank=True)
    fecha_consulta = models.DateField(verbose_name='fecha de consulta', blank=True, null=True)
    fecha_inicio_sintomas = models.DateField(verbose_name='fecha de inicio de sintomas', blank=True, null=True)
    clasificacion_inicial_caso = models.CharField(max_length=2, choices=CLASIFICACIONES_INICIALES_CASO, verbose_name='clasificación inicial de caso', blank=True)
    hospitalizado = models.CharField(max_length=2, choices=SI_NO_OPCIONES, blank=True)
    fecha_hospitalizacion = models.DateField(verbose_name='fecha de hospitalización', blank=True, null=True)
    condicion_final = models.CharField(max_length=2, choices=CONDICIONES_FINALES, blank=True)
    fecha_defuncion = models.DateField(verbose_name='fecha de defunción', blank=True, null=True)
    certificado_defuncion = models.CharField(max_length=100, verbose_name='número de certificado de defunción', blank=True)
    causa_muerte = models.ForeignKey('cie10_django.CIE10', related_name='+', verbose_name='causa básica de muerte', on_delete=models.CASCADE, blank=True, null=True)
    profesional_diligenciante = models.CharField(max_length=200, verbose_name='nombre del profesional que diligencio la ficha', blank=True)
    telefono = models.CharField(max_length=15, blank=True)

    class Meta:
        abstract = True

class EnteTerritorialMixin(models.Model):

    fecha_ajuste = models.DateField(verbose_name='fecha de ajuste', blank=True, null=True)
    clasificacion_final_caso = models.CharField(max_length=2, choices=CLASIFICACIONES_FINALES_CASO, verbose_name='seguimiento y clasificación final de caso', blank=True)

    class Meta:
        abstract = True

class InfoGeneral346(InfoGeneralMixin, NotificacionMixin, EnteTerritorialMixin):
    # IRA virus nuevo
    trabajador_salud = models.CharField(
        blank=True,
        max_length=2,
        choices=SI_NO_OPCIONES,
        verbose_name='¿Es trabajador de la salud otro personal del ambito hospitalario que haya tenido contacto estrecho con un caso probable o confirmado por nuevo virus?'
    )
    viajo_area_con_virus = models.CharField(max_length=2, choices=SI_NO_OPCIONES, verbose_name='¿Viajo a areas de circulación del virus nuevo?', blank=True)
    viaje_nacional = models.CharField(max_length=2, choices=SI_NO_OPCIONES, verbose_name='¿El Viaje fue en territorio nacional?', blank=True)
    municipio_viaje_nacional = models.ForeignKey('trazabilidad.Municipio', related_name='+', null=True, blank=True, verbose_name='¿Donde?', on_delete=models.CASCADE)
    viaje_internacional = models.CharField(max_length=2, choices=SI_NO_OPCIONES, verbose_name='¿El Viaje fue internacional?', blank=True)
    pais_viaje_iternacional = CountryField(verbose_name='¿donde?', blank=True)
    contacto_caso_confirmado = models.CharField(
        blank=True,
        max_length=2,
        choices=SI_NO_OPCIONES,
        verbose_name='¿tuvo contacto estrecho en los últimos 14 días con un caso probable o confirmado con infección respiratoria aguda grave por virus nuevo?'
    )
    sintomas = ArrayField(models.CharField(max_length=4, choices=OPCIONES_SINTOMAS), blank=True, null=True)

    # Antecedentes vacunales
    influenza_estacional = models.CharField(max_length=2, choices=SI_NO_DES_OPCIONES, blank=True)
    dosis_influenza_estacional = models.CharField(max_length=10, blank=True, verbose_name='dosis')

    # Antecedentes clinicos
    antecedentes_clinicos = ArrayField(models.CharField(max_length=3, choices=ANTECEDENTES_CLINICOS), blank=True, null=True)
    otros_antecedentes_clinicos = models.CharField(max_length=200, verbose_name='¿cuáles otros?', blank=True)

    # Diagnostico y tratamiento
    radiografia_torax = models.CharField(max_length=2, choices=HALLAZGOS_RADIOGRAFIA, blank=True)
    antibiotico_ultimas_semanas = models.CharField(max_length=2, choices=SI_NO_OPCIONES, blank=True)

    def get_sintomas_display(self):
        return [label_from(OPCIONES_SINTOMAS, item) for item in self.sintomas]
    
    def get_antecedentes_clinicos_display(self):
        return [label_from(ANTECEDENTES_CLINICOS, item) for item in self.antecedentes_clinicos]

class Muestra346(Muestra):

    fecha_toma = models.DateField(blank=True, null=True)
    informacion_general = models.ForeignKey(InfoGeneral346, on_delete=models.CASCADE)
    tipo_muestra = models.ForeignKey('trazabilidad.TipoMuestra', related_name='muestras_346', on_delete=models.CASCADE, blank=True, null=True)

    @property
    def tipo(self):
        return enums.TipoMuestraEnum.COVID346.value

    @property
    def solicitante(self):
        return self.informacion_general.upgd

    @property
    def municipio_upgd(self):
        return self.informacion_general.municipio_upgd

    @property
    def departamento_upgd(self):
        if self.informacion_general.municipio_upgd_id:
            return self.informacion_general.municipio_upgd.departamento.nombre

    @property
    def info_paciente(self):
        return self.informacion_general.info_paciente
    
    def paciente(self):
        return self.informacion_general.info_paciente.paciente
    
    @property
    def tipificacion(self):
        return self.informacion_general.info_paciente.tipificacion

    @property
    def pais_residencia(self):
        return self.informacion_general.pais_residencia

    @property
    def departamento_residencia(self):
        if self.informacion_general.municipio_residencia_id:
            return self.informacion_general.municipio_residencia.departamento.nombre

    @property
    def municipio_residencia(self):
        return self.informacion_general.municipio_residencia

class InfoGeneral348(InfoGeneralMixin, NotificacionMixin, EnteTerritorialMixin):
    # IRAG Inusitada. Cod INS 348
    seleccione_opciones = ArrayField(models.CharField(max_length=2, choices=SELECCIONE_OPCIONES), blank=True, null=True)
    viaje_nacional = models.CharField(max_length=2, choices=SI_NO_OPCIONES, verbose_name='¿El Viaje fue en territorio nacional?', blank=True)
    municipio_viaje_nacional = models.ForeignKey('trazabilidad.Municipio', related_name='+', null=True, blank=True, verbose_name='¿Donde?', on_delete=models.CASCADE)
    viaje_internacional = models.CharField(max_length=2, choices=SI_NO_OPCIONES, verbose_name='¿El Viaje fue internacional?', blank=True)
    pais_viaje_iternacional = CountryField(verbose_name='¿donde?', blank=True)

    caso_irag = ArrayField(models.CharField(max_length=4, choices=OPCIONES_IRAG), blank=True, null=True)

    # Antecedentes vacunales
    neumococo = models.CharField(max_length=2, choices=SI_NO_DES_OPCIONES, blank=True, verbose_name='Streptococcus pneumoniae (neumococo)')
    dosis_neumococo = models.CharField(max_length=10, blank=True, verbose_name='dosis')
    influenza_estacional = models.CharField(max_length=2, choices=SI_NO_DES_OPCIONES, blank=True)
    dosis_influenza_estacional = models.CharField(max_length=10, blank=True, verbose_name='dosis')

    # Antecedentes clinicos
    antecedentes_clinicos = ArrayField(models.CharField(max_length=3, choices=ANTECEDENTES_CLINICOS), blank=True, null=True)
    otros_antecedentes_clinicos = models.CharField(max_length=200, verbose_name='¿cuáles otros?', blank=True)

    # Diagnostico y tratamiento
    radiografia_torax = models.CharField(max_length=2, choices=HALLAZGOS_RADIOGRAFIA, blank=True)
    antibiotico_ultimas_semanas = models.CharField(max_length=2, choices=SI_NO_OPCIONES, blank=True)

    uso_antivirales = models.CharField(max_length=2, choices=SI_NO_OPCIONES, blank=True, verbose_name='¿Usó antivirales en la última semana?')
    fecha_antiviral = models.DateField(verbose_name='¿Fecha de inicio de antiviral?', blank=True, null=True)

    servicio_hospitalizo = models.CharField(max_length=3, choices=SERVICIO_HOSPITALIZO, blank=True, verbose_name='Servicio en el que se hospitalizó')
    fecha_ingreso_uci = models.DateField(verbose_name='Fecha de Ingreso a UCI', blank=True, null=True)
    complicaciones = ArrayField(models.CharField(max_length=3, choices=COMPLICACIONES), blank=True, null=True, verbose_name='Si hubo complicaciones, ¿Cuáles se presentaron?')

    def get_seleccione_opciones_display(self):
        return [label_from(SELECCIONE_OPCIONES, item) for item in self.seleccione_opciones]
    
    def get_caso_irag_display(self):
        return [label_from(OPCIONES_IRAG, item) for item in self.caso_irag]
    
    def get_antecedentes_clinicos_display(self):
        return [label_from(ANTECEDENTES_CLINICOS, item) for item in self.antecedentes_clinicos]
    
    def get_complicaciones_display(self):
        return [label_from(COMPLICACIONES, item) for item in self.complicaciones]

class Muestra348(Muestra):

    fecha_toma = models.DateField(blank=True, null=True)
    informacion_general = models.ForeignKey(InfoGeneral348, on_delete=models.CASCADE)
    tipo_muestra = models.ForeignKey('trazabilidad.TipoMuestra', related_name='muestras_348', on_delete=models.CASCADE, blank=True, null=True)

    @property
    def tipo(self):
        return enums.TipoMuestraEnum.COVID348.value

    @property
    def solicitante(self):
        return self.informacion_general.upgd

    @property
    def municipio_upgd(self):
        return self.informacion_general.municipio_upgd

    @property
    def departamento_upgd(self):
        if self.informacion_general.municipio_upgd_id:
            return self.informacion_general.municipio_upgd.departamento.nombre

    def paciente(self):
        return self.informacion_general.info_paciente.paciente
    
    @property
    def tipificacion(self):
        return self.informacion_general.info_paciente.tipificacion

    @property
    def pais_residencia(self):
        return self.informacion_general.pais_residencia

    @property
    def departamento_residencia(self):
        if self.informacion_general.municipio_residencia_id:
            return self.informacion_general.municipio_residencia.departamento.nombre

    @property
    def municipio_residencia(self):
        return self.informacion_general.municipio_residencia
    



