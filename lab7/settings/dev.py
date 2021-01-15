from .base import *

INSTALLED_APPS = INSTALLED_APPS + [
    'debug_toolbar', 
    'silk',
    'django_extensions',
]

MIDDLEWARE = MIDDLEWARE + [
    # 'silk.middleware.SilkyMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug toolbar
INTERNAL_IPS = ['127.0.0.1']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
