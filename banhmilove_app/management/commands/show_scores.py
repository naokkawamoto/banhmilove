from django.core.management.base import BaseCommand
from banhmilove_app.models import Store

class Command(BaseCommand):
    help = 'Show current store data and scores'

    def handle(self, *args, **kwargs):
        stores = Store.objects.all()
        for store in stores:
            print(f'Name: {store.name}')
            print(f'Prefecture: {store.prefecture}')
            print(f'Registered Date: {store.registered_date}')
            print(f'Rating: {store.rating}')
            print(f'Review Count: {store.review_count}')
            print(f'Weighted Score: {store.weighted_score}')
            print('---')
