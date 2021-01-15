from enum import Enum

class ProgramaEnum(Enum):
    EEDD = 'eedd'
    EEID = 'eeid'
    AGUAS = 'aguas'
    COVID19 = 'covid19'
    CLINICO = 'clinica'
    ALIMENTOS = 'alimentos'
    ENTOMOLOGIA = 'entomologia'
    BANCO_SANGRE = 'banco_sangre'
    CITOHISTOPATOLOGIA = 'citohistopatologia'
    BEBIDAS_ALCOHOLICAS = 'bebidas_alcoholicas'

class TipoMuestraEnum(Enum):
    AGUAS = 'agua'
    CLINICA = 'clinica'
    COVID346 = 'covid346'
    COVID348 = 'covid348'
    ALIMENTOS = 'alimentos'
    ENTOMOLOGIA = 'entomologia'
    BANCO_SANGRE = 'banco de sangre'
    CITOHISTOPATOLOGIA = 'citohistopatologia'
    BEBIDAS_ALCOHOLICAS = 'bebidas_alcoholicas'
    EEDD = 'evaluacion externa desempeño directo'
    EEID = 'evaluacion externa desempeño indirecto'

class EstadoIngresoEnum(Enum):
    PENDIENTE = 'Pendiente Aceptación'
    EN_CURSO = 'En Curso'
    RESULTADO = 'Resultado Emitido'
    RECHAZADA = 'Rechazada'
    EN_APROBACION = 'Pendiente Aprobación'

class EstadoResultadoEnum(Enum):
    SIN_RESULTADO = 'Sin Resultado'
    RESULTADO_ENVIADO = 'Resultado enviado'
    RESULTADO_NO_ENVIADO = 'Resultado no enviado'