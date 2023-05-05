from ecampus_api.settings.site_settings import * 

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', False)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

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

CORS_ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', False).split(' ')

SMS_API_ENDPOINT = os.environ.get('SMS_API_ENDPOINT', False)
# 'https://api.textlocal.in/send/?'

SMS_API_KEY = os.environ.get('SMS_API_KEY', False)
# 'EC28M2FgjL8-v45PpkRDTOu9xxAjdoKRtesSphgFEV'
SMS_SENDER_ID = os.environ.get('SMS_SENDER_ID', False)
# 'CHILDR'

SMS_PREFIX = 'MAX MULLER PUBLIC SCHOOL: '

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': os.environ.get('DB_BACKUP_PATH', False)}