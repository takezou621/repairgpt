#!/usr/bin/env python3
"""
夜間自動化システム検証デモンストレーション

このスクリプトは検証フレームワークの動作例を示します。
Issue #36 の動作検証要件に対応しています。
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from verification.automation_test_framework import NightAutomationVerifier


def run_demo():
    """デモンストレーション実行"""
    print("=" * 60)
    print("🌙 夜間自動化システム動作検証デモ")
    print("=" * 60)
    print()
    
    print("📋 検証対象コンポーネント:")
    print("🔄 Claude Code: ブランチ作成・実装")
    print("🔄 夜間自動PR作成: システム動作確認")
    print("🔄 夜間自動マージ: 完全自動実行")
    print("🔄 Issue自動クローズ: バッチ処理確認")
    print("🔄 ブランチ自動削除: クリーンアップ確認")
    print()
    
    # 検証実行
    verifier = NightAutomationVerifier()
    
    print("🚀 検証開始...")
    print("-" * 40)
    
    summary = verifier.run_complete_verification()
    
    print("-" * 40)
    print("✅ 検証完了")
    print()
    
    # 結果サマリー表示
    print(f"📊 検証結果サマリー:")
    print(f"   総実行時間: {summary['total_duration']:.2f}秒")
    print(f"   成功: {summary['passed']}/{summary['total_tests']}")
    print(f"   失敗: {summary['failed']}/{summary['total_tests']}")  
    print(f"   未設定: {summary['pending']}/{summary['total_tests']}")
    print(f"   成功率: {summary['success_rate']:.1f}%")
    print()
    
    # 各コンポーネント結果表示
    print("📝 詳細結果:")
    for result in verifier.results:
        status_emoji = {
            "passed": "✅",
            "failed": "❌",
            "pending": "⏳", 
            "skipped": "⏭️"
        }
        emoji = status_emoji.get(result.status.value, "❓")
        print(f"   {emoji} {result.component}")
        print(f"      ステータス: {result.status.value}")
        print(f"      メッセージ: {result.message}")
        if result.duration:
            print(f"      実行時間: {result.duration:.3f}秒")
        print()
    
    # 重要な注意事項
    print("⚠️  重要な注意事項:")
    print("   • このシステムはCLAUDE.mdの方針に従い正直な結果を報告します")
    print("   • 「完了！」の安易な報告は行いません") 
    print("   • 実際の動作確認後にのみ成功を報告します")
    print("   • 未設定項目は「未設定」として正直に報告します")
    print()
    
    # 次のステップ
    print("🔧 推奨される次のステップ:")
    print("   1. GitHub Actions ワークフロー設定")
    print("   2. 段階的な自動化機能の導入")
    print("   3. 安全性チェック機能の実装")
    print("   4. エラーハンドリングの強化")
    print()
    
    # レポート生成案内
    print("📄 詳細レポート:")
    print("   実行コマンド: python verification/run_verification.py")
    print("   レポートファイル: verification_report.md")
    print()
    
    print("=" * 60)
    print("✨ デモンストレーション完了")
    print("=" * 60)
    
    return summary


if __name__ == "__main__":
    try:
        summary = run_demo()
        
        # 終了コード設定（CI/CD での使用を考慮）
        if summary['failed'] > 0:
            print(f"⚠️  {summary['failed']} 件の失敗が検出されました")
            sys.exit(1)
        elif summary['pending'] > 0:
            print(f"ℹ️  {summary['pending']} 件の未設定項目があります")
            sys.exit(0)  # 未設定は正常終了
        else:
            print("🎉 すべての検証が成功しました")
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ デモ実行中にエラーが発生しました: {e}")
        sys.exit(1)