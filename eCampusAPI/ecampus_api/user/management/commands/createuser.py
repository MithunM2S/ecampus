from django.core.management.base import BaseCommand, CommandError
from user.models import AuthUser
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Create user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('--staff', action='store_true')

    def handle(self, *args, **options):
        try:
            is_staff = False
            if options['staff']:
                is_staff = True
            if not AuthUser.objects.filter(username=options['username']).exists():
                user = AuthUser.objects.create_user(
                    username = options['username'],
                    password = options['password']
                )
                group = Group.objects.get(name='admin')
                auth_user = AuthUser.objects.get(username = options['username'])
                auth_user.groups.add(group)
                self.stdout.write(self.style.SUCCESS('user created "%s"' % options['username']))
            else:
                self.stdout.write(self.style.SUCCESS('user already exists "%s"' % options['username']))
        except AuthUser.DoesNotExist:
            raise CommandError('Technocal error "%s", please try again' %user)

