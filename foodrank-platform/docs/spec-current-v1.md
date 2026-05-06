# FoodRank Platform 現時点仕様 v1

更新日: 2026-05-06

## 1. 目的

ログイン不要で、地域 x ジャンルの外食店ランキングを表示する。  
バインミーは先行ジャンルの1つで、今後同じ仕組みでジャンルを増やす。

## 2. スコープ（現時点）

- 対象地域: 日本国内
- 地域管理: 固定マスタ（都道府県、主要エリア）
- MVPジャンル: バインミー、マーラータン
- データソース: Google Places API
- ログイン: なし
- 言語: 日本語先行（英語は後フェーズ）
- 収益化: 後フェーズ（PR枠販売、広告）

## 3. データモデル（実装済み）

- `Region`（apps.core）
  - `code`, `name`, `level`, `parent`, `is_active`, `is_major_focus`
  - `search_keywords`, `center_lat`, `center_lng`, `radius_m`, `sort_order`
- `Category`（apps.core）
  - `code`, `name`, `search_keyword`, `is_active`, `sort_order`
- `Venue`（apps.catalog）
  - `place_id`, `name`, `address`, `lat`, `lng`, `rating`, `review_count`
  - `website_url`, `google_maps_url`, `is_active`, `last_fetched_at`
- `Listing`（apps.catalog）
  - `region`, `category`, `venue`, `weighted_score`, `fetched_at`
  - 一意制約: `(region, category, venue)`
- `Post`（apps.content）
  - `title`, `slug`, `body`, `lang`, `status`, `meta_description`, `published_at`

## 4. 画面・URL（実装済み）

- `/` : 地域 x ジャンル選択トップ
- `/ranking/<region_code>/<category_code>/` : ランキング表示
- `/blog/` : ブログ一覧（`?lang=ja|en`）
- `/blog/<slug>/` : ブログ詳細（`?lang=ja|en`）
- `/admin/` : 管理画面
- `/health/` : ヘルスチェック

## 5. バッチ/API運用方針（確定）

- Places API:
  - ランキング用データはDB保存
  - 定期更新は月1回を基本
  - 必要時に手動実行可能
- 地図表示時の絞り込み:
  - リアルタイムAPIは必要時のみ
  - 方式: 半径 + 車（driving）時間で絞る想定
- YouTube:
  - 週1回更新（DB or キャッシュ保存）
  - 表示時の毎回APIコールは避ける

## 6. Places取得コマンド（実装済み）

コマンド:

`python manage.py fetch_places --region <code> --category <code> [--limit N] [--dry-run]`

仕様:

- `Region` の中心座標 + 半径で Nearby Search
- 件数不足時は半径を段階拡張（例: 3000 -> 5000 -> 8000...）
- `banh-mi` は複数キーワード検索して統合
- `place_id` で重複排除
- 関連度フィルタ（店名に `banh` / `bánh` / `バインミー`）
- `Venue` / `Listing` を upsert

## 7. 初期データ（実装済み）

`python manage.py seed_initial_data`

- Category:
  - `banh-mi`（バインミー）
  - `malatang`（マーラータン）
- Region:
  - `tokyo`
  - `tokyo-shimokitazawa`
  - `tokyo-sangenjaya`
  - `tokyo-futakotamagawa`

## 8. インフラ方針

- 開発: Docker Compose + Postgres
- 本番候補: Lightsail 先行（コスト優先）
- 将来移行: App Runner/ECS + RDS を検討

## 9. 進捗マイルストーン（現時点）

- M1 基盤: 100%
- M2 取得バッチ: 100%
- M3 表示/SEOブログ: 100%
- M4 本番化（AWS）: 0%（次フェーズ）

## 10. 次フェーズ（M4）タスク

1. Lightsail構築（Docker本番起動）
2. ドメイン接続・HTTPS化
3. 本番用Secrets/環境変数整理
4. バッチ実行（月1/週1）のスケジューリング
5. バックアップ/監視の最小導入

