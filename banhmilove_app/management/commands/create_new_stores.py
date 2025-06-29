import datetime
from django.core.management.base import BaseCommand
from banhmilove_app.models import Store, NewStore

class Command(BaseCommand):
    help = 'Extract new stores registered this month and save them to the NewStore table.'

    def handle(self, *args, **kwargs):
        current_date = datetime.date.today()
        current_month = current_date.strftime('%Y-%m')
        
        # 前月の日付を計算
        previous_month = current_date.replace(day=1) - datetime.timedelta(days=1)
        previous_month_str = previous_month.strftime('%Y-%m')

        self.stdout.write(f"新規店舗データを生成します: 現在の月 {current_month} と前月 {previous_month_str}")

        # 前月に登録された店舗のplace_idを取得
        previous_month_stores = Store.objects.filter(registered_month=previous_month_str).values_list('place_id', flat=True)
        
        # 今月に登録された店舗のうち、前月には存在しないものを取得
        new_stores = Store.objects.filter(registered_month=current_month).exclude(place_id__in=previous_month_stores)

        # 新規店舗をNewStoreテーブルに保存
        for store in new_stores:
            NewStore.objects.get_or_create(
                store=store,
                registered_date=store.registered_date,
                month=current_month
            )
            self.stdout.write(f"新規店舗を保存しました: {store.name}")

        self.stdout.write("新規店舗の保存が完了しました。")
