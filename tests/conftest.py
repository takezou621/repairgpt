"""
テスト設定ファイル - pytest configuration for automation tests

Issue #33: 夜間自動化システム動作確認テスト
"""

import pytest
import os
from pathlib import Path


@pytest.fixture(scope="session")
def repo_root():
    """リポジトリのルートディレクトリを取得"""
    current_dir = Path(__file__).parent
    while not (current_dir / ".git").exists():
        if current_dir.parent == current_dir:
            break
        current_dir = current_dir.parent
    return current_dir


@pytest.fixture(scope="session") 
def github_workflows_dir(repo_root):
    """GitHub Actionsワークフローディレクトリのパス"""
    return repo_root / ".github" / "workflows"


@pytest.fixture
def automation_test_data():
    """自動化テスト用のデータ"""
    return {
        "issue_number": 33,
        "issue_title": "テスト: 夜間自動化システム動作確認",
        "branch_name": "claude/issue-33-20250713_015100",
        "expected_workflows": [
            "claude-perfect-automation.yml",
            "claude-full-automation.yml", 
            "claude-auto-merge.yml"
        ],
        "automation_features": [
            "Claude Code: ブランチ作成・実装",
            "夜間自動PR作成",
            "夜間自動マージ", 
            "Issue自動クローズ",
            "ブランチ自動削除"
        ]
    }


def pytest_configure(config):
    """pytest設定の初期化"""
    print("\n🚀 夜間自動化システム動作確認テスト - Issue #33")
    print("実行時刻: #午後")
    print("-" * 60)


def pytest_collection_modifyitems(config, items):
    """テスト項目の修正"""
    for item in items:
        # 自動化テストにマーカーを追加
        if "night_automation" in item.name or "automation" in str(item.fspath):
            item.add_marker(pytest.mark.automation)


@pytest.fixture(autouse=True)
def test_environment_setup():
    """各テスト前の環境設定"""
    # 現在のディレクトリがリポジトリルートかチェック
    if not Path(".github").exists():
        pytest.skip("GitHub Actions環境でないため、スキップします")


def pytest_sessionfinish(session, exitstatus):
    """テストセッション終了時の処理"""
    if exitstatus == 0:
        print("\n✅ 夜間自動化システム動作確認テスト: 全て完了")
        print("🎯 自動化システム準備完了 - Issue #33")
    else:
        print(f"\n❌ テスト失敗 (exit code: {exitstatus})")