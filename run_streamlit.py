#!/usr/bin/env python3
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
