#!/usr/bin/env python3
"""
RepairGPT簡単起動スクリプト - インポートエラー完全回避
"""

import os
import sys
from pathlib import Path

def main():
    """メイン起動関数"""
    print("🚀 RepairGPT Easy Startup")
    print("=" * 40)
    
    # プロジェクトルートとソースパスを設定
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    
    # PYTHONPATHを確実に設定
    os.environ['PYTHONPATH'] = str(src_path)
    
    print(f"📁 Project: {project_root}")
    print(f"🐍 PYTHONPATH: {src_path}")
    print()
    
    print("🌟 Choose startup option:")
    print("1️⃣ Web Interface (Streamlit) - Recommended")
    print("2️⃣ API Server (FastAPI)")
    print("3️⃣ Both (Web + API)")
    print("4️⃣ Test Mode (Import-free testing)")
    print()
    
    try:
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            start_streamlit()
        elif choice == "2":
            start_api()
        elif choice == "3":
            start_both()
        elif choice == "4":
            start_test()
        else:
            print("❌ Invalid choice")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

def start_streamlit():
    """Streamlitアプリを起動"""
    print("\n🎨 Starting Streamlit Web Interface...")
    os.system("streamlit run src/ui/repair_app.py --server.port 8501")

def start_api():
    """FastAPIサーバーを起動"""
    print("\n🔧 Starting FastAPI Server...")
    os.chdir(Path(__file__).parent)
    os.system("uvicorn api.main:app --host localhost --port 8004")

def start_both():
    """両方を起動"""
    print("\n🌟 Starting both Web Interface and API Server...")
    print("⚠️  This will start API in background and Web in foreground")
    print("📝 Press Ctrl+C to stop both services")
    
    import subprocess
    import time
    
    # APIをバックグラウンドで起動
    api_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "api.main:app", 
        "--host", "localhost", "--port", "8004"
    ], cwd=Path(__file__).parent / "src")
    
    time.sleep(3)  # APIが起動するまで待機
    
    try:
        # Streamlitをフォアグラウンドで起動
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "src/ui/repair_app.py",
            "--server.port", "8501"
        ])
    finally:
        print("\n🛑 Stopping API server...")
        api_process.terminate()

def start_test():
    """テストモードで起動"""
    print("\n🧪 Starting Test Mode...")
    os.system("python3 run_without_imports.py")

if __name__ == "__main__":
    main()