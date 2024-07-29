import datetime
from django.core.management.base import BaseCommand
import requests
from banhmilove_app.models import Store, MonthlyData
from django.db import transaction
from django.conf import settings

class Command(BaseCommand):
    help = 'Fetches Banh Mi shop data from Japan'

    PREFECTURE_MAPPING = {
        "Hokkaido": "北海道", "Aomori": "青森県", "Iwate": "岩手県", "Miyagi": "宮城県",
        "Akita": "秋田県", "Yamagata": "山形県", "Fukushima": "福島県", "Ibaraki": "茨城県",
        "Tochigi": "栃木県", "Gunma": "群馬県", "Saitama": "埼玉県", "Chiba": "千葉県",
        "Tokyo": "東京都", "Kanagawa": "神奈川県", "Niigata": "新潟県", "Toyama": "富山県",
        "Ishikawa": "石川県", "Fukui": "福井県", "Yamanashi": "山梨県", "Nagano": "長野県",
        "Gifu": "岐阜県", "Shizuoka": "静岡県", "Aichi": "愛知県", "Mie": "三重県",
        "Shiga": "滋賀県", "Kyoto": "京都府", "Osaka": "大阪府", "Hyogo": "兵庫県",
        "Nara": "奈良県", "Wakayama": "和歌山県", "Tottori": "鳥取県", "Shimane": "島根県",
        "Okayama": "岡山県", "Hiroshima": "広島県", "Yamaguchi": "山口県", "Tokushima": "徳島県",
        "Kagawa": "香川県", "Ehime": "愛媛県", "Kochi": "高知県", "Fukuoka": "福岡県",
        "Saga": "佐賀県", "Nagasaki": "長崎県", "Kumamoto": "熊本県", "Oita": "大分県",
        "Miyazaki": "宮崎県", "Kagoshima": "鹿児島県", "Okinawa": "沖縄県"
    }

    def handle(self, *args, **options):
        self.stdout.write("Fetching Banh Mi shops in Japan...")
        self.fetch_places()

    def fetch_places(self):
        locations = list(self.PREFECTURE_MAPPING.keys())
        current_date = datetime.date.today()
        current_month = current_date.strftime("%Y-%m")
        api_key = settings.GOOGLE_MAPS_API_KEY

        for location in locations:
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": f"Banh Mi shop in {location} Japan",
                "key": api_key,
                "language": "ja"
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                results = response.json().get('results', [])
                if not results:
                    self.stdout.write("No data received from API.")
                else:
                    self.save_data(results, location, current_date, current_month)
                    self.stdout.write(f"Stores in {location} fetched and saved successfully.")
            else:
                self.stdout.write(f"Failed to fetch data for {location}: {response.status_code} - {response.text}")

    def save_data(self, results, location, current_date, current_month):
        with transaction.atomic():
            for place in results:
                city = self.fetch_place_details(place['place_id'])
                prefecture_jp = self.PREFECTURE_MAPPING.get(location, location)
                store, created = Store.objects.get_or_create(
                    place_id=place.get('place_id'),
                    defaults={
                        'name': place.get('name'),
                        'prefecture': prefecture_jp,
                        'prefecture_en': location,
                        'city': city if city else "N/A",
                        'url': place.get('website', ''),
                        'rating': place.get('rating', 0),
                        'review_count': place.get('user_ratings_total', 0),
                        'latitude': place.get('geometry', {}).get('location', {}).get('lat', 0),
                        'longitude': place.get('geometry', {}).get('location', {}).get('lng', 0),
                        'registered_date': current_date,
                        'registered_month': current_month
                    }
                )
                if not created:
                    store.name = place.get('name')
                    store.prefecture = prefecture_jp
                    store.prefecture_en = location
                    store.city = city if city else "N/A"
                    store.url = place.get('website', '')
                    store.rating = place.get('rating', 0)
                    store.review_count = place.get('user_ratings_total', 0)
                    store.latitude = place.get('geometry', {}).get('location', {}).get('lat', 0)
                    store.longitude = place.get('geometry', {}).get('location', {}).get('lng', 0)
                    store.registered_date = current_date
                    store.registered_month = current_month
                    store.save()

                MonthlyData.objects.update_or_create(
                    date=current_date,
                    store=store,
                    defaults={
                        'ranking': 0,  # ランキングは後で更新する
                        'weighted_score': store.weighted_score
                    }
                )
                print(f"Saved store: {store.name} with registered date: {store.registered_date}")

    def fetch_place_details(self, place_id):
        detail_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "address_component,website",
            "key": settings.GOOGLE_MAPS_API_KEY,
            "language": "ja"
        }
        response = requests.get(detail_url, params=params)
        if response.status_code == 200:
            details = response.json().get('result', {})
            city = None
            for component in details.get('address_components', []):
                if 'locality' in component['types']:
                    city = component['long_name']
            return city
        return None
