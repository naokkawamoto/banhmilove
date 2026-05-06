from django.db import models


class Region(models.Model):
    class Level(models.TextChoices):
        PREFECTURE = "prefecture", "都道府県"
        DESIGNATED_CITY = "designated_city", "政令指定都市"
        CITY = "city", "市区町村"
        WARD = "ward", "区"
        MAJOR_AREA = "major_area", "主要エリア"

    code = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=Level.choices)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    is_active = models.BooleanField(default=True)
    is_major_focus = models.BooleanField(
        default=False,
        help_text="人口上位都道府県など、主要エリア展開対象の地域フラグ",
    )
    search_keywords = models.JSONField(
        default=list,
        blank=True,
        help_text="Places API 検索補助キーワード",
    )
    center_lat = models.FloatField(null=True, blank=True)
    center_lng = models.FloatField(null=True, blank=True)
    radius_m = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Places検索半径（メートル）。未設定の場合は上位地域の設定を利用できるようにする想定。",
    )
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["level", "is_active"]),
            models.Index(fields=["parent", "sort_order"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.level})"


class Category(models.Model):
    code = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    search_keyword = models.CharField(
        max_length=255,
        help_text="Google Places API 検索キーワード",
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["is_active", "sort_order"]),
        ]

    def __str__(self):
        return self.name
