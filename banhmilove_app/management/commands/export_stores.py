import csv
from django.core.management.base import BaseCommand
from banhmilove_app.models import Store
import os

class Command(BaseCommand):
    help = 'Export store data to CSV'

    def handle(self, *args, **kwargs):
        # CSVファイルのパスを指定
        file_path = os.path.join(os.path.dirname(__file__), 'stores_list.csv')

        # フィールド名を定義
        fieldnames = ['name', 'prefecture', 'city', 'website', 'url', 'rating', 'review_count', 'latitude', 'longitude', 'place_id', 'registered_date']

        # CSVファイルを作成
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(fieldnames)

            # データベースからストアデータを取得して書き込む
            stores = Store.objects.all()
            for store in stores:
                writer.writerow([
                    store.name,
                    store.prefecture,
                    store.city,
                    store.website,
                    store.url,
                    store.rating,
                    store.review_count,
                    store.latitude,
                    store.longitude,
                    store.place_id,
                    store.registered_date,
                ])

        self.stdout.write(self.style.SUCCESS(f'Successfully exported store data to {file_path}'))
