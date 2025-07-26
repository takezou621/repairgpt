#!/usr/bin/env python3
"""Check if RepairGPT is running properly"""

import requests
import json

def check_streamlit():
    """Check if Streamlit is running"""
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit is running on http://localhost:8501")
            return True
        else:
            print(f"⚠️  Streamlit returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Streamlit is not accessible: {e}")
        return False

def check_api():
    """Check if API is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running on http://localhost:8000")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"⚠️  API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API is not accessible: {e}")
        return False

def main():
    print("🔍 Checking RepairGPT Status...")
    print("-" * 40)
    
    streamlit_ok = check_streamlit()
    api_ok = check_api()
    
    print("-" * 40)
    if streamlit_ok and api_ok:
        print("🎉 RepairGPT is fully operational!")
        print("\n📱 Open http://localhost:8501 in your browser to use the app")
    elif streamlit_ok:
        print("⚠️  Streamlit is running but API is not available")
        print("   Some features may be limited")
        print("\n📱 Open http://localhost:8501 in your browser")
    else:
        print("❌ RepairGPT is not running properly")
        print("\nTry running: python run_repairgpt.py")

if __name__ == "__main__":
    main()