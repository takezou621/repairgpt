#!/usr/bin/env python3
"""
Integration test for mock AI functionality
Tests the complete flow from UI configuration to API response
"""

import requests
import json
import time

def test_integration():
    """Test integration of mock AI functionality"""
    print("🔗 RepairGPT Mock AI Integration Test")
    print("=" * 60)
    
    # Configuration
    api_base = "http://localhost:8004"
    
    # Test cases for different scenarios
    test_cases = [
        {
            "name": "Joy-Con Drift Issue",
            "endpoint": "/api/v1/chat",
            "payload": {
                "message": "My Nintendo Switch Joy-Con is drifting to the left",
                "device_type": "nintendo_switch",
                "skill_level": "beginner"
            },
            "expected_keywords": ["Joy-Con", "drift", "Mock AI Response", "Tripoint screwdriver"]
        },
        {
            "name": "iPhone Screen Diagnosis",
            "endpoint": "/api/v1/diagnose", 
            "payload": {
                "device_type": "iphone",
                "issue_description": "Screen is cracked and touch not working properly",
                "skill_level": "intermediate"
            },
            "expected_keywords": ["Display assembly", "Pentalobe", "confidence"]
        },
        {
            "name": "Generic Battery Issue",
            "endpoint": "/api/v1/chat",
            "payload": {
                "message": "My laptop battery drains very fast",
                "device_type": "laptop",
                "skill_level": "expert"
            },
            "expected_keywords": ["battery", "Mock AI Response", "Safety First"]
        }
    ]
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Make API request
            url = f"{api_base}{test_case['endpoint']}"
            response = requests.post(
                url,
                json=test_case['payload'],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if test_case['endpoint'] == '/api/v1/chat':
                    response_text = data.get('response', '')
                    print(f"✅ Chat Response: {len(response_text)} characters")
                    
                elif test_case['endpoint'] == '/api/v1/diagnose':
                    diagnosis = data.get('diagnosis', '')
                    confidence = data.get('confidence', 0)
                    print(f"✅ Diagnosis: {diagnosis}")
                    print(f"✅ Confidence: {confidence}")
                    response_text = json.dumps(data, indent=2)
                
                # Check for expected keywords
                keyword_checks = []
                for keyword in test_case['expected_keywords']:
                    found = keyword.lower() in response_text.lower()
                    keyword_checks.append(found)
                    status = "✅" if found else "❌"
                    print(f"{status} Keyword '{keyword}': {'Found' if found else 'Not found'}")
                
                # Overall test result
                all_passed = all(keyword_checks)
                result_status = "✅ PASSED" if all_passed else "❌ FAILED"
                print(f"🎯 Test Result: {result_status}")
                
                # Show sample response
                if len(response_text) > 300:
                    print(f"📝 Sample: {response_text[:200]}...")
                else:
                    print(f"📝 Response: {response_text}")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
    
    # Test API health
    print(f"\n🏥 API Health Check")
    print("-" * 40)
    try:
        health_response = requests.get(f"{api_base}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ API Health: {health_data.get('status')}")
            print(f"✅ Version: {health_data.get('version')}")
        else:
            print(f"❌ Health Check Failed: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Integration test completed!")
    
    # Test configuration detection
    print(f"\n⚙️  Configuration Test")
    print("-" * 40)
    print("Testing automatic mock mode detection...")
    
    try:
        # Test with root endpoint to see configuration
        root_response = requests.get(f"{api_base}/", timeout=5)
        if root_response.status_code == 200:
            root_data = root_response.json()
            print(f"✅ App: {root_data.get('app_name')}")
            print(f"✅ Environment: {root_data.get('environment')}")
            print(f"✅ Version: {root_data.get('version')}")
        else:
            print(f"❌ Root endpoint error: {root_response.status_code}")
    except Exception as e:
        print(f"❌ Configuration test error: {e}")


if __name__ == "__main__":
    # Wait a moment for servers to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(2)
    
    test_integration()