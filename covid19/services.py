import io
from django.template.loader import render_to_string
from django.utils import timezone
from zipfile import ZipFile
from weasyprint import HTML

from trazabilidad import services as traza_s
from trazabilidad import enums

def generate_zip_fichas_covid(request, ingresos):
    mem_file = io.BytesIO()
    with ZipFile(mem_file, 'w') as zip_file:
        for ingreso in ingresos:
            data = data_ficha(ingreso)
            paciente = data["paciente"]
            nombre = f'{ingreso.fecha_recepcion}_{paciente}_{paciente.identificacion}_{data["title"]}.pdf'
            zip_file.writestr(nombre, generate_ficha_pdf(request, data=data))
            data = traza_s.data_informe_resultados(ingreso=ingreso)
            nombre = f'{ingreso.fecha_recepcion}_{paciente}_{paciente.identificacion}.pdf'
            zip_file.writestr(nombre, traza_s.generate_results_pdf(request, data=data))

    mem_file.seek(0)
    return mem_file

def data_ficha(ingreso):
    d = {}
    if ingreso.muestra.tipo == enums.TipoMuestraEnum.COVID346.value:
        d = {
            'title': 'Ficha 346',
            'ficha': 'covid19/_ficha_346.html',
        }
    else:
        d = {
            'title': 'Ficha 348',
            'ficha': 'covid19/_ficha_348.html',
        }

    return {
        **d,
        'imprimir': False,
        'ingreso': ingreso,
        'fecha_impresion': timezone.now(),
        'muestras': ingreso.muestras.all(),
        'info_general': ingreso.muestra.informacion_general,
        'info_paciente': ingreso.muestra.informacion_general.info_paciente,
        'paciente': ingreso.muestra.informacion_general.info_paciente.paciente,
    }

def generate_ficha_pdf(request, data, target=None):
    html = render_to_string('covid19/ficha_covid.html', context=data, request=request)

    return HTML(string=html).write_pdf(target=target, stylesheets=[
        'static/css/bootstrap.min.css',
        'static/css/estilos.css',
        'static/css/_informe_nuevo_grande.css',
    ])
