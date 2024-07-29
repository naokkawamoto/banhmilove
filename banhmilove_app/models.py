from django.db import models

class Store(models.Model):
    name = models.CharField(max_length=255)  # 店名
    prefecture = models.CharField(max_length=100)  # 都道府県
    prefecture_en = models.CharField(max_length=100, default="Unknown")
    city = models.CharField(max_length=100)  # 市区町村
    website = models.URLField(blank=True, null=True)
    url = models.URLField()  # URL
    rating = models.FloatField()  # レーティング
    review_count = models.IntegerField()  # レビュー数
    latitude = models.FloatField()  # 緯度
    longitude = models.FloatField()  # 経度
    place_id = models.CharField(max_length=255, unique=True) # Google Place ID
    weighted_score = models.FloatField(null=True, blank=True)  # 加重スコア
    registered_date = models.DateField()  # 取得日
    registered_month = models.CharField(max_length=7, default='2024-01')  # 取得月 (YYYY-MM形式)


    class Store(models.Model):
        name = models.CharField(max_length=255)  # 店名
        prefecture = models.CharField(max_length=100)  # 都道府県
        prefecture_en = models.CharField(max_length=100, default="Unknown")
        city = models.CharField(max_length=100)  # 市区町村
        website = models.URLField(blank=True, null=True)
        url = models.URLField()  # URL
        rating = models.FloatField()  # レーティング
        review_count = models.IntegerField()  # レビュー数
        latitude = models.FloatField()  # 緯度
        longitude = models.FloatField()  # 経度
        place_id = models.CharField(max_length=255, unique=True)  # Google Place ID
        weighted_score = models.FloatField(null=True, blank=True)  # 加重スコア
        registered_date = models.DateField()  # 取得日
        registered_month = models.CharField(max_length=7, default='2024-01')  # 取得月 (YYYY-MM形式)

    def calculate_weighted_score(self):
        if self.review_count == 0 or self.rating < 4.5:
            self.weighted_score = 0
            return

        avg_rating = Store.objects.aggregate(models.Avg('rating'))['rating__avg'] or 0
        avg_reviews = Store.objects.aggregate(models.Avg('review_count'))['review_count__avg'] or 0

        m = avg_reviews
        C = avg_rating

        # Adjusting the weight factor based on the number of reviews
        weight_factor = min((self.review_count / m) ** 0.5, 2)  # Upper limit for weight_factor

        self.weighted_score = ((weight_factor * self.review_count / (self.review_count + m)) * self.rating) + ((m / (self.review_count + m)) * C)

        # Adjusting score for exceptionally high review counts to prevent manipulation
        if self.review_count > 3 * avg_reviews:
            self.weighted_score *= 0.9

    def save(self, *args, **kwargs):
        self.calculate_weighted_score()
        super().save(*args, **kwargs)    
            
class MonthlyData(models.Model):
    date = models.DateField()  # 取得日
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    ranking = models.IntegerField(default=0)  # ランキング順位にデフォルト値を設定
    weighted_score = models.FloatField()  # 加重スコア

    class Meta:
        unique_together = ('date', 'store')