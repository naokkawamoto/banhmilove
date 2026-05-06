from django.urls import path

from .views import home_view, rank_view, ranking_view, store_list_view

app_name = "catalog"

urlpatterns = [
    path("", home_view, name="home"),
    path("rank/", rank_view, name="rank"),
    path("store_list/", store_list_view, name="store_list"),
    path("ranking/<slug:region_code>/<slug:category_code>/", ranking_view, name="ranking"),
]
