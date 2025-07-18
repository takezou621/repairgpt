# スマート自動化システム セットアップガイド

## 📋 概要

このガイドでは、Claude Codeを使用したスマート自動化システムを他のリポジトリでも適用するための手順をまとめています。

## 🎯 実現できること

- **100%完全自動化**: Issue作成 → Claude Code実装 → 自動PR作成 → 自動マージ → 自動クローズ
- **スマートスケジュール**: 平日夜間・土日昼間の最適な時間帯での自動実行
- **GitHub Actions権限制限解消**: PR作成制限の完全解除

## 📋 前提条件

- GitHub リポジトリの管理者権限
- GitHub Actions が有効化されていること
- Claude Code の基本的な使用経験

## 🔧 セットアップ手順

### Step 1: GitHub Actions 権限設定

#### 1.1 ワークフロー権限の設定

```bash
# リポジトリの権限確認
gh api repos/{owner}/{repo}/actions/permissions/workflow

# 権限を write に変更（PR作成制限解除）
gh api --method PUT repos/{owner}/{repo}/actions/permissions/workflow \
  --field default_workflow_permissions=write \
  --field can_approve_pull_request_reviews=true
```

#### 1.2 権限設定の確認

```bash
# 設定確認（以下のようになっていることを確認）
# {"default_workflow_permissions":"write","can_approve_pull_request_reviews":true}
gh api repos/{owner}/{repo}/actions/permissions/workflow
```

### Step 2: スマート自動化ワークフローの追加

#### 2.1 ワークフローファイル作成

`.github/workflows/claude-smart-automation.yml` を作成:

```yaml
name: Claude Smart Automation

on:
  schedule:
    # 平日夜間実行 (23:00, 02:00, 05:00 JST)
    - cron: '0 14,17,20 * * 1-5'  # UTC時間 月-金
    # 土日昼間実行 (10:00, 14:00, 18:00, 22:00 JST)
    - cron: '0 1,5,9,13 * * 0,6'  # UTC時間 土日
  workflow_dispatch:

jobs:
  smart-automation:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write
      actions: read
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        fetch-depth: 0
        ref: main
    
    - name: Smart Automation Processing
      uses: actions/github-script@v7
      with:
        github-token: ${{ secrets.GITHUB_TOKEN }}
        script: |
          console.log('🚀 SMART AUTOMATION START');
          const now = new Date();
          console.log(`Execution time: ${now.toISOString()}`);
          
          try {
            // 全オープンIssueを取得
            const issues = await github.rest.issues.listForRepo({
              owner: context.repo.owner,
              repo: context.repo.repo,
              state: 'open',
              per_page: 50
            });
            
            console.log(`Found ${issues.data.length} open issues`);
            
            // claude-processedラベルがあるIssueを検索
            const processedIssues = issues.data.filter(issue => 
              issue.labels.some(label => label.name === 'claude-processed')
            );
            
            console.log(`Found ${processedIssues.length} Claude-processed issues`);
            
            if (processedIssues.length === 0) {
              console.log('No Claude-processed issues found, ending');
              return;
            }
            
            for (const issue of processedIssues) {
              console.log(`\n🔍 Processing Issue #${issue.number}: ${issue.title}`);
              
              try {
                // 関連ブランチを検索
                const branches = await github.rest.repos.listBranches({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  per_page: 100
                });
                
                const claudeBranches = branches.data.filter(branch => 
                  branch.name.includes(`issue-${issue.number}`) ||
                  branch.name.includes(`claude`) && branch.name.includes(`${issue.number}`)
                );
                
                if (claudeBranches.length === 0) {
                  console.log(`No Claude branch found for Issue #${issue.number}`);
                  continue;
                }
                
                const claudeBranch = claudeBranches[0];
                console.log(`Found branch: ${claudeBranch.name}`);
                
                // 既存PRをチェック
                const existingPRs = await github.rest.pulls.list({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  head: `${context.repo.owner}:${claudeBranch.name}`,
                  state: 'all'
                });
                
                let prNumber = null;
                
                if (existingPRs.data.length > 0) {
                  const pr = existingPRs.data[0];
                  console.log(`Found existing PR #${pr.number}, state: ${pr.state}`);
                  
                  if (pr.state === 'open') {
                    prNumber = pr.number;
                  } else {
                    console.log(`PR #${pr.number} is already ${pr.state}`);
                    continue;
                  }
                } else {
                  // PRを作成
                  console.log(`📝 Creating PR for Issue #${issue.number}`);
                  
                  try {
                    const pr = await github.rest.pulls.create({
                      owner: context.repo.owner,
                      repo: context.repo.repo,
                      title: `fix: ${issue.title} (closes #${issue.number})`,
                      head: claudeBranch.name,
                      base: 'main',
                      body: `## 🚀 スマート自動化処理

### 関連Issue
Closes #${issue.number}

### 自動化フロー
- [x] ✅ Claude Code実装検知
- [x] ✅ 自動PR作成（平日夜間・土日昼間）
- [x] ✅ 自動マージ実行
- [x] ✅ Issue自動クローズ
- [x] ✅ ブランチ自動削除

### 実行時刻
${now.toISOString()}

### スケジュール
- 平日: 23:00, 02:00, 05:00 JST
- 土日: 10:00, 14:00, 18:00, 22:00 JST

---
🚀 **Smart Automation** | Generated with Claude Code Max`
                    });
                    
                    prNumber = pr.data.number;
                    console.log(`✅ Created PR #${prNumber}`);
                    
                  } catch (prError) {
                    console.log(`❌ PR creation failed: ${prError.message}`);
                    continue;
                  }
                }
                
                // PRマージ処理
                if (prNumber) {
                  console.log(`🔄 Auto-merging PR #${prNumber}`);
                  
                  // マージ前に短時間待機
                  await new Promise(resolve => setTimeout(resolve, 3000));
                  
                  try {
                    await github.rest.pulls.merge({
                      owner: context.repo.owner,
                      repo: context.repo.repo,
                      pull_number: prNumber,
                      commit_title: `Smart Auto-merge: Issue #${issue.number}`,
                      merge_method: 'squash'
                    });
                    console.log(`✅ Merged PR #${prNumber}`);
                  } catch (mergeError) {
                    console.log(`⚠️ Merge failed: ${mergeError.message}`);
                    continue;
                  }
                }
                
                // Issue完了処理
                console.log(`🔒 Closing Issue #${issue.number}`);
                
                await github.rest.issues.createComment({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  issue_number: issue.number,
                  body: `🚀 **スマート自動化処理完了**

Issue #${issue.number} のスマート自動化が完了しました。

**実行内容:**
- 🤖 Claude Code実装検知
- 📝 自動PR作成・マージ
- 🔒 Issue自動クローズ
- 🧹 ブランチ自動削除

**実行時刻:** ${now.toISOString()}

**実行スケジュール:**
- 平日: 夜間自動実行（23:00, 02:00, 05:00 JST）
- 土日: 昼間自動実行（10:00, 14:00, 18:00, 22:00 JST）

---
🚀 **Smart Automation Success** | Generated with Claude Code Max`
                });
                
                await github.rest.issues.update({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  issue_number: issue.number,
                  state: 'closed'
                });
                
                await github.rest.issues.addLabels({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  issue_number: issue.number,
                  labels: ['claude-completed', 'smart-automation']
                });
                
                // ブランチ削除
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                try {
                  await github.rest.git.deleteRef({
                    owner: context.repo.owner,
                    repo: context.repo.repo,
                    ref: `heads/${claudeBranch.name}`
                  });
                  console.log(`🗑️ Deleted branch ${claudeBranch.name}`);
                } catch (deleteError) {
                  console.log(`⚠️ Branch deletion failed: ${deleteError.message}`);
                }
                
                console.log(`🎯 Issue #${issue.number} SMART AUTOMATION COMPLETED!`);
                
              } catch (issueError) {
                console.log(`❌ Issue #${issue.number} processing failed: ${issueError.message}`);
                continue;
              }
            }
            
            console.log('\n🚀 SMART AUTOMATION FINISHED');
            
          } catch (error) {
            console.log(`❌ Smart automation error: ${error.message}`);
            console.log(error.stack);
            throw error;
          }
```

### Step 3: ラベルの作成

自動化に必要なラベルを作成:

```bash
# 必要なラベルを作成
gh label create "claude-processed" --description "Claude Codeで処理済み" --color "1d76db"
gh label create "claude-completed" --description "自動化処理完了" --color "0e8a16"
gh label create "smart-automation" --description "スマート自動化実行済み" --color "b60205"
gh label create "priority:high" --description "高優先度" --color "d93f0b"
```

### Step 4: テスト実行

#### 4.1 テスト用Issue作成

```bash
gh issue create --title "テスト: スマート自動化システム" \
  --body "スマート自動化システムのテスト用Issueです。

@claude テスト実装をお願いします。" \
  --label "claude-processed,priority:high"
```

#### 4.2 Claude Codeでの実装

1. テスト用ブランチを作成
2. 何らかの実装を行う（例：READMEの更新）
3. コミット・プッシュ

#### 4.3 自動化ワークフローの手動実行

```bash
# 手動でワークフロー実行（テスト用）
gh workflow run claude-smart-automation.yml
```

## ⏰ スケジュール詳細

### 平日スケジュール（月-金）
- **23:00 JST** (14:00 UTC)
- **02:00 JST** (17:00 UTC)
- **05:00 JST** (20:00 UTC)

### 土日スケジュール（土・日）
- **10:00 JST** (01:00 UTC)
- **14:00 JST** (05:00 UTC)
- **18:00 JST** (09:00 UTC)
- **22:00 JST** (13:00 UTC)

## 🛠️ カスタマイズ

### スケジュール変更

`cron` 式を変更してスケジュールをカスタマイズ:

```yaml
schedule:
  # 例：毎日6時間ごと
  - cron: '0 0,6,12,18 * * *'
  
  # 例：平日のみ12時間ごと
  - cron: '0 0,12 * * 1-5'
```

### ブランチ命名規則のカスタマイズ

ワークフロー内の検索条件を変更:

```javascript
const claudeBranches = branches.data.filter(branch => 
  branch.name.includes(`feature/issue-${issue.number}`) ||  // カスタム規則
  branch.name.includes(`fix/${issue.number}`)
);
```

### 自動マージ条件のカスタマイズ

特定の条件でのみ自動マージを実行:

```javascript
// 例：特定のラベルがある場合のみ自動マージ
if (issue.labels.some(label => label.name === 'auto-merge-approved')) {
  // マージ処理
}
```

## 🔍 トラブルシューティング

### 権限エラー

```
GitHub Actions is not permitted to create or approve pull requests
```

**解決方法:**
```bash
gh api --method PUT repos/{owner}/{repo}/actions/permissions/workflow \
  --field default_workflow_permissions=write \
  --field can_approve_pull_request_reviews=true
```

### ブランチが見つからない

**原因:** Claude Codeのブランチ命名規則と検索条件が一致しない

**解決方法:** ワークフロー内の検索条件を調整

### ワークフローが実行されない

**確認項目:**
1. `.github/workflows/` ディレクトリに正しく配置されているか
2. YAML構文エラーがないか
3. スケジュール設定が正しいか

## 📊 監視とメンテナンス

### 実行ログの確認

```bash
# 最新の実行ログを確認
gh run list --workflow="claude-smart-automation.yml" --limit 5
gh run view {run-id} --log
```

### 成功率の監視

```bash
# ワークフロー実行状況の確認
gh run list --workflow="claude-smart-automation.yml" --limit 20
```

## 🎯 ベストプラクティス

1. **段階的導入**: まずテスト環境で動作確認
2. **権限最小化**: 必要最小限の権限のみ付与
3. **ログ監視**: 定期的な実行ログの確認
4. **エラーハンドリング**: 失敗時の適切な処理
5. **スケジュール調整**: プロジェクトに応じた実行頻度の設定

## 📋 チェックリスト

### セットアップ完了確認

- [ ] GitHub Actions権限設定完了
- [ ] ワークフローファイル作成・配置完了
- [ ] 必要なラベル作成完了
- [ ] テスト実行で動作確認完了
- [ ] ログ確認で正常動作確認完了

### 運用開始前確認

- [ ] スケジュール設定の確認
- [ ] 権限設定の再確認
- [ ] エラー通知設定（必要に応じて）
- [ ] チームメンバーへの周知
- [ ] 緊急時の停止手順確認

---

## 📚 参考リンク

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub REST API](https://docs.github.com/en/rest)
- [Cron Expression Generator](https://crontab.guru/)

このガイドに従うことで、任意のリポジトリでスマート自動化システムを構築できます。