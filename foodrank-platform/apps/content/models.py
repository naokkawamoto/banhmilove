from django.db import models
from django.utils import timezone


class Post(models.Model):
    class Language(models.TextChoices):
        JA = "ja", "日本語"
        EN = "en", "English"

    class Status(models.TextChoices):
        DRAFT = "draft", "下書き"
        PUBLISHED = "published", "公開"

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    body = models.TextField()
    lang = models.CharField(max_length=2, choices=Language.choices, default=Language.JA)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    meta_description = models.CharField(max_length=255, blank=True, default="")
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["slug", "lang"], name="uniq_post_slug_lang"),
        ]
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "lang", "-published_at"]),
        ]

    def publish(self):
        self.status = self.Status.PUBLISHED
        if not self.published_at:
            self.published_at = timezone.now()

    def __str__(self):
        return f"[{self.lang}] {self.title}"
