from django.core.management.base import BaseCommand
from banhmilove_app.models import Store, MonthlyData
from django.utils import timezone
from django.db.models import Max

class Command(BaseCommand):
    help = 'Update or create monthly data for stores'

    def handle(self, *args, **kwargs):
        current_date = timezone.now().date()
        stores = Store.objects.all()

        for store in stores:
            store.save()  # ここでcalculate_weighted_scoreが呼び出される

            MonthlyData.objects.update_or_create(
                store=store,
                date=current_date,
                defaults={'weighted_score': store.weighted_score}
            )
        self.stdout.write(self.style.SUCCESS('Successfully updated monthly data for all stores.'))
