from django.core.management.base import BaseCommand, CommandError
from api_authentication import models


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)

    def handle(self, *args, **options):
        try:
            name = options.get('name', 'eCampus')
            org = models.Organization.objects.create(name=name)
            key, value = models.OrganizationAPIKey.objects.create_key(organization=org, name=name)
            self.stdout.write(self.style.SUCCESS('New API key - %s' % value))
        except AuthUser.DoesNotExist:
            raise CommandError('Technocal error "%s", please try again' %user)

