import requests
import uuid
import time
import re
from django.utils import timezone
from django.core.management.base import BaseCommand
from banhmilove_app.models import Store,MonthlyStoreData
from django.db import transaction
from django.conf import settings

# Google Places APIキー
API_KEY = settings.GOOGLE_MAPS_API_KEY

# クエリを「banhmi」に制限
SEARCH_QUERIES = ["banhmi","banh mi"]

# 都道府県の中心緯度経度リスト
PREFECTURE_COORDS = {    
    'Hokkaido': (43.06417, 141.34694),    
    'Aomori': (40.82444, 140.74),    
    'Iwate': (39.70361, 141.1525),    
    'Miyagi': (38.26889, 140.87194),    
    'Akita': (39.71861, 140.1025),    
    'Yamagata': (38.24056, 140.36333),    
    'Fukushima': (37.75, 140.46778),    
    'Ibaraki': (36.34139, 140.44667),    
    'Tochigi': (36.56583, 139.88361),    
    'Gunma': (36.3912, 139.0608),    
    'Saitama': (35.85694, 139.64889),    
    'Chiba': (35.60472, 140.12333),    
    'Tokyo': (35.682839, 139.759455),    
    'Kanagawa': (35.44778, 139.6425),    
    'Niigata': (37.90222, 139.02361),    
    'Toyama': (36.69528, 137.21139),    
    'Ishikawa': (36.59444, 136.62556),    
    'Fukui': (36.06528, 136.22194),    
    'Yamanashi': (35.66389, 138.56833),    
    'Nagano': (36.65139, 138.18111),    
    'Gifu': (35.39111, 136.72222),    
    'Shizuoka': (34.97694, 138.38306),    
    'Aichi': (35.18028, 136.90667),    
    'Mie': (34.73028, 136.50861),    
    'Shiga': (35.00444, 135.86833),    
    'Kyoto': (35.02139, 135.75556),    
    'Osaka': (34.693725, 135.502255),    
    'Hyogo': (34.69139, 135.18306),    
    'Nara': (34.68528, 135.83278),    
    'Wakayama': (34.22611, 135.1675),    
    'Tottori': (35.50361, 134.23833),    
    'Shimane': (35.47222, 133.05056),    
    'Okayama': (34.66167, 133.935),    
    'Hiroshima': (34.39639, 132.45944),    
    'Yamaguchi': (34.18583, 131.47139),    
    'Tokushima': (34.06583, 134.55944),    
    'Kagawa': (34.34028, 134.04333),    
    'Ehime': (33.84167, 132.76583),    
    'Kochi': (33.55972, 133.53111),    
    'Fukuoka': (33.60639, 130.41806),    
    'Saga': (33.24944, 130.29889),    
    'Nagasaki': (32.74472, 129.87361),    
    'Kumamoto': (32.78972, 130.74167),    
    'Oita': (33.23806, 131.6125),    
    'Miyazaki': (31.91111, 131.42389),    
    'Kagoshima': (31.56028, 130.55806),    
    'Okinawa': (26.2125, 127.68111)
}

def normalize_name(name):
    """店舗名の正規化: スペースや特殊文字を削除して比較可能にする"""
    return re.sub(r'\s+|☆', '', name).lower()  # スペースや特殊文字を削除して小文字化


def extract_from_address_components(address_components, types):
    """address_componentsから指定されたtypesの情報を抽出"""
    for component in address_components:
        if any(t in component['types'] for t in types):
            return component['long_name']
    return "不明"

# 例: 都道府県の抽出
prefecture = extract_from_address_components(address_components, ['administrative_area_level_1'])
# 例: 市区町村の抽出
city = extract_from_address_components(address_components, ['locality'])


def is_in_japan(address_components):
    """address_components から国が日本（Japan）であるかを確認"""
    for component in address_components:
        if 'country' in component['types'] and component['long_name'] == 'Japan':
            return True
    return False

def fetch_place_details(place_id, api_key):
    """Google Places APIのPlace Detailsから住所情報とカテゴリ、ウェブサイトを取得"""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": api_key,
        "fields": "address_components,website"
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        result = response.json().get('result', {})
        address_components = result.get('address_components', [])
        if not is_in_japan(address_components):  # 日本国外の場合はデータを無視
            return "国外", "国外", ""

        prefecture = extract_prefecture_from_address_components(address_components)
        city = extract_city_from_address_components(address_components)
        website = result.get('website', '')
        return prefecture, city, website
    else:
        print(f"Place Details APIでエラーが発生しました: {response.status_code}")
        return "不明", "不明", ""

def fetch_places():
    """Google Places API から都道府県ごとのデータを取得し、DBに保存"""
    result_count = 0  # 取得した結果の数をカウント

    for prefecture_name, coords in PREFECTURE_COORDS.items():
        for query in SEARCH_QUERIES:  # クエリを「banhmi」に制限
            session_token = uuid.uuid4()
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": query,
                "location": f"{coords[0]},{coords[1]}",
                "radius": 10000,  # 半径10km以内を指定
                "key": API_KEY,
                "language": "ja"
            }
import requests
import uuid
import time
import re
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from banhmilove_app.models import Store

# Google Places APIキー
API_KEY = settings.GOOGLE_MAPS_API_KEY

# 検索クエリを制限
SEARCH_QUERIES = ["banhmi", "banh mi"]

# 都道府県の中心緯度経度リスト
PREFECTURE_COORDS = {    
    'Hokkaido': (43.06417, 141.34694),    
    'Aomori': (40.82444, 140.74),    
    'Iwate': (39.70361, 141.1525),    
    'Miyagi': (38.26889, 140.87194),    
    'Akita': (39.71861, 140.1025),    
    'Yamagata': (38.24056, 140.36333),    
    'Fukushima': (37.75, 140.46778),    
    'Ibaraki': (36.34139, 140.44667),    
    'Tochigi': (36.56583, 139.88361),    
    'Gunma': (36.3912, 139.0608),    
    'Saitama': (35.85694, 139.64889),    
    'Chiba': (35.60472, 140.12333),    
    'Tokyo': (35.682839, 139.759455),    
    'Kanagawa': (35.44778, 139.6425),    
    'Niigata': (37.90222, 139.02361),    
    'Toyama': (36.69528, 137.21139),    
    'Ishikawa': (36.59444, 136.62556),    
    'Fukui': (36.06528, 136.22194),    
    'Yamanashi': (35.66389, 138.56833),    
    'Nagano': (36.65139, 138.18111),    
    'Gifu': (35.39111, 136.72222),    
    'Shizuoka': (34.97694, 138.38306),    
    'Aichi': (35.18028, 136.90667),    
    'Mie': (34.73028, 136.50861),    
    'Shiga': (35.00444, 135.86833),    
    'Kyoto': (35.02139, 135.75556),    
    'Osaka': (34.693725, 135.502255),    
    'Hyogo': (34.69139, 135.18306),    
    'Nara': (34.68528, 135.83278),    
    'Wakayama': (34.22611, 135.1675),    
    'Tottori': (35.50361, 134.23833),    
    'Shimane': (35.47222, 133.05056),    
    'Okayama': (34.66167, 133.935),    
    'Hiroshima': (34.39639, 132.45944),    
    'Yamaguchi': (34.18583, 131.47139),    
    'Tokushima': (34.06583, 134.55944),    
    'Kagawa': (34.34028, 134.04333),    
    'Ehime': (33.84167, 132.76583),    
    'Kochi': (33.55972, 133.53111),    
    'Fukuoka': (33.60639, 130.41806),    
    'Saga': (33.24944, 130.29889),    
    'Nagasaki': (32.74472, 129.87361),    
    'Kumamoto': (32.78972, 130.74167),    
    'Oita': (33.23806, 131.6125),    
    'Miyazaki': (31.91111, 131.42389),    
    'Kagoshima': (31.56028, 130.55806),    
    'Okinawa': (26.2125, 127.68111)
}

def normalize_name(name):
    """店舗名の正規化: スペースや特殊文字を削除して比較可能にする"""
    return re.sub(r'\s+|☆', '', name).lower()  # スペースや特殊文字を削除して小文字化

def extract_from_address_components(address_components, types):
    """address_componentsから指定されたtypesの情報を抽出"""
    for component in address_components:
        if any(t in component['types'] for t in types):
            return component['long_name']
    return "不明"

def is_in_japan(address_components):
    """address_components から国が日本（Japan）であるかを確認"""
    for component in address_components:
        if 'country' in component['types'] and component['long_name'] == 'Japan':
            return True
    return False

def fetch_place_details(place_id, api_key):
    """Google Places APIのPlace Detailsから住所情報とウェブサイトを取得"""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": api_key,
        "fields": "address_components,website"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Place Details APIでエラーが発生しました: {e}")
        return "不明", "不明", ""

    result = response.json().get('result', {})
    address_components = result.get('address_components', [])

    if not is_in_japan(address_components):  # 日本国外の場合は無視
        return "国外", "国外", ""

    prefecture = extract_from_address_components(address_components, ['administrative_area_level_1'])
    city = extract_from_address_components(address_components, ['locality'])
    website = result.get('website', '')
    
    return prefecture, city, website

def fetch_places():
    """Google Places API から都道府県ごとのデータを取得し、マスターDBに保存"""
    result_count = 0  # 取得した結果の数をカウント

    for prefecture_name, coords in PREFECTURE_COORDS.items():
        for query in SEARCH_QUERIES:
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": query,
                "location": f"{coords[0]},{coords[1]}",
                "radius": 10000,  # 半径10km以内を指定
                "key": API_KEY,
                "language": "ja"
            }

            while True:  # ページングを繰り返して全データを取得
                try:
                    response = requests.get(url, params=params)
                    response.raise_for_status()
                except requests.RequestException as e:
                    print(f"データ取得中にエラーが発生しました: {e}")
                    break

                results = response.json().get('results', [])
                if not results:
                    break

                with transaction.atomic():
                    for place in results:
                        name = place.get('name', 'N/A')
                        place_id = place.get('place_id')

                        # Place Detailsから住所、ウェブサイト情報を取得
                        prefecture, city, website = fetch_place_details(place_id, API_KEY)

                        # 日本国内のデータかどうかを確認
                        if prefecture == "国外":
                            continue

                        latitude = place['geometry']['location'].get('lat')
                        longitude = place['geometry']['location'].get('lng')
                        rating = place.get('rating', 0)
                        review_count = place.get('user_ratings_total', 0)
                        registered_date = timezone.now().date()

                        # DBに保存（データの重複を防ぐために正規化を使用）
                        normalized_name = normalize_name(name)
                        Store.objects.update_or_create(
                            place_id=place_id,
                            defaults={
                                'name': normalized_name,  # 正規化された名前
                                'prefecture': prefecture,
                                'city': city,
                                'url': website or '',
                                'rating': rating,
                                'review_count': review_count,
                                'latitude': latitude,
                                'longitude': longitude,
                                'registered_date': registered_date
                            }
                        )

                        result_count += 1
                        print(f"現在までに保存したデータ数: {result_count}")

                next_page_token = response.json().get('next_page_token')
                if next_page_token:
                    params['pagetoken'] = next_page_token
                    time.sleep(2)  # APIリクエストの間隔を開ける
                else:
                    break

class Command(BaseCommand):
    help = "Google Places APIから都道府県ごとのデータを取得し、DBに保存"

    def handle(self, *args, **kwargs):
        fetch_places()
        self.stdout.write(self.style.SUCCESS('データの取得とDBへの保存が完了しました。'))
            while True:  # ページングを繰り返して全データを取得
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    results = response.json().get('results', [])
                    if not results:
                        break
                    with transaction.atomic():
                        for place in results:
                            name = place.get('name', 'N/A')
                            place_id = place.get('place_id')

                            # Place Detailsから住所、カテゴリ、ウェブサイト情報を取得
                            prefecture, city, website = fetch_place_details(place_id, API_KEY)

                            # 日本国内のデータかどうかを確認
                            if prefecture == "国外":
                                continue

                            latitude = place['geometry']['location'].get('lat')
                            longitude = place['geometry']['location'].get('lng')
                            rating = place.get('rating', 0)
                            review_count = place.get('user_ratings_total', 0)
                            registered_date = timezone.now().date()

                            # DBに保存
                            normalized_name = normalize_name(name)
                            Store.objects.update_or_create(
                                place_id=place_id,
                                defaults={
                                    'name': name,
                                    'prefecture': prefecture,
                                    'city': city,
                                    'url': website or '',
                                    'rating': rating,
                                    'review_count': review_count,
                                    'latitude': latitude,
                                    'longitude': longitude,
                                    'registered_date': registered_date
                                }
                            )

                            result_count += 1
                            print(f"現在までに保存したデータ数: {result_count}")

                    next_page_token = response.json().get('next_page_token')
                    if next_page_token:  # 次のページがあれば取得
                        params['pagetoken'] = next_page_token
                        time.sleep(2)
                    else:
                        break
                else:
                    print(f"Error fetching data: {response.status_code}, {response.text}")
                    break

class Command(BaseCommand):
    help = "Google Places APIから都道府県ごとのデータを取得し、DBに保存"

    def handle(self, *args, **kwargs):
        fetch_places()
        self.stdout.write(self.style.SUCCESS('データの取得とDBへの保存が完了しました。'))

