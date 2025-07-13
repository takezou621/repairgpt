# RepairGPT - Claude Code Assistant Instructions

**Note**: このプロジェクトではClaude Code Max (Opus 4)を使用しています。

## プロジェクト概要

RepairGPT は、AI を活用して電子機器の修理をサポートするオープンソースプロジェクトです。LLM とマルチモーダル機能を使用して、ゲーム機、スマートフォン、PC などの消費者向け電子機器の診断と修理を支援します。

## 技術スタック

### バックエンド
- **言語**: Python 3.9+
- **Webフレームワーク**: FastAPI 0.100+
- **データベース**: PostgreSQL 14+ (本番)、SQLite (開発)
- **ORM**: SQLAlchemy 2.0+
- **キャッシュ**: Redis 7.0+

### フロントエンド
- **UI**: Streamlit 1.25+
- **カスタムコンポーネント**: HTML/CSS/JavaScript

### AI/ML
- **LLM**: OpenAI GPT-4、Claude-3
- **Vision API**: OpenAI Vision API
- **プロンプト管理**: LangChain
- **画像処理**: Pillow、OpenCV

### 外部サービス
- **iFixit API**: 修理手順データ
- **OpenAI API**: 自然言語処理
- **Claude API**: 高度な推論

## プロジェクト構造

```
repairgpt/
├── README.md               # プロジェクト概要
├── docs/                   # 包括的なドキュメント
│   ├── architecture/       # アーキテクチャ設計
│   ├── setup/             # セットアップガイド
│   ├── specs/             # 仕様書
│   ├── api/               # API仕様
│   ├── development/       # 開発ガイド
│   └── deployment/        # デプロイメント
├── src/                   # ソースコード（未実装）
├── tests/                 # テストコード（未実装）
└── config/                # 設定ファイル（未実装）
```

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

## 開発コマンド

### 環境構築
```bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# 開発用データベース初期化
python scripts/init_db.py
```

### 開発サーバー起動
```bash
# FastAPI サーバー
uvicorn src.main:app --reload --port 8000

# Streamlit UI
streamlit run src/ui/app.py --server.port 8501
```

### テスト実行
```bash
# 全テスト実行
pytest

# カバレッジ付きテスト
pytest --cov=src tests/

# 特定のテストのみ
pytest tests/test_repair_service.py
```

### コード品質チェック
```bash
# リンター
flake8 src/

# 型チェック
mypy src/

# フォーマッター
black src/
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

最終更新日: 2025-01-12

## 自動化フローテスト

自動化ワークフローの動作確認テスト (Issue #20) - 2025-07-12