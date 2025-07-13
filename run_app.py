#!/usr/bin/env python3
"""
RepairGPT Application Launcher
Simple script to run the Streamlit application
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the RepairGPT Streamlit application"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    app_path = project_root / "src" / "ui" / "repair_app.py"
    
    # Check if the app file exists
    if not app_path.exists():
        print(f"❌ Error: Application file not found at {app_path}")
        sys.exit(1)
    
    print("🔧 Starting RepairGPT...")
    print(f"📁 Project root: {project_root}")
    print(f"🚀 Running: {app_path}")
    print("🌐 Open your browser to the URL shown below when ready.")
    print("-" * 60)
    
    try:
        # Run streamlit with the app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(app_path),
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ], cwd=project_root)
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user.")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()