#!/usr/bin/env python3
"""
ユーザーが報告したapi.health_warningエラーの具体的デバッグ
"""

import sys
import os
import subprocess
from pathlib import Path

def test_all_possible_scenarios():
    """考えられるすべてのシナリオでテスト"""
    print("🔍 Testing all possible api.health_warning error scenarios")
    print("=" * 70)
    
    scenarios = [
        {
            "name": "Direct Python execution",
            "command": ["python3", "src/ui/repair_app.py"],
            "description": "Running repair_app.py directly with Python"
        },
        {
            "name": "Streamlit command execution", 
            "command": ["python3", "-m", "streamlit", "run", "src/ui/repair_app.py", "--server.port", "8503"],
            "description": "Running with streamlit run command"
        },
        {
            "name": "Module import test",
            "command": ["python3", "-c", "import sys; sys.path.insert(0, 'src'); from ui.repair_app import main; print('Import successful')"],
            "description": "Testing module import directly"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🧪 Scenario {i}: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print("-" * 50)
        
        try:
            result = subprocess.run(
                scenario["command"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=Path(__file__).parent
            )
            
            # stdout と stderr の両方をチェック
            output = result.stdout + result.stderr
            
            if "api.health_warning" in output:
                print(f"❌ ERROR FOUND: api.health_warning in output")
                print(f"Full error output:")
                print("-" * 30)
                print(output)
                print("-" * 30)
            else:
                print(f"✅ No api.health_warning error")
                if result.returncode != 0:
                    print(f"⚠️  Other errors present (return code: {result.returncode})")
                    if output.strip():
                        print(f"Output: {output[:200]}...")
                
        except subprocess.TimeoutExpired:
            print("⏱️  Timeout (normal for interactive apps)")
        except Exception as e:
            print(f"⚠️  Test error: {e}")

def test_translation_file_integrity():
    """翻訳ファイルの整合性をチェック"""
    print("\n🔍 Translation file integrity check")
    print("=" * 50)
    
    try:
        import json
        
        # 英語版チェック
        en_file = Path("src/i18n/locales/en.json")
        if en_file.exists():
            with open(en_file, 'r') as f:
                en_data = json.load(f)
            
            if 'api' in en_data and 'health_warning' in en_data['api']:
                print(f"✅ English file: api.health_warning exists")
                print(f"   Value: {en_data['api']['health_warning'][:50]}...")
            else:
                print("❌ English file: api.health_warning MISSING")
                return False
        else:
            print("❌ English translation file not found")
            return False
        
        # 日本語版チェック  
        ja_file = Path("src/i18n/locales/ja.json")
        if ja_file.exists():
            with open(ja_file, 'r') as f:
                ja_data = json.load(f)
            
            if 'api' in ja_data and 'health_warning' in ja_data['api']:
                print(f"✅ Japanese file: api.health_warning exists")
                print(f"   Value: {ja_data['api']['health_warning'][:50]}...")
            else:
                print("❌ Japanese file: api.health_warning MISSING")
                return False
        else:
            print("❌ Japanese translation file not found") 
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Translation file check failed: {e}")
        return False

def test_i18n_system():
    """i18nシステム自体をテスト"""
    print("\n🔍 i18n system test")
    print("=" * 50)
    
    test_code = '''
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))

try:
    from i18n import _, i18n
    
    # Test the specific key
    result = _("api.health_warning")
    print(f"SUCCESS: {result}")
    
except KeyError as e:
    print(f"KEYERROR: Missing translation key: {e}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
'''
    
    try:
        result = subprocess.run([
            sys.executable, "-c", test_code
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if "SUCCESS:" in result.stdout:
            print("✅ i18n system working correctly")
            print(f"Translation: {result.stdout.strip()}")
            return True
        elif "KEYERROR:" in result.stdout:
            print("❌ KEYERROR: Translation key missing")
            print(result.stdout.strip())
            return False
        else:
            print("❌ i18n system error")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ i18n test failed: {e}")
        return False

def main():
    print("🐛 RepairGPT api.health_warning Error Debug")
    print("=" * 70)
    print("Investigating the specific error reported by user")
    print()
    
    # 翻訳ファイル整合性チェック
    translation_ok = test_translation_file_integrity()
    
    # i18nシステムテスト
    i18n_ok = test_i18n_system()
    
    # 実行シナリオテスト
    test_all_possible_scenarios()
    
    print("\n" + "=" * 70)
    print("📊 Debug Summary:")
    print(f"Translation files: {'✅ OK' if translation_ok else '❌ ISSUE'}")
    print(f"i18n system: {'✅ OK' if i18n_ok else '❌ ISSUE'}")
    
    if not translation_ok or not i18n_ok:
        print("\n❌ ISSUE FOUND: Translation system has problems")
        print("💡 This explains why the user still sees api.health_warning errors")
    else:
        print("\n🤔 Translation system appears to be working")
        print("💡 The error might occur in specific execution conditions")
    
    print("\n💬 User feedback needed:")
    print("1. Which exact command produces the error?")
    print("2. What is the complete error message?")
    print("3. In what context does the error appear?")

if __name__ == "__main__":
    main()