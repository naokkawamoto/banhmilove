from django.http import Http404
from django.shortcuts import render
from django.core.paginator import Paginator
from django.conf import settings
import requests

from .models import Listing
from apps.core.models import Category, Region


def home_view(request):
    regions = Region.objects.filter(is_active=True).order_by("sort_order", "name")
    categories = Category.objects.filter(is_active=True).order_by("sort_order", "name")
    ranking_base = (
        Listing.objects.select_related("venue", "region", "category")
        .filter(category__code="banh-mi")
        .order_by("-weighted_score", "-venue__rating", "-venue__review_count")
    )
    top_rows = []
    seen = set()
    for item in ranking_base:
        if item.venue_id in seen:
            continue
        seen.add(item.venue_id)
        top_rows.append(item)
        if len(top_rows) >= 5:
            break

    videos = []
    news_error = None
    youtube_api_key = getattr(settings, "YOUTUBE_API_KEY", "")
    if youtube_api_key:
        try:
            response = requests.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "part": "id,snippet",
                    "q": "バインミー",
                    "maxResults": 3,
                    "type": "video",
                    "key": youtube_api_key,
                },
                timeout=20,
            )
            response.raise_for_status()
            payload = response.json()
            for item in payload.get("items", []):
                video_id = (item.get("id") or {}).get("videoId")
                snippet = item.get("snippet") or {}
                if not video_id:
                    continue
                videos.append(
                    {
                        "video_id": video_id,
                        "title": snippet.get("title", ""),
                        "thumbnail": ((snippet.get("thumbnails") or {}).get("medium") or {}).get("url", ""),
                    }
                )
        except Exception as exc:  # pragma: no cover
            news_error = f"YouTube取得に失敗しました: {exc}"
    else:
        news_error = "YOUTUBE_API_KEY が未設定です。"

    return render(
        request,
        "catalog/home.html",
        {
            "regions": regions,
            "categories": categories,
            "top_rows": top_rows,
            "videos": videos,
            "news_error": news_error,
            "google_maps_api_key": getattr(settings, "GOOGLE_PLACES_API_KEY", ""),
        },
    )


def ranking_view(request, region_code: str, category_code: str):
    listings = (
        Listing.objects.select_related("venue", "region", "category")
        .filter(region__code=region_code, category__code=category_code)
        .order_by("-weighted_score")
    )
    if not listings.exists():
        raise Http404("Ranking not found for this region/category.")

    top_listings = listings[:50]
    first = top_listings[0]
    return render(
        request,
        "catalog/ranking.html",
        {
            "region": first.region,
            "category": first.category,
            "listings": top_listings,
        },
    )


def rank_view(request):
    # 既存互換URL: /rank/
    # MVPではバインミーカテゴリのListingを横断して上位を表示（同一venue重複は先着を採用）
    base = (
        Listing.objects.select_related("venue", "region", "category")
        .filter(category__code="banh-mi")
        .order_by("-weighted_score", "-venue__rating", "-venue__review_count")
    )
    seen = set()
    rows = []
    for item in base:
        if item.venue_id in seen:
            continue
        seen.add(item.venue_id)
        rows.append(item)
        if len(rows) >= 100:
            break
    return render(request, "catalog/rank.html", {"rows": rows})


def store_list_view(request):
    q = (request.GET.get("name") or "").strip()
    venues = (
        Listing.objects.select_related("venue")
        .filter(category__code="banh-mi", venue__is_active=True)
        .order_by("-venue__rating", "-venue__review_count")
    )

    # 同一venueの重複排除
    unique = []
    seen = set()
    for item in venues:
        if item.venue_id in seen:
            continue
        if q and q.lower() not in item.venue.name.lower():
            continue
        seen.add(item.venue_id)
        unique.append(item.venue)

    paginator = Paginator(unique, 50)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "catalog/store_list.html", {"page_obj": page_obj, "name_query": q})
