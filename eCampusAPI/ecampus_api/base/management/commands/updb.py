from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = 'Update DB'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''delete from django_migrations where app='admin';''')
        cursor.execute('''drop table django_admin_log''')

        self.stdout.write(self.style.SUCCESS('db update successfully'))
