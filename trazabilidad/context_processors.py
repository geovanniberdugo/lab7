from . import enums as e

def enums(request):
    return {
        'sin_resultado': e.EstadoResultadoEnum.SIN_RESULTADO,
    }