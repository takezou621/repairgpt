# RepairGPT 開発ガイドライン

## 1. 開発フロー

### 1.1 ブランチ戦略
```
main (本番)
├── develop (開発統合)
│   ├── feature/issue-{number}-{short-description}
│   ├── bugfix/issue-{number}-{short-description}
│   └── hotfix/issue-{number}-{short-description}
```

### 1.2 Issue管理
- **Issue作成**: 実装前に必ずIssueを作成
- **ラベル付け**: `priority:high/medium/low`, `type:feature/bug/docs`
- **担当者指定**: Self-assignでもOK
- **時間見積もり**: 見積もり時間をコメントに記載

### 1.3 Pull Request手順
1. **Issue番号を含むブランチ名**: `feature/issue-6-ifixit-api-investigation`
2. **Pull Request作成**: 適切なタイトルとテンプレートを使用
3. **レビュー**: 他の開発者（または自己レビュー）
4. **マージ**: Squash mergeを推奨

## 2. コード品質基準

### 2.1 コード規約
- **PEP 8**: Python標準コーディング規約に準拠
- **型ヒント**: すべての関数・メソッドに型ヒントを付与
- **Docstring**: Google形式のdocstringを使用

```python
def get_repair_guide(device: str, issue: str) -> RepairGuide:
    """指定されたデバイスと問題に対する修理ガイドを取得する.
    
    Args:
        device: デバイス名 (例: "Nintendo Switch")
        issue: 問題の説明 (例: "電源が入らない")
        
    Returns:
        RepairGuide: 修理ガイドオブジェクト
        
    Raises:
        DeviceNotSupportedError: サポートされていないデバイスの場合
        APIConnectionError: 外部API接続エラーの場合
    """
```

### 2.2 ディレクトリ構造
```
repairgpt/
├── src/
│   ├── chatbot/          # チャットボット関連
│   ├── clients/          # 外部API クライアント
│   ├── models/           # データモデル
│   ├── utils/            # ユーティリティ関数
│   └── templates/        # プロンプトテンプレート
├── tests/                # テストファイル
├── docs/                 # ドキュメント
├── scripts/              # スクリプト
└── requirements.txt      # 依存関係
```

### 2.3 命名規則
- **関数・変数**: snake_case
- **クラス**: PascalCase
- **定数**: UPPER_CASE
- **ファイル**: snake_case.py

## 3. テストガイドライン

### 3.1 テスト種別
- **Unit Tests**: `tests/unit/`
- **Integration Tests**: `tests/integration/`
- **E2E Tests**: `tests/e2e/`

### 3.2 テストファイル命名
```
tests/
├── unit/
│   └── test_ifixit_client.py
├── integration/
│   └── test_chatbot_integration.py
└── e2e/
    └── test_user_scenarios.py
```

### 3.3 テスト実行コマンド
```bash
# すべてのテスト実行
pytest

# カバレッジ付きテスト
pytest --cov=src --cov-report=html

# 特定のテストファイル
pytest tests/unit/test_ifixit_client.py
```

## 4. 環境管理

### 4.1 依存関係管理
```bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 依存関係インストール
pip install -r requirements.txt

# 新しい依存関係追加後
pip freeze > requirements.txt
```

### 4.2 環境変数管理
- **開発環境**: `.env` ファイル（gitignore対象）
- **本番環境**: 環境変数またはシークレット管理

```bash
# .env ファイル例
OPENAI_API_KEY=your_api_key_here
CLAUDE_API_KEY=your_claude_key_here
DATABASE_URL=sqlite:///local.db
DEBUG=True
```

## 5. コミット規約

### 5.1 コミットメッセージ形式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### 5.2 Type一覧
- **feat**: 新機能
- **fix**: バグ修正
- **docs**: ドキュメント変更
- **style**: フォーマット変更
- **refactor**: リファクタリング
- **test**: テスト追加・変更
- **chore**: その他の変更

### 5.3 コミット例
```
feat(chatbot): Add basic LLM integration

- OpenAI API client implementation
- Basic conversation handling
- Error handling for API failures

Closes #9
```

## 6. コードレビュー基準

### 6.1 必須チェック項目
- [ ] コードが要件を満たしているか
- [ ] テストが十分に書かれているか
- [ ] セキュリティ上の問題がないか
- [ ] パフォーマンスに問題がないか
- [ ] ドキュメントが更新されているか

### 6.2 レビューコメント例
```
# 良いコメント
- "この実装は効率的ですね。ただし、エラーハンドリングを追加した方が良いでしょう。"
- "テストケースが不足しているようです。異常系のテストを追加してください。"

# 避けるべきコメント
- "これは間違っています。"
- "なぜこのように書いたのですか？"
```

## 7. セキュリティガイドライン

### 7.1 機密情報管理
- **APIキー**: 環境変数で管理、コードに直接書かない
- **データベース接続**: 暗号化された接続を使用
- **ログ**: 機密情報をログに出力しない

### 7.2 入力検証
```python
def validate_user_input(user_input: str) -> str:
    """ユーザー入力を検証・サニタイズする."""
    # 長すぎる入力を拒否
    if len(user_input) > 1000:
        raise ValueError("入力が長すぎます")
    
    # 危険な文字列をエスケープ
    return html.escape(user_input)
```

### 7.3 外部API利用
- **レート制限**: 適切な間隔でAPI呼び出し
- **タイムアウト**: 適切なタイムアウト設定
- **エラーハンドリング**: 外部API障害時の対応

## 8. パフォーマンス最適化

### 8.1 レスポンス時間最適化
- **キャッシュ**: 頻繁に使用するデータのキャッシュ
- **非同期処理**: 長時間処理の非同期化
- **データベース**: 適切なインデックス設定

### 8.2 メモリ使用量最適化
- **大きなファイル**: ストリーミング処理
- **画像処理**: 適切なサイズ制限
- **メモリリーク**: 適切なリソース解放

## 9. 監視・ログ

### 9.1 ログレベル
- **DEBUG**: 開発時のデバッグ情報
- **INFO**: 一般的な情報
- **WARNING**: 注意が必要な状況
- **ERROR**: エラー発生時
- **CRITICAL**: システム停止レベル

### 9.2 ログ形式
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Repair guide generated for device: %s", device_name)
```

## 10. ドキュメント管理

### 10.1 ドキュメント種別
- **要件定義**: `docs/specs/`
- **API仕様**: `docs/api/`
- **開発ガイド**: `docs/development/`
- **運用ガイド**: `docs/deployment/`

### 10.2 ドキュメント更新
- **機能追加時**: 関連ドキュメントの更新
- **API変更時**: API仕様書の更新
- **設定変更時**: 運用ガイドの更新

## 11. 継続的改善

### 11.1 定期的なレビュー
- **月次**: コード品質レビュー
- **四半期**: アーキテクチャレビュー
- **半年**: 技術スタックレビュー

### 11.2 改善提案
- **Issue作成**: 改善案をIssueとして作成
- **Discussion**: 大きな変更は事前に議論
- **実験**: 小規模な実験から開始

## 12. 緊急時対応

### 12.1 障害対応
1. **検知**: 監視システムによる検知
2. **初動**: 障害状況の把握
3. **対応**: 一時的な回避策
4. **復旧**: 根本的な修正
5. **報告**: 障害報告書の作成

### 12.2 ホットフィックス
- **緊急性**: 本番環境への影響度を判断
- **最小限**: 必要最小限の変更
- **レビュー**: 迅速だが確実なレビュー
- **テスト**: 影響範囲の確認テスト