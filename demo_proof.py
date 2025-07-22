#!/usr/bin/env python3
"""
RepairGPT実稼働証明デモスクリプト
実際の動作画面とレスポンスを記録・証明
"""

import requests
import json
import time
import datetime
from typing import Dict, Any

class RepairGPTDemo:
    def __init__(self):
        self.api_base = "http://localhost:8004"
        self.streamlit_url = "http://localhost:8501"
        self.demo_log = []
        
    def log_action(self, action: str, result: Any, success: bool = True):
        """アクションと結果をログに記録"""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "result": result,
            "success": success
        }
        self.demo_log.append(entry)
        print(f"📝 {action}: {'✅ Success' if success else '❌ Failed'}")
        
    def test_server_status(self):
        """サーバー状態を確認"""
        print("\n🔍 === サーバー状態確認 ===")
        
        try:
            # API Health Check
            response = requests.get(f"{self.api_base}/health", timeout=5)
            health_data = response.json()
            self.log_action(
                "API Health Check",
                {
                    "status_code": response.status_code,
                    "health": health_data.get("status"),
                    "version": health_data.get("version")
                },
                response.status_code == 200
            )
            
            # Streamlit Accessibility
            streamlit_response = requests.get(self.streamlit_url, timeout=5)
            self.log_action(
                "Streamlit UI Access",
                {
                    "status_code": streamlit_response.status_code,
                    "content_length": len(streamlit_response.content),
                    "content_type": streamlit_response.headers.get('content-type')
                },
                streamlit_response.status_code == 200
            )
            
        except Exception as e:
            self.log_action("Server Status Check", str(e), False)
    
    def demo_chat_functionality(self):
        """チャット機能のデモンストレーション"""
        print("\n💬 === チャット機能デモ ===")
        
        chat_demos = [
            {
                "scenario": "Nintendo Switch Joy-Con問題",
                "payload": {
                    "message": "私のNintendo SwitchのJoy-Conが勝手に動いてしまいます",
                    "device_type": "nintendo_switch",
                    "skill_level": "beginner",
                    "language": "ja"
                }
            },
            {
                "scenario": "iPhone画面修理",
                "payload": {
                    "message": "My iPhone screen is cracked and touch doesn't work",
                    "device_type": "iphone", 
                    "skill_level": "intermediate",
                    "language": "en"
                }
            }
        ]
        
        for demo in chat_demos:
            try:
                print(f"\n🎯 シナリオ: {demo['scenario']}")
                
                response = requests.post(
                    f"{self.api_base}/api/v1/chat",
                    json=demo["payload"],
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get("response", "")
                    
                    self.log_action(
                        f"Chat Demo - {demo['scenario']}",
                        {
                            "input_message": demo["payload"]["message"],
                            "response_length": len(response_text),
                            "contains_mock_indicator": "🤖" in response_text,
                            "device_context": data.get("context", {}),
                            "language": data.get("language"),
                            "first_200_chars": response_text[:200]
                        }
                    )
                    
                    print(f"   📊 応答長: {len(response_text)}文字")
                    print(f"   🤖 モック表示: {'あり' if '🤖' in response_text else 'なし'}")
                    print(f"   📝 応答例: {response_text[:150]}...")
                    
                else:
                    self.log_action(
                        f"Chat Demo - {demo['scenario']}", 
                        f"HTTP {response.status_code}: {response.text}",
                        False
                    )
                    
            except Exception as e:
                self.log_action(f"Chat Demo - {demo['scenario']}", str(e), False)
    
    def demo_diagnosis_functionality(self):
        """診断機能のデモンストレーション"""
        print("\n🔬 === 診断機能デモ ===")
        
        diagnosis_demos = [
            {
                "scenario": "Switch Joy-Con精密診断",
                "payload": {
                    "device_type": "nintendo_switch",
                    "issue_description": "アナログスティックが勝手に動く、キャリブレーションしても直らない",
                    "skill_level": "beginner",
                    "symptoms": ["drift", "calibration_failed", "random_movement"]
                }
            },
            {
                "scenario": "iPhone電池診断",
                "payload": {
                    "device_type": "iphone",
                    "issue_description": "Battery drains very quickly, phone gets hot",
                    "device_model": "iPhone 12",
                    "skill_level": "expert"
                }
            }
        ]
        
        for demo in diagnosis_demos:
            try:
                print(f"\n🔍 診断シナリオ: {demo['scenario']}")
                
                response = requests.post(
                    f"{self.api_base}/api/v1/diagnose",
                    json=demo["payload"],
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    self.log_action(
                        f"Diagnosis Demo - {demo['scenario']}",
                        {
                            "diagnosis": data.get("diagnosis"),
                            "confidence": data.get("confidence"),
                            "possible_causes_count": len(data.get("possible_causes", [])),
                            "recommended_actions_count": len(data.get("recommended_actions", [])),
                            "tools_required": data.get("required_tools", [])[:3],  # 最初の3つだけ
                            "difficulty": data.get("estimated_difficulty"),
                            "time_estimate": data.get("estimated_time"),
                            "success_rate": data.get("success_rate")
                        }
                    )
                    
                    print(f"   🎯 診断結果: {data.get('diagnosis')}")
                    print(f"   📊 信頼度: {data.get('confidence', 0):.1%}")
                    print(f"   ⚡ 難易度: {data.get('estimated_difficulty')}")
                    print(f"   ⏱️  推定時間: {data.get('estimated_time')}")
                    print(f"   🛠️  必要工具: {', '.join(data.get('required_tools', [])[:3])}")
                    
                else:
                    self.log_action(
                        f"Diagnosis Demo - {demo['scenario']}", 
                        f"HTTP {response.status_code}: {response.text}",
                        False
                    )
                    
            except Exception as e:
                self.log_action(f"Diagnosis Demo - {demo['scenario']}", str(e), False)
    
    def test_mock_configuration(self):
        """モック設定の動作確認"""
        print("\n⚙️  === モック設定確認 ===")
        
        try:
            # アプリケーション情報取得
            response = requests.get(f"{self.api_base}/", timeout=5)
            if response.status_code == 200:
                app_info = response.json()
                self.log_action(
                    "App Configuration Check",
                    {
                        "app_name": app_info.get("app_name"),
                        "version": app_info.get("version"),
                        "environment": app_info.get("environment"),
                        "supported_languages": app_info.get("supported_languages")
                    }
                )
                
                print(f"   📱 アプリ名: {app_info.get('app_name')}")
                print(f"   🏷️  バージョン: {app_info.get('version')}")
                print(f"   🌍 環境: {app_info.get('environment')}")
                print(f"   🗣️  対応言語: {app_info.get('supported_languages')}")
                
        except Exception as e:
            self.log_action("Mock Configuration Check", str(e), False)
    
    def generate_proof_report(self):
        """動作証明レポートを生成"""
        print("\n📋 === 動作証明レポート生成 ===")
        
        report = {
            "proof_timestamp": datetime.datetime.now().isoformat(),
            "total_tests": len(self.demo_log),
            "successful_tests": sum(1 for entry in self.demo_log if entry["success"]),
            "failed_tests": sum(1 for entry in self.demo_log if not entry["success"]),
            "test_details": self.demo_log
        }
        
        success_rate = (report["successful_tests"] / report["total_tests"]) * 100 if report["total_tests"] > 0 else 0
        
        print(f"   ✅ 成功テスト: {report['successful_tests']}/{report['total_tests']}")
        print(f"   📈 成功率: {success_rate:.1f}%")
        
        # レポートをファイルに保存
        with open("repairgpt_proof_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log_action("Proof Report Generation", f"Report saved with {success_rate:.1f}% success rate")
        
        return report
    
    def run_full_demo(self):
        """完全デモンストレーションを実行"""
        print("🚀 RepairGPT 完全動作証明デモ開始")
        print("=" * 60)
        print(f"📅 実行日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 各テストを順次実行
        self.test_server_status()
        self.test_mock_configuration()
        self.demo_chat_functionality()
        self.demo_diagnosis_functionality()
        
        # 最終レポート
        report = self.generate_proof_report()
        
        print("\n" + "=" * 60)
        print("🎉 動作証明デモ完了!")
        
        if report["failed_tests"] == 0:
            print("✅ 全ての機能が正常に動作しています!")
        else:
            print(f"⚠️  {report['failed_tests']}件の問題が検出されました")
        
        print(f"📊 詳細レポート: repairgpt_proof_report.json に保存されました")
        
        return report


if __name__ == "__main__":
    demo = RepairGPTDemo()
    demo.run_full_demo()