
ENGINE = 'django.db.backends.postgresql_psycopg2'
USER = 'german1234'
PASSWORD = '1234'
HOST = '127.0.0.1'
PORT = '5432'

DATABASES = {
    'default': {
        'ENGINE': ENGINE,
        'NAME': 'lab7',
        'USER': USER,
        'PASSWORD': PASSWORD,
        'HOST': HOST,
        'PORT': PORT,
    },
    'backup': {
        'ENGINE': ENGINE,
        'NAME': 'backup',
        'USER': USER,
        'PASSWORD': PASSWORD,
        'HOST': HOST,
        'PORT': PORT,
    }
}


def main():
    from django.contrib.auth.models import User
    from trazabilidad.models import PruebasRealizadas as model, Muestra

    for prueba in model.objects.all():
        try:
            prueba_vieja = model.objects.using('backup').get(id=prueba.id)

            prueba.ultima_modificacion = prueba_vieja.ultima_modificacion
            prueba.save()
        except model.DoesNotExist:
            try:
                if prueba.muestra.registro_recepcion.reportes.first() is not None:
                    if prueba.muestra.registro_recepcion.reportes.first().fecha is not None:
                        prueba.ultima_modificacion = prueba.muestra.registro_recepcion.reportes.first().fecha
                        prueba.save()
                        continue
            except Muestra.DoesNotExist:
                pass

            if prueba.fecha_pre_analisis is not None and prueba.prueba.duracion is not None:
                prueba.ultima_modificacion = prueba.fecha_pre_analisis + prueba.prueba.duracion
                prueba.save()

if __name__ == '__main__':
    import os
    from django.core.wsgi import get_wsgi_application
    from django.conf import settings
    import django

    # os.environ['DJANGO_SETTINGS_MODULE'] = 'lab7.settings'
    # application = get_wsgi_application()
    settings.configure(DATABASES=DATABASES)
    django.setup()
    main()
