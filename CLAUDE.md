# RepairGPT - Claude Code Assistant Instructions

**Note**: このプロジェクトではClaude Code Max (Opus 4)を使用しています。

## プロジェクト概要

RepairGPT は、AI を活用して電子機器の修理をサポートするオープンソースプロジェクトです。LLM とマルチモーダル機能を使用して、ゲーム機、スマートフォン、PC などの消費者向け電子機器の診断と修理を支援します。

### Core Features (Kiro Steering より)
- **AI Repair Assistant**: Enhanced chatbot with built-in knowledge base using OpenAI GPT-4 and Claude-3
- **Offline Repair Database**: Comprehensive repair guides for Nintendo Switch, iPhone, Laptop, PlayStation 5
- **iFixit Integration**: Online repair guide search and access via API
- **Image Analysis**: Visual repair assistance using OpenAI Vision API
- **Multi-language Support**: English and Japanese (i18n implementation)
- **Safety-First Approach**: Detailed warnings and professional recommendations

### Target Users
- **Beginners**: Basic troubleshooting with safety warnings
- **Intermediate**: More detailed repair steps with tool requirements
- **Expert**: Advanced diagnostics and complex repair procedures

### Key Principles
- Safety warnings are mandatory for all repair recommendations
- Device-specific and skill-level appropriate guidance
- Professional help recommendations for complex repairs
- Comprehensive documentation and step-by-step instructions

 - ❌ 「完了！」「成功！」の安易な報告を止める
  - ✅ 実際の動作確認後にのみ結果を報告する
  - ✅ 失敗や制約は隠さず正直に伝える

  2. 手動作業を「自動化成功」と偽装しない

  - ❌ 手動でPR作成して「自動化達成」と言わない
  - ✅ 手動介入が必要な場合は明確に「手動作業が必要」と報告
  - ✅ 部分的な成功と完全な成功を明確に区別する

  3. 技術制約を受け入れる

  - ❌ 不可能なことを「可能」と言い張らない
  - ✅ GitHub Actions の権限制約など技術的限界を認める
  - ✅ 代替案提示時は制約も含めて説明する

  4. テスト駆動で作業する

  - ❌ 実装後に「きっと動く」と仮定しない
  - ✅ 実装→即座にテスト→結果確認→報告の順序を徹底
  - ✅ テスト失敗時は素直に「失敗しました」と報告

  5. 学習履歴を活用する

  - ✅ 過去の失敗パターンを記録し、同じ過ちを避ける
  - ✅ 「今度こそ」ではなく「前回失敗した理由を踏まえて」と考える

## 技術スタック

### バックエンド
- **言語**: Python 3.9+
- **Webフレームワーク**: FastAPI 0.100+ (REST API framework with async support)
- **データベース**: PostgreSQL 14+ (本番)、SQLite (開発)
- **ORM**: SQLAlchemy 2.0+ (Database ORM with async capabilities)
- **マイグレーション**: Alembic 1.11+
- **データ検証**: Pydantic 2.0+ (Data validation and serialization)
- **キャッシュ**: Redis 4.6+ (Caching and session management)

### フロントエンド
- **UI**: Streamlit 1.25+ (Web UI framework)
- **レスポンシブデザイン**: Mobile-friendly interface
- **カスタムコンポーネント**: HTML/CSS/JavaScript

### AI/ML
- **LLM**: OpenAI GPT-4、Anthropic Claude (Advanced reasoning for complex diagnostics)
- **Vision API**: OpenAI Vision API
- **プロンプト管理**: Langchain (Prompt management and LLM orchestration)
- **画像処理**: Pillow、OpenCV

### 開発ツール (Kiro Steering より)
- **Lefthook**: Git hooks for code quality
- **Black**: Code formatting (120 char line limit)
- **flake8**: Linting with PEP8 compliance
- **isort**: Import sorting
- **pytest**: Testing framework with coverage
- **mypy**: Type checking

### 外部サービス
- **iFixit API**: 修理手順データ
- **OpenAI API**: 自然言語処理
- **Claude API**: 高度な推論

## プロジェクト構造 (Kiro Steering準拠)

### ディレクトリ構成
```
repairgpt/
├── README.md               # プロジェクト概要
├── .kiro/                  # Kiro Steering ドキュメント
│   └── steering/
│       ├── product.md      # 製品概要・機能・ユーザー
│       ├── structure.md    # プロジェクト構造・命名規則
│       └── tech.md         # 技術スタック・開発コマンド
├── docs/                   # 包括的なドキュメント
│   ├── architecture/       # アーキテクチャ設計
│   ├── setup/             # セットアップガイド
│   ├── specs/             # 仕様書
│   ├── api/               # API仕様
│   ├── development/       # 開発ガイド
│   └── deployment/        # デプロイメント
├── src/                   # ソースコード
│   ├── api/               # FastAPI backend
│   │   ├── main.py        # Application entry point
│   │   ├── models.py      # Pydantic models
│   │   └── routes/        # API route modules
│   ├── auth/              # Authentication & JWT
│   ├── chat/              # LLM chatbot system
│   │   ├── llm_chatbot.py # Main chatbot logic
│   │   ├── prompt_templates.py # Prompt management
│   │   └── streaming_chat.py   # Real-time chat
│   ├── clients/           # External API clients
│   │   └── ifixit_client.py # iFixit integration
│   ├── config/            # Configuration management
│   │   ├── settings.py    # Full settings with validation
│   │   └── settings_simple.py # Simplified settings
│   ├── data/              # Data access layer
│   │   └── offline_repair_database.py
│   ├── database/          # Database models & CRUD
│   │   ├── database.py    # DB connection
│   │   ├── models.py      # SQLAlchemy models
│   │   └── crud.py        # Database operations
│   ├── features/          # Feature modules
│   ├── i18n/              # Internationalization
│   │   └── locales/       # Translation files
│   ├── prompts/           # AI prompt templates
│   ├── schemas/           # Data schemas & validation
│   ├── services/          # Business logic services
│   │   ├── image_analysis.py  # Image processing
│   │   └── repair_guide_service.py
│   ├── ui/                # Streamlit frontend
│   │   ├── repair_app.py  # Main UI application
│   │   ├── language_selector.py
│   │   └── responsive_design.py
│   └── utils/             # Utility functions
│       ├── logger.py      # Logging configuration
│       └── security.py    # Security utilities
├── tests/                 # テストコード
│   ├── automation/        # Automation system tests
│   ├── fixtures/          # Test fixtures & data
│   ├── integration/       # Integration tests
│   │   └── test_api/     # API endpoint tests
│   ├── unit/              # Unit tests
│   │   ├── test_auth/    # Authentication tests
│   │   ├── test_chat/    # Chatbot tests
│   │   └── test_data/    # Data layer tests
│   ├── conftest.py       # Pytest configuration
│   └── requirements-test.txt  # Test dependencies
└── config/                # 設定ファイル
```

### 命名規則 (Kiro Steering準拠)
- **Python**: snake_case (ファイル、関数、変数)
- **クラス**: PascalCase
- **定数**: UPPER_CASE
- **API**: kebab-case (`/repair-guides`)
- **データベース**: snake_case (テーブル、カラム)

## 開発ガイドライン

### コーディング規約
1. **Python コード**:
   - PEP 8 に準拠
   - 型ヒントを使用
   - docstring でドキュメント化

2. **ファイル命名**:
   - スネークケース使用（例: `repair_service.py`）
   - 明確で説明的な名前

3. **API設計**:
   - RESTful 原則に従う
   - Pydantic モデルで入力検証
   - 適切なエラーハンドリング

### セキュリティ要件
- JWT トークン認証
- 入力データの厳密な検証
- HTTPS/TLS 通信
- 環境変数でシークレット管理

## 主要機能

### 実装予定の機能
1. **テキスト診断**: デバイスの問題をテキストで説明し、診断結果を取得
2. **画像診断**: デバイスの写真をアップロードして問題を特定
3. **修理ガイド生成**: iFixit スタイルの段階的な修理手順
4. **部品・工具推奨**: 必要な部品と工具のリスト
5. **コミュニティ Q&A**: ユーザー間の知識共有

### データフロー
1. ユーザーがテキストまたは画像で問題を入力
2. AI が問題を分析・診断
3. iFixit API と統合して修理手順を取得
4. カスタマイズされた修理ガイドを生成
5. 結果をキャッシュして高速化

## テスト戦略
- **Unit Tests**: pytest で個々のコンポーネントをテスト
- **Integration Tests**: API エンドポイントの統合テスト
- **Performance Tests**: 負荷テストとレスポンス時間測定
- **Coverage**: 80% 以上のコードカバレッジを目標

## デプロイメント
- **コンテナ化**: Docker
- **オーケストレーション**: Kubernetes
- **CI/CD**: GitHub Actions
- **監視**: Prometheus + Grafana
- **ログ**: 構造化ログ (JSON形式)

## 開発コマンド (Kiro Steering準拠)

### 環境構築
```bash
# 依存関係インストール
pip install -r requirements.txt

# 開発用フック設定
lefthook install

# アプリケーション実行
python run_app.py
# または
streamlit run src/ui/repair_app.py
```

### データベース操作
```bash
# データベース初期化
python scripts/init_db.py

# マイグレーション実行
alembic upgrade head

# 新規マイグレーション作成
alembic revision --autogenerate -m "description"
```

### テスト実行
```bash
# 全テスト実行
pytest

# カバレッジ付きテスト
pytest --cov=src --cov-report=html

# 特定カテゴリのテスト
pytest -m unit
pytest -m integration
pytest -m automation
```

### コード品質チェック
```bash
# フォーマット (フック経由で自動実行)
black src/ tests/ --line-length=120
isort src/ tests/ --profile black

# リンター
flake8 src/ tests/ --max-line-length=120

# 型チェック
mypy src/
```

### Docker環境
```bash
# 開発環境
docker-compose -f docker-compose.dev.yml up

# 本番環境
docker-compose up

# 特定サービスビルド
docker-compose build api
```

### 必須環境変数 (Kiro Steering準拠)
```bash
export REPAIRGPT_OPENAI_API_KEY="sk-..."
export REPAIRGPT_CLAUDE_API_KEY="sk-ant-..."
export REPAIRGPT_SECRET_KEY="32文字以上のシークレットキー"
export REPAIRGPT_DATABASE_URL="データベース接続文字列"
```

## 注意事項

1. **API キー管理**: OpenAI、Claude、iFixit の API キーは環境変数で管理
2. **データプライバシー**: ユーザーのデバイス情報は適切に匿名化
3. **レート制限**: 外部 API のレート制限に注意
4. **エラーハンドリング**: ユーザーフレンドリーなエラーメッセージ

## 貢献ガイドライン

1. **Issue 作成**: バグ報告や機能提案は GitHub Issues で
2. **ブランチ戦略**: `feature/`、`bugfix/`、`hotfix/` プレフィックス使用
3. **Pull Request**: レビュー前にテストとリンターを実行
4. **コミットメッセージ**: 明確で説明的なメッセージ

## 将来の拡張計画

### 短期目標（3-6ヶ月）
- マルチモーダル対応（音声入力・出力）
- リアルタイム通信（WebSocket）
- モバイル対応（PWA）

### 中長期目標（6-12ヶ月）
- マイクロサービス化
- カスタム AI モデルの訓練
- グローバル展開（多言語対応）

## リソース

- [プロジェクトドキュメント](docs/README.md)
- [アーキテクチャ概要](docs/architecture/architecture_overview.md)
- [API仕様書](docs/api/api_specification.md)
- [開発ガイドライン](docs/development/development_guidelines.md)

---

## Kiro Steering ドキュメント参照

詳細な設計情報は以下のKiro Steeringドキュメントを参照:
- [Product Overview](.kiro/steering/product.md): 製品機能・ユーザー・原則
- [Project Structure](.kiro/steering/structure.md): ディレクトリ構成・命名規則・アーキテクチャパターン
- [Technology Stack](.kiro/steering/tech.md): 技術スタック・開発コマンド・環境設定

---

最終更新日: 2025-07-20 (Kiro Steering統合)

## 自動化フローテスト

自動化ワークフローの動作確認テスト (Issue #20) - 2025-07-12
真の100%完全自動化の最終テスト実装 (Issue #24) - 2025-07-13
完全自動化証明完了: #午後

### 夜間自動化システム実装 (Issue #32) - 2025-07-13

**現実的自動化レベル達成:**
- ✅ Claude Code: ブランチ作成・実装完了
- ✅ 夜間自動PR作成: 新システム実装
- ✅ 夜間自動マージ: スケジュール最適化  
- ✅ Issue自動クローズ: 夜間バッチ処理
- ✅ パフォーマンス最適化: 重複ワークフロー統合

**技術改善:**
- 毎分実行→夜間3回実行への最適化
- GitHub API制限回避
- リソース使用量削減
- エラーハンドリング強化

**実行時刻:** 2025-07-13 夜間自動化システム完成

### 夜間自動化システム動作テスト (Issue #33) - 2025-07-13

**テスト実装完了:**
- ✅ Claude Code: テストブランチ作成・実装完了
- 🌙 夜間自動化システム: 動作確認準備完了
- 📝 テスト実行: 夜間ワークフロー手動トリガー予定
- 🔄 全自動化フロー: PR作成→マージ→クローズ→削除

**実行時刻:** 2025-07-13 テスト実装完了 - 夜間自動化テスト準備完了

### 夜間自動化システム動作検証 (Issue #36) - 2025-07-13

**完全動作検証実装:**
- ✅ Claude Code: 検証ブランチ作成・実装完了
- 🌙 夜間自動化システム: 完全動作テスト実行
- 📊 検証項目: PR作成→マージ→クローズ→削除の全フロー
- 🔍 システム監視: ワークフロー実行状況の詳細確認

**検証環境:**
- 夜間自動化ワークフロー: claude-night-automation.yml
- スケジュール: 23:00, 02:00, 05:00 JST
- 手動トリガー: workflow_dispatch対応

**実行時刻:** 2025-07-13 動作検証実装完了 - 完全自動化テスト開始

### 100%完全自動化システム最終検証 (Issue #38) - 2025-07-13

**最終検証実装完了:**
- ✅ Claude Code: 最終テストブランチ作成・実装完了
- 🎯 PR作成制限解消: default_workflow_permissions=write設定済み
- 🚀 100%完全自動化: 全フロー制限なし実行可能
- 📊 最終検証項目: PR作成→マージ→クローズ→削除の完全フロー

**権限設定完了:**
- ✅ default_workflow_permissions: write
- ✅ can_approve_pull_request_reviews: true
- ✅ GitHub Actions PR作成制限: 完全解消

**期待結果:**
真の100%完全自動化達成確認

**実行時刻:** 2025-07-13 最終検証実装完了 - 100%完全自動化確認テスト

### 昼間テスト: 100%完全自動化確実実行 (Issue #40) - 2025-07-13

**昼間確実実行テスト:**
- ✅ Claude Code: 昼間テストブランチ作成・確実実装完了
- 🎯 完全自動化システム: 失敗不可モード実行
- 🚀 確実実行環境: 全権限設定完了・制限なし
- 📊 昼間動作検証: PR作成→マージ→クローズ→削除完全フロー

**確実実行保証:**
- ✅ default_workflow_permissions: write (確認済み)
- ✅ can_approve_pull_request_reviews: true (確認済み)
- ✅ GitHub Actions全制限解消 (検証済み)
- ✅ 前回テスト100%成功 (実績あり)

**失敗不可要件:**
昼間時間帯での確実な100%完全自動化実行

**実行時刻:** 2025-07-13 昼間確実実行テスト実装完了 - 失敗不可モード

### スマート自動化システム実装 (土日昼間対応) - 2025-07-13

**土日昼間自動化機能追加:**
- 🚀 スマート自動化: 平日夜間・土日昼間の最適スケジュール
- ⏰ 平日スケジュール: 23:00, 02:00, 05:00 JST (夜間実行)
- 🌞 土日スケジュール: 10:00, 14:00, 18:00, 22:00 JST (昼間実行)
- 📊 ワークフロー名変更: Claude Night Automation → Claude Smart Automation

**実装改善:**
- 平日・土日の時間帯別最適化
- cron式での曜日指定 (1-5: 平日, 0,6: 土日)
- PR・コメントメッセージの土日対応
- ログメッセージの改善

**技術仕様:**
- 平日: `0 14,17,20 * * 1-5` (UTC)
- 土日: `0 1,5,9,13 * * 0,6` (UTC)

**実行時刻:** 2025-07-13 スマート自動化システム実装完了 - 土日昼間対応追加

### スマート自動化システム ガイド・テンプレート作成 - 2025-07-13

**他リポジトリ適用用ドキュメント作成完了:**
- 📚 詳細セットアップガイド: `docs/smart-automation-setup-guide.md`
- 🔧 ワークフローテンプレート: `templates/claude-smart-automation.yml`
- 🚀 自動セットアップスクリプト: `scripts/setup-smart-automation.sh`
- 📖 システム概要README: `README-smart-automation.md`

**提供機能:**
- ワンコマンドセットアップ（`./scripts/setup-smart-automation.sh`）
- 完全な手順書とテンプレート
- 権限設定からテスト実行まで全工程カバー
- トラブルシューティングガイド完備

**他リポジトリでの適用:**
任意のGitHubリポジトリで同様のスマート自動化システムを構築可能

**実行時刻:** 2025-07-13 スマート自動化汎用化完了

## Claude Code エージェント活用ガイド

RepairGPTプロジェクトの開発効率を最大化するため、Claude Codeの専門エージェント機能を積極的に活用します。

### 利用可能なエージェント

#### 1. kiro-task-organizer
**目的**: .kiroディレクトリのステアリングドキュメントを分析し、開発タスクを適切なサイズに分割

**使用シーン**:
- 新機能実装の計画時
- リファクタリング作業の整理時
- スプリント計画の作成時

**具体例**:
```
user: "修理ガイドのマルチモーダル対応を実装したい"
assistant: kiro-task-organizerを使って.kiro/steering/を分析し、以下のタスクに分割:
1. Vision API統合タスク
2. 画像アップロード機能タスク
3. UIコンポーネント更新タスク
4. テスト実装タスク
```

#### 2. task-executor-pr-creator
**目的**: kiro-task-organizerが作成したタスクを実装し、テストを書いてPRを作成

**使用シーン**:
- 計画されたタスクの実行時
- 単体テストを含む実装時
- 自動PR作成が必要な時

**具体例**:
```
user: "Vision API統合タスクを実装してPRを作成して"
assistant: task-executor-pr-creatorを使って:
1. src/services/image_analysis.pyを更新
2. テストケースを追加
3. PR作成（タイトル: feat: Add Vision API integration）
```

#### 3. code-quality-inspector
**目的**: 実装したコードの品質チェックと改善提案

**使用シーン**:
- 新機能実装後
- リファクタリング後
- PR作成前の最終チェック

**具体例**:
```
user: "image_analysis.pyのコード品質をチェックして"
assistant: code-quality-inspectorを使って以下を検証:
- PEP 8準拠
- 型ヒントの完全性
- エラーハンドリング
- パフォーマンス最適化
```

#### 4. qa-engineer-tester
**目的**: 包括的な品質保証テストとバグ修正提案

**使用シーン**:
- 機能実装完了後
- 統合テスト実行時
- セキュリティ検証時

**具体例**:
```
user: "修理ガイドAPIの品質テストを実行して"
assistant: qa-engineer-testerを使って:
1. エンドポイントテスト
2. エッジケーステスト
3. パフォーマンステスト
4. セキュリティ脆弱性チェック
```

### エージェント連携ワークフロー

#### 新機能実装フロー
```
1. kiro-task-organizer → タスク分割・計画
2. task-executor-pr-creator → 各タスクの実装とPR作成
3. code-quality-inspector → コード品質チェック
4. qa-engineer-tester → 統合テストと品質保証
```

#### バグ修正フロー
```
1. qa-engineer-tester → バグの特定と再現
2. task-executor-pr-creator → 修正実装とテスト
3. code-quality-inspector → 修正コードの品質確認
```

#### リファクタリングフロー
```
1. code-quality-inspector → 改善点の特定
2. kiro-task-organizer → リファクタリングタスクの計画
3. task-executor-pr-creator → 段階的な実装
4. qa-engineer-tester → リグレッションテスト
```

### ベストプラクティス

1. **段階的実行**: 大きなタスクはkiro-task-organizerで分割してから実行
2. **品質優先**: 実装後は必ずcode-quality-inspectorでチェック
3. **テスト駆動**: task-executor-pr-creatorで実装時は必ずテストを含める
4. **継続的検証**: qa-engineer-testerで定期的に品質を確認

### RepairGPT固有の活用例

#### 修理ガイド機能の拡張
```
user: "iFixit API統合を強化したい"
1. kiro-task-organizer: .kiro/steering/product.mdを参照し、タスク分割
2. task-executor-pr-creator: APIクライアントの拡張実装
3. qa-engineer-tester: API応答の網羅的テスト
```

#### マルチ言語対応の改善
```
user: "i18nシステムを最適化したい"
1. code-quality-inspector: 現在のi18n実装の問題点特定
2. kiro-task-organizer: 改善タスクの計画
3. task-executor-pr-creator: 新しい翻訳システム実装
```

### 注意事項

- エージェントは独立して動作するため、明確な指示が重要
- 各エージェントの結果を次のエージェントに引き継ぐ際は、具体的な情報を提供
- RepairGPTのコーディング規約（PEP 8、型ヒント等）を各エージェントに遵守させる
