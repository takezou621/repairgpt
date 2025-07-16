# 🐳 RepairGPT Docker Guide

このガイドでは、RepairGPTをDockerを使用してセットアップ・実行する方法を説明します。

## 📋 前提条件

- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)

## 🚀 クイックスタート

### 1. 環境設定

```bash
# 環境設定ファイルをコピー
cp .env.example .env

# .envファイルを編集してAPIキーを設定
nano .env  # または任意のエディタ
```

### 2. 開発環境の起動

```bash
# セットアップスクリプトを実行可能にする
chmod +x docker-setup.sh

# 開発環境を起動（ホットリロード有効）
./docker-setup.sh dev
```

### 3. 本番環境の起動

```bash
# 本番環境を起動
./docker-setup.sh prod
```

## 🔧 詳細な使用方法

### セットアップスクリプト

`docker-setup.sh` スクリプトは以下のコマンドをサポートしています：

```bash
./docker-setup.sh dev     # 開発環境を起動
./docker-setup.sh prod    # 本番環境を起動
./docker-setup.sh stop    # サービスを停止
./docker-setup.sh clean   # コンテナとボリュームをクリーンアップ
./docker-setup.sh build   # Dockerイメージをビルド
./docker-setup.sh logs    # ログを表示
./docker-setup.sh help    # ヘルプを表示
```

### 手動でのDocker Compose使用

#### 開発環境

```bash
# 開発環境を起動
docker-compose -f docker-compose.dev.yml up --build -d

# ログを確認
docker-compose -f docker-compose.dev.yml logs -f

# 停止
docker-compose -f docker-compose.dev.yml down
```

#### 本番環境

```bash
# 本番環境を起動
docker-compose up --build -d

# ログを確認
docker-compose logs -f

# 停止
docker-compose down
```

## 🌐 アクセス情報

サービス起動後、以下のURLでアクセスできます：

- **API**: http://localhost:8000
- **API ドキュメント**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501
- **PostgreSQL**: localhost:5432 (開発: 5433)
- **Redis**: localhost:6379 (開発: 6380)

## 📁 Docker構成ファイル

### メインファイル

- `Dockerfile` - FastAPI バックエンド用
- `Dockerfile.streamlit` - Streamlit UI用
- `docker-compose.yml` - 本番環境構成
- `docker-compose.dev.yml` - 開発環境構成
- `.dockerignore` - ビルド最適化
- `.env.example` - 環境変数テンプレート

### サービス構成

#### FastAPI Backend (`api`)
- **ポート**: 8000
- **ヘルスチェック**: `http://localhost:8000/`
- **依存**: PostgreSQL, Redis

#### Streamlit UI (`ui`)
- **ポート**: 8501
- **ヘルスチェック**: `http://localhost:8501/`
- **依存**: FastAPI Backend

#### PostgreSQL Database (`postgres`)
- **ポート**: 5432 (本番), 5433 (開発)
- **データベース**: repairgpt
- **永続化**: Dockerボリューム

#### Redis Cache (`redis`)
- **ポート**: 6379 (本番), 6380 (開発)
- **永続化**: Dockerボリューム
- **設定**: AOF有効

## 🔐 環境変数

以下の環境変数が必要です：

### 必須API キー
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
IFIXIT_API_KEY=your-ifixit-api-key-here
```

### データベース設定
```bash
POSTGRES_DB=repairgpt
POSTGRES_USER=repairgpt
POSTGRES_PASSWORD=secure_password_change_me
DATABASE_URL=postgresql://repairgpt:secure_password_change_me@postgres:5432/repairgpt
```

### Redis設定
```bash
REDIS_PASSWORD=secure_redis_password
REDIS_URL=redis://:secure_redis_password@redis:6379/0
```

### アプリケーション設定
```bash
ENVIRONMENT=production
SECRET_KEY=generate_a_secure_secret_key_here
DEBUG=false
```

## 🔧 トラブルシューティング

### よくある問題

#### 1. ポートが使用中
```bash
# 使用中のポートを確認
lsof -i :8000
lsof -i :8501

# 環境変数でポートを変更
export API_PORT=8001
export UI_PORT=8502
```

#### 2. データベース接続エラー
```bash
# PostgreSQLのヘルスチェック
docker-compose exec postgres pg_isready -U repairgpt

# データベースログを確認
docker-compose logs postgres
```

#### 3. APIキーエラー
```bash
# 環境変数を確認
docker-compose exec api env | grep API_KEY

# .envファイルの設定を確認
cat .env
```

#### 4. Docker ビルドエラー
```bash
# キャッシュをクリアしてビルド
docker-compose build --no-cache

# 未使用リソースをクリーンアップ
docker system prune -f
```

### ログの確認

```bash
# 全サービスのログ
./docker-setup.sh logs

# 特定のサービスのログ
./docker-setup.sh logs api
./docker-setup.sh logs ui
./docker-setup.sh logs postgres
./docker-setup.sh logs redis

# リアルタイムログ
docker-compose logs -f api
```

### データベースのリセット

```bash
# データベースボリュームを削除してリセット
docker-compose down -v
docker-compose up -d
```

## 🔒 セキュリティ考慮事項

### 本番環境での推奨設定

1. **強力なパスワード**: デフォルトパスワードを変更
2. **HTTPS**: リバースプロキシ（Nginx/Traefik）の使用
3. **ファイアウォール**: 必要なポートのみ開放
4. **シークレット管理**: Docker secrets または環境変数管理ツールの使用
5. **定期更新**: 定期的なイメージ・依存関係の更新

### 非rootユーザー

Dockerfileは非rootユーザー（`repairgpt`）で実行されるよう設定されています。

## 📊 監視とパフォーマンス

### ヘルスチェック

各サービスにはヘルスチェックが設定されています：

```bash
# ヘルスチェック状態を確認
docker-compose ps
```

### リソース使用量

```bash
# コンテナのリソース使用量を確認
docker stats

# ディスク使用量を確認
docker system df
```

## 🚀 本番デプロイメント

### 推奨構成

1. **ロードバランサー**: Nginx/HAProxy
2. **SSL/TLS**: Let's Encrypt/Cloudflare
3. **監視**: Prometheus + Grafana
4. **ログ管理**: ELK Stack/Fluentd
5. **バックアップ**: 定期的なデータベースバックアップ

### スケーリング

```bash
# APIサービスをスケール
docker-compose up -d --scale api=3

# リソース制限を設定（docker-compose.yml内）
resources:
  limits:
    cpus: '0.5'
    memory: 512M
```

## 📞 サポート

問題が発生した場合：

1. ログを確認してエラーメッセージを確認
2. [GitHub Issues](https://github.com/takezou621/repairgpt/issues)で報告
3. 設定ファイルと環境変数を再確認

---

🐳 Dockerを使用してRepairGPTをお楽しみください！