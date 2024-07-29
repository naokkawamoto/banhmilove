from django.core.management.base import BaseCommand
from django.db.models import Max
from banhmilove_app.models import MonthlyData

class Command(BaseCommand):
    help = 'Cleanse old monthly data, keeping only the latest data for each store.'

    def handle(self, *args, **kwargs):
        latest_monthly_data = MonthlyData.objects.values('store').annotate(latest_date=Max('date'))

        for data in latest_monthly_data:
            MonthlyData.objects.filter(store=data['store']).exclude(date=data['latest_date']).delete()

        self.stdout.write(self.style.SUCCESS('Successfully cleansed old monthly data.'))
