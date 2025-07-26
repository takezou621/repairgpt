"""
Security configuration and management feature
Comprehensive security validation and monitoring
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List

from config.settings_simple import (
    get_required_env_vars,
    get_settings,
    validate_production_config,
)
from utils.security import (
    RateLimiter,
    mask_sensitive_data,
    validate_api_key,
)

logger = logging.getLogger(__name__)


class SecurityConfigurationManager:
    """Central manager for security and configuration features"""

    def __init__(self):
        """Initialize the security configuration manager"""
        self.settings = get_settings()
        self.rate_limiter = RateLimiter(max_requests=self.settings.rate_limit_requests_per_minute, window_seconds=60)
        logger.info("Security Configuration Manager initialized")

    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the current configuration setup"""
        validation_results = {
            "timestamp": time.time(),
            "environment": self.settings.environment.value,
            "overall_status": "unknown",
            "configuration": {},
            "security": {},
            "api_keys": {},
            "production_readiness": {},
            "recommendations": [],
        }

        # Validate components
        validation_results["configuration"] = self._validate_basic_config()
        validation_results["security"] = self._validate_security_config()
        validation_results["api_keys"] = self._validate_all_api_keys()
        validation_results["production_readiness"] = self._validate_production_readiness()
        validation_results["recommendations"] = self._generate_recommendations(validation_results)
        validation_results["overall_status"] = self._determine_overall_status(validation_results)

        logger.info(f"Configuration validation completed: {validation_results['overall_status']}")
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
                "log_level": self.settings.log_level.value,
            },
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
                "rate_limiting": True,
                "cors_configured": len(self.settings.cors_origins) > 0,
                "secret_key_set": bool(self.settings.secret_key),
                "input_sanitization": True,
                "audit_logging": True,
            },
        }

        # Check secret key
        if not self.settings.secret_key:
            security_status["issues"].append("Secret key not configured")
            security_status["valid"] = False
        elif len(self.settings.secret_key) < 32:
            security_status["issues"].append("Secret key too short (minimum 32 characters)")
            security_status["valid"] = False

        return security_status

    def _validate_all_api_keys(self) -> Dict[str, Any]:
        """Validate all configured API keys"""
        api_validation = {
            "valid": True,
            "configured_services": [],
            "missing_services": [],
            "invalid_keys": [],
            "details": {},
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
                    "error": "Not configured",
                }

        return api_validation

    def _validate_production_readiness(self) -> Dict[str, Any]:
        """Validate production readiness"""
        production_status = {
            "ready": True,
            "environment": self.settings.environment.value,
            "issues": [],
            "requirements_met": [],
            "requirements_missing": [],
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

        # API key recommendations
        api_keys = validation_results["api_keys"]
        if api_keys["missing_services"]:
            recommendations.append(f"Configure API keys for: {', '.join(api_keys['missing_services'])}")

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

    def get_security_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive security status report"""
        logger.info("Generating security status report")

        report = {
            "report_metadata": {
                "timestamp": time.time(),
                "environment": self.settings.environment.value,
                "app_version": self.settings.app_version,
            },
            "configuration_validation": self.validate_configuration(),
            "summary": {},
        }

        # Generate summary
        config_status = report["configuration_validation"]["overall_status"]

        report["summary"] = {
            "overall_status": config_status,
            "configuration_status": config_status,
            "total_recommendations": len(report["configuration_validation"]["recommendations"]),
            "critical_issues": self._count_critical_issues(report),
        }

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

        return critical_count
