# AWS / Google API セットアップ手順

## 1. Google Cloud

1. プロジェクトを作成
2. 以下APIを有効化
   - Places API
   - YouTube Data API v3（ニュース表示で利用する場合）
3. APIキーを発行
4. APIキー制限を設定
   - HTTPリファラ制限（本番ドメイン）
   - 必要APIのみに制限

## 2. X / TikTok 連携の注意

- X APIは有料プラン・レート制限を確認してから導入
- TikTokは利用用途制限があるため、導入前に審査要件を確認
- MVPでは必須にせず、後続フェーズで検証

## 3. AWS（推奨最小構成）

- アプリ: ECS Fargate または App Runner
- DB: RDS PostgreSQL
- 静的ファイル: S3 + CloudFront
- シークレット管理: AWS Secrets Manager
- ログ: CloudWatch Logs

## 4. 環境変数

`.env.example` の全項目を本番環境変数に設定する。

## 5. デプロイ時チェック

- `DEBUG=False`
- `ALLOWED_HOSTS` に本番ドメインを設定
- DB接続先がRDSになっていること
- APIキーがコードへ直書きされていないこと
