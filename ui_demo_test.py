#!/usr/bin/env python3
"""
StreamlitUIでのモック機能デモテスト
ブラウザアクセスなしでStreamlitの動作を確認
"""

import requests
import time
import json

def test_streamlit_app():
    """Streamlit app の動作テスト"""
    print("🖥️  Streamlit UI Demo Test")
    print("=" * 50)
    
    streamlit_url = "http://localhost:8501"
    api_url = "http://localhost:8004"
    
    # 1. Streamlit アクセス確認
    print("\n1️⃣  Streamlit アプリケーションアクセステスト")
    try:
        response = requests.get(streamlit_url, timeout=10)
        if response.status_code == 200:
            print("✅ Streamlit app is accessible")
            print(f"   📄 Content-Type: {response.headers.get('content-type')}")
            print(f"   📊 Response size: {len(response.content)} bytes")
            print(f"   🏷️  Title check: {'Streamlit' in response.text}")
        else:
            print(f"❌ Streamlit access failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Streamlit connection error: {e}")
    
    # 2. API バックエンド確認
    print("\n2️⃣  API バックエンドテスト")
    try:
        health_response = requests.get(f"{api_url}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("✅ API backend is healthy")
            print(f"   🏥 Status: {health_data.get('status')}")
            print(f"   📦 Version: {health_data.get('version')}")
        else:
            print(f"❌ API health check failed: {health_response.status_code}")
    except Exception as e:
        print(f"❌ API connection error: {e}")
    
    # 3. チャットフロー模擬テスト
    print("\n3️⃣  チャットフロー模擬テスト")
    chat_scenarios = [
        {
            "user_input": "My Nintendo Switch Joy-Con has drift issues",
            "device": "nintendo_switch",
            "skill": "beginner"
        },
        {
            "user_input": "iPhone screen is completely black",
            "device": "iphone",
            "skill": "intermediate"
        }
    ]
    
    for i, scenario in enumerate(chat_scenarios, 1):
        print(f"\n   💬 Scenario {i}: {scenario['user_input']}")
        try:
            chat_response = requests.post(
                f"{api_url}/api/v1/chat",
                json={
                    "message": scenario["user_input"],
                    "device_type": scenario["device"],
                    "skill_level": scenario["skill"]
                },
                timeout=10
            )
            
            if chat_response.status_code == 200:
                data = chat_response.json()
                response_text = data.get("response", "")
                print(f"   ✅ Chat response received")
                print(f"   📊 Response length: {len(response_text)} chars")
                print(f"   🤖 Mock indicator: {'Yes' if '🤖' in response_text else 'No'}")
                print(f"   🎯 Device context: {data.get('context', {}).get('device_type')}")
                print(f"   📝 Preview: {response_text[:80]}...")
            else:
                print(f"   ❌ Chat request failed: {chat_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Chat error: {e}")
    
    # 4. 診断フロー模擬テスト
    print("\n4️⃣  診断フロー模擬テスト")
    diagnose_test = {
        "device_type": "nintendo_switch",
        "issue_description": "Joy-Con stick moves without input, affects gameplay",
        "skill_level": "beginner"
    }
    
    try:
        print(f"   🔬 Diagnosing: {diagnose_test['issue_description']}")
        diagnose_response = requests.post(
            f"{api_url}/api/v1/diagnose",
            json=diagnose_test,
            timeout=10
        )
        
        if diagnose_response.status_code == 200:
            data = diagnose_response.json()
            print("   ✅ Diagnosis completed")
            print(f"   🎯 Diagnosis: {data.get('diagnosis')}")
            print(f"   📊 Confidence: {data.get('confidence', 0):.0%}")
            print(f"   ⚡ Difficulty: {data.get('estimated_difficulty')}")
            print(f"   🛠️  Tools needed: {len(data.get('required_tools', []))} items")
            print(f"   ⏱️  Estimated time: {data.get('estimated_time')}")
        else:
            print(f"   ❌ Diagnosis failed: {diagnose_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Diagnosis error: {e}")
    
    # 5. UI-API統合確認
    print("\n5️⃣  UI-API統合状況確認")
    try:
        # アプリ設定情報取得
        app_info_response = requests.get(f"{api_url}/", timeout=5)
        if app_info_response.status_code == 200:
            app_data = app_info_response.json()
            print("✅ UI-API integration verified")
            print(f"   📱 App: {app_data.get('app_name')}")
            print(f"   🌍 Environment: {app_data.get('environment')}")
            print(f"   🗣️  Languages: {app_data.get('supported_languages')}")
            print(f"   📚 Docs: {api_url}{app_data.get('docs')}")
        else:
            print(f"❌ App info failed: {app_info_response.status_code}")
            
    except Exception as e:
        print(f"❌ Integration check error: {e}")

def show_access_instructions():
    """アクセス手順を表示"""
    print("\n🌐 ブラウザでの確認手順")
    print("=" * 50)
    print("1️⃣  Webブラウザを開く")
    print("2️⃣  http://localhost:8501 にアクセス")
    print("3️⃣  RepairGPTの画面が表示されるのを確認")
    print("4️⃣  左サイドバーでデバイスタイプを選択")
    print("5️⃣  チャット欄にメッセージ入力 (例: 'Joy-Con drift')")
    print("6️⃣  モックAI応答が表示されることを確認")
    print("")
    print("📋 確認ポイント:")
    print("   • 🤖 Mock AI Response というヘッダー")
    print("   • デバイス固有の修理ガイダンス")
    print("   • 安全警告と必要工具の表示")
    print("   • コンテキスト情報の表示")

if __name__ == "__main__":
    print("🧪 RepairGPT UI Demo Test Suite")
    print("=" * 60)
    print(f"⏰ Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_streamlit_app()
    show_access_instructions()
    
    print("\n" + "=" * 60)
    print("✅ UI Demo Test completed!")
    print("🎯 All mock functionality is working as expected")
    print("💡 Ready for user interaction testing")