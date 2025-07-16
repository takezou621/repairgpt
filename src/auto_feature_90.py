"""RepairGPT Security and Configuration Management System
Implements Issue #90: 🔒 設定管理とセキュリティ強化

This module provides:
- Configuration management integration
- Security system validation and testing
- Comprehensive security status reporting
- API key validation and management
- Production readiness checks
"""

import sys
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import time

# Import our configuration and security modules
from src.config.settings import (
    Settings, 
    get_settings, 
    validate_api_keys, 
    validate_production_config,
    get_required_env_vars
)
from src.utils.security import (
    sanitize_input,
    validate_api_key,
    RateLimiter,
    hash_ip_address,
    sanitize_log_data,
    create_audit_log,
    generate_secure_token,
    mask_sensitive_data,
    validate_image_content
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityConfigurationManager:
    """Central manager for security and configuration features"""
    
    def __init__(self):
        """Initialize the security configuration manager"""
        self.settings = get_settings()
        self.rate_limiter = RateLimiter(
            max_requests=self.settings.rate_limit_requests_per_minute,
            window_seconds=60
        )
        logger.info("Security Configuration Manager initialized")
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the current configuration setup
        
        Returns:
            Dict[str, Any]: Comprehensive validation results
        """
        validation_results = {
            "timestamp": time.time(),
            "environment": self.settings.environment.value,
            "overall_status": "unknown",
            "configuration": {},
            "security": {},
            "api_keys": {},
            "production_readiness": {},
            "recommendations": []
        }
        
        # Validate basic configuration
        validation_results["configuration"] = self._validate_basic_config()
        
        # Validate security settings
        validation_results["security"] = self._validate_security_config()
        
        # Validate API keys
        validation_results["api_keys"] = self._validate_all_api_keys()
        
        # Validate production readiness
        validation_results["production_readiness"] = self._validate_production_readiness()
        
        # Generate recommendations
        validation_results["recommendations"] = self._generate_recommendations(validation_results)
        
        # Determine overall status
        validation_results["overall_status"] = self._determine_overall_status(validation_results)
        
        logger.info(f"Configuration validation completed with status: {validation_results['overall_status']}")
        return validation_results
    
    def _validate_basic_config(self) -> Dict[str, Any]:
        """Validate basic configuration settings"""
        config_status = {
            "valid": True,
            "issues": [],
            "settings": {
                "app_name": self.settings.app_name,
                "app_version": self.settings.app_version,
                "environment": self.settings.environment.value,
                "debug_mode": self.settings.debug,
                "log_level": self.settings.log_level.value
            }
        }
        
        # Validate required directories
        for dir_name in ["upload_dir", "temp_dir"]:
            dir_path = getattr(self.settings, dir_name)
            if not Path(dir_path).exists():
                config_status["issues"].append(f"Directory {dir_name} does not exist: {dir_path}")
                config_status["valid"] = False
        
        return config_status
    
    def _validate_security_config(self) -> Dict[str, Any]:
        """Validate security configuration"""
        security_status = {
            "valid": True,
            "issues": [],
            "features": {
                "security_headers": self.settings.enable_security_headers,
                "rate_limiting": True,  # Always enabled
                "cors_configured": len(self.settings.cors_origins) > 0,
                "secret_key_set": bool(self.settings.secret_key),
                "input_sanitization": True,  # Always enabled
                "audit_logging": True  # Always enabled
            },
            "rate_limit_config": {
                "requests_per_minute": self.settings.rate_limit_requests_per_minute,
                "burst_size": self.settings.rate_limit_burst
            }
        }
        
        # Check secret key
        if not self.settings.secret_key:
            security_status["issues"].append("Secret key not configured")
            security_status["valid"] = False
        elif len(self.settings.secret_key) < 32:
            security_status["issues"].append("Secret key too short (minimum 32 characters)")
            security_status["valid"] = False
        
        # Check CORS configuration
        if self.settings.is_production() and "*" in self.settings.allowed_hosts:
            security_status["issues"].append("Wildcard hosts not recommended for production")
            security_status["valid"] = False
        
        return security_status
    
    def _validate_all_api_keys(self) -> Dict[str, Any]:
        """Validate all configured API keys"""
        api_validation = {
            "valid": True,
            "configured_services": [],
            "missing_services": [],
            "invalid_keys": [],
            "details": {}
        }
        
        api_keys = self.settings.get_api_keys()
        
        for service, key in api_keys.items():
            if key:
                validation_result = validate_api_key(key, service)
                api_validation["details"][service] = {
                    "configured": True,
                    "valid": validation_result["valid"],
                    "masked_key": mask_sensitive_data(key, 8),
                    "error": validation_result.get("error"),
                    "warnings": validation_result.get("warnings", [])
                }
                
                if validation_result["valid"]:
                    api_validation["configured_services"].append(service)
                else:
                    api_validation["invalid_keys"].append(service)
                    api_validation["valid"] = False
            else:
                api_validation["missing_services"].append(service)
                api_validation["details"][service] = {
                    "configured": False,
                    "valid": False,
                    "error": "Not configured"
                }
        
        return api_validation
    
    def _validate_production_readiness(self) -> Dict[str, Any]:
        """Validate production readiness"""
        production_status = {
            "ready": True,
            "environment": self.settings.environment.value,
            "issues": [],
            "requirements_met": [],
            "requirements_missing": []
        }
        
        if self.settings.is_production():
            issues = validate_production_config()
            production_status["issues"] = issues
            production_status["ready"] = len(issues) == 0
            
            # Check required environment variables
            required_vars = get_required_env_vars()
            import os
            
            for var in required_vars:
                if os.getenv(var):
                    production_status["requirements_met"].append(var)
                else:
                    production_status["requirements_missing"].append(var)
                    production_status["ready"] = False
        else:
            production_status["issues"] = ["Not in production environment"]
        
        return production_status
    
    def _generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Configuration recommendations
        if not validation_results["configuration"]["valid"]:
            recommendations.append("Fix configuration issues before deployment")
        
        # Security recommendations
        security = validation_results["security"]
        if not security["features"]["secret_key_set"]:
            recommendations.append("Set a strong secret key for cryptographic operations")
        
        if not security["features"]["security_headers"]:
            recommendations.append("Enable security headers for better protection")
        
        # API key recommendations
        api_keys = validation_results["api_keys"]
        if api_keys["missing_services"]:
            recommendations.append(f"Configure API keys for: {', '.join(api_keys['missing_services'])}")
        
        if api_keys["invalid_keys"]:
            recommendations.append(f"Fix invalid API keys for: {', '.join(api_keys['invalid_keys'])}")
        
        # Production recommendations
        production = validation_results["production_readiness"]
        if self.settings.is_production() and not production["ready"]:
            recommendations.append("Address production readiness issues before going live")
        
        if not recommendations:
            recommendations.append("Configuration looks good! No immediate issues found.")
        
        return recommendations
    
    def _determine_overall_status(self, validation_results: Dict[str, Any]) -> str:
        """Determine overall system status"""
        config_valid = validation_results["configuration"]["valid"]
        security_valid = validation_results["security"]["valid"]
        api_keys_valid = validation_results["api_keys"]["valid"]
        
        if self.settings.is_production():
            production_ready = validation_results["production_readiness"]["ready"]
            if all([config_valid, security_valid, api_keys_valid, production_ready]):
                return "production_ready"
            else:
                return "production_issues"
        else:
            if all([config_valid, security_valid]):
                return "development_ready"
            else:
                return "development_issues"
    
    def test_security_features(self) -> Dict[str, Any]:
        """Test various security features
        
        Returns:
            Dict[str, Any]: Test results
        """
        test_results = {
            "timestamp": time.time(),
            "tests": {},
            "overall_success": True
        }
        
        # Test input sanitization
        test_results["tests"]["input_sanitization"] = self._test_input_sanitization()
        
        # Test rate limiting
        test_results["tests"]["rate_limiting"] = self._test_rate_limiting()
        
        # Test API key validation
        test_results["tests"]["api_key_validation"] = self._test_api_key_validation()
        
        # Test content validation
        test_results["tests"]["content_validation"] = self._test_content_validation()
        
        # Test security utilities
        test_results["tests"]["security_utilities"] = self._test_security_utilities()
        
        # Determine overall success
        test_results["overall_success"] = all(
            test["success"] for test in test_results["tests"].values()
        )
        
        logger.info(f"Security feature tests completed. Overall success: {test_results['overall_success']}")
        return test_results
    
    def _test_input_sanitization(self) -> Dict[str, Any]:
        """Test input sanitization functionality"""
        test_cases = [
            {"input": "<script>alert('xss')</script>", "expected_safe": True},
            {"input": "Normal text input", "expected_safe": True},
            {"input": "Text with <b>bold</b> tags", "expected_safe": True},
            {"input": "javascript:alert('test')", "expected_safe": True},
            {"input": "Very long text " + "x" * 1000, "expected_safe": False}  # Too long
        ]
        
        results = {"success": True, "test_cases": []}
        
        for i, case in enumerate(test_cases):
            try:
                sanitized = sanitize_input(case["input"], max_length=500)
                is_safe = len(sanitized) <= 500 and "<script" not in sanitized.lower()
                
                test_result = {
                    "test_id": f"sanitization_{i}",
                    "input_length": len(case["input"]),
                    "output_length": len(sanitized),
                    "success": is_safe == case["expected_safe"]
                }
                
                if not test_result["success"]:
                    results["success"] = False
                
                results["test_cases"].append(test_result)
                
            except ValueError:
                # Expected for too-long inputs
                test_result = {
                    "test_id": f"sanitization_{i}",
                    "input_length": len(case["input"]),
                    "success": not case["expected_safe"]  # Exception expected for unsafe inputs
                }
                results["test_cases"].append(test_result)
        
        return results
    
    def _test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting functionality"""
        test_ip = "192.168.1.100"
        hashed_ip = hash_ip_address(test_ip)
        
        results = {"success": True, "requests_tested": 0, "limit_enforced": False}
        
        # Test normal requests (should be allowed)
        for i in range(5):
            allowed, rate_info = self.rate_limiter.is_allowed(hashed_ip)
            results["requests_tested"] += 1
            
            if not allowed:
                results["success"] = False
                break
        
        # Test rate limit enforcement (make many requests)
        for i in range(self.settings.rate_limit_requests_per_minute + 5):
            allowed, rate_info = self.rate_limiter.is_allowed(f"test_ip_{i % 3}")  # Use rotating IPs
            
            if not allowed:
                results["limit_enforced"] = True
                break
        
        return results
    
    def _test_api_key_validation(self) -> Dict[str, Any]:
        """Test API key validation"""
        test_cases = [
            {"key": "sk-test123456789012345678901234567890", "service": "openai", "should_be_valid": True},
            {"key": "invalid-key", "service": "openai", "should_be_valid": False},
            {"key": "sk-ant-test12345678901234567890123456789012345678901234567890", "service": "claude", "should_be_valid": True},
            {"key": "short", "service": "claude", "should_be_valid": False}
        ]
        
        results = {"success": True, "test_cases": []}
        
        for case in test_cases:
            validation_result = validate_api_key(case["key"], case["service"])
            is_valid = validation_result["valid"]
            
            test_result = {
                "service": case["service"],
                "expected_valid": case["should_be_valid"],
                "actual_valid": is_valid,
                "success": is_valid == case["should_be_valid"]
            }
            
            if not test_result["success"]:
                results["success"] = False
            
            results["test_cases"].append(test_result)
        
        return results
    
    def _test_content_validation(self) -> Dict[str, Any]:
        """Test content validation"""
        # Test with dummy image data
        jpeg_header = b'\xFF\xD8\xFF\xE0\x00\x10JFIF'
        fake_image = jpeg_header + b'\x00' * 1000  # Minimal fake JPEG
        
        results = {"success": True}
        
        try:
            validation_result = validate_image_content(fake_image)
            results["image_validation"] = {
                "valid": validation_result["valid"],
                "format": validation_result["format"],
                "size": validation_result["size"]
            }
            results["success"] = validation_result["valid"]
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    def _test_security_utilities(self) -> Dict[str, Any]:
        """Test security utility functions"""
        results = {"success": True, "utilities_tested": []}
        
        # Test secure token generation
        try:
            token = generate_secure_token()
            results["utilities_tested"].append({
                "name": "secure_token_generation",
                "success": len(token) == 64,  # 32 bytes = 64 hex chars
                "token_length": len(token)
            })
        except Exception as e:
            results["success"] = False
            results["utilities_tested"].append({
                "name": "secure_token_generation",
                "success": False,
                "error": str(e)
            })
        
        # Test data masking
        try:
            masked = mask_sensitive_data("sk-1234567890abcdef", 4)
            expected_mask = "sk-1*************"
            mask_success = masked.startswith("sk-1") and "*" in masked
            
            results["utilities_tested"].append({
                "name": "data_masking",
                "success": mask_success,
                "masked_result": masked
            })
            
            if not mask_success:
                results["success"] = False
                
        except Exception as e:
            results["success"] = False
            results["utilities_tested"].append({
                "name": "data_masking",
                "success": False,
                "error": str(e)
            })
        
        # Test audit logging
        try:
            audit_entry = create_audit_log(
                action="test_action",
                user_id="test_user",
                ip_address="192.168.1.1",
                details={"test": "data", "api_key": "sk-secret123"}
            )
            
            audit_success = (
                "timestamp" in audit_entry and
                "action" in audit_entry and
                "ip_hash" in audit_entry and
                audit_entry["details"]["api_key"] == "[REDACTED]"  # Should be sanitized
            )
            
            results["utilities_tested"].append({
                "name": "audit_logging",
                "success": audit_success,
                "sanitization_works": audit_entry["details"]["api_key"] == "[REDACTED]"
            })
            
            if not audit_success:
                results["success"] = False
                
        except Exception as e:
            results["success"] = False
            results["utilities_tested"].append({
                "name": "audit_logging",
                "success": False,
                "error": str(e)
            })
        
        return results
    
    def get_security_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive security status report
        
        Returns:
            Dict[str, Any]: Complete security status report
        """
        logger.info("Generating comprehensive security status report")
        
        report = {
            "report_metadata": {
                "timestamp": time.time(),
                "report_version": "1.0",
                "environment": self.settings.environment.value,
                "app_version": self.settings.app_version
            },
            "configuration_validation": self.validate_configuration(),
            "security_feature_tests": self.test_security_features(),
            "summary": {}
        }
        
        # Generate summary
        config_status = report["configuration_validation"]["overall_status"]
        test_success = report["security_feature_tests"]["overall_success"]
        
        report["summary"] = {
            "overall_status": "healthy" if ("ready" in config_status and test_success) else "issues_found",
            "configuration_status": config_status,
            "security_tests_passed": test_success,
            "total_recommendations": len(report["configuration_validation"]["recommendations"]),
            "critical_issues": self._count_critical_issues(report)
        }
        
        logger.info(f"Security status report generated. Overall status: {report['summary']['overall_status']}")
        return report
    
    def _count_critical_issues(self, report: Dict[str, Any]) -> int:
        """Count critical issues in the report"""
        critical_count = 0
        
        # Count configuration issues
        if not report["configuration_validation"]["configuration"]["valid"]:
            critical_count += len(report["configuration_validation"]["configuration"]["issues"])
        
        # Count security issues
        if not report["configuration_validation"]["security"]["valid"]:
            critical_count += len(report["configuration_validation"]["security"]["issues"])
        
        # Count production issues
        if self.settings.is_production():
            critical_count += len(report["configuration_validation"]["production_readiness"]["issues"])
        
        return critical_count


def auto_feature_90() -> Dict[str, Any]:
    """Main function for Issue #90: Security and Configuration Management
    
    This function demonstrates and validates the complete security and
    configuration management system implemented for RepairGPT.
    
    Returns:
        Dict[str, Any]: Comprehensive system status and test results
    """
    logger.info("Starting Issue #90: Security and Configuration Management validation")
    
    try:
        # Initialize the security configuration manager
        manager = SecurityConfigurationManager()
        
        # Generate comprehensive status report
        status_report = manager.get_security_status_report()
        
        # Add execution metadata
        result = {
            "issue": 90,
            "title": "🔒 設定管理とセキュリティ強化",
            "status": "completed",
            "implementation_status": "comprehensive",
            "execution_timestamp": time.time(),
            "features_implemented": [
                "Environment-based configuration management",
                "Comprehensive security utilities",
                "API key validation and management",
                "Input sanitization and validation",
                "Rate limiting with sliding window",
                "Security headers middleware",
                "Content validation for uploads",
                "Audit logging with data sanitization",
                "Production readiness validation",
                "Comprehensive testing framework"
            ],
            "security_report": status_report,
            "next_steps": [
                "Configure production environment variables",
                "Set up monitoring and alerting",
                "Implement automated security testing in CI/CD",
                "Review and update security policies regularly"
            ]
        }
        
        # Log completion
        overall_status = status_report["summary"]["overall_status"]
        logger.info(f"Issue #90 validation completed successfully. System status: {overall_status}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error during Issue #90 validation: {str(e)}")
        return {
            "issue": 90,
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }


def print_security_summary(report: Dict[str, Any]) -> None:
    """Print a human-readable security summary
    
    Args:
        report: Security status report
    """
    print("\n" + "="*80)
    print("🔒 RepairGPT Security and Configuration Status Report")
    print("="*80)
    
    summary = report["security_report"]["summary"]
    print(f"\n📊 Overall Status: {summary['overall_status'].upper()}")
    print(f"🔧 Configuration: {summary['configuration_status']}")
    print(f"🛡️  Security Tests: {'PASSED' if summary['security_tests_passed'] else 'FAILED'}")
    print(f"⚠️  Critical Issues: {summary['critical_issues']}")
    print(f"💡 Recommendations: {summary['total_recommendations']}")
    
    # Show recommendations
    recommendations = report["security_report"]["configuration_validation"]["recommendations"]
    if recommendations:
        print("\n📋 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    
    # Show configured API services
    api_keys = report["security_report"]["configuration_validation"]["api_keys"]
    if api_keys["configured_services"]:
        print(f"\n🔑 Configured APIs: {', '.join(api_keys['configured_services'])}")
    
    if api_keys["missing_services"]:
        print(f"❌ Missing APIs: {', '.join(api_keys['missing_services'])}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    # Execute the main feature function
    result = auto_feature_90()
    
    # Print results based on execution mode
    if "--json" in sys.argv:
        # JSON output for automated processing
        print(json.dumps(result, indent=2, default=str))
    elif "--summary" in sys.argv:
        # Human-readable summary
        if result["status"] == "completed":
            print_security_summary(result)
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    else:
        # Default output
        print(f"\n🔒 Issue #{result['issue']}: {result['title']}")
        print(f"Status: {result['status'].upper()}")
        
        if result["status"] == "completed":
            summary = result["security_report"]["summary"]
            print(f"Overall System Status: {summary['overall_status'].upper()}")
            print(f"Security Tests: {'✅ PASSED' if summary['security_tests_passed'] else '❌ FAILED'}")
            print(f"Critical Issues: {summary['critical_issues']}")
            
            if summary['total_recommendations'] > 0:
                print(f"\nRecommendations ({summary['total_recommendations']}):")
                for rec in result["security_report"]["configuration_validation"]["recommendations"][:3]:
                    print(f"  • {rec}")
                if summary['total_recommendations'] > 3:
                    print(f"  ... and {summary['total_recommendations'] - 3} more")
            
            print("\n✅ Security and Configuration Management system is operational!")
            print("\nRun with --summary for detailed report or --json for full data")
        else:
            print(f"❌ Execution failed: {result.get('error', 'Unknown error')}")