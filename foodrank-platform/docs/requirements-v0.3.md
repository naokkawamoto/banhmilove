# 要件定義 v0.3

## 1. 目的

ユーザーが「地域 x ジャンル」で外食候補を素早く比較できるランキングサイトを提供する。

## 2. スコープ

- ログインなし
- 日本国内のみ
- 多言語対応: 日本語・英語（インバウンド向け）
- 地域マスタは固定管理
- ジャンルはMVPで2件（バインミー、マーラータン）
- 店舗データはGoogle Places APIのみ

## 3. 地域要件

- 都道府県: 47件
- 都市圏:
  - 東京23区
  - 政令指定都市
- URLの最小単位は `region_slug` で管理

## 4. ランキング要件

- 店舗並び順は `weighted_score DESC, rating DESC, review_count DESC`
- `weighted_score` は共通スコア関数を利用
- PR枠はランキング本体と分離表示

## 5. 収益化要件

- ベータ料金: 月額1000円
- 価格改定: PV増加時に月額5000円
- 販売単位: `地域 x ジャンル x 月`
- 表示単位:
  - 都道府県ページは都道府県契約を表示
  - 区市ページは区市契約を表示

## 6. 非機能要件

- 秘密情報は環境変数で管理
- 本番はAWSで稼働
- 本番DBはRDB（PostgreSQL想定）
- API取得失敗時はログを記録して表示を継続
- i18n対応:
  - URLまたはUI切替で `ja` / `en` を選択可能
  - 地域名・ジャンル名・固定文言は翻訳テーブルまたはDjango i18nで管理
  - SEO用に言語別メタ情報と hreflang を設定

## 7. 初期データ項目（論理）

- Category: code, name, search_keyword, is_active
- Region: code, name, level, parent_code, is_active
- Venue: place_id, name, address, rating, review_count, lat, lng, maps_url
- Listing: category_code, region_code, venue_id, weighted_score, fetched_at
- SponsorSlot: region_code, category_code, plan_price, start_at, end_at, status

## 8. 多言語要件（MVP）

- 対応言語: 日本語（既定）/ 英語
- 英語ページの目的: インバウンドユーザー向けの検索流入獲得
- 英語化対象:
  - ナビゲーション、固定ページ、ランキング見出し、フィルタ文言
  - 地域名・ジャンル名（管理画面で翻訳可能にする）
- データソース由来の店舗名は原文優先（無理な機械翻訳はしない）
- URL案:
  - 日本語: `/ja/{region}/{category}/`
  - 英語: `/en/{region}/{category}/`
