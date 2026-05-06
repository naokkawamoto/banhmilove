from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.models import Category, Region


class Command(BaseCommand):
    help = "Seed initial Categories and Regions (idempotent)."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding categories...")
        categories = [
            {"code": "banh-mi", "name": "バインミー", "search_keyword": "バインミー", "sort_order": 10},
            {"code": "malatang", "name": "マーラータン", "search_keyword": "麻辣湯", "sort_order": 20},
        ]
        for data in categories:
            obj, created = Category.objects.update_or_create(code=data["code"], defaults=data)
            self.stdout.write(f"- {'created' if created else 'updated'} Category: {obj.code}")

        self.stdout.write("Seeding regions...")
        tokyo, _ = Region.objects.update_or_create(
            code="tokyo",
            defaults={
                "name": "東京都",
                "level": Region.Level.PREFECTURE,
                "parent": None,
                "is_active": True,
                "is_major_focus": True,
                "search_keywords": ["Tokyo", "東京都"],
                "center_lat": 35.6896,
                "center_lng": 139.6917,
                "radius_m": 30000,
                "sort_order": 10,
            },
        )

        major_areas = [
            {
                "code": "tokyo-shimokitazawa",
                "name": "下北沢",
                "center_lat": 35.6617,
                "center_lng": 139.6686,
                "radius_m": 3000,
                "sort_order": 11,
                "search_keywords": ["下北沢", "Shimokitazawa", "下北沢駅"],
            },
            {
                "code": "tokyo-sangenjaya",
                "name": "三軒茶屋",
                "center_lat": 35.6433,
                "center_lng": 139.6690,
                "radius_m": 3000,
                "sort_order": 12,
                "search_keywords": ["三軒茶屋", "Sangenjaya", "三軒茶屋駅"],
            },
            {
                "code": "tokyo-futakotamagawa",
                "name": "二子玉川",
                "center_lat": 35.6122,
                "center_lng": 139.6277,
                "radius_m": 3000,
                "sort_order": 13,
                "search_keywords": ["二子玉川", "Futakotamagawa", "二子玉川駅"],
            },
        ]

        for data in major_areas:
            obj, created = Region.objects.update_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "level": Region.Level.MAJOR_AREA,
                    "parent": tokyo,
                    "is_active": True,
                    "is_major_focus": False,
                    "search_keywords": data["search_keywords"],
                    "center_lat": data["center_lat"],
                    "center_lng": data["center_lng"],
                    "radius_m": data["radius_m"],
                    "sort_order": data["sort_order"],
                },
            )
            self.stdout.write(f"- {'created' if created else 'updated'} Region: {obj.code}")

        self.stdout.write(self.style.SUCCESS("Seed completed."))

