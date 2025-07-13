#!/usr/bin/env python3
"""
夜間自動化システム検証実行スクリプト

使用方法:
    python verification/run_verification.py
    python verification/run_verification.py --component claude-code
    python verification/run_verification.py --report-only
"""

import argparse
import sys
import json
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from verification.automation_test_framework import NightAutomationVerifier


def main():
    parser = argparse.ArgumentParser(
        description="夜間自動化システム検証を実行"
    )
    parser.add_argument(
        "--component",
        choices=["claude-code", "auto-pr", "auto-merge", "auto-close", "auto-delete"],
        help="特定のコンポーネントのみ検証"
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="検証を実行せず、前回の結果レポートのみ表示"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="verification_report.md",
        help="レポート出力ファイル名"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON形式で結果を出力"
    )
    
    args = parser.parse_args()
    
    verifier = NightAutomationVerifier()
    
    if args.report_only:
        # 前回の結果があれば表示（今回は新規実装なので現在の状態を報告）
        print("前回の検証結果はありません。新規検証を実行してください。")
        return
    
    if args.component:
        # 特定コンポーネントのみ検証
        print(f"=== {args.component} 検証実行 ===")
        verifier.start_verification()
        
        if args.component == "claude-code":
            result = verifier.verify_claude_code_branch_creation()
        elif args.component == "auto-pr":
            result = verifier.verify_night_auto_pr_creation()
        elif args.component == "auto-merge":
            result = verifier.verify_night_auto_merge()
        elif args.component == "auto-close":
            result = verifier.verify_issue_auto_close()
        elif args.component == "auto-delete":
            result = verifier.verify_branch_auto_deletion()
        
        print(f"結果: {result.status.value}")
        print(f"メッセージ: {result.message}")
        
        if args.json:
            output_data = {
                "component": result.component,
                "status": result.status.value,
                "message": result.message,
                "timestamp": result.timestamp.isoformat(),
                "duration": result.duration,
                "details": result.details
            }
            print("\n=== JSON出力 ===")
            print(json.dumps(output_data, ensure_ascii=False, indent=2))
    
    else:
        # 全体検証実行
        print("=== 夜間自動化システム完全検証実行 ===")
        summary = verifier.run_complete_verification()
        
        if args.json:
            print("\n=== JSON出力 ===")
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(f"\n=== 検証完了 ===")
            print(f"総実行時間: {summary['total_duration']:.2f}秒")
            print(f"成功: {summary['passed']}/{summary['total_tests']}")
            print(f"失敗: {summary['failed']}/{summary['total_tests']}")
            print(f"未設定: {summary['pending']}/{summary['total_tests']}")
            print(f"成功率: {summary['success_rate']:.1f}%")
        
        # レポート生成・保存
        report = verifier.generate_report()
        
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n詳細レポートを {output_path} に保存しました。")
        
        # 簡易結果表示
        if not args.json:
            print("\n=== 簡易結果 ===")
            for result in verifier.results:
                status_emoji = {
                    "passed": "✅",
                    "failed": "❌", 
                    "pending": "⏳",
                    "skipped": "⏭️"
                }
                print(f"{status_emoji.get(result.status.value, '❓')} {result.component}: {result.message}")


if __name__ == "__main__":
    main()