from .base import *

DEBUG = False

EMAIL_HOST_PASSWORD = ENV('EMAIL_HOST_PASSWORD')
EMAIL_HOST_USER = ENV('EMAIL_HOST_USER')
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_USE_TLS = True
EMAIL_PORT = '587'