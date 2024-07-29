from django.core.management.base import BaseCommand
from banhmilove_app.models import Store

class Command(BaseCommand):
    help = 'Delete all existing store data'

    def handle(self, *args, **options):
        Store.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all store data'))
