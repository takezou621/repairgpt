#!/usr/bin/env python3
"""
Test script for Claude Code Action automation
"""
import sys
import os
sys.path.insert(0, 'scripts')

# Mock environment variables for testing
os.environ['GH_TOKEN'] = 'test_token'
os.environ['GH_REPO'] = 'test_user/test_repo'

from comment_issue import generate_code_with_claude

def test_claude_code_generation():
    """Test the Claude Code CLI integration"""
    print("Testing Claude Code generation...")
    
    issue_title = "Add hello world function"
    issue_description = "Create a simple hello world function in Python that prints 'Hello, World!'"
    
    try:
        result = generate_code_with_claude(issue_description, issue_title)
        print(f"✅ Code generation successful: {result}")
        return True
    except Exception as e:
        print(f"❌ Code generation failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("Testing file structure...")
    
    required_files = [
        'scripts/comment_issue.py',
        '.github/workflows/nightly-claude.yml'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_script_syntax():
    """Test that the Python script has valid syntax"""
    print("Testing script syntax...")
    
    try:
        import scripts.comment_issue
        print("✅ Script syntax is valid")
        return True
    except Exception as e:
        print(f"❌ Script syntax error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Claude Code Action Tests\n")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Script Syntax", test_script_syntax),
        ("Claude Code Generation", test_claude_code_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Ready for GitHub Actions")
    else:
        print("❌ Some tests failed. Please fix before deploying")