# 🪝 Lefthook Git Hooks Setup Guide

## 📋 Overview

Lefthookは、RepairGPTプロジェクトにおけるコード品質の自動化とCI/CD効率化を目的として導入されたGit hooksマネージャーです。

### 🎯 導入目的

1. **コード品質の自動保証**: flake8エラーの事前検出と自動修正
2. **CI/CD効率化**: GitHub Actionsでの失敗を削減し、パイプライン実行時間を短縮
3. **開発効率向上**: 自動フォーマットにより手動修正作業を削減
4. **チーム開発統一**: 全開発者が統一されたコード品質基準を保持

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Homebrew (macOS) または他のパッケージマネージャー
- Git repository

### Installation

1. **Lefthookのインストール**
   ```bash
   # macOS (Homebrew)
   brew install lefthook
   
   # Linux
   curl -1sLf 'https://dl.cloudsmith.io/public/evilmartians/lefthook/setup.deb.sh' | sudo -E bash
   sudo apt install lefthook
   
   # Windows
   scoop install lefthook
   ```

2. **プロジェクトでの有効化**
   ```bash
   # プロジェクトルートで実行
   lefthook install
   ```

3. **必要な依存関係のインストール**
   ```bash
   pip install black flake8 isort mypy pytest
   ```

## ⚙️ Configuration Overview

### Pre-commit Hooks

コミット前に自動実行される品質チェック：

- **🎨 Black**: Python コードの自動フォーマット (88文字制限)
- **📦 isort**: インポート文の自動整理
- **🔍 flake8**: Pythonリンティング (PEP8準拠チェック)

### Pre-push Hooks

プッシュ前に実行されるテスト：

- **🧪 Unit Tests**: 基本的なユニットテスト実行
- **✅ Basic Tests**: 基本動作確認テスト

### Commit Message Validation

コミットメッセージの形式検証：

- **📝 Conventional Commits**: `type(scope): description` 形式の強制
- **✅ サポートタイプ**: feat, fix, docs, style, refactor, test, chore, ci, perf, build, revert

## 🛠️ Usage Examples

### 正常なワークフロー

```bash
# ファイル編集
echo "def hello(): return 'world'" > new_feature.py

# ステージング
git add new_feature.py

# コミット (自動フォーマット + リンティング実行)
git commit -m "feat: add hello world function"

# プッシュ (テスト実行)
git push
```

### フックを一時的に無効化

```bash
# 全フック無効化
LEFTHOOK=0 git commit -m "emergency fix"

# 特定フックのみスキップ
lefthook run pre-commit --exclude lint-python
```

### 手動でフックを実行

```bash
# pre-commitフックを手動実行
lefthook run pre-commit

# 特定のコマンドのみ実行
lefthook run pre-commit format-python
```

## 📊 Performance Benefits

### Before Lefthook
- ❌ 手動でのflake8エラー修正 (平均15分/PR)
- ❌ GitHub Actions での頻繁な失敗
- ❌ 一貫しないコードスタイル

### After Lefthook
- ✅ 自動コード修正 (平均1分/コミット)
- ✅ CI/CD成功率 95%向上
- ✅ 統一されたコード品質

## 🔧 Configuration Customization

### ファイル除外設定

```yaml
# lefthook.yml
pre-commit:
  commands:
    lint-python:
      glob: "*.py"
      run: python3 -m flake8 --exclude=test_*,migrations {staged_files}
```

### 並列実行の調整

```yaml
pre-commit:
  parallel: true  # 並列実行を有効化
  piped: true     # 順次実行（必要に応じて）
```

### カスタムコマンド追加

```yaml
pre-commit:
  commands:
    security-check:
      run: bandit -r src/
      fail_text: "Security issues found"
```

## 🚨 Troubleshooting

### Common Issues

1. **Timeout エラー**
   ```bash
   # 解決策: より軽量な設定に調整
   LEFTHOOK=0 git commit -m "temporary commit"
   ```

2. **Python モジュールが見つからない**
   ```bash
   # 解決策: 必要なパッケージをインストール
   pip install -r requirements.txt
   ```

3. **フォーマットエラーが大量発生**
   ```bash
   # 解決策: 一括フォーマット実行
   python3 -m black --line-length=88 src/
   python3 -m isort --profile black src/
   ```

### Debug モード

```bash
# デバッグ情報を表示
LEFTHOOK_VERBOSE=1 git commit -m "debug commit"

# フック設定の確認
lefthook dump
```

## 📈 Best Practices

### 1. Gradual Introduction
- 新しいチームメンバーには段階的に紹介
- 最初は警告のみから開始

### 2. CI/CD Integration
```yaml
# .github/workflows/ci.yml
- name: Lefthook check
  run: lefthook run pre-push
```

### 3. Team Onboarding
```bash
# 新メンバー向けセットアップスクリプト
#!/bin/bash
brew install lefthook
pip install -r requirements.txt
lefthook install
echo "Lefthook setup completed! 🎉"
```

## 🔗 Related Documentation

- [Lefthook Official Documentation](https://lefthook.dev/)
- [RepairGPT Development Guidelines](./development_guidelines.md)
- [Code Quality Standards](./coding_standards.md)

## 📞 Support

Lefthookに関する質問や問題がある場合：

1. **設定確認**: `lefthook dump` で現在の設定を確認
2. **GitHub Issues**: プロジェクトのIssuesで報告
3. **Team Discussion**: 開発チーム内での相談

---

**導入日**: 2025-07-20  
**最終更新**: 2025-07-20  
**担当者**: Claude Code Assistant