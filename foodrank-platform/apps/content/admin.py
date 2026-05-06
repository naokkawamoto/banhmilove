from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "lang", "status", "published_at", "updated_at")
    list_filter = ("lang", "status")
    search_fields = ("title", "slug", "body")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-published_at", "-updated_at")
