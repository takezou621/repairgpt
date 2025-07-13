# GitHub Actions ワークフロー

このディレクトリには、RepairGPTプロジェクトの自動化ワークフローが含まれています。

**Note**: 全てのワークフローでClaude Code Max (Opus 4モデル)を使用しています。

## ワークフロー一覧

### 1. Claude Issue Processor (`claude-issue-processor.yml`)
- **目的**: 未処理のGitHub Issueを自動的にClaudeに割り当てて解決
- **実行タイミング**: 毎日23:00 (JST) または手動実行
- **動作**:
  1. `claude-processed`ラベルがないオープンなissueを検索
  2. 優先度（high > medium > low）でソート
  3. 最初の未処理issueに@claudeメンションを追加
  4. `claude-processed`ラベルを付与

### 2. Claude PR Assistant (`claude-pr-assistant.yml`)
- **目的**: PRに対してClaudeによる詳細なコードレビューを依頼
- **実行タイミング**: PRコメントで@claudeがメンションされた時
- **動作**:
  1. PR情報と変更ファイルを収集
  2. レビュー観点を含むコメントを作成
  3. `claude-review-requested`ラベルを付与

### 3. Claude Code Review (`claude-code-review.yml`)
- **目的**: 新しいPRに対して自動的にコードレビューを実行
- **実行タイミング**: PRが開かれた時、または更新された時
- **動作**:
  1. 変更内容を分析
  2. RepairGPT固有のレビュー観点でフィードバック
  3. セキュリティ、パフォーマンス、ベストプラクティスをチェック

### 4. Claude Auto PR and Merge (`claude-auto-merge.yml`)
- **目的**: Claudeの作業完了後、自動でPR作成・レビュー・マージ・クリーンアップを実行
- **実行タイミング**: Claudeが作業完了を報告した時
- **動作**:
  1. Claudeの完了コメントを検知
  2. 自動的にPRを作成
  3. PRを自動レビュー・マージ
  4. 関連Issueをクローズ
  5. 不要なブランチを削除

### 5. Claude Full Automation (`claude-full-automation.yml`) ⭐**新機能**
- **目的**: 🚀 **100%完全自動化** - Claude Codeワークフロー完了を検知して完全自動でPR作成〜マージまで実行
- **実行タイミング**: Claude Codeワークフローが成功完了した時
- **動作**:
  1. workflow_runトリガーでClaude Code完了を自動検知
  2. Issue番号とClaudeブランチを自動特定
  3. 自動的にPRを作成（人間の介入不要）
  4. 自動マージ実行
  5. Issue自動クローズ
  6. ブランチ自動削除
  7. **完全無人実行** 🤖

## セットアップ

### 前提条件
- GitHubリポジトリにClaude GitHub Appがインストール済み
- Claude Code Maxの認証が完了済み

### 必要なシークレット
- 特になし（Claude GitHub App認証により自動的に処理されます）

### ラベルの設定
以下のラベルをリポジトリに作成してください：
- `claude-processed`: 処理済みのissue
- `claude-completed`: 完了したissue（自動クローズ済み）
- `fully-automated`: 100%完全自動化で処理されたissue ⭐**新規**
- `claude-review-requested`: Claudeレビュー依頼済み
- `claude-auto-generated`: Claude生成のPR
- `claude-full-automation`: 完全自動化フローで作成されたPR ⭐**新規**
- `ready-for-merge`: マージ準備完了
- `needs-review`: レビューが必要
- `security-review-required`: セキュリティレビューが必要
- `priority:high`: 高優先度
- `priority:medium`: 中優先度
- `priority:low`: 低優先度

## 使用方法

### Issue自動処理
1. 新しいissueを作成し、適切な優先度ラベルを付ける
2. 毎晩23時に自動的に処理が開始される
3. または手動でワークフローを実行

### PRレビュー依頼
1. PRを作成
2. コメントに「@claude レビューをお願いします」と記載
3. Claudeが詳細なレビューを提供

### 自動コードレビュー
- PRを作成すると自動的に基本的なレビューが実行される
- 大きな変更や重要なファイルの変更時は追加レビューを推奨

### 🚀 100%完全自動化フロー ⭐**新機能**
1. **Issue作成** → 優先度ラベル付きで作成
2. **Claude Code Max自動実行** → Issue番号を検知して自動開始
3. **workflow_run自動検知** → Claude Codeワークフロー完了を即座に検知
4. **自動PR作成** → 人間の介入なしでPR作成
5. **自動マージ** → CI/CDチェック後に自動マージ実行
6. **Issue自動クローズ** → 完了ラベル付きで自動クローズ
7. **ブランチ自動削除** → クリーンアップ完了

**🤖 完全無人実行**: Issue作成からマージまで人間の操作は一切不要

## 注意事項

- Claude APIの利用制限に注意してください
- セキュリティ関連のファイル変更時は人間によるレビューも必須です
- 自動処理の結果は必ず確認してください

## トラブルシューティング

### ワークフローが実行されない
- GitHub Actionsが有効になっているか確認
- Claude GitHub Appがリポジトリにインストールされているか確認
- 必要な権限が設定されているか確認

### Claudeが応答しない
- Claude GitHub Appの認証状態を確認
- Claude Code Maxの契約状況を確認
- ワークフローのログを確認

---

最終更新日: 2025-01-12