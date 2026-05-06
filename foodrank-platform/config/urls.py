from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import include, path
from django.utils import timezone

from apps.content.models import Post
from apps.core.models import Category, Region


def health(_request):
    return JsonResponse({"status": "ok"})


def robots_txt(_request):
    body = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Sitemap: /sitemap.xml",
        ]
    )
    return HttpResponse(body, content_type="text/plain; charset=utf-8")


def sitemap_xml(request):
    base = f"{request.scheme}://{request.get_host()}"
    urls = [
        f"{base}/",
        f"{base}/rank/",
        f"{base}/store_list/",
        f"{base}/news/",
        f"{base}/about/",
        f"{base}/about_us/",
        f"{base}/blog/",
    ]

    for region in Region.objects.filter(is_active=True):
        for category in Category.objects.filter(is_active=True):
            urls.append(f"{base}/ranking/{region.code}/{category.code}/")

    for post in Post.objects.filter(status=Post.Status.PUBLISHED, published_at__lte=timezone.now()):
        urls.append(f"{base}/blog/{post.slug}/?lang={post.lang}")

    xml_items = "".join([f"<url><loc>{loc}</loc></url>" for loc in urls])
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{xml_items}</urlset>'
    return HttpResponse(xml, content_type="application/xml; charset=utf-8")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health, name="health"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap_xml, name="sitemap_xml"),
    path("", include("apps.content.urls")),
    path("", include("apps.catalog.urls")),
]
