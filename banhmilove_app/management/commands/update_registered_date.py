import datetime
from django.core.management.base import BaseCommand
from banhmilove_app.models import Store

class Command(BaseCommand):
    help = 'Update registered date for existing store data'

    def handle(self, *args, **options):
        may_date = datetime.date(2024, 5, 16)
        june_date = datetime.date(2024, 6, 16)

        # デフォルト値で設定された登録日を使って5月と6月のデータを区別します
        default_date = datetime.date(2024, 1, 1)

        # 5月のデータを更新
        may_stores = Store.objects.filter(registered_date=default_date).exclude(place_id__in=Store.objects.filter(registered_date=june_date).values_list('place_id', flat=True))
        for store in may_stores:
            store.registered_date = may_date
            store.save()
            self.stdout.write(f'Updated {store.name} with registered date {may_date}')

        # 6月のデータを更新
        june_stores = Store.objects.filter(registered_date=default_date, place_id__in=Store.objects.filter(registered_date=june_date).values_list('place_id', flat=True))
        for store in june_stores:
            store.registered_date = june_date
            store.save()
            self.stdout.write(f'Updated {store.name} with registered date {june_date}')
