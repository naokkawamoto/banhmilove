import time
from dataclasses import dataclass

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.catalog.models import Listing, Venue
from apps.core.models import Category, Region


PLACES_NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"


@dataclass(frozen=True)
class PlaceResult:
    place_id: str
    name: str
    address: str
    lat: float | None
    lng: float | None
    rating: float
    review_count: int


def weighted_score(rating: float, review_count: int) -> float:
    if review_count <= 0 or rating <= 0:
        return 0.0
    rating_weight = 0.7
    review_weight = 0.3
    normalized_reviews = min(review_count / 100, 10)  # 0..10
    return (rating * rating_weight) + (normalized_reviews * review_weight) * 10


def maps_url(place_id: str) -> str:
    return f"https://www.google.com/maps/place/?q=place_id:{place_id}"


def fetch_nearby(*, key: str, lat: float, lng: float, radius_m: int, keyword: str, limit: int) -> list[PlaceResult]:
    results: list[PlaceResult] = []
    pagetoken: str | None = None

    while len(results) < limit:
        params = {
            "key": key,
            "location": f"{lat},{lng}",
            "radius": radius_m,
            "keyword": keyword,
            "type": "restaurant",
        }
        if pagetoken:
            params["pagetoken"] = pagetoken

        r = requests.get(PLACES_NEARBY_URL, params=params, timeout=20)
        r.raise_for_status()
        payload = r.json()
        status = payload.get("status")

        if status == "INVALID_REQUEST" and pagetoken:
            # pagetoken は生成後すぐは使えないので少し待つ
            time.sleep(2)
            continue

        if status not in ("OK", "ZERO_RESULTS"):
            raise CommandError(f"Places API error: status={status} message={payload.get('error_message')}")

        for item in payload.get("results", []):
            geom = (item.get("geometry") or {}).get("location") or {}
            results.append(
                PlaceResult(
                    place_id=item.get("place_id", ""),
                    name=item.get("name", ""),
                    address=item.get("vicinity", "") or item.get("formatted_address", "") or "",
                    lat=geom.get("lat"),
                    lng=geom.get("lng"),
                    rating=float(item.get("rating") or 0.0),
                    review_count=int(item.get("user_ratings_total") or 0),
                )
            )
            if len(results) >= limit:
                break

        pagetoken = payload.get("next_page_token")
        if not pagetoken:
            break
        time.sleep(2)

    # place_idが空のものを除外
    return [p for p in results if p.place_id]


def default_keywords_for(category: Category) -> list[str]:
    base = (category.search_keyword or "").strip()
    if category.code == "banh-mi":
        # 表記揺れ対策（ノイズを増やしにくい範囲に限定）
        extras = ["Banh Mi", "バインミー専門"]
        return [k for k in [base, *extras] if k]
    if category.code == "malatang":
        extras = ["麻辣湯", "マーラータン", "malatang"]
        uniq: list[str] = []
        for k in [base, *extras]:
            k = (k or "").strip()
            if k and k not in uniq:
                uniq.append(k)
        return uniq
    return [base] if base else []


def merge_results(results: list[PlaceResult]) -> list[PlaceResult]:
    # place_idで重複排除しつつ、より情報量が多いものを優先
    by_id: dict[str, PlaceResult] = {}
    for r in results:
        existing = by_id.get(r.place_id)
        if not existing:
            by_id[r.place_id] = r
            continue
        # review_countが多い方を残す（同点ならratingが高い方）
        if (r.review_count, r.rating) > (existing.review_count, existing.rating):
            by_id[r.place_id] = r
    return list(by_id.values())


def is_relevant_result(category: Category, place: PlaceResult) -> bool:
    name = (place.name or "").lower()
    if category.code == "banh-mi":
        return any(token in name for token in ["banh", "bánh", "バインミー"])
    if category.code == "malatang":
        return any(token in name for token in ["麻辣湯", "マーラータン", "malatang"])
    return True


class Command(BaseCommand):
    help = "Fetch venues from Google Places API and upsert Venue/Listing."

    def add_arguments(self, parser):
        parser.add_argument("--region", required=True, help="Region.code (e.g. tokyo-shimokitazawa)")
        parser.add_argument("--category", required=True, help="Category.code (e.g. banh-mi)")
        parser.add_argument("--limit", type=int, default=20, help="Max results to fetch (default: 20)")
        parser.add_argument("--min-results", type=int, default=5, help="If results < this, expand radius")
        parser.add_argument(
            "--radius-steps",
            default="3000,5000,8000,15000,30000",
            help="Comma-separated radius meters used for fallback expansion",
        )
        parser.add_argument(
            "--keywords",
            default="",
            help="Override keywords (comma-separated). If empty, uses category defaults (with aliases).",
        )
        parser.add_argument("--dry-run", action="store_true", help="Do not write to DB")

    @transaction.atomic
    def handle(self, *args, **options):
        key = getattr(settings, "GOOGLE_PLACES_API_KEY", "") or ""
        if not key:
            raise CommandError("GOOGLE_PLACES_API_KEY is not set.")

        region_code: str = options["region"]
        category_code: str = options["category"]
        limit: int = options["limit"]
        min_results: int = options["min_results"]
        dry_run: bool = options["dry_run"]

        try:
            region = Region.objects.get(code=region_code, is_active=True)
        except Region.DoesNotExist as e:
            raise CommandError(f"Region not found or inactive: {region_code}") from e

        try:
            category = Category.objects.get(code=category_code, is_active=True)
        except Category.DoesNotExist as e:
            raise CommandError(f"Category not found or inactive: {category_code}") from e

        # region の中心点が無い場合は親を遡る
        search_region = region
        while search_region and (search_region.center_lat is None or search_region.center_lng is None):
            search_region = search_region.parent
        if not search_region or search_region.center_lat is None or search_region.center_lng is None:
            raise CommandError("Region center_lat/center_lng is not set (and no parent has it).")

        # radius は region -> 親を遡って利用できるようにする
        radius_region = region
        while radius_region and not radius_region.radius_m:
            radius_region = radius_region.parent
        base_radius = int(radius_region.radius_m) if radius_region and radius_region.radius_m else 3000

        try:
            radius_steps = [int(x.strip()) for x in str(options["radius_steps"]).split(",") if x.strip()]
        except ValueError as e:
            raise CommandError("--radius-steps must be comma-separated integers") from e

        if base_radius not in radius_steps:
            radius_steps = [base_radius] + [r for r in radius_steps if r != base_radius]

        override_keywords = [k.strip() for k in str(options["keywords"]).split(",") if k.strip()]
        keywords = override_keywords or default_keywords_for(category)
        if not keywords:
            raise CommandError("No keywords configured for this category.")
        fetched_at = timezone.now()

        self.stdout.write(
            f"Fetching: region={region.code} category={category.code} keywords={keywords} "
            f"center=({search_region.center_lat},{search_region.center_lng}) base_radius={base_radius}m limit={limit}"
        )

        all_results: list[PlaceResult] = []
        used_radius: int | None = None
        for r_m in radius_steps:
            used_radius = r_m
            merged: list[PlaceResult] = []
            for kw in keywords:
                res = fetch_nearby(
                    key=key,
                    lat=float(search_region.center_lat),
                    lng=float(search_region.center_lng),
                    radius_m=r_m,
                    keyword=kw,
                    limit=limit,
                )
                merged.extend(res)

            merged = merge_results(merged)
            merged = [p for p in merged if is_relevant_result(category, p)]
            # スコア順にソートして上位だけ残す
            merged.sort(key=lambda p: (weighted_score(p.rating, p.review_count), p.rating, p.review_count), reverse=True)
            all_results = merged[:limit]
            self.stdout.write(f"- radius={r_m}m keywords={len(keywords)} unique_results={len(all_results)}")
            if len(all_results) >= min_results or r_m == radius_steps[-1]:
                break

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run: no DB writes."))
            for p in all_results[:5]:
                self.stdout.write(f"  * {p.name} rating={p.rating} reviews={p.review_count} {p.address}")
            return

        upserted_venues = 0
        upserted_listings = 0
        for p in all_results:
            venue_defaults = {
                "name": p.name,
                "address": p.address,
                "lat": p.lat,
                "lng": p.lng,
                "rating": p.rating,
                "review_count": p.review_count,
                "google_maps_url": maps_url(p.place_id),
                "last_fetched_at": fetched_at,
                "is_active": True,
            }
            venue, _created = Venue.objects.update_or_create(place_id=p.place_id, defaults=venue_defaults)
            upserted_venues += 1

            Listing.objects.update_or_create(
                region=region,
                category=category,
                venue=venue,
                defaults={
                    "weighted_score": weighted_score(p.rating, p.review_count),
                    "fetched_at": fetched_at,
                },
            )
            upserted_listings += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. radius_used={used_radius}m venues_upserted={upserted_venues} listings_upserted={upserted_listings}"
            )
        )

