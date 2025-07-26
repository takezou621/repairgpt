"""
テスト設定ファイル - pytest configuration for RepairGPT

Issue #88: 基本的なユニットテストとテスト環境の構築
Issue #33: 夜間自動化システム動作確認テスト
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator

import pytest

# Ensure src directory is in Python path for all tests
repo_root = Path(__file__).parent.parent
src_dir = repo_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


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


# ===== 基本的なユニットテスト用フィクスチャ (Issue #88) =====


@pytest.fixture
def sample_test_data() -> Dict[str, Any]:
    """基本的なテスト用サンプルデータ"""
    return {
        "test_key": "test_value",
        "numbers": [1, 2, 3],
        "config": {"debug": True, "timeout": 30},
        "items": ["item1", "item2", "item3"],
    }


@pytest.fixture
def mock_japanese_device_mapper():
    """Mock Japanese device mapper for testing"""
    from unittest.mock import Mock
    
    mapper = Mock()
    mapper.map_device_name.return_value = "Nintendo Switch"
    mapper.find_best_match.return_value = ("Nintendo Switch", 0.8)
    mapper.is_device_name.return_value = True
    mapper.get_supported_devices.return_value = ["Nintendo Switch", "iPhone", "PlayStation"]
    
    return mapper


@pytest.fixture
def mock_repair_guide_service():
    """Mock repair guide service for testing"""
    from unittest.mock import Mock, AsyncMock
    from datetime import datetime
    
    service = Mock()
    service.search_guides = AsyncMock(return_value=[])
    service.get_guide_details = AsyncMock(return_value=None)
    service._calculate_confidence_score.return_value = 0.8
    service._preprocess_japanese_query.return_value = "processed query"
    service._is_japanese_query.return_value = False
    
    return service


@pytest.fixture
def stable_confidence_score():
    """Fixture that provides deterministic confidence scores for testing"""
    def _calculate_score(guide, query, filters):
        # Deterministic scoring based on simple string matching
        score = 0.5
        if hasattr(guide, 'title') and query.lower() in guide.title.lower():
            score += 0.3
        if hasattr(guide, 'device') and hasattr(filters, 'device_type') and filters.device_type:
            if filters.device_type.lower() in guide.device.lower():
                score += 0.2
        return min(score, 1.0)
    return _calculate_score


@pytest.fixture
def temp_test_directory() -> Generator[Path, None, None]:
    """一時テストディレクトリの作成と削除"""
    temp_dir = Path(tempfile.mkdtemp(prefix="repairgpt_test_"))
    try:
        yield temp_dir
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


@pytest.fixture
def mock_api_response() -> Dict[str, Any]:
    """模擬API応答データ"""
    return {
        "status": "success",
        "data": {"id": 123, "name": "Test Device", "type": "smartphone", "issues": ["screen_crack", "battery_drain"]},
        "timestamp": "2025-07-16T21:30:00Z",
    }


@pytest.fixture
def test_device_data() -> Dict[str, Any]:
    """テスト用デバイスデータ"""
    return {
        "device_id": "test_device_001",
        "manufacturer": "TestCorp",
        "model": "TestPhone Pro",
        "os_version": "TestOS 15.0",
        "symptoms": ["Device won't turn on", "Battery drains quickly", "Screen flickering"],
        "repair_history": [],
    }


# ===== 自動化テスト用フィクスチャ (Issue #33) =====


@pytest.fixture
def automation_test_data():
    """自動化テスト用のデータ"""
    return {
        "issue_number": 33,
        "issue_title": "テスト: 夜間自動化システム動作確認",
        "branch_name": "claude/issue-33-20250713_015100",
        "expected_workflows": ["claude-perfect-automation.yml", "claude-full-automation.yml", "claude-auto-merge.yml"],
        "automation_features": [
            "Claude Code: ブランチ作成・実装",
            "夜間自動PR作成",
            "夜間自動マージ",
            "Issue自動クローズ",
            "ブランチ自動削除",
        ],
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
def test_environment_setup(request):
    """各テスト前の環境設定とクリーンアップ"""
    # Test isolation: Clear any existing module-level state
    import sys
    
    # Store original sys.path
    original_path = sys.path.copy()
    
    # Reset any module-level singletons
    try:
        from src.services.repair_guide_service import reset_repair_guide_service
        reset_repair_guide_service()
    except ImportError:
        pass
    
    try:
        from src.utils.japanese_device_mapper import _mapper_instance
        if '_mapper_instance' in globals():
            globals()['_mapper_instance'] = None
    except ImportError:
        pass
    
    # 自動化テストのみGitHub Actions環境が必要
    if hasattr(request, "node"):
        test_path = str(request.node.fspath)
        if "automation" in test_path or "night_automation" in request.node.name:
            # 自動化テストの場合はGitHub Actions環境が必要
            if not Path(".github").exists():
                pytest.skip("GitHub Actions環境でないため、自動化テストをスキップします")
    
    # Yield control to the test
    yield
    
    # Post-test cleanup
    # Restore original sys.path
    sys.path[:] = original_path
    
    # Clear any test-specific state
    try:
        from src.services.repair_guide_service import reset_repair_guide_service
        reset_repair_guide_service()
    except ImportError:
        pass


def pytest_sessionfinish(session, exitstatus):
    """テストセッション終了時の処理"""
    if exitstatus == 0:
        print("\n✅ 夜間自動化システム動作確認テスト: 全て完了")
        print("🎯 自動化システム準備完了 - Issue #33")
    else:
        print(f"\n❌ テスト失敗 (exit code: {exitstatus})")
