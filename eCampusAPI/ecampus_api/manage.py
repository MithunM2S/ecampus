#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import environ
from pathlib import Path

def main():
    """Run administrative tasks."""
    try:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
