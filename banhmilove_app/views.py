from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone
from django.db import models
from .models import Store, MonthlyData
from collections import defaultdict
from django.conf import settings
from django.db.models import Count, Max
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime

def home(request):
    current_year = timezone.now().year
    current_month = timezone.now().month

    top_ranking_stores = MonthlyData.objects.filter(
        date__year=current_year, date__month=current_month
    ).order_by('-weighted_score')[:5]

    youtube_api_key = settings.YOUTUBE_API_KEY
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    search_response = {}

    try:
        search_response = youtube.search().list(
            q='バインミー',
            part='id,snippet',
            maxResults=3,
            type='video'
        ).execute()
    except HttpError as e:
        print(f"An error occurred: {e}")
        print(f"Error details: {e.content}")
        return render(request, 'banhmilove_app/home.html', {
            'top_ranking_stores': top_ranking_stores,
            'videos': [],
            'error': str(e),
            'error_details': e.content
        })

    videos = []
    for item in search_response.get('items', []):
        video_data = {
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'video_id': item['id']['videoId'],
            'thumbnail': item['snippet']['thumbnails']['default']['url']
        }
        videos.append(video_data)

    return render(request, 'banhmilove_app/home.html', {
        'top_ranking_stores': top_ranking_stores,
        'videos': videos
    })

def new_store(request):
    current_month = timezone.now().month
    current_year = timezone.now().year

    new_stores = Store.objects.filter(registered_date__year=current_year, registered_date__month=current_month)

    return render(request, 'banhmilove_app/new_store.html', {
        'new_stores': new_stores,
    })
    


def analysis(request):
    # 都道府県別の店舗数をカウント
    latest_month = datetime.date(2024, 6, 1)
    prefecture_counts = Store.objects.filter(registered_date__year=2024, registered_date__month=6).values('prefecture_en').annotate(count=Count('id'))

    # ヒートマップ用データの準備
    heatmap_data = [["都道府県", "店舗数"]]
    for item in prefecture_counts:
        heatmap_data.append([item['prefecture_en'], item['count']])

    # 月別の店舗数をカウント
    monthly_counts = Store.objects.values('registered_month').annotate(count=Count('id')).order_by('registered_month')

    # グラフ用データの準備
    graph_data = [["月", "店舗数"]]
    for item in monthly_counts:
        month_str = item['registered_month']  # 既に文字列であればそのまま使用
        graph_data.append([month_str, item['count']])

    # デバッグ用のログ出力
    print("ヒートマップ用データ:", heatmap_data)
    print("グラフ用データ:", graph_data)

    return render(request, 'banhmilove_app/analysis.html', {
        'heatmap_data': heatmap_data,
        'graph_data': graph_data,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
    })
    
def news(request):
    youtube_api_key = settings.YOUTUBE_API_KEY
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)

    try:
        search_response = youtube.search().list(
            q='バインミー',
            part='id,snippet',
            maxResults=10,
            type='video'
        ).execute()
    except HttpError as e:
        return render(request, 'banhmilove_app/news.html', {'error': str(e)})

    videos = [
        {
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'video_id': item['id']['videoId'],
            'thumbnail': item['snippet']['thumbnails']['default']['url']
        }
        for item in search_response.get('items', [])
    ]

    return render(request, 'banhmilove_app/news.html', {'videos': videos})

def about(request):
    return render(request, 'banhmilove_app/about.html')

def about_us(request):
    return render(request, 'banhmilove_app/about_us.html')

def store_list(request):
    prefecture = request.GET.get('prefecture')
    name_query = request.GET.get('name')
    
    # 5月のストアを取得
    may_stores = Store.objects.filter(registered_date__year=2024, registered_date__month=5)
    # 6月のストアを取得
    june_stores = Store.objects.filter(registered_date__year=2024, registered_date__month=6)

    # 6月のストアIDリスト
    june_store_ids = june_stores.values_list('id', flat=True)

    # 閉鎖した店舗リスト
    closed_stores = may_stores.exclude(id__in=june_store_ids)

    # 5月と6月のストアリストをマージ
    stores = june_stores.union(may_stores).order_by('registered_date')

    # 検索フィルタ
    if prefecture:
        stores = stores.filter(prefecture=prefecture)
    
    if name_query:
        stores = stores.filter(name__icontains=name_query)

    paginator = Paginator(stores, 50)  # 1ページに表示する店舗数を50に設定
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    prefectures = Store.objects.values_list('prefecture', flat=True).distinct()

    return render(request, 'banhmilove_app/store_list.html', {
        'page_obj': page_obj,
        'prefecture': prefecture,
        'name_query': name_query,
        'prefectures': prefectures,
        'closed_stores': closed_stores,
    })

from django.db.models import Max
from django.utils import timezone

def national_ranking(request):
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))

    # 最新の月次データを取得
    latest_monthly_data = MonthlyData.objects.filter(
        date__year=year, date__month=month, store__review_count__gte=100, store__rating__gte=4.5
    ).order_by('-weighted_score', '-store__review_count')

    for idx, data in enumerate(latest_monthly_data):
        data.ranking = idx + 1

    months = list(range(1, 13))
    data_exists = latest_monthly_data.exists()

    return render(request, 'banhmilove_app/rank.html', {
        'stores': latest_monthly_data,
        'year': year,
        'month': month,
        'months': months,
        'data_exists': data_exists,
    })

