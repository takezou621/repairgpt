# RepairGPT テストスイート

**Issue #88**: 基本的なユニットテストとテスト環境の構築  
**Issue #33**: 夜間自動化システム動作確認（既存）

## 概要

このテストスイートは RepairGPT プロジェクトの包括的なテスト環境を提供します：

1. **基本的なユニットテスト環境** (Issue #88)
2. **夜間自動化システムテスト** (Issue #33)

## 基本的なユニットテスト環境 (Issue #88)

### 機能

- **pytest** を使用した包括的なテスト環境
- **カバレッジ測定** (目標: 80%以上)
- **フィクスチャ** による再利用可能なテストデータ
- **パラメータ化テスト** による効率的なテスト実行
- **型ヒント** と **docstring** による明確な仕様

### テストファイル構成

```
tests/
├── conftest.py                 # pytest設定とフィクスチャ
├── test_basic_examples.py      # 基本的なユニットテストの例
├── pytest.ini                 # pytest設定ファイル
├── requirements-test.txt       # テスト依存関係
└── README.md                   # このファイル
```

### 利用可能なフィクスチャ

- `sample_test_data`: 基本的なテスト用サンプルデータ
- `temp_test_directory`: 一時テストディレクトリ
- `mock_api_response`: 模擬API応答データ
- `test_device_data`: テスト用デバイスデータ

### テスト例

```python
def test_basic_functionality(sample_test_data):
    """基本機能のテスト例"""
    assert sample_test_data["test_key"] == "test_value"
    assert len(sample_test_data["numbers"]) == 3

@pytest.mark.parametrize("input,expected", [
    (1, 2), (2, 4), (3, 6)
])
def test_parametrized_example(input, expected):
    """パラメータ化テストの例"""
    assert input * 2 == expected
```

## 夜間自動化システムテスト (Issue #33)

### テスト項目

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

### 基本的なユニットテストの実行

```bash
# テスト依存関係のインストール
pip install -r tests/requirements-test.txt

# 基本的なユニットテストのみ実行
pytest tests/test_basic_examples.py

# カバレッジ付きで基本テスト実行（推奨）
pytest --cov=src tests/test_basic_examples.py

# 全テスト実行（基本テスト + 自動化テスト）
pytest tests/

# 詳細出力で実行
pytest -v tests/

# 特定のマーカーのテストのみ実行
pytest -m "basic" tests/          # 基本テストのみ
pytest -m "automation" tests/     # 自動化テストのみ
pytest -m "slow" tests/           # 時間のかかるテストのみ
```

### pytest設定の特徴

- **カバレッジ目標**: 80%以上 (`--cov-fail-under=80`)
- **カバレッジレポート**: ターミナル表示 + HTML レポート (`htmlcov/`)
- **テストマーカー**: `basic`, `unit`, `automation`, `slow`, `integration`

### 自動化システムテストの実行

```bash
# 1. pytest を使用した実行

# 全自動化テスト実行
pytest -m "automation" tests/

# 詳細出力で実行
pytest -v -m "automation" tests/

# カバレッジ付きで実行
pytest --cov=. -m "automation" tests/
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