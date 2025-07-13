# Claude Code Action 完全自動化システム - テストセットアップ

## 🚀 実装完了機能

### 1. 完全自動化フロー
- **Issue検索**: 優先度順（high → middle → low）で `status:todo` ラベル付きIssueを検索
- **ブランチ作成**: `auto-fix-issue-{issue_number}` 形式で自動ブランチ作成
- **コード生成**: Claude APIを使用して完全なコード解決策を生成
- **コード適用**: 生成されたコードを自動的にファイルに適用・コミット
- **PR作成**: 自動的にPull Requestを作成
- **自動レビュー**: Botが自動的にPRを承認
- **自動マージ**: 承認後、自動的にマージ実行
- **Issue完了**: 自動的にIssueをクローズ＆完了コメント追加

### 2. 必要なGitHub Secrets
```
GITHUB_TOKEN: 自動提供（権限設定済み）
```
**注意**: Claude APIキーは不要！Claude Code CLIを直接使用

### 3. 実行スケジュール
- **夜間実行**: JST 23:00〜06:00（30分間隔）
- **手動実行**: GitHub Actions画面から手動トリガー可能

## 🧪 テスト方法

### 1. テストIssue作成
```bash
# GitHubでIssueを作成し、以下ラベルを付与
- status:todo
- priority:high (または middle, low)
```

### 2. 手動テスト実行
1. GitHubリポジトリの「Actions」タブを開く
2. 「Nightly Claude Code Action (Full Automation)」を選択
3. 「Run workflow」ボタンをクリック
4. 実行ログを確認

### 3. 期待される動作
1. ✅ Issue検索＆選択
2. ✅ ブランチ作成
3. ✅ Claude APIでコード生成
4. ✅ コード適用＆コミット
5. ✅ PR作成
6. ✅ 自動レビュー＆承認
7. ✅ 自動マージ
8. ✅ Issue完了＆クローズ

## 🔧 トラブルシューティング

### よくある問題
1. **Claude Code CLI未インストール**: 自動インストールされるはずですが、失敗した場合はログを確認
2. **権限不足**: GitHub Actionsの権限設定を確認
3. **ブランチ競合**: 既存ブランチがある場合は自動的に再利用

### ログ確認
GitHub Actions実行ログで各ステップの成功/失敗を確認可能

## 🎯 完全自動化保証

このシステムは以下を**完全自動化**します：
- ✅ コード作成・編集
- ✅ PR作成
- ✅ 自動レビュー
- ✅ 自動マージ
- ✅ Issue完了

**寝てる間にコードが完成する**世界を実現！