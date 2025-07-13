#!/usr/bin/env python3
"""
夜間自動化システム動作確認テスト実行スクリプト

Issue #33: テスト: 夜間自動化システム動作確認
実行時刻: #午後

使用方法:
    python tests/run_automation_tests.py
"""

import sys
import os
from pathlib import Path
import subprocess
import yaml
import re

# プロジェクトルートを sys.path に追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class NightAutomationTestRunner:
    """夜間自動化システムテスト実行クラス"""
    
    def __init__(self):
        self.project_root = project_root
        self.workflows_dir = self.project_root / ".github" / "workflows"
        self.test_results = []
    
    def log_result(self, test_name: str, status: str, details: str = ""):
        """テスト結果をログ"""
        self.test_results.append({
            "test": test_name,
            "status": status, 
            "details": details
        })
        symbol = "✅" if status == "PASS" else "❌"
        print(f"{symbol} {test_name}: {status}")
        if details:
            print(f"   {details}")
    
    def test_claude_implementation(self):
        """✅ Claude Code: ブランチ作成・実装テスト"""
        test_file = Path("tests/test_night_automation.py")
        if test_file.exists():
            self.log_result("Claude Code実装", "PASS", "テストファイル作成完了")
        else:
            self.log_result("Claude Code実装", "FAIL", "テストファイルが見つからない")
    
    def test_workflow_files(self):
        """🔄 ワークフローファイル存在確認"""
        required_workflows = [
            "claude-perfect-automation.yml",
            "claude-full-automation.yml",
            "claude-auto-merge.yml"
        ]
        
        missing_files = []
        for workflow in required_workflows:
            workflow_path = self.workflows_dir / workflow
            if not workflow_path.exists():
                missing_files.append(workflow)
        
        if not missing_files:
            self.log_result("ワークフローファイル", "PASS", 
                          f"{len(required_workflows)}個のワークフローファイル確認")
        else:
            self.log_result("ワークフローファイル", "FAIL", 
                          f"不足ファイル: {', '.join(missing_files)}")
    
    def test_pr_creation_logic(self):
        """🔄 夜間自動PR作成ロジック"""
        full_automation_file = self.workflows_dir / "claude-full-automation.yml"
        
        if not full_automation_file.exists():
            self.log_result("PR作成ロジック", "FAIL", "ワークフローファイル不足")
            return
        
        with open(full_automation_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # PR作成ロジックの確認
        pr_patterns = [
            r"pulls\.create",
            r"head.*branch",
            r"base.*main"
        ]
        
        missing_patterns = []
        for pattern in pr_patterns:
            if not re.search(pattern, content):
                missing_patterns.append(pattern)
        
        if not missing_patterns:
            self.log_result("PR作成ロジック", "PASS", "PR作成処理確認完了")
        else:
            self.log_result("PR作成ロジック", "FAIL", 
                          f"不足パターン: {', '.join(missing_patterns)}")
    
    def test_auto_merge_logic(self):
        """🔄 夜間自動マージロジック"""
        auto_merge_file = self.workflows_dir / "claude-auto-merge.yml"
        
        if not auto_merge_file.exists():
            self.log_result("自動マージロジック", "FAIL", "ワークフローファイル不足")
            return
        
        with open(auto_merge_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # マージロジックの確認
        merge_patterns = [
            r"pulls\.merge",
            r"merge_method",
            r"squash"
        ]
        
        missing_patterns = []
        for pattern in merge_patterns:
            if not re.search(pattern, content):
                missing_patterns.append(pattern)
        
        if not missing_patterns:
            self.log_result("自動マージロジック", "PASS", "マージ処理確認完了")
        else:
            self.log_result("自動マージロジック", "FAIL", 
                          f"不足パターン: {', '.join(missing_patterns)}")
    
    def test_issue_close_logic(self):
        """🔄 Issue自動クローズロジック"""
        workflows_to_check = [
            "claude-full-automation.yml",
            "claude-auto-merge.yml"
        ]
        
        close_logic_found = False
        
        for workflow in workflows_to_check:
            workflow_path = self.workflows_dir / workflow
            if workflow_path.exists():
                with open(workflow_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if re.search(r"issues\.update.*state.*closed", content):
                    close_logic_found = True
                    break
        
        if close_logic_found:
            self.log_result("Issue自動クローズ", "PASS", "クローズ処理確認完了")
        else:
            self.log_result("Issue自動クローズ", "FAIL", "クローズ処理が見つからない")
    
    def test_branch_deletion_logic(self):
        """🔄 ブランチ自動削除ロジック"""
        workflows_to_check = [
            "claude-full-automation.yml",
            "claude-auto-merge.yml"
        ]
        
        delete_logic_found = False
        
        for workflow in workflows_to_check:
            workflow_path = self.workflows_dir / workflow
            if workflow_path.exists():
                with open(workflow_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if re.search(r"git\.deleteRef.*heads", content):
                    delete_logic_found = True
                    break
        
        if delete_logic_found:
            self.log_result("ブランチ自動削除", "PASS", "削除処理確認完了")
        else:
            self.log_result("ブランチ自動削除", "FAIL", "削除処理が見つからない")
    
    def test_schedule_configuration(self):
        """スケジュール設定確認"""
        perfect_automation_file = self.workflows_dir / "claude-perfect-automation.yml"
        
        if not perfect_automation_file.exists():
            self.log_result("スケジュール設定", "FAIL", "ワークフローファイル不足")
            return
        
        try:
            with open(perfect_automation_file, 'r', encoding='utf-8') as f:
                workflow = yaml.safe_load(f)
            
            if "schedule" in workflow.get("on", {}):
                cron = workflow["on"]["schedule"][0]["cron"]
                self.log_result("スケジュール設定", "PASS", f"CRON設定: {cron}")
            else:
                self.log_result("スケジュール設定", "FAIL", "スケジュール設定なし")
                
        except Exception as e:
            self.log_result("スケジュール設定", "FAIL", f"YAML解析エラー: {e}")
    
    def run_all_tests(self):
        """全テスト実行"""
        print("🚀 夜間自動化システム動作確認テスト開始")
        print("Issue #33: テスト: 夜間自動化システム動作確認")
        print("実行時刻: #午後")
        print("-" * 60)
        
        # 各テストを実行
        self.test_claude_implementation()
        self.test_workflow_files()
        self.test_pr_creation_logic()
        self.test_auto_merge_logic()
        self.test_issue_close_logic()
        self.test_branch_deletion_logic()
        self.test_schedule_configuration()
        
        # 結果サマリー
        print("\n" + "=" * 60)
        print("🎯 夜間自動化システム動作確認テスト結果")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["status"] == "PASS")
        total = len(self.test_results)
        
        for result in self.test_results:
            symbol = "✅" if result["status"] == "PASS" else "❌"
            print(f"{symbol} {result['test']}: {result['status']}")
        
        print(f"\n📊 テスト結果: {passed}/{total} 完了")
        
        if passed == total:
            print("🎉 全テスト完了! 夜間自動化システム準備完了")
            print("\n夜間自動化フロー:")
            print("- ✅ Claude Code: ブランチ作成・実装")
            print("- ✅ 夜間自動PR作成: テスト実行")
            print("- ✅ 夜間自動マージ: テスト実行")
            print("- ✅ Issue自動クローズ: テスト実行")
            print("- ✅ ブランチ自動削除: テスト実行")
            return True
        else:
            print("⚠️  一部テストに問題があります。詳細を確認してください。")
            return False


def main():
    """メイン実行関数"""
    runner = NightAutomationTestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n✨ 夜間自動化システム動作確認テスト: 完全成功!")
        sys.exit(0)
    else:
        print("\n❌ テストに失敗しました。")
        sys.exit(1)


if __name__ == "__main__":
    main()