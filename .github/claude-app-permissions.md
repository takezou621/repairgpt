# Claude GitHub App権限設定ガイド

完全自動化フローを実現するために、Claude GitHub Appに以下の権限が必要です。

## 必要な権限一覧

### Repository Permissions
- **Actions**: Read and write
  - ワークフロー実行結果の読み取り
  - workflow_runトリガーの動作
  
- **Contents**: Write
  - ブランチ作成
  - ファイル変更のコミット
  - リポジトリ内容の読み書き
  
- **Issues**: Write
  - Issueの読み取り、更新、クローズ
  - ラベルの追加・削除
  - コメントの作成
  
- **Pull requests**: Write
  - PR作成、更新、マージ
  - PRコメントの作成
  - レビューの実行
  
- **Metadata**: Read
  - リポジトリメタデータの読み取り
  
- **Checks**: Read
  - CI/CDチェック結果の読み取り

### Account Permissions
- **Email addresses**: Read (optional)
  - ユーザー情報の取得

## 権限設定手順

### 1. GitHub Appの設定画面にアクセス
```
https://github.com/settings/apps/claude
```

### 2. Repository permissions セクションで以下を設定
```
Actions: Read and write
Contents: Write  
Issues: Write
Pull requests: Write
Metadata: Read
Checks: Read
```

### 3. 設定を保存し、リポジトリに再インストール

### 4. 権限変更の確認
```bash
# 権限が正しく設定されているかテスト
gh api repos/OWNER/REPO/installation
```

## トラブルシューティング

### よくある権限エラー

1. **"Resource not accessible by integration"**
   - Contents: Write 権限が不足
   - Pull requests: Write 権限が不足
   
2. **"Branch creation failed"**
   - Contents: Write 権限の確認
   - リポジトリの保護ルール設定の確認
   
3. **"PR creation failed"**
   - Pull requests: Write 権限の確認
   - ブランチ保護ルールの確認

### 権限設定の確認方法

```yaml
# ワークフロー内で権限を確認
- name: Check permissions
  uses: actions/github-script@v7
  with:
    script: |
      const permissions = context.payload.installation?.permissions;
      console.log('Current permissions:', permissions);
```

## セキュリティ考慮事項

- 最小権限の原則に従い、必要な権限のみを付与
- 定期的な権限の見直し
- ログの監視とアクセス制御

## 参考資料
- [GitHub App permissions](https://docs.github.com/en/developers/apps/building-github-apps/setting-permissions-for-github-apps)
- [Claude GitHub Integration](https://support.anthropic.com/en/articles/10167454-using-the-github-integration)