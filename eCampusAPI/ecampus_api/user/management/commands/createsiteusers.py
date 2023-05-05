from django.core.management.base import BaseCommand, CommandError
from user.models import AuthUser
from django.contrib.auth.models import Group
import json
from django.contrib.auth.models import Group
import boto3, os
from django.conf import settings


class Command(BaseCommand):
    help = 'Create site users'

    def handle(self, *args, **options):
        try:
            data = None
            # S3 credentilas
            if os.getenv('ENVIRONMENT', None) == "PROD":
                access_key_id = os.environ.get('AWS_S3_ACCESS_KEY_ID', None)
                secret_access_key = os.environ.get('AWS_S3_SECRET_ACCESS_KEY', None)
                # connecting with s3
                s3_client = boto3.client('s3', aws_access_key_id= access_key_id, aws_secret_access_key=secret_access_key)
                obj = s3_client.get_object(Bucket='creaxio', Key='creaxio-ecampus-config.json')
                data = json.loads(obj['Body'].read())
                site_users = data.get('site_users', None)
            else:
                lab = {"site_users":[{
                            "username": "superadmin",
                            "password": "superadmin",
                            "is_superuser": 1,
                            "is_staff": 1,
                            "is_active": 1
                        },
                        {
                            "username": "lab.admin",
                            "password": "lab.admin",
                            "is_superuser": 0,
                            "is_staff": 1,
                            "is_active": 1
                        }]
                }
                site_users = lab.get('site_users')
            if site_users:
                for site_user in site_users:
                    if not AuthUser.objects.filter(username=site_user.get('username')).exists():
                        # creating user
                        user = AuthUser.objects.create_user(**site_user)
                        if not Group.objects.filter(name='admin').exists():
                            Group.objects.create(name='admin')
                        group = Group.objects.get(name='admin')
                        group.user_set.add(user)
        except AuthUser.DoesNotExist:
            raise CommandError('Technocal error please try again')
        self.stdout.write(self.style.SUCCESS('Site users are created'))
