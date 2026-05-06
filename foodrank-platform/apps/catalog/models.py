from django.db import models


class Venue(models.Model):
    place_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, default="")
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    rating = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)
    website_url = models.URLField(blank=True, default="")
    google_maps_url = models.URLField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    last_fetched_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-rating", "-review_count", "name"]
        indexes = [
            models.Index(fields=["is_active", "-rating", "-review_count"]),
        ]

    def __str__(self):
        return self.name


class Listing(models.Model):
    region = models.ForeignKey("core.Region", on_delete=models.CASCADE)
    category = models.ForeignKey("core.Category", on_delete=models.CASCADE)
    venue = models.ForeignKey("catalog.Venue", on_delete=models.CASCADE)
    weighted_score = models.FloatField(default=0.0)
    fetched_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["region", "category", "venue"],
                name="uniq_listing_region_category_venue",
            )
        ]
        indexes = [
            models.Index(fields=["region", "category", "-weighted_score"]),
            models.Index(fields=["fetched_at"]),
        ]

    def __str__(self):
        return f"{self.region} / {self.category} / {self.venue}"
