#!/bin/bash

# Claude Smart Automation Setup Script
# このスクリプトは新しいリポジトリでスマート自動化システムをセットアップします

set -e

# 色付きログ出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 引数チェック
if [ "$#" -ne 2 ]; then
    log_error "使用方法: $0 <owner> <repo>"
    log_info "例: $0 username my-repo"
    exit 1
fi

OWNER=$1
REPO=$2

log_info "🚀 Claude Smart Automation セットアップ開始"
log_info "リポジトリ: ${OWNER}/${REPO}"

# GitHub CLI の確認
if ! command -v gh &> /dev/null; then
    log_error "GitHub CLI (gh) がインストールされていません"
    log_info "インストール: https://cli.github.com/"
    exit 1
fi

# GitHub認証確認
if ! gh auth status &> /dev/null; then
    log_error "GitHub CLI の認証が必要です"
    log_info "認証: gh auth login"
    exit 1
fi

log_success "GitHub CLI 認証確認完了"

# Step 1: GitHub Actions 権限設定
log_info "📋 Step 1: GitHub Actions 権限設定"

# 現在の権限確認
log_info "現在の権限設定を確認中..."
CURRENT_PERMISSIONS=$(gh api repos/${OWNER}/${REPO}/actions/permissions/workflow 2>/dev/null || echo "ERROR")

if [ "$CURRENT_PERMISSIONS" = "ERROR" ]; then
    log_error "リポジトリにアクセスできません。権限を確認してください。"
    exit 1
fi

echo "現在の設定: $CURRENT_PERMISSIONS"

# 権限を write に変更
log_info "権限を write に変更中..."
gh api --method PUT repos/${OWNER}/${REPO}/actions/permissions/workflow \
  --field default_workflow_permissions=write \
  --field can_approve_pull_request_reviews=true

# 変更確認
NEW_PERMISSIONS=$(gh api repos/${OWNER}/${REPO}/actions/permissions/workflow)
echo "新しい設定: $NEW_PERMISSIONS"

if [[ $NEW_PERMISSIONS == *'"default_workflow_permissions":"write"'* ]]; then
    log_success "GitHub Actions 権限設定完了"
else
    log_error "権限設定に失敗しました"
    exit 1
fi

# Step 2: ワークフローファイルの配置
log_info "📋 Step 2: ワークフローファイルの配置"

# .github/workflows ディレクトリ作成
mkdir -p .github/workflows

# テンプレートファイルの存在確認
TEMPLATE_FILE="templates/claude-smart-automation.yml"
if [ ! -f "$TEMPLATE_FILE" ]; then
    log_error "テンプレートファイルが見つかりません: $TEMPLATE_FILE"
    log_info "このスクリプトはrepairgptリポジトリのルートから実行してください"
    exit 1
fi

# ワークフローファイルをコピー
cp "$TEMPLATE_FILE" .github/workflows/claude-smart-automation.yml

log_success "ワークフローファイル配置完了"

# Step 3: 必要なラベル作成
log_info "📋 Step 3: 必要なラベル作成"

# ラベル作成関数
create_label() {
    local name=$1
    local description=$2
    local color=$3
    
    if gh label create "$name" --description "$description" --color "$color" 2>/dev/null; then
        log_success "ラベル作成: $name"
    else
        log_warning "ラベル既存または作成失敗: $name"
    fi
}

create_label "claude-processed" "Claude Codeで処理済み" "1d76db"
create_label "claude-completed" "自動化処理完了" "0e8a16"
create_label "smart-automation" "スマート自動化実行済み" "b60205"
create_label "priority:high" "高優先度" "d93f0b"

log_success "ラベル作成完了"

# Step 4: テスト用Issue作成
log_info "📋 Step 4: テスト用Issue作成"

ISSUE_URL=$(gh issue create \
  --title "テスト: スマート自動化システム" \
  --body "スマート自動化システムのセットアップテスト用Issueです。

**テスト項目:**
- Claude Code実装
- 自動PR作成
- 自動マージ
- Issue自動クローズ
- ブランチ自動削除

@claude テスト実装をお願いします。" \
  --label "claude-processed,priority:high")

log_success "テスト用Issue作成完了: $ISSUE_URL"

# Step 5: セットアップ完了確認
log_info "📋 Step 5: セットアップ完了確認"

cat << 'EOF'

✅ スマート自動化システム セットアップ完了！

📋 次のステップ:
1. Claude Codeでテスト用Issueを実装
2. ワークフローの手動実行でテスト:
   gh workflow run claude-smart-automation.yml
3. 実行ログの確認:
   gh run list --workflow="claude-smart-automation.yml"

⏰ 自動実行スケジュール:
- 平日: 23:00, 02:00, 05:00 JST (夜間実行)
- 土日: 10:00, 14:00, 18:00, 22:00 JST (昼間実行)

📚 詳細ガイド: docs/smart-automation-setup-guide.md

EOF

log_success "🎉 セットアップ完了！"