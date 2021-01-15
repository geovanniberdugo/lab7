# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import environ

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = environ.Path(__file__) - 3

ENV = environ.Env()
ENV.read_env()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENV('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ENV.list('ALLOWED_HOSTS', default=['localhost'])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'polymorphic',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sequences.apps.SequencesConfig',
    'django_countries',
    'rest_framework',
    'cie10_django',
    'crispy_forms',
    'import_export',
    'reversion',
    'waffle',

    'administracion',
    'trazabilidad',
    'bebidas_alcoholicas',
    'alimentos',
    'equipos',
    'covid19',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'waffle.middleware.WaffleMiddleware',
    'reversion.middleware.RevisionMiddleware',
]

ROOT_URLCONF = 'lab7.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'context_processors.site',
                'trazabilidad.context_processors.enums',
            ],
        },
    },
]

WSGI_APPLICATION = 'lab7.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': ENV.db()
}

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    # { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    # { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
]

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'es-CO'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_L10N = True

USE_TZ = True

FORMAT_MODULE_PATH = [
    'lab7.formats',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR('../static')
STATICFILES_DIRS = (BASE_DIR('static'),)

# Media files

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR('../media')
FILE_UPLOAD_PERMISSIONS = 0o644

# Authentication URLs

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'trazabilidad:home'

# Cryspi template
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Rest framework
REST_FRAMEWORK = {
    'DATETIME_FORMAT': '%d de %B de %Y a las %I:%M %p',
}

DEFAULT_FROM_EMAIL = ENV('EMAIL_SENDER')

# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG'
    }
}
