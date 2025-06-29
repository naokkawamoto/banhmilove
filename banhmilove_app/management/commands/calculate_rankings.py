import datetime
from django.core.management.base import BaseCommand
from banhmilove_app.models import Store, MonthlyData
from django.db.models import F
from django.db import transaction

class Command(BaseCommand):
    help = '店舗のランキングを計算して保存するコマンド'

    def handle(self, *args, **options):
        self.stdout.write("店舗のランキングを計算しています...")

        try:
            # 現在の年月を取得
            current_date = datetime.date.today()
            year = current_date.year
            month = current_date.month

            # トランザクション内でランキングを計算して保存
            with transaction.atomic():
                # 上位100位までの店舗データを取得 (weighted_scoreとreview_countで降順ソート)
                stores = MonthlyData.objects.filter(
                    date__year=year,
                    date__month=month,
                    store__isnull=False
                ).order_by('-weighted_score', '-store__review_count')[:100]  # トップ100店舗のみ取得

                # ランキング順位を計算して保存
                for rank, store_data in enumerate(stores, start=1):
                    store_data.ranking = rank
                    store_data.save()
                    self.stdout.write(f"{store_data.store.name}のランキング: {rank}位, 加重スコア: {store_data.weighted_score}")

            self.stdout.write(f"{year}年{month}月のランキングを保存しました。")

        except Exception as e:
            self.stderr.write(f"ランキング計算中にエラーが発生しました: {str(e)}")
