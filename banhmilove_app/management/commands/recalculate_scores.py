from django.core.management.base import BaseCommand
from banhmilove_app.models import Store

class Command(BaseCommand):
    help = 'Recalculate weighted scores for all stores'

    def handle(self, *args, **kwargs):
        stores = Store.objects.all()
        for store in stores:
            store.calculate_weighted_score()
            store.save()
            self.stdout.write(self.style.SUCCESS(f'Updated {store.name} with new weighted score: {store.weighted_score}'))
