#!/usr/bin/env python3
"""
RepairGPT Startup Script
APIサーバーとStreamlitの両方を起動
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path

def start_servers():
    """APIサーバーとStreamlitを起動"""
    processes = []
    
    try:
        print("🚀 Starting RepairGPT...")
        
        # API server start
        print("📡 Starting API server...")
        api_env = os.environ.copy()
        api_env["FASTAPI_BASE_URL"] = "http://localhost:8000"
        
        api_proc = subprocess.Popen([
            sys.executable, "src/api/main.py"
        ], env=api_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        processes.append(("API Server", api_proc))
        
        # Wait for API to start
        time.sleep(3)
        
        # Streamlit start
        print("🎨 Starting Streamlit UI...")
        streamlit_env = os.environ.copy()
        streamlit_env["FASTAPI_BASE_URL"] = "http://localhost:8000"
        
        streamlit_proc = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "src/ui/repair_app.py",
            "--server.port", "8504",
            "--server.address", "localhost"
        ], env=streamlit_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        processes.append(("Streamlit", streamlit_proc))
        
        # Wait for Streamlit to start
        time.sleep(5)
        
        print("\n🎉 RepairGPT is running!")
        print("📱 Access URL: http://localhost:8504")
        print("📡 API URL: http://localhost:8000")
        print("\n⌨️  Press Ctrl+C to stop")
        
        # Keep running and show output
        while True:
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"❌ {name} stopped unexpectedly")
                    return
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping RepairGPT...")
        for name, proc in processes:
            print(f"🔻 Stopping {name}...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("✅ RepairGPT stopped")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        for name, proc in processes:
            proc.terminate()

if __name__ == "__main__":
    start_servers()