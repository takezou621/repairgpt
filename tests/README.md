# RepairGPT 夜間自動化システムテスト

**Issue #33**: テスト: 夜間自動化システム動作確認  
**実行時刻**: #午後

## 概要

このテストスイートは RepairGPT プロジェクトの夜間自動化システムの動作確認を行います。

## テスト項目

- ✅ **Claude Code**: ブランチ作成・実装
- 🔄 **夜間自動PR作成**: テスト実行
- 🔄 **夜間自動マージ**: テスト実行
- 🔄 **Issue自動クローズ**: テスト実行
- 🔄 **ブランチ自動削除**: テスト実行

## ファイル構成

```
tests/
├── __init__.py                 # テストパッケージ初期化
├── README.md                   # このファイル
├── conftest.py                 # pytest設定
├── requirements-test.txt       # テスト依存関係
├── run_automation_tests.py     # 独立実行可能なテストランナー
└── test_night_automation.py    # メインテストファイル
```

## 実行方法

### 1. pytest を使用した実行

```bash
# テスト依存関係のインストール
pip install -r tests/requirements-test.txt

# 全テスト実行
pytest tests/

# 詳細出力で実行
pytest -v tests/

# カバレッジ付きで実行
pytest --cov=. tests/
```

### 2. 独立テストランナーの使用

```bash
# 依存関係なしで実行可能
python tests/run_automation_tests.py
```

## テスト内容

### 1. ワークフロー検証
- GitHub Actions YAML ファイルの存在確認
- YAML 構文の妥当性チェック
- 必要な権限設定の確認

### 2. 自動化ロジック検証
- PR作成ロジックの確認
- 自動マージ処理の確認
- Issue自動クローズ処理の確認
- ブランチ自動削除処理の確認

### 3. スケジュール設定確認
- 夜間実行スケジュールの妥当性
- トリガー条件の確認

### 4. エラーハンドリング確認
- 各ワークフローのエラー処理
- 失敗時の適切な通知機能

## 期待される結果

全テストが正常に完了し、夜間自動化システムが以下のフローで動作することを確認:

1. **Claude Code** が Issue を処理しブランチに実装をコミット
2. **夜間自動化システム** がClaudeブランチを検出
3. **自動PR作成** でプルリクエストを生成
4. **自動マージ** でメインブランチにマージ
5. **Issue自動クローズ** で関連Issueをクローズ
6. **ブランチ自動削除** でClaudeブランチをクリーンアップ

## 自動化ワークフロー

### 関連ワークフロー
- `claude-perfect-automation.yml`: 完全自動化メインワークフロー
- `claude-full-automation.yml`: 包括的自動化処理
- `claude-auto-merge.yml`: 自動マージ処理

### トリガー条件
- **schedule**: `*/1 * * * *` (毎分実行)
- **workflow_run**: Claude Code完了時
- **push**: `claude/**` ブランチ

## トラブルシューティング

### テスト失敗時の対処

1. **ワークフローファイル不足**
   ```bash
   ls -la .github/workflows/claude-*.yml
   ```

2. **YAML構文エラー**
   ```bash
   yamllint .github/workflows/
   ```

3. **権限不足**
   - GitHub Actions の repository permissions を確認
   - workflow の permissions 設定を確認

## Issue #33 要件対応

このテストスイートは Issue #33 の要件を満たし、夜間自動化システムの完全な動作確認を提供します。

**実行時刻**: #午後