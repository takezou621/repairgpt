#!/usr/bin/env python3
"""
相対インポートの問題を一括修正するスクリプト
"""

import os
import re
from pathlib import Path

def fix_relative_imports():
    """相対インポートを修正"""
    print("🔧 Fixing relative import issues...")
    
    src_dir = Path("/Users/kawai/dev/repairgpt/src")
    
    # 修正対象ファイルを検索
    python_files = list(src_dir.rglob("*.py"))
    
    fixes_applied = 0
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # パターン1: from ..module import
            pattern1 = r'from \.\.([a-zA-Z_][a-zA-Z0-9_]*) import'
            if re.search(pattern1, content):
                # フォールバック付きインポートに置換
                content = re.sub(
                    pattern1,
                    lambda m: f'''try:
    from ..{m.group(1)} import''',
                    content
                )
                
                # except節を追加（まだない場合）
                if 'except ImportError:' not in content:
                    content = content.replace(
                        'try:\n    from ..', 
                        '''try:
    from ..'''
                    )
                    
                    # except節とフォールバックを追加
                    imports_to_fix = re.findall(r'from \.\.([a-zA-Z_][a-zA-Z0-9_]*) import ([^\n]+)', original_content)
                    for module, imports in imports_to_fix:
                        content = content.replace(
                            f'from ..{module} import {imports}',
                            f'''try:
    from ..{module} import {imports}
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from {module} import {imports}'''
                        )
            
            # 変更があった場合のみファイルを更新
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixes_applied += 1
                print(f"✅ Fixed: {file_path.relative_to(src_dir)}")
                
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
    
    print(f"\n🎉 Fixed {fixes_applied} files")

def test_imports():
    """インポートテスト"""
    print("\n🧪 Testing imports...")
    
    test_modules = [
        'chat.llm_chatbot',
        'services.image_analysis', 
        'config.settings_simple'
    ]
    
    import sys
    sys.path.insert(0, '/Users/kawai/dev/repairgpt/src')
    
    for module in test_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")

def create_package_init_files():
    """__init__.pyファイルを作成"""
    print("\n📦 Creating __init__.py files...")
    
    src_dir = Path("/Users/kawai/dev/repairgpt/src")
    
    # 各ディレクトリに__init__.pyを作成
    directories = [
        src_dir,
        src_dir / "api",
        src_dir / "api" / "routes", 
        src_dir / "auth",
        src_dir / "chat",
        src_dir / "clients",
        src_dir / "config",
        src_dir / "data",
        src_dir / "database",
        src_dir / "features",
        src_dir / "i18n",
        src_dir / "prompts",
        src_dir / "schemas",
        src_dir / "services",
        src_dir / "ui",
        src_dir / "utils"
    ]
    
    for directory in directories:
        if directory.exists():
            init_file = directory / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Package initialization"""')
                print(f"✅ Created: {init_file.relative_to(src_dir.parent)}")

if __name__ == "__main__":
    print("🚀 RepairGPT Import Fix Tool")
    print("=" * 50)
    
    create_package_init_files()
    fix_relative_imports() 
    test_imports()
    
    print("\n✅ Import fixes completed!")