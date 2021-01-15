from .models import Programa


def organiza_areas(ingresos):
    """"""

    detalle_areas = {}

    for ingreso in ingresos:
        if ingreso.programa in [Programa.objects.alimentos(), Programa.objects.aguas()]:
            nombre = ingreso.programa.nombre
            if nombre not in detalle_areas:
                detalle_areas[nombre] = []

            detalle_areas[nombre].append({
                'radicado': ingreso.radicado,
                'fecha_recepcion': ingreso.fecha_recepcion,
                'solicitante': ingreso.solicitante,
                'nombre': ' - '.join(ingreso.areas.values_list('nombre', flat=True))
            })
        else:
            for area in ingreso.areas:
                if area.nombre not in detalle_areas:
                    detalle_areas[area.nombre] = []

                detalle_areas[area.nombre].append({
                    'radicado': ingreso.radicado,
                    'fecha_recepcion': ingreso.fecha_recepcion,
                    'solicitante': ingreso.solicitante
                })

    total = 0
    resumen = []
    for detalle in detalle_areas:
        resumen.append({
            'resultado': detalle,
            'frecuencia': len(detalle_areas[detalle]),
            'porcentaje': 0,
            'acumulado': 0,
            'detalle': detalle_areas[detalle]
        })

        total += len(detalle_areas[detalle])

    return (sorted(resumen, key=lambda k: k['frecuencia'], reverse=True), total)