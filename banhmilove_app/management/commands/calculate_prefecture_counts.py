import datetime
from django.core.management.base import BaseCommand
from banhmilove_app.models import Store, MonthlyData
from django.db.models import Count

class Command(BaseCommand):
    help = 'Calculates and saves the number of Banh Mi shops by prefecture for the current month.'

    def handle(self, *args, **options):
        self.stdout.write("都道府県別の店舗数を集計します...")
        
        current_date = datetime.date.today()
        current_month = current_date.strftime("%Y-%m")

        # 都道府県ごとの店舗数をカウント
        prefecture_counts = Store.objects.values('prefecture').annotate(store_count=Count('id'))

        for data in prefecture_counts:
            prefecture = data['prefecture']
            store_count = data['store_count']

            # MonthlyDataに都道府県ごとのデータを保存
            MonthlyData.objects.create(
                date=current_date,
                store=None,  # 店舗単位ではないのでNoneにします
                prefecture=prefecture,  # 都道府県名を保存
                count=store_count,  # 各都道府県の店舗数を保存
                weighted_score=0,  # 店舗の加重スコアは関係ないため0に設定
            )

            self.stdout.write(f"{prefecture} の店舗数 {store_count} を保存しました。")

        self.stdout.write("都道府県ごとの集計が完了しました。")

