from django.contrib import admin

from .models import Listing, Venue


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "place_id", "rating", "review_count", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "place_id", "address")
    ordering = ("-rating", "-review_count", "name")


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("region", "category", "venue", "weighted_score", "fetched_at")
    list_filter = ("region", "category")
    search_fields = ("venue__name", "venue__place_id", "region__name", "category__name")
    ordering = ("-fetched_at", "-weighted_score")
