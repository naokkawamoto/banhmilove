from django.contrib import admin
from django.urls import path
from banhmilove_app import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('rank/', views.national_ranking, name='rank'),
    path('new_store/', views.new_store, name='new_store'),
    path('analysis/', views.analysis, name='analysis'),
    path('news/', views.news, name='news'),
    path('about/', views.about, name='about'),
    path('about_us/', views.about_us, name='about_us'),
    path('store_list/', views.store_list, name='store_list'), 
]
