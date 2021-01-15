from .models import RegistroTemperatura


def convertidor_unidad_temperatura(temperatura, origen, destino):
    """Convierte un valor de temperatura de la unidad origen a la unidad destino pasados como parametro.

    Las unidades de conversion pueden ser Celcius o Farhenheit."""

    if origen != destino:
        # Celcius a Farhenheit
        if destino == RegistroTemperatura.FARHENHEIT:
            temperatura = float(9/5)*float(temperatura)+float(32)
        else:  # Farhenheit a Celcius
            temperatura = (float(temperatura)-float(32))*float(5/9)

    return float(temperatura)
