from django.urls import path

from .views import about_us_view, about_view, blog_detail_view, blog_index_view, news_view

app_name = "content"

urlpatterns = [
    path("about/", about_view, name="about"),
    path("about_us/", about_us_view, name="about_us"),
    path("news/", news_view, name="news"),
    path("blog/", blog_index_view, name="blog_index"),
    path("blog/<slug:slug>/", blog_detail_view, name="blog_detail"),
]
