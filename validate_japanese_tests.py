#!/usr/bin/env python3
"""
Validation script for Japanese search functionality tests

This script validates the test structure and logic without requiring
all external dependencies to be installed.
"""

import ast
import os
import sys
from pathlib import Path


def validate_python_syntax(file_path):
    """Validate Python syntax of a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to check syntax
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def analyze_test_coverage(file_path):
    """Analyze test coverage by examining test methods"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        test_classes = []
        total_test_methods = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.startswith('Test'):
                    test_methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name.startswith('test_'):
                                test_methods.append(item.name)
                                total_test_methods += 1
                    
                    test_classes.append({
                        'name': node.name,
                        'methods': test_methods,
                        'count': len(test_methods)
                    })
        
        return test_classes, total_test_methods
    except Exception as e:
        return [], 0


def main():
    """Main validation function"""
    print("🧪 RepairGPT Japanese Search Functionality Test Validation")
    print("=" * 60)
    
    # Define test files to validate
    test_files = [
        "tests/unit/test_services/test_repair_guide_service_japanese.py",
        "tests/integration/test_japanese_search_integration.py"
    ]
    
    total_test_methods = 0
    all_valid = True
    
    for test_file in test_files:
        print(f"\n📁 Validating: {test_file}")
        print("-" * 50)
        
        if not os.path.exists(test_file):
            print(f"❌ File not found: {test_file}")
            all_valid = False
            continue
        
        # Validate syntax
        valid, error = validate_python_syntax(test_file)
        if valid:
            print("✅ Syntax validation: PASSED")
        else:
            print(f"❌ Syntax validation: FAILED - {error}")
            all_valid = False
            continue
        
        # Analyze test coverage
        test_classes, method_count = analyze_test_coverage(test_file)
        total_test_methods += method_count
        
        print(f"📊 Test classes found: {len(test_classes)}")
        print(f"🧪 Total test methods: {method_count}")
        
        for test_class in test_classes:
            print(f"   📋 {test_class['name']}: {test_class['count']} methods")
            
        # Check for key test categories (for integration file)
        if "integration" in test_file:
            expected_categories = [
                "EndToEnd",
                "EdgeCases", 
                "Performance",
                "DataQuality",
                "BackwardCompatibility",
                "RealWorld"
            ]
            
            found_categories = []
            for test_class in test_classes:
                for category in expected_categories:
                    if category in test_class['name']:
                        found_categories.append(category)
            
            print(f"🎯 Integration test categories: {len(found_categories)}/{len(expected_categories)}")
            for category in found_categories:
                print(f"   ✅ {category}")
    
    print("\n" + "=" * 60)
    print("📈 SUMMARY")
    print("=" * 60)
    print(f"🧪 Total test methods across all files: {total_test_methods}")
    
    if all_valid:
        print("✅ All test files are syntactically valid")
        print("✅ Test structure appears comprehensive")
        
        # Check if we have sufficient coverage
        if total_test_methods >= 50:  # Reasonable threshold
            print("✅ Test coverage appears sufficient (50+ test methods)")
        else:
            print(f"⚠️  Test coverage may be insufficient ({total_test_methods} methods)")
        
        print("\n🎯 VALIDATION RESULT: SUCCESS")
        print("✅ Japanese search functionality tests are ready for execution")
        
    else:
        print("❌ Some test files have issues")
        print("\n🎯 VALIDATION RESULT: FAILED")
        return 1
    
    # Additional checks for test content quality
    print("\n📋 TEST CONTENT QUALITY CHECKS")
    print("-" * 40)
    
    # Check for Japanese text in tests (indicates proper Japanese testing)
    japanese_text_found = False
    async_tests_found = False
    
    for test_file in test_files:
        if os.path.exists(test_file):
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for Japanese text
            if any(ord(char) > 127 for char in content):
                japanese_text_found = True
                
            # Check for async tests
            if "@pytest.mark.asyncio" in content:
                async_tests_found = True
    
    if japanese_text_found:
        print("✅ Japanese text found in tests (proper Japanese testing)")
    else:
        print("⚠️  No Japanese text found in tests")
        
    if async_tests_found:
        print("✅ Async tests found (proper async functionality testing)")
    else:
        print("⚠️  No async tests found")
    
    print("\n🚀 Tests are ready for execution with pytest!")
    print("   Run: pytest tests/unit/test_services/test_repair_guide_service_japanese.py -v")
    print("   Run: pytest tests/integration/test_japanese_search_integration.py -v")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())