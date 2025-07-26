#!/usr/bin/env python3
"""
Smart Automation Test Runner

土日昼間スマート自動化システムのテスト実行スクリプト
Test runner for the weekend daytime smart automation system
"""

import importlib.util
import sys
import unittest
from pathlib import Path


def run_smart_automation_tests():
    """スマート自動化テストの実行"""
    print("🧪 スマート自動化システムテスト実行開始")
    print("=" * 60)
    
    # テストディレクトリのパス
    test_dir = Path(__file__).parent
    
    # テストスイートの作成
    test_suite = unittest.TestSuite()
    
    # test_smart_automation.pyをロード
    test_module_path = test_dir / "test_smart_automation.py"
    
    if test_module_path.exists():
        # モジュールの動的インポート
        spec = importlib.util.spec_from_file_location("test_smart_automation", test_module_path)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        
        # テストクラスを取得してスイートに追加
        test_classes = [
            test_module.SmartAutomationTest,
            test_module.SmartAutomationIntegrationTest
        ]
        
        for test_class in test_classes:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            test_suite.addTests(tests)
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    successes = total_tests - failures - errors
    
    success_rate = (successes / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📈 実行テスト数: {total_tests}")
    print(f"✅ 成功: {successes}")
    print(f"❌ 失敗: {failures}")
    print(f"🚫 エラー: {errors}")
    print(f"🎯 成功率: {success_rate:.1f}%")
    
    if success_rate == 100.0:
        print("\n🚀 スマート自動化システムテスト: 完全成功!")
        print("🌞 土日昼間自動化: 正常動作確認")
    else:
        print(f"\n⚠️  一部テストに問題があります。詳細を確認してください。")
    
    return result


def run_demo():
    """デモンストレーションの実行"""
    print("\n🎭 スマート自動化デモ実行")
    print("=" * 60)
    
    try:
        # デモモジュールのインポートと実行
        demo_module_path = Path(__file__).parent / "smart_automation_demo.py"
        
        if demo_module_path.exists():
            spec = importlib.util.spec_from_file_location("smart_automation_demo", demo_module_path)
            demo_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(demo_module)
            
            # デモ実行
            demo = demo_module.SmartAutomationDemo()
            report = demo.run_demonstration()
            
            return report
        else:
            print("❌ デモファイルが見つかりません")
            return None
            
    except Exception as e:
        print(f"❌ デモ実行エラー: {e}")
        return None


def main():
    """メイン実行関数"""
    print("🚀 土日昼間スマート自動化システム - テスト実行開始")
    print(f"⏰ 実行時刻: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 1. ユニットテスト実行
    test_result = run_smart_automation_tests()
    
    # 2. デモンストレーション実行
    demo_report = run_demo()
    
    # 3. 最終結果
    print("\n🏁 最終結果")
    print("=" * 70)
    
    test_success = test_result.wasSuccessful() if test_result else False
    demo_success = demo_report is not None
    
    if test_success and demo_success:
        print("🎯 ✅ スマート自動化システムテスト: 完全成功")
        print("🌞 ✅ 土日昼間自動化: 正常動作確認")
        print("🚀 ✅ システム準備完了: 100%完全自動化可能")
        return 0
    else:
        print("⚠️  一部のテストまたはデモに問題があります")
        return 1


if __name__ == "__main__":
    sys.exit(main())