from django.core.management.base import BaseCommand
from banhmilove_app.models import Store, MonthlyData
from datetime import date

class Command(BaseCommand):
    help = 'Updates monthly rankings for Banh Mi shops'

    def handle(self, *args, **options):
        self.stdout.write("Updating monthly rankings for Banh Mi shops...")
        self.update_rankings()

    def update_rankings(self):
        current_date = date.today()
        # Filtering data for the current month
        monthly_data = MonthlyData.objects.filter(
            date__year=current_date.year,
            date__month=current_date.month
        ).select_related('store').order_by('-weighted_score', '-store__review_count')

        for rank, data in enumerate(monthly_data, start=1):
            data.ranking = rank
            data.save()
            self.stdout.write(f"Updated ranking for store: {data.store.name} to {rank}")
