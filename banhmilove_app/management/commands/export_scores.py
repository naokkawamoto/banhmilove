import csv
from django.core.management.base import BaseCommand
from banhmilove_app.models import Store

class Command(BaseCommand):
    help = 'Export store data and scores to a CSV file'

    def handle(self, *args, **kwargs):
        # CSVファイルのパス
        file_path = 'store_scores.csv'

        # CSVファイルのヘッダー
        headers = ['Name', 'Prefecture', 'Registered Date', 'Rating', 'Review Count', 'Weighted Score']

        # データを取得
        stores = Store.objects.all()

        # CSVファイルにデータを書き込む
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)  # ヘッダーを書き込む
            for store in stores:
                writer.writerow([
                    store.name,
                    store.prefecture,
                    store.registered_date,
                    store.rating,
                    store.review_count,
                    store.weighted_score
                ])

        self.stdout.write(self.style.SUCCESS(f'Data exported successfully to {file_path}'))
