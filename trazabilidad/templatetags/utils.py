from django import template
from django.contrib.auth.models import Group

__author__ = 'tania'

register = template.Library()


@register.filter
def pertenece_grupo(usuario, nombre_grupo):
    """Indica si un usuario pertenece al grupo especificado."""

    try:
        Group.objects.get(name=nombre_grupo)
    except:
        return False

    return usuario.groups.filter(name=nombre_grupo).exists()


@register.filter
def values_list(queryset, id):
    """Indica si un usuario pertenece al grupo especificado."""

    try:
        return queryset.values_list(id, flat=True)
    except:
        return queryset.none()


@register.filter
def filter_by_area(queryset, filt):
    """Filtra el queryset por area."""

    try:
        return queryset.filter(area=filt)
    except:
        return queryset.none()
