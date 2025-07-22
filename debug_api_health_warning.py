#!/usr/bin/env python3
"""
Debug script to identify api.health_warning error
ユーザーがどこでこのエラーに遭遇しているかを特定
"""

import sys
import json
from pathlib import Path

def check_translation_files():
    """翻訳ファイルの状態をチェック"""
    print("🔍 Checking translation files...")
    
    en_file = Path("src/i18n/locales/en.json")
    ja_file = Path("src/i18n/locales/ja.json")
    
    for file_path, lang in [(en_file, "English"), (ja_file, "Japanese")]:
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                has_api = 'api' in data
                has_health_warning = has_api and 'health_warning' in data['api']
                
                print(f"  {lang} ({file_path}):")
                print(f"    - Has 'api' section: {has_api}")
                print(f"    - Has 'health_warning': {has_health_warning}")
                
                if has_health_warning:
                    print(f"    - Value: {data['api']['health_warning'][:50]}...")
                
            except Exception as e:
                print(f"  {lang} - ERROR: {e}")
        else:
            print(f"  {lang} - FILE NOT FOUND: {file_path}")

def test_i18n_system():
    """i18n システムをテスト"""
    print("\n🔍 Testing i18n system...")
    
    sys.path.insert(0, str(Path.cwd() / 'src'))
    
    try:
        from i18n import _, i18n
        
        # 英語でテスト
        i18n.set_language('en')
        en_result = _('api.health_warning')
        print(f"  English: {en_result[:50]}...")
        
        # 日本語でテスト
        i18n.set_language('ja')
        ja_result = _('api.health_warning')
        print(f"  Japanese: {ja_result[:50]}...")
        
        print("  ✅ i18n system working correctly")
        
    except Exception as e:
        print(f"  ❌ i18n system error: {e}")
        import traceback
        print(traceback.format_exc())

def test_safe_translate():
    """safe_translate 関数をテスト"""
    print("\n🔍 Testing safe_translate function...")
    
    sys.path.insert(0, str(Path.cwd() / 'src'))
    
    try:
        # Safe translate function (copied from repair_app.py)
        def safe_translate(key: str, fallback: str = "") -> str:
            """安全な翻訳関数（フォールバック付き）"""
            translations = {
                "api.health_warning": "⚠️ API server is not running. Some features may be limited. Start the API server with: python3 src/api/main.py",
                "app.title": "RepairGPT - AI Repair Assistant", 
                "app.tagline": "AI-Powered Electronic Device Repair Assistant",
            }
            
            if key in translations:
                return translations[key]
            
            try:
                from i18n import _
                return _(key)
            except:
                return fallback or key
        
        result = safe_translate('api.health_warning')
        print(f"  Result: {result[:50]}...")
        print("  ✅ safe_translate working correctly")
        
    except Exception as e:
        print(f"  ❌ safe_translate error: {e}")
        import traceback
        print(traceback.format_exc())

def test_repair_app_import():
    """repair_app.py のインポートをテスト"""
    print("\n🔍 Testing repair_app.py import...")
    
    sys.path.insert(0, str(Path.cwd() / 'src'))
    
    try:
        # Try to import the safe_translate function from repair_app
        from ui.repair_app import safe_translate
        result = safe_translate('api.health_warning')
        print(f"  Import successful: {result[:50]}...")
        print("  ✅ repair_app.py import working")
        
    except Exception as e:
        print(f"  ❌ repair_app.py import error: {e}")
        import traceback
        print(traceback.format_exc())

def main():
    print("🔧 API Health Warning Debug Tool")
    print("=" * 50)
    print("This tool helps identify where the 'api.health_warning' error occurs")
    print()
    
    check_translation_files()
    test_i18n_system()
    test_safe_translate()
    test_repair_app_import()
    
    print("\n" + "=" * 50)
    print("🏁 Debug Complete")
    print()
    print("If all tests pass but you still see 'api.health_warning' error:")
    print("1. Try running: streamlit run src/ui/repair_app_safe.py")
    print("2. Check browser console for JavaScript errors")
    print("3. Clear browser cache and try again")
    print("4. Report exact steps to reproduce the error")

if __name__ == "__main__":
    main()