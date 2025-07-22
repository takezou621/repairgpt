#!/usr/bin/env python3
"""
相対インポートエラーを完全回避するRepairGPTアプリ起動スクリプト
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# プロジェクトルートを設定
PROJECT_ROOT = Path(__file__).parent
SRC_PATH = PROJECT_ROOT / "src"

def setup_python_path():
    """PYTHONPATHを確実にセットアップ"""
    python_path = str(SRC_PATH)
    
    # sys.pathに追加
    if python_path not in sys.path:
        sys.path.insert(0, python_path)
    
    # 環境変数にも設定
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    if python_path not in current_pythonpath:
        if current_pythonpath:
            os.environ['PYTHONPATH'] = f"{python_path}:{current_pythonpath}"
        else:
            os.environ['PYTHONPATH'] = python_path
    
    print(f"✅ PYTHONPATH set to: {os.environ['PYTHONPATH']}")

def start_api_server():
    """API サーバーを起動"""
    print("🚀 Starting API server...")
    
    # run_api.pyを作成してそこからAPIを起動
    api_script = PROJECT_ROOT / "run_api.py"
    
    api_script_content = '''#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# プロジェクトルートをPYTHONPATHに追加
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
os.environ['PYTHONPATH'] = str(src_path)

print("🔧 Starting FastAPI server with safe imports...")

try:
    import uvicorn
    from api.main import app
    
    print("✅ All imports successful")
    print("🌐 Starting server on http://localhost:8004")
    
    uvicorn.run(
        "api.main:app",
        host="localhost", 
        port=8004,
        reload=False,
        log_level="info"
    )
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Trying alternative approach...")
    
    # フォールバック方法
    try:
        from api.main import create_app
        app = create_app()
        uvicorn.run(app, host="localhost", port=8004)
    except Exception as e2:
        print(f"❌ Alternative approach failed: {e2}")
        print("API server startup failed")

except Exception as e:
    print(f"❌ API server error: {e}")
'''
    
    with open(api_script, 'w', encoding='utf-8') as f:
        f.write(api_script_content)
    
    # サブプロセスでAPIサーバーを起動
    try:
        api_process = subprocess.Popen([
            sys.executable, str(api_script)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 少し待ってから接続テスト
        time.sleep(3)
        
        try:
            import requests
            response = requests.get("http://localhost:8004/health", timeout=5)
            if response.status_code == 200:
                print("✅ API server started successfully")
                return api_process
            else:
                print(f"⚠️ API server health check failed: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️ API server not responding yet")
        except ImportError:
            print("⚠️ requests module not available for testing")
            
        return api_process
        
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_streamlit_app():
    """Streamlit アプリを起動"""
    print("🎨 Starting Streamlit app...")
    
    # run_streamlit.pyを作成
    streamlit_script = PROJECT_ROOT / "run_streamlit.py"
    
    streamlit_script_content = '''#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# プロジェクトルートをPYTHONPATHに追加
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
os.environ['PYTHONPATH'] = str(src_path)

print("🎨 Starting Streamlit with safe imports...")

try:
    import streamlit as st
    print("✅ Streamlit import successful")
    
    # repair_app.pyを直接実行
    from ui.repair_app import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Streamlit import error: {e}")
    print("Please install streamlit: pip install streamlit")
    
except Exception as e:
    print(f"❌ Streamlit app error: {e}")
'''
    
    with open(streamlit_script, 'w', encoding='utf-8') as f:
        f.write(streamlit_script_content)
    
    # Streamlitを起動
    try:
        streamlit_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", str(streamlit_script),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        
        time.sleep(2)
        print("✅ Streamlit app started on http://localhost:8501")
        return streamlit_process
        
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")
        return None

def test_functionality():
    """基本機能をテスト"""
    print("\n🧪 Testing basic functionality...")
    
    setup_python_path()
    
    try:
        # チャットボット機能テスト
        from chat.llm_chatbot import RepairChatbot
        
        chatbot = RepairChatbot(use_mock=True)
        print("✅ ChatBot initialized successfully")
        
        response = chatbot.chat("Test message")
        print(f"✅ Chat response generated: {len(response)} chars")
        
        # 画像解析機能テスト
        from services.image_analysis import ImageAnalysisService
        
        image_service = ImageAnalysisService(use_mock=True)
        print("✅ Image analysis service initialized successfully")
        
        print("🎉 All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """メイン実行関数"""
    print("🚀 RepairGPT Safe Startup Script")
    print("=" * 50)
    
    # PYTHONPATHをセットアップ
    setup_python_path()
    
    # 基本機能をテスト
    if not test_functionality():
        print("❌ Basic functionality test failed. Cannot start applications.")
        return
    
    print("\n🌟 Starting RepairGPT Applications...")
    
    # APIサーバーを起動
    api_process = start_api_server()
    
    time.sleep(2)
    
    # Streamlitアプリを起動
    streamlit_process = start_streamlit_app()
    
    print("\n" + "=" * 50)
    print("🎉 RepairGPT Applications Started!")
    print("🌐 Web Interface: http://localhost:8501")
    print("🔧 API Server: http://localhost:8004")
    print("📚 API Docs: http://localhost:8004/docs")
    print("\n💡 Press Ctrl+C to stop all services")
    
    try:
        # プロセスが終了するまで待機
        if streamlit_process:
            streamlit_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        
        if api_process:
            api_process.terminate()
        if streamlit_process:
            streamlit_process.terminate()
            
        print("✅ All services stopped")

if __name__ == "__main__":
    main()