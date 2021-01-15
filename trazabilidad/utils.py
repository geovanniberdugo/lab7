from sequences import get_next_value


def nuevo_radicado(alternativo=False):
    """
    Devuelve el nuevo radicado.

    Se usa la secuencia radicado_alternativo para las muestras de los programas EEDD, EEID y Citohistopatologia y
    radicado para los demas programas.
    """

    if alternativo:
        radicado = get_next_value('radicado_alternativo')
    else:
        radicado = get_next_value('radicado', initial_value=172)

    return radicado
