from django.contrib.auth.decorators import user_passes_test

__author__ = 'tania'


def grupo_requerido(*grupos):
    """Chequea que el usuario pertenezca a alguno de los grupos ingresados."""

    def en_grupos(user):
        if user.is_authenticated:
            if user.groups.filter(name__in=grupos).exists() | user.groups.filter(name='super usuario').exists():
                return True
            return False
        return False

    return user_passes_test(en_grupos)