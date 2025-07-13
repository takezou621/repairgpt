# RepairGPT Test Suite

スマート自動化システムのテストスイート

## 概要

このディレクトリには、RepairGPT プロジェクトのスマート自動化システムをテストするためのテストコードが含まれています。

## テストの種類

### 1. Smart Automation Tests (`test_smart_automation.py`)

土日昼間スマート自動化システムの包括的なテスト:

- **スケジュールテスト**: 平日夜間 vs 土日昼間の実行時間検証
- **ワークフローテスト**: 自動化ステップの完全性確認
- **統合テスト**: エンドツーエンドの自動化フロー検証

### テスト対象の自動化スケジュール

#### 平日夜間実行 (月-金)
- 23:00 JST (14:00 UTC)
- 02:00 JST (17:00 UTC) 
- 05:00 JST (20:00 UTC)

#### 土日昼間実行 (土日)
- 10:00 JST (01:00 UTC)
- 14:00 JST (05:00 UTC)
- 18:00 JST (09:00 UTC)
- 22:00 JST (13:00 UTC)

## 自動化フロー

完全自動化システムの実行フロー:

1. ✅ **Claude Code実装検知**: `claude-processed`ラベル付きIssue検出
2. ✅ **自動PR作成**: 平日夜間・土日昼間スケジュール対応
3. ✅ **自動マージ**: 即座実行・競合回避
4. ✅ **Issue自動クローズ**: 完了コメント付きクローズ
5. ✅ **ブランチ自動削除**: 完全クリーンアップ

## テスト実行

### 単体テスト実行
```bash
python -m pytest tests/test_smart_automation.py -v
```

### 全テスト実行
```bash
python -m pytest tests/ -v
```

### カバレッジ付きテスト
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

## テスト目標

- **100%完全自動化**: 手動介入なしでの完全フロー実行
- **スケジュール最適化**: 平日夜間・土日昼間の適切な時間配分
- **エラーハンドリング**: 失敗時の適切な処理とリトライ
- **リソース効率**: GitHub API制限内での効率的実行

## テスト環境

- Python 3.9+
- pytest
- unittest (標準ライブラリ)
- datetime (タイムゾーン処理)

## 期待結果

### 成功条件
- 全テストがパス (100% success rate)
- スケジュール正確性の確認
- 自動化フローの完全性証明

### 実行例
```
🧪 スマート自動化システムテスト開始
==================================================
test_weekend_daytime_schedule ✅ PASS
test_weekday_nighttime_schedule ✅ PASS  
test_automation_workflow_steps ✅ PASS
test_weekend_vs_weekday_scheduling ✅ PASS
test_smart_automation_detection ✅ PASS
test_full_automation_flow ✅ PASS
==================================================
🎯 土日昼間スマート自動化テスト完了
🚀 スマート自動化成功率: 100%
```

## 関連ドキュメント

- [Smart Automation Workflow](../.github/workflows/claude-night-automation.yml)
- [Project Guidelines](../CLAUDE.md)
- [Testing Strategy](../docs/development/testing_strategy.md)

---

**最終更新**: 2025-07-13  
**テスト実装**: Issue #43 - 土日昼間スマート自動化システムテスト