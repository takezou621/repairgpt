# ブランチ命名規則

このドキュメントでは、RepairGPTプロジェクトにおけるブランチ命名の推奨規則を定義します。

## 基本原則

1. **明確性**: ブランチ名から作業内容が理解できる
2. **一貫性**: 全開発者が同じルールに従う
3. **自動化対応**: GitHub ActionsワークフローがIssueとブランチを自動的に関連付けできる

## 推奨ブランチ命名形式

### 1. Issue対応ブランチ

**形式**: `{prefix}-issue-{issue-number}`

```
claude-issue-67          # Claude Codeによる Issue #67 の対応
feature-issue-42         # 新機能実装 Issue #42
bugfix-issue-15          # バグ修正 Issue #15
hotfix-issue-8           # 緊急修正 Issue #8
docs-issue-23            # ドキュメント更新 Issue #23
```

### 2. 作業種別による命名

#### 新機能開発
```
feature-issue-{number}         # Issue番号付き
feature-user-authentication    # Issue番号なし（詳細説明）
feature-repair-ai-enhancement  # 修理AIの機能強化
```

#### バグ修正
```
bugfix-issue-{number}          # Issue番号付き
bugfix-login-validation        # ログイン検証の修正
bugfix-api-rate-limit          # APIレート制限の修正
```

#### 緊急修正（ホットフィックス）
```
hotfix-issue-{number}          # Issue番号付き
hotfix-security-vulnerability  # セキュリティ脆弱性の緊急修正
hotfix-database-connection     # データベース接続の緊急修正
```

#### ドキュメント更新
```
docs-issue-{number}            # Issue番号付き
docs-api-specification         # API仕様書の更新
docs-setup-guide              # セットアップガイドの更新
```

#### リファクタリング
```
refactor-issue-{number}        # Issue番号付き
refactor-user-service          # ユーザーサービスのリファクタリング
refactor-database-schema       # データベーススキーマの改善
```

## 自動化システム対応

### Claude Code自動化ブランチ

Claude Codeによる自動実装では以下の形式を使用：

```
claude-issue-{number}          # 基本形式（推奨）
claude-{description}-{number}  # 説明付き
claude-fix-{number}            # 修正作業
claude-feature-{number}        # 新機能実装
```

### 自動検出パターン

GitHub Actions ワークフローは以下のパターンでブランチを自動検出します：

1. `issue-{number}` を含むもの
2. `claude` + `{number}` を含むもの
3. `fix-{number}` を含むもの
4. `feature-{number}` を含むもの

## 禁止事項

❌ **避けるべき命名**：
```
test-branch                    # 内容が不明
my-feature                     # 個人的な命名
temp-fix                       # 一時的な命名
new-branch                     # 汎用的すぎる
123-fix                        # Issue番号のみ
```

## 特殊ケース

### 実験的ブランチ
```
experiment-{description}       # 実験的な実装
poc-{description}              # Proof of Concept
spike-{description}            # 技術調査
```

### リリースブランチ
```
release-v{version}             # リリース準備
release-{date}                 # 日付ベースリリース
```

### メンテナンスブランチ
```
maintenance-{description}      # メンテナンス作業
chore-dependency-update        # 依存関係更新
chore-cleanup                  # コードクリーンアップ
```

## ブランチライフサイクル

1. **作成**: Issue作成後、対応するブランチを作成
2. **作業**: ブランチ上で機能実装・修正
3. **PR作成**: Pull Requestを作成してレビュー
4. **マージ**: レビュー完了後にmainブランチにマージ
5. **削除**: マージ後、自動的にブランチを削除

## 自動化連携

### ラベル管理
- `claude-processing`: 処理中のIssue
- `claude-completed`: 完了したIssue
- `automation-error`: 自動化エラー

### ワークフロー連携
- Issue番号からブランチを自動検出
- PR作成・マージ・ブランチ削除を自動実行
- エラー発生時の自動通知

## ベストプラクティス

✅ **推奨**：
- Issue番号を含める
- 作業内容がわかる説明を追加
- 英語での命名（国際化対応）
- ハイフン区切りでの単語分割

✅ **例**：
```
claude-issue-67               # ✅ 理想的
feature-issue-42-user-auth    # ✅ 詳細説明付き
bugfix-issue-15-login-error   # ✅ バグ内容も明示
```

---

このブランチ命名規則により、自動化システムとの連携が円滑になり、開発効率が向上します。

**最終更新**: 2025-07-14
**適用開始**: Issue #67 対応より