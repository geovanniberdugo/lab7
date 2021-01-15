from django.template.loader import render_to_string
from django.db.models.query import Prefetch
from django.utils import timezone
from django.conf import settings
from weasyprint import HTML

from . import models as m
from . import enums

def data_informe_resultados(ingreso, muestras=None):
    informe = ingreso.reportes.all()[0]

    if not muestras:
        muestras = ingreso.muestras.all().prefetch_related(Prefetch(
            'pruebasrealizadas_set',
            queryset=(
                m.PruebasRealizadas.objects
                    .select_related('prueba', 'metodo')
                    .order_by('prueba__area__nombre', 'prueba')
            )
        ))

    templates = {
        enums.ProgramaEnum.COVID19.value: 'covid19/cuerpo_informe_resultados.html',
        enums.ProgramaEnum.ALIMENTOS.value: 'alimentos/cuerpo_informe_resultados.html',
        enums.ProgramaEnum.EEID.value: 'trazabilidad/cuerpo_informe_resultados_eeid.html',
        enums.ProgramaEnum.EEDD.value: 'trazabilidad/cuerpo_informe_resultados_eedd.html',
        enums.ProgramaEnum.AGUAS.value: 'trazabilidad/cuerpo_informe_resultados_aguas.html',
        enums.ProgramaEnum.CLINICO.value: 'trazabilidad/cuerpo_informe_resultados_clinicos.html',
        enums.ProgramaEnum.ENTOMOLOGIA.value: 'trazabilidad/cuerpo_informe_resultados_entomologia.html',
        enums.ProgramaEnum.BANCO_SANGRE.value: 'trazabilidad/cuerpo_informe_resultados_banco_sangre.html',
        enums.ProgramaEnum.BEBIDAS_ALCOHOLICAS.value: 'bebidas_alcoholicas/cuerpo_informe_resultados.html',
        enums.ProgramaEnum.CITOHISTOPATOLOGIA.value: 'trazabilidad/cuerpo_informe_resultados_citohistopatologia.html',
    }

    return {
        'ingreso': ingreso,
        'informe': informe,
        'muestras': muestras,
        'fecha_impresion': timezone.now(),
        'imprimir': bool(informe.fecha_aprobacion),
        'cuerpo_informe': templates.get(ingreso.programa.codigo, None)
    }

def generate_results_pdf(request, data, target=None):
    html = render_to_string('trazabilidad/reporte.html', context=data, request=request)
    
    return HTML(string=html).write_pdf(target=target, stylesheets=[
        'static/css/bootstrap.min.css',
        'static/css/estilos.css',
        'static/css/_informe_nuevo_grande.css',
    ])
