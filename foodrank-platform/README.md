# FoodRank Platform

地域 x ジャンルで飲食店ランキングを表示する、ログイン不要の汎用プラットフォームです。

## MVP方針

- 対象: 日本国内のみ
- 地域: 固定マスタ（都道府県、東京23区、政令指定都市）
- ジャンル: バインミー、マーラータン
- データソース: Google Places APIのみ（手動登録なし）
- 収益化: ベータ時はPR枠月額1000円（将来5000円へ改定）

## ディレクトリ

- `docs/requirements-v0.3.md`: 要件定義
- `docs/setup-aws-google.md`: AWS / Google API設定手順
- `.env.example`: 環境変数テンプレート
- `docker-compose.yml`: ローカル開発用コンテナ定義

## 次ステップ

1. `.env.example` を `.env` にコピーして値を設定
2. 既存 `banhmilove` からモデル・ビューを汎用構造へ移植
3. Django新規プロジェクトをこの配下に作成
4. AWS本番構成（RDS / ECS or App Runner）を確定
