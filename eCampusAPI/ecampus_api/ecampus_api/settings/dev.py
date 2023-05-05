from ecampus_api.settings.site_settings import * 

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', False)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', True)

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', False).split(' ')

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DATABASE_NAME', False),
        'HOST': '',
        'USER': os.environ.get('DATABASE_USER', False),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', False),
        'PORT': '',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}


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

CORS_ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', False).split(' ')

SMS_API_ENDPOINT = os.environ.get('SMS_API_ENDPOINT', False)
SMS_API_KEY = os.environ.get('SMS_API_KEY', False)
SMS_SENDER_ID = os.environ.get('SMS_SENDER_ID', False)
SMS_PREFIX = 'MAX MULLER PUBLIC SCHOOL: '

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': os.environ.get('DB_BACKUP_PATH', False)}