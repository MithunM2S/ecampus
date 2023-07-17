from ecampus_api.settings.site_settings import * 

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'U5MeEsZr.BtRlbnseTsLBwYW0ptAV7QgORibuVuq3SY9yGpIrvf1NnQR8yLWd7hz8dRCVsdfq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
import os

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ihs_ganesha_building',
        'HOST': '',
        'USER': 'surya-dev',
        'PASSWORD': '111111',
        'PORT': '',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}


CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:8080",
    "http://localhost:8000",
    'http://creaxiotechnologies.com',
    'http://vbes.in',
    "http://localhost:4200"
]

SWAGGER_SETTINGS = {
   'SECURITY_DEFINITIONS': {
        'APIKey': {
            'type': 'apiKey',
            'name': 'X-API-KEY',
            'in': 'header'
        },
        'eCampus': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            "bearerFormat": "eCampus ",
        },
   },
}

SMS_API_ENDPOINT = 'http://msg.mtalkz.com/V2/http-api-post.php'
SMS_API_KEY = 'DXEwv8fjp9utApl6'
SMS_SENDER_ID = 'CREAXO'
SMS_PREFIX = 'MAX MULLER PUBLIC SCHOOL: '

STATIC_URL = 'static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/var/ecampus-backup/db/'}