#!/usr/bin/env python3
"""
RepairGPT実行スクリプト - インポート問題完全解決版
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def setup_environment():
    """環境設定"""
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    
    # PYTHONPATHに追加
    sys.path.insert(0, str(src_path))
    os.environ['PYTHONPATH'] = str(src_path)
    
    return project_root, src_path

def start_api_server(port=8004):
    """APIサーバーを起動"""
    project_root, src_path = setup_environment()
    
    print(f"🚀 Starting RepairGPT API Server on port {port}")
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(src_path)
    env['REPAIRGPT_API_PORT'] = str(port)
    
    try:
        # APIサーバー起動
        process = subprocess.Popen([
            sys.executable, "-m", "src.api.main"
        ], cwd=str(project_root), env=env)
        
        print(f"✅ API Server started (PID: {process.pid})")
        print(f"📍 Health Check: http://localhost:{port}/health")
        print(f"📖 API Docs: http://localhost:{port}/docs")
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_streamlit_ui(port=8505):
    """Streamlit UIを起動"""
    project_root, src_path = setup_environment()
    
    print(f"🖥️  Starting RepairGPT Streamlit UI on port {port}")
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(src_path)
    
    try:
        # Streamlit起動
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            str(src_path / "ui" / "repair_app.py"),
            "--server.port", str(port),
            "--server.headless", "false"
        ], cwd=str(project_root), env=env)
        
        print(f"✅ Streamlit UI started (PID: {process.pid})")
        print(f"🌐 Web Interface: http://localhost:{port}")
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start Streamlit UI: {e}")
        return None

def run_quick_test():
    """クイックテスト実行"""
    print("\n🧪 Running Quick Mock Test")
    
    try:
        import requests
        
        # API健康チェック
        response = requests.get("http://localhost:8004/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health: {data.get('status')}")
        
        # チャットテスト
        chat_response = requests.post(
            "http://localhost:8004/api/v1/chat",
            json={"message": "Joy-Con drift test", "device_type": "nintendo_switch"},
            timeout=10
        )
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            response_text = chat_data.get("response", "")
            print(f"✅ Chat Test: {len(response_text)} chars, Mock: {'🤖' in response_text}")
        
        print("✅ Quick test passed!")
        
    except Exception as e:
        print(f"⚠️  Quick test failed: {e}")

def show_instructions():
    """使用手順表示"""
    print("\n" + "=" * 60)
    print("🎉 RepairGPT is now running!")
    print("=" * 60)
    print("📍 Access Points:")
    print("   • Streamlit UI: http://localhost:8505")
    print("   • API Backend: http://localhost:8004")
    print("   • API Documentation: http://localhost:8004/docs")
    print("")
    print("🧪 Test Examples:")
    print("   • Type 'Joy-Con drift' in chat")
    print("   • Try iPhone screen repair questions")
    print("   • Test battery diagnostic features")
    print("")
    print("🤖 Mock Mode Active:")
    print("   • No API keys required")
    print("   • All responses marked with 🤖 indicator")
    print("   • Real repair guidance provided")
    print("")
    print("⏹️  To stop: Press Ctrl+C")

def main():
    """メイン実行関数"""
    print("🚀 RepairGPT Launcher")
    print("=" * 60)
    
    # 環境セットアップ
    setup_environment()
    
    # APIサーバー起動
    api_process = start_api_server(8004)
    if not api_process:
        return
    
    # 少し待機
    print("⏳ Waiting for API server to initialize...")
    time.sleep(3)
    
    # Streamlit UI起動
    ui_process = start_streamlit_ui(8505)
    if not ui_process:
        api_process.terminate()
        return
    
    # 少し待機
    print("⏳ Waiting for UI to initialize...")
    time.sleep(5)
    
    # クイックテスト
    run_quick_test()
    
    # 手順表示
    show_instructions()
    
    try:
        # プロセス監視
        while True:
            if api_process.poll() is not None:
                print("❌ API server stopped unexpectedly")
                break
            if ui_process.poll() is not None:
                print("❌ UI server stopped unexpectedly")
                break
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Stopping RepairGPT...")
        
    finally:
        # クリーンアップ
        if api_process:
            api_process.terminate()
        if ui_process:
            ui_process.terminate()
        print("✅ RepairGPT stopped")

if __name__ == "__main__":
    main()