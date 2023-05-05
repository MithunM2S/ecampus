"""
WSGI config for ecampus_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import environ
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    BASE_DIR = Path(__file__).parents[2]
    if os.path.exists(os.path.join(BASE_DIR, '.env')):
        environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))
        if os.getenv('ENVIRONMENT') == "DEV":
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecampus_api.settings.dev')
        elif os.getenv('ENVIRONMENT') == "PROD":
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecampus_api.settings.prod')
        else:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecampus_api.settings.local')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecampus_api.settings.local')
except:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecampus_api.settings.local')

application = get_wsgi_application()
