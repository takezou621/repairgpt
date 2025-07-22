#!/usr/bin/env python3
"""
RepairGPT完全起動スクリプト
APIサーバーとStreamlitを正しく起動してapi.health_warning問題を解決
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

def cleanup():
    """既存のプロセスをクリーンアップ"""
    os.system("pkill -f 'streamlit\\|uvicorn' 2>/dev/null")
    time.sleep(2)

def start_api_server():
    """APIサーバーを起動"""
    print("📡 Starting API Server...")
    
    # APIサーバー用環境変数
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd() / "src")
    
    # Uvicornを直接起動
    proc = subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "api.main:app",
        "--host", "0.0.0.0",
        "--port", "8001",
        "--reload"
    ], env=env, cwd=str(Path.cwd()))
    
    time.sleep(8)  # APIサーバー起動待機
    return proc

def start_streamlit():
    """Streamlitを起動"""
    print("🎨 Starting Streamlit UI...")
    
    # Streamlit用環境変数
    env = os.environ.copy()
    env["FASTAPI_BASE_URL"] = "http://localhost:8001"
    env["PYTHONPATH"] = str(Path.cwd() / "src")
    
    proc = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run",
        "src/ui/repair_app.py",
        "--server.port", "8507",
        "--server.address", "0.0.0.0"
    ], env=env, cwd=str(Path.cwd()))
    
    time.sleep(6)  # Streamlit起動待機
    return proc

def test_connections():
    """接続テスト"""
    import requests
    
    print("🧪 Testing connections...")
    
    try:
        # API test
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Server: OK")
        else:
            print(f"⚠️ API Server: {response.status_code}")
    except Exception as e:
        print(f"❌ API Server: {e}")
    
    try:
        # Streamlit test
        response = requests.get("http://localhost:8507", timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit: OK")
            if "api.health_warning" in response.text:
                print("❌ Found api.health_warning error!")
            else:
                print("✅ No api.health_warning error found!")
        else:
            print(f"⚠️ Streamlit: {response.status_code}")
    except Exception as e:
        print(f"❌ Streamlit: {e}")

def main():
    print("🔧 RepairGPT Complete Startup")
    print("=" * 50)
    
    try:
        cleanup()
        
        # Start services
        api_proc = start_api_server()
        streamlit_proc = start_streamlit()
        
        # Test connections
        test_connections()
        
        print("\n🎉 RepairGPT完全起動成功!")
        print("📱 Streamlit: http://localhost:8507")
        print("📡 API Server: http://localhost:8001")
        print("\n⌨️  Press Ctrl+C to stop all services")
        
        # Keep alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            api_proc.terminate()
            streamlit_proc.terminate()
            
            try:
                api_proc.wait(timeout=5)
                streamlit_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                api_proc.kill()
                streamlit_proc.kill()
            
            print("✅ All services stopped")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        cleanup()

if __name__ == "__main__":
    main()