import requests
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone
from django.conf import settings

from .models import Post


def blog_index_view(request):
    lang = request.GET.get("lang", "ja")
    if lang not in ("ja", "en"):
        lang = "ja"

    posts = Post.objects.filter(
        status=Post.Status.PUBLISHED,
        lang=lang,
        published_at__lte=timezone.now(),
    ).order_by("-published_at")

    return render(
        request,
        "content/blog_index.html",
        {
            "posts": posts,
            "lang": lang,
        },
    )


def blog_detail_view(request, slug: str):
    lang = request.GET.get("lang", "ja")
    if lang not in ("ja", "en"):
        lang = "ja"

    try:
        post = Post.objects.get(
            slug=slug,
            lang=lang,
            status=Post.Status.PUBLISHED,
            published_at__lte=timezone.now(),
        )
    except Post.DoesNotExist as exc:
        raise Http404("Post not found.") from exc

    return render(request, "content/blog_detail.html", {"post": post, "lang": lang})


def about_view(request):
    return render(request, "content/about.html")


def about_us_view(request):
    return render(request, "content/about_us.html")


def news_view(request):
    api_key = getattr(settings, "YOUTUBE_API_KEY", "")
    videos = []
    error = None

    if not api_key:
        error = "YOUTUBE_API_KEY が未設定です。"
    else:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "id,snippet",
            "q": "バインミー",
            "maxResults": 10,
            "type": "video",
            "key": api_key,
        }
        try:
            response = requests.get(url, params=params, timeout=20)
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
                        "description": snippet.get("description", ""),
                        "thumbnail": ((snippet.get("thumbnails") or {}).get("medium") or {}).get("url", ""),
                    }
                )
        except Exception as exc:  # pragma: no cover
            error = f"ニュース取得に失敗しました: {exc}"

    return render(request, "content/news.html", {"videos": videos, "error": error})
