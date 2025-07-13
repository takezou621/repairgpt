# 夜間自動化システム動作検証フレームワーク

## 概要

このフレームワークは、RepairGPT プロジェクトの夜間自動化システムの動作を検証し、CLAUDE.md の方針に従って正直で実証的な結果報告を行います。

## 検証対象コンポーネント

### 🔄 Claude Code: ブランチ作成・実装
- **ステータス**: ✅ 動作中
- **機能**: Issue に基づく自動ブランチ作成と実装
- **検証内容**: ブランチ命名規則、実装状況確認

### 🔄 夜間自動PR作成: システム動作確認
- **ステータス**: ⏳ 未設定
- **機能**: 夜間スケジュールでのPR自動作成
- **検証内容**: GitHub Actions ワークフロー、スケジュール設定

### 🔄 夜間自動マージ: 完全自動実行  
- **ステータス**: ⏳ 未設定
- **機能**: 条件満たしたPRの自動マージ
- **検証内容**: 安全性チェック、マージ条件確認

### 🔄 Issue自動クローズ: バッチ処理確認
- **ステータス**: ⏳ 未設定  
- **機能**: PR完了後のIssue自動クローズ
- **検証内容**: クローズ条件、誤クローズ防止機能

### 🔄 ブランチ自動削除: クリーンアップ確認
- **ステータス**: ⏳ 未設定
- **機能**: 不要ブランチの自動削除
- **検証内容**: 削除条件、保護ルール確認

## 使用方法

### 完全検証実行
```bash
# 全コンポーネントの検証実行
python verification/run_verification.py

# JSON形式で結果出力
python verification/run_verification.py --json
```

### 個別コンポーネント検証
```bash
# Claude Code のみ検証
python verification/run_verification.py --component claude-code

# 夜間自動PR作成のみ検証
python verification/run_verification.py --component auto-pr

# 夜間自動マージのみ検証  
python verification/run_verification.py --component auto-merge

# Issue自動クローズのみ検証
python verification/run_verification.py --component auto-close

# ブランチ自動削除のみ検証
python verification/run_verification.py --component auto-delete
```

### レポート生成
```bash
# デフォルトレポート生成
python verification/run_verification.py --output verification_report.md

# カスタムファイル名でレポート生成
python verification/run_verification.py --output "automation_test_$(date +%Y%m%d).md"
```

## ファイル構成

```
verification/
├── README.md                      # このファイル
├── automation_test_framework.py   # メイン検証フレームワーク
├── run_verification.py           # 検証実行スクリプト
└── config.json                   # 設定ファイル
```

## 検証結果の解釈

### ステータス説明
- ✅ **PASSED**: 検証成功、システム正常動作
- ❌ **FAILED**: 検証失敗、問題発生
- ⏳ **PENDING**: 未設定、設定が必要
- ⏭️ **SKIPPED**: スキップ、条件未満たし

### 重要な原則

このフレームワークはCLAUDE.mdの以下の原則に従います：

1. **正直な報告**
   - 「完了！」「成功！」の安易な報告を避ける
   - 実際の動作確認後にのみ結果を報告
   - 失敗や制約は隠さず正直に伝える

2. **手動作業の明示**
   - 手動でPR作成して「自動化達成」と偽装しない
   - 手動介入が必要な場合は明確に「手動作業が必要」と報告
   - 部分的な成功と完全な成功を明確に区別

3. **技術制約の受け入れ**
   - 不可能なことを「可能」と言い張らない
   - GitHub Actions の権限制約など技術的限界を認める
   - 代替案提示時は制約も含めて説明

## 設定カスタマイズ

`config.json` ファイルで以下をカスタマイズできます：

- 各コンポーネントの有効/無効
- タイムアウト設定
- 安全性チェック条件
- レポート形式
- GitHub統合設定

## トラブルシューティング

### よくある問題

1. **GitHub Actions ワークフローが見つからない**
   ```
   解決策: .github/workflows/ ディレクトリにワークフローファイルを作成
   ```

2. **権限エラー**
   ```
   解決策: GitHub リポジトリの Settings > Actions で権限を確認
   ```

3. **Python モジュールが見つからない**
   ```
   解決策: プロジェクトルートから実行するか、PYTHONPATH を設定
   ```

## 実装ロードマップ

### 段階1: 基礎検証（現在）
- ✅ Claude Code ブランチ作成検証
- ✅ 検証フレームワーク構築
- ✅ 正直な報告システム

### 段階2: ワークフロー設定
- ⏳ GitHub Actions ワークフロー作成
- ⏳ 夜間スケジュール設定
- ⏳ 安全性チェック実装

### 段階3: 完全自動化
- ⏳ 自動マージシステム
- ⏳ Issue自動クローズ
- ⏳ ブランチクリーンアップ

### 段階4: 監視・改善
- ⏳ エラー監視システム
- ⏳ パフォーマンス最適化
- ⏳ アラート機能

## 関連ドキュメント

- [CLAUDE.md](../CLAUDE.md) - プロジェクト全体指針
- [開発ガイドライン](../docs/development/development_guidelines.md)
- [GitHub Actions ベストプラクティス](https://docs.github.com/ja/actions/learn-github-actions/best-practices-for-github-actions)

## サポート

質問や問題がある場合は、以下で報告してください：

- GitHub Issues: タグ `verification`, `automation`  
- 緊急時: プロジェクトメンテナーに直接連絡

---

**注意**: このシステムは実際の動作確認に基づいた正直な結果を提供します。  
「完璧な自動化」よりも「信頼性の高い段階的自動化」を目指しています。