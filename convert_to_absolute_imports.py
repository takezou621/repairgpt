#!/usr/bin/env python3
"""
すべての相対インポートを絶対インポートに変換する
"""

import os
import re
from pathlib import Path

def convert_relative_to_absolute(file_path: Path, src_root: Path) -> bool:
    """ファイル内の相対インポートを絶対インポートに変換"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # ファイルのソースルートからの相対パスを計算
        rel_path = file_path.relative_to(src_root)
        depth = len(rel_path.parts) - 1  # ファイル自体を除く
        
        # パターン1: from ..module import something
        pattern1 = r'from (\.+)([a-zA-Z_][a-zA-Z0-9_.]*) import (.+)'
        
        def replace_import(match):
            dots = match.group(1)
            module_path = match.group(2)
            imports = match.group(3)
            
            # ドット数から上位階層数を計算
            levels_up = len(dots) - 1
            
            # 絶対パス作成
            if levels_up == 1:  # .. (一つ上)
                absolute_path = module_path
            elif levels_up == 2:  # ... (二つ上)
                # 現在のディレクトリから計算
                current_dir = file_path.parent.relative_to(src_root)
                if len(current_dir.parts) >= levels_up:
                    parent_parts = current_dir.parts[:-levels_up+1] if levels_up > 1 else ()
                    if parent_parts:
                        absolute_path = '.'.join(parent_parts) + '.' + module_path
                    else:
                        absolute_path = module_path
                else:
                    absolute_path = module_path
            else:
                absolute_path = module_path
            
            return f'from {absolute_path} import {imports}'
        
        content = re.sub(pattern1, replace_import, content)
        
        # すでにtry/exceptで囲まれていない場合は追加
        if content != original_content:
            # 新しい絶対インポートにフォールバック機構を追加
            lines = content.split('\n')
            new_lines = []
            in_import_block = False
            
            for line in lines:
                if re.match(r'^from [a-zA-Z_][a-zA-Z0-9_.]*import', line.strip()) and 'try:' not in ''.join(new_lines[-5:]):
                    # 絶対インポートにフォールバック追加
                    module_match = re.match(r'from ([a-zA-Z_][a-zA-Z0-9_.]*) import (.+)', line.strip())
                    if module_match:
                        module_name = module_match.group(1)
                        import_items = module_match.group(2)
                        
                        # 相対インポート版を推測
                        relative_version = f"from ..{module_name} import {import_items}"
                        if file_path.parent.name in ['routes']:
                            relative_version = f"from ...{module_name} import {import_items}"
                        
                        new_lines.extend([
                            'try:',
                            f'    {relative_version}',
                            'except ImportError:',
                            '    # Fallback for direct execution',
                            '    import sys',
                            '    import os',
                            '    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))',
                            f'    from {module_name} import {import_items}'
                        ])
                        continue
                
                new_lines.append(line)
            
            content = '\n'.join(new_lines)
        
        # ファイル更新
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Converted: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """メイン変換処理"""
    print("🔄 Converting all relative imports to absolute imports")
    print("=" * 60)
    
    src_root = Path("/Users/kawai/dev/repairgpt/src")
    
    # 全Pythonファイルを取得
    python_files = list(src_root.rglob("*.py"))
    
    converted_count = 0
    
    for py_file in python_files:
        if py_file.name == '__init__.py':
            continue  # __init__.pyはスキップ
            
        if convert_relative_to_absolute(py_file, src_root):
            converted_count += 1
    
    print("\n" + "=" * 60)
    print(f"🎉 Conversion completed!")
    print(f"✅ Converted {converted_count} files")
    
    # 最終的にすべてを絶対インポートのみにする
    print("\n🔧 Applying final absolute import conversion...")
    apply_final_absolute_imports()

def apply_final_absolute_imports():
    """最終的な絶対インポート変換"""
    files_to_convert = [
        "/Users/kawai/dev/repairgpt/src/clients/ifixit_client.py",
        "/Users/kawai/dev/repairgpt/src/chat/llm_chatbot.py", 
        "/Users/kawai/dev/repairgpt/src/chat/streaming_chat.py",
        "/Users/kawai/dev/repairgpt/src/auth/jwt_auth.py",
        "/Users/kawai/dev/repairgpt/src/features/auth.py",
        "/Users/kawai/dev/repairgpt/src/features/security.py",
        "/Users/kawai/dev/repairgpt/src/api/__init__.py",
        "/Users/kawai/dev/repairgpt/src/api/routes_old.py",
        "/Users/kawai/dev/repairgpt/src/api/main.py",
        "/Users/kawai/dev/repairgpt/src/api/routes/auth.py",
        "/Users/kawai/dev/repairgpt/src/api/routes/image_analysis.py",
        "/Users/kawai/dev/repairgpt/src/api/routes/diagnose.py",
        "/Users/kawai/dev/repairgpt/src/api/routes/chat.py",
        "/Users/kawai/dev/repairgpt/src/services/image_analysis.py",
        "/Users/kawai/dev/repairgpt/src/services/repair_guide_service.py"
    ]
    
    conversions = {
        # 基本的な相対->絶対変換
        r'from \.\.utils\.logger import': 'from utils.logger import',
        r'from \.\.config\.settings_simple import': 'from config.settings_simple import',
        r'from \.\.auth\.jwt_auth import': 'from auth.jwt_auth import', 
        r'from \.\.features\.auth import': 'from features.auth import',
        r'from \.\.utils\.security import': 'from utils.security import',
        r'from \.\.clients\.ifixit_client import': 'from clients.ifixit_client import',
        r'from \.\.data\.offline_repair_database import': 'from data.offline_repair_database import',
        r'from \.\.services\.image_analysis import': 'from services.image_analysis import',
        r'from \.\.chat\.llm_chatbot import': 'from chat.llm_chatbot import',
        r'from \.\.schemas\.image_analysis import': 'from schemas.image_analysis import',
        
        # 3レベル上の相対->絶対変換 
        r'from \.\.\.utils\.logger import': 'from utils.logger import',
        r'from \.\.\.config\.settings_simple import': 'from config.settings_simple import',
        r'from \.\.\.auth\.jwt_auth import': 'from auth.jwt_auth import',
        r'from \.\.\.features\.auth import': 'from features.auth import',
        r'from \.\.\.utils\.security import': 'from utils.security import',
        r'from \.\.\.clients\.ifixit_client import': 'from clients.ifixit_client import',
        r'from \.\.\.data\.offline_repair_database import': 'from data.offline_repair_database import',
        r'from \.\.\.services\.image_analysis import': 'from services.image_analysis import',
        r'from \.\.\.chat\.llm_chatbot import': 'from chat.llm_chatbot import',
        r'from \.\.\.schemas\.image_analysis import': 'from schemas.image_analysis import',
    }
    
    for file_path in files_to_convert:
        path = Path(file_path)
        if not path.exists():
            continue
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            
            for pattern, replacement in conversions.items():
                content = re.sub(pattern, replacement, content)
            
            if content != original:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Final conversion: {path.name}")
                
        except Exception as e:
            print(f"❌ Error in final conversion {path}: {e}")

if __name__ == "__main__":
    main()