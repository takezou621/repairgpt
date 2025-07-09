# RepairGPT クイックスタートガイド

## 📋 前提条件

### システム要件
- **OS**: macOS 10.15+, Ubuntu 20.04+, Windows 10+
- **Python**: 3.9以上
- **メモリ**: 8GB以上推奨
- **ストレージ**: 10GB以上の空き容量

### 必要なアカウント
- **GitHub**: ソースコード取得
- **OpenAI**: GPT-4 API利用（オプション）
- **Anthropic**: Claude API利用（オプション）

## 🚀 5分でスタート

### 1. リポジトリクローン

```bash
# HTTPSでクローン
git clone https://github.com/takezou621/repairgpt.git
cd repairgpt

# または SSH でクローン
git clone git@github.com:takezou621/repairgpt.git
cd repairgpt
```

### 2. 仮想環境セットアップ

```bash
# Python仮想環境作成
python -m venv venv

# 仮想環境アクティベート
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 依存関係インストール

```bash
# 基本依存関係
pip install -r requirements.txt

# 開発依存関係（開発者のみ）
pip install -r requirements-dev.txt
```

### 4. 環境設定

```bash
# 環境変数ファイル作成
cp .env.example .env

# 設定値編集
nano .env  # またはお好みのエディタ
```

**`.env` ファイル例**:
```env
# API Keys（オプション）
OPENAI_API_KEY=your_openai_key_here
CLAUDE_API_KEY=your_claude_key_here

# データベース設定
DATABASE_URL=sqlite:///./repairgpt.db

# アプリケーション設定
DEBUG=True
LOG_LEVEL=INFO
```

### 5. アプリケーション起動

```bash
# Streamlit UIを起動
streamlit run src/main.py

# または開発サーバー
python -m uvicorn src.api.main:app --reload
```

### 6. 動作確認

ブラウザで以下にアクセス:
- **Streamlit UI**: http://localhost:8501
- **API ドキュメント**: http://localhost:8000/docs

## 🔧 詳細セットアップ

### 開発環境構築

#### 1. 開発ツールセットアップ

```bash
# コード品質ツール
pip install flake8 black isort mypy

# テストツール
pip install pytest pytest-cov pytest-mock

# セキュリティツール
pip install bandit safety
```

#### 2. Git設定

```bash
# Git hooks設定
cp scripts/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit

# コミットメッセージテンプレート
git config commit.template .gitmessage
```

#### 3. IDE設定

**VS Code** (推奨):
```bash
# 拡張機能インストール
code --install-extension ms-python.python
code --install-extension ms-python.flake8
code --install-extension ms-python.black-formatter
```

**PyCharm**:
- Python Interpreter: `./venv/bin/python`
- Code Style: Black
- Linter: flake8

### データベース設定

#### 開発環境（SQLite）

```bash
# データベース初期化
python scripts/init_db.py

# マイグレーション実行
python scripts/migrate.py
```

#### 本番環境（PostgreSQL）

```bash
# PostgreSQL接続設定
export DATABASE_URL="postgresql://user:password@localhost/repairgpt"

# テーブル作成
python scripts/create_tables.py
```

### API設定

#### iFixit API

```bash
# API キー取得（無料）
# https://www.ifixit.com/api/2.0/doc

# 環境変数設定
export IFIXIT_API_KEY="your_ifixit_key"
```

#### OpenAI API

```bash
# API キー取得
# https://platform.openai.com/api-keys

# 環境変数設定
export OPENAI_API_KEY="your_openai_key"
```

#### Claude API

```bash
# API キー取得
# https://console.anthropic.com/

# 環境変数設定
export CLAUDE_API_KEY="your_claude_key"
```

## 🧪 テスト実行

### 単体テスト

```bash
# 全テスト実行
pytest

# カバレッジ付き
pytest --cov=src --cov-report=html

# 特定のテストファイル
pytest tests/test_chatbot.py

# 詳細出力
pytest -v -s
```

### 統合テスト

```bash
# API テスト
pytest tests/integration/

# E2E テスト
pytest tests/e2e/
```

### コード品質チェック

```bash
# リント
flake8 src/

# フォーマット
black src/

# インポート整理
isort src/

# 型チェック
mypy src/

# セキュリティチェック
bandit -r src/
```

## 🐳 Docker セットアップ

### 開発環境

```bash
# イメージビルド
docker build -t repairgpt:dev .

# コンテナ起動
docker run -p 8501:8501 -p 8000:8000 repairgpt:dev

# または docker-compose
docker-compose up --build
```

### 本番環境

```bash
# 本番用イメージビルド
docker build -f Dockerfile.prod -t repairgpt:prod .

# 本番環境起動
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 監視・ログ

### ログ設定

```bash
# ログディレクトリ作成
mkdir -p logs

# ログレベル設定
export LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

### メトリクス

```bash
# Prometheus メトリクス
curl http://localhost:8000/metrics

# アプリケーション統計
curl http://localhost:8000/health
```

## 🔒 セキュリティ

### 設定チェック

```bash
# 脆弱性スキャン
safety check

# 設定ファイル検証
python scripts/verify_config.py
```

### 本番環境セキュリティ

```bash
# SSL証明書設定
export SSL_CERT_PATH="/path/to/cert.pem"
export SSL_KEY_PATH="/path/to/key.pem"

# セキュリティヘッダー有効化
export SECURITY_HEADERS=True
```

## 🚨 トラブルシューティング

### よくある問題

#### 1. Python バージョンエラー

```bash
# Python バージョン確認
python --version

# pyenv でバージョン管理
pyenv install 3.9.18
pyenv local 3.9.18
```

#### 2. 依存関係の競合

```bash
# 仮想環境をクリーンアップ
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. データベース接続エラー

```bash
# データベース接続確認
python -c "from src.database import engine; print('DB connected')"

# SQLite ファイル権限確認
ls -la repairgpt.db
```

#### 4. API接続エラー

```bash
# API キー確認
python -c "import os; print(os.environ.get('OPENAI_API_KEY'))"

# 接続テスト
python scripts/test_api_connection.py
```

### ログの確認

```bash
# アプリケーションログ
tail -f logs/app.log

# エラーログ
tail -f logs/error.log

# アクセスログ
tail -f logs/access.log
```

### パフォーマンス問題

```bash
# メモリ使用量確認
python scripts/memory_check.py

# プロファイリング
python -m cProfile -o profile.out src/main.py
```

## 📚 次のステップ

### 開発を始める

1. [開発ガイドライン](../development/development_guidelines.md)を確認
2. [コーディング規約](../development/coding_standards.md)を理解
3. [API仕様書](../api/api_specification.md)を参照

### 機能追加

1. [Issue作成](https://github.com/takezou621/repairgpt/issues/new)
2. [ブランチ作成](../development/development_guidelines.md#ブランチ戦略)
3. [プルリクエスト](../development/development_guidelines.md#pull-request手順)

### 本番デプロイ

1. [デプロイメントガイド](../deployment/deployment_guide.md)を確認
2. [運用監視](../deployment/deployment_guide.md#監視設定)を設定
3. [バックアップ戦略](../deployment/deployment_guide.md#バックアップ)を実装

## 🆘 サポート

### 質問・問題報告

- **Issue**: [GitHub Issues](https://github.com/takezou621/repairgpt/issues)
- **Discussion**: [GitHub Discussions](https://github.com/takezou621/repairgpt/discussions)

### コミュニティ

- **Discord**: [RepairGPT Community](https://discord.gg/repairgpt)
- **Twitter**: [@repairgpt](https://twitter.com/repairgpt)

### 緊急時サポート

- **本番障害**: [運用チーム連絡先](../deployment/deployment_guide.md#緊急時対応)
- **セキュリティ**: [セキュリティチーム](mailto:security@repairgpt.com)

---

**最終更新日**: 2024-01-09  
**バージョン**: 1.0.0  
**メンテナー**: RepairGPT開発チーム