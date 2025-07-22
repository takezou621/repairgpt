#!/usr/bin/env python3
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
