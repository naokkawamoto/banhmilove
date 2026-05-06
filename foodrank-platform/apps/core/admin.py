from django.contrib import admin

from .models import Category, Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "level", "parent", "is_active", "is_major_focus")
    list_filter = ("level", "is_active", "is_major_focus")
    search_fields = ("name", "code")
    ordering = ("sort_order", "name")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "search_keyword", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "code", "search_keyword")
    ordering = ("sort_order", "name")
