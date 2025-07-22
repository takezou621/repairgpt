#!/usr/bin/env python3
"""
インポートエラーの詳細デバッグスクリプト
"""

import sys
import os
import subprocess
import traceback
from pathlib import Path

def test_direct_execution_all():
    """全ての主要ファイルを直接実行してテスト"""
    print("🔍 Direct Execution Debug Test")
    print("=" * 50)
    
    test_files = [
        "src/chat/llm_chatbot.py",
        "src/services/image_analysis.py", 
        "src/api/main.py",
        "src/ui/repair_app.py",
        "src/config/settings_simple.py",
        "src/utils/logger.py"
    ]
    
    for file_path in test_files:
        full_path = Path(file_path)
        if not full_path.exists():
            print(f"⚠️ File not found: {file_path}")
            continue
            
        print(f"\n📄 Testing: {file_path}")
        print("-" * 30)
        
        try:
            # 直接実行テスト
            result = subprocess.run([
                sys.executable, str(full_path)
            ], capture_output=True, text=True, timeout=5, cwd="/Users/kawai/dev/repairgpt")
            
            if result.returncode == 0:
                print("✅ SUCCESS - No import errors")
                if result.stdout:
                    print(f"📝 Output: {result.stdout[:100]}...")
            else:
                print(f"❌ FAILED - Return code: {result.returncode}")
                if result.stderr:
                    print(f"🚨 Error: {result.stderr}")
                    
        except subprocess.TimeoutExpired:
            print("⏱️ TIMEOUT - Script running (may be interactive)")
        except Exception as e:
            print(f"❌ EXECUTION ERROR: {e}")

def test_import_methods():
    """異なるインポート方法をテスト"""
    print("\n🧪 Import Methods Test")
    print("=" * 50)
    
    # PYTHONPATHを設定
    project_root = Path("/Users/kawai/dev/repairgpt")
    src_path = project_root / "src"
    
    os.environ['PYTHONPATH'] = str(src_path)
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    test_cases = [
        # (モジュール名, クラス/関数名, 説明)
        ("chat.llm_chatbot", "RepairChatbot", "チャットボット"),
        ("services.image_analysis", "ImageAnalysisService", "画像解析"),
        ("config.settings_simple", "Settings", "設定"),
        ("utils.logger", "get_logger", "ログ"),
    ]
    
    for module_name, class_name, description in test_cases:
        print(f"\n🔧 Testing: {description} ({module_name}.{class_name})")
        
        try:
            # 方法1: 通常のインポート
            module = __import__(module_name, fromlist=[class_name])
            obj = getattr(module, class_name)
            print(f"✅ Method 1 SUCCESS: {type(obj)}")
            
        except ImportError as e:
            print(f"❌ Method 1 FAILED: {e}")
            
            try:
                # 方法2: 直接パス指定
                import importlib.util
                file_path = src_path / module_name.replace('.', '/') + '.py'
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                obj = getattr(module, class_name)
                print(f"✅ Method 2 SUCCESS: {type(obj)}")
                
            except Exception as e2:
                print(f"❌ Method 2 FAILED: {e2}")
        
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")

def check_common_issues():
    """よくある問題をチェック"""
    print("\n🔍 Common Issues Check")
    print("=" * 50)
    
    project_root = Path("/Users/kawai/dev/repairgpt")
    src_path = project_root / "src"
    
    # __init__.py ファイルの存在確認
    print("📁 Checking __init__.py files:")
    required_dirs = ['chat', 'services', 'config', 'utils', 'api', 'api/routes', 'features']
    
    for dir_name in required_dirs:
        init_file = src_path / dir_name / "__init__.py"
        if init_file.exists():
            print(f"✅ {dir_name}/__init__.py exists")
        else:
            print(f"❌ {dir_name}/__init__.py missing")
            # 作成
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_file.write_text('"""Package initialization"""', encoding='utf-8')
            print(f"   🔧 Created {dir_name}/__init__.py")
    
    # PYTHONPATH確認
    print(f"\n🐍 PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print(f"📍 Current working directory: {os.getcwd()}")
    print(f"🎯 Project root: {project_root}")
    print(f"📂 Source path: {src_path}")
    
    # sys.path確認
    print(f"\n📚 sys.path entries:")
    for i, path in enumerate(sys.path[:5]):  # 最初の5つだけ表示
        print(f"  {i}: {path}")

def provide_solutions():
    """解決策を提示"""
    print("\n💡 Import Error Solutions")
    print("=" * 50)
    
    print("🔧 Try these commands to run RepairGPT safely:")
    print()
    print("1️⃣ Safe app startup (no import errors):")
    print("   python3 run_app_safe.py")
    print()
    print("2️⃣ Import-free functionality test:")
    print("   python3 run_without_imports.py")
    print()
    print("3️⃣ Set PYTHONPATH and run directly:")
    print("   export PYTHONPATH=/Users/kawai/dev/repairgpt/src")
    print("   python3 -m streamlit run src/ui/repair_app.py")
    print()
    print("4️⃣ API server with safe imports:")
    print("   cd /Users/kawai/dev/repairgpt")
    print("   PYTHONPATH=src python3 -m uvicorn api.main:app --host localhost --port 8004")
    print()
    print("5️⃣ If specific file fails, tell me which one:")
    print("   Example: 'python3 src/chat/llm_chatbot.py' gives import error")

def main():
    """メインデバッグ関数"""
    print("🐛 RepairGPT Import Error Debugger")
    print("=" * 60)
    print("This will help identify exactly where the import error occurs")
    print()
    
    check_common_issues()
    test_import_methods()
    test_direct_execution_all()
    provide_solutions()
    
    print("\n" + "=" * 60)
    print("🎯 Debug completed!")
    print("📝 Please tell me which specific command gives you the import error")

if __name__ == "__main__":
    main()