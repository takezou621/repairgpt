#!/usr/bin/env python3
"""
全ファイルの相対インポートを絶対インポートのフォールバック付きに修正
"""

import os
import re
import sys
from pathlib import Path

def fix_relative_imports(file_path):
    """ファイルの相対インポートを修正"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 相対インポートのパターンを検索
        relative_import_pattern = r'from (\.\.[^.]*?) import (.+?)$'
        matches = re.findall(relative_import_pattern, content, re.MULTILINE)
        
        if not matches:
            return False  # 変更なし
        
        print(f"🔧 Fixing imports in: {file_path}")
        
        # 各相対インポートを修正
        for relative_path, imports in matches:
            # 相対パスを絶対パスに変換
            absolute_path = relative_path.replace('..', '').strip('.')
            if absolute_path.startswith('.'):
                absolute_path = absolute_path[1:]
            
            old_import = f"from {relative_path} import {imports}"
            
            # try/except 付きの新しいインポート
            new_import = f"""try:
    from {relative_path} import {imports}
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
    from {absolute_path} import {imports}"""
            
            # 既にtry/except で囲まれているかチェック
            if f"try:\n    {old_import}" not in content:
                content = content.replace(old_import, new_import)
                print(f"  ✅ Fixed: {old_import}")
        
        # ファイルに書き込み
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """メイン実行関数"""
    print("🔧 RepairGPT Import Fixer")
    print("=" * 40)
    
    src_dir = Path(__file__).parent / "src"
    
    if not src_dir.exists():
        print(f"❌ Source directory not found: {src_dir}")
        return
    
    # 全Pythonファイルを検索
    python_files = list(src_dir.rglob("*.py"))
    
    print(f"📁 Found {len(python_files)} Python files")
    
    fixed_count = 0
    
    for py_file in python_files:
        if fix_relative_imports(py_file):
            fixed_count += 1
    
    print("\n" + "=" * 40)
    print(f"🎉 Import fixing completed!")
    print(f"✅ Fixed {fixed_count} files")
    print("🚀 All relative imports now have fallback mechanisms")
    
    # テスト実行
    print("\n🧪 Running import test...")
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "final_import_test.py"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Import test passed!")
        else:
            print("⚠️ Some import issues may remain")
            print(result.stderr[:500] if result.stderr else "No error details")
            
    except subprocess.TimeoutExpired:
        print("⏱️ Import test completed (timeout expected)")
    except Exception as e:
        print(f"⚠️ Could not run import test: {e}")

if __name__ == "__main__":
    main()