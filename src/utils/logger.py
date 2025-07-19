"""
Logger Configuration for RepairGPT
Implements Issue #86: 基本的なエラーハンドリングとログ機能の実装

Provides centralized logging configuration with:
- Structured logging with JSON format
- Log file rotation
- Different log levels (INFO, WARNING, ERROR, CRITICAL)
- Console and file output
- Sanitized output for security
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_entry["extra"] = record.extra_data

        # Add request context if available
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        return json.dumps(log_entry, ensure_ascii=False)


class SanitizedFormatter(logging.Formatter):
    """Formatter that sanitizes sensitive information"""

    SENSITIVE_PATTERNS = [
        "api_key",
        "password",
        "token",
        "secret",
        "auth",
        "bearer",
        "key=",
        "pwd=",
        "pass=",
    ]

    def format(self, record: logging.LogRecord) -> str:
        """Format record with sanitized content"""
        # Create a copy of the record to avoid modifying the original
        record_copy = logging.makeLogRecord(record.__dict__)

        # Sanitize the message
        message = record_copy.getMessage()
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern.lower() in message.lower():
                # Replace with masked version
                message = f"{message[:50]}... [SANITIZED]"
                break

        record_copy.msg = message
        record_copy.args = ()

        return super().format(record_copy)


class RepairGPTLogger:
    """Centralized logger configuration for RepairGPT"""

    def __init__(
        self,
        log_dir: str = "logs",
        log_level: str = "INFO",
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        enable_console: bool = True,
        enable_file: bool = True,
        json_format: bool = False,
    ):
        """
        Initialize logger configuration

        Args:
            log_dir: Directory for log files
            log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_file_size: Maximum size of each log file in bytes
            backup_count: Number of backup files to keep
            enable_console: Whether to log to console
            enable_file: Whether to log to files
            json_format: Whether to use JSON format for logs
        """
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.json_format = json_format

        # Create log directory
        self.log_dir.mkdir(exist_ok=True)

        # Configure logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        # Clear any existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        # Set root logger level
        root_logger.setLevel(self.log_level)

        # Console handler
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)

            if self.json_format:
                console_formatter = JsonFormatter()
            else:
                console_formatter = SanitizedFormatter(
                    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )

            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)

        # File handlers
        if self.enable_file:
            # Main application log
            app_handler = logging.handlers.RotatingFileHandler(
                filename=self.log_dir / "repairgpt.log",
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
            app_handler.setLevel(self.log_level)

            # Error log (only ERROR and CRITICAL)
            error_handler = logging.handlers.RotatingFileHandler(
                filename=self.log_dir / "repairgpt_errors.log",
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
            error_handler.setLevel(logging.ERROR)

            # Set formatters
            if self.json_format:
                file_formatter = JsonFormatter()
            else:
                file_formatter = SanitizedFormatter(
                    fmt="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )

            app_handler.setFormatter(file_formatter)
            error_handler.setFormatter(file_formatter)

            root_logger.addHandler(app_handler)
            root_logger.addHandler(error_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance with the given name"""
        return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

    def log_method_call(self, method_name: str, **kwargs):
        """Log method call with parameters"""
        self.logger.debug(f"Calling {method_name}", extra={"extra_data": kwargs})

    def log_error(self, error: Exception, context: str = "", **kwargs):
        """Log error with context"""
        extra_data = {"context": context, **kwargs}
        self.logger.error(
            f"Error in {context}: {str(error)}",
            exc_info=True,
            extra={"extra_data": extra_data},
        )

    def log_warning(self, message: str, **kwargs):
        """Log warning with context"""
        self.logger.warning(message, extra={"extra_data": kwargs})

    def log_info(self, message: str, **kwargs):
        """Log info with context"""
        self.logger.info(message, extra={"extra_data": kwargs})


def setup_logging(
    log_dir: str = "logs", log_level: str = None, json_format: bool = None
) -> RepairGPTLogger:
    """
    Setup RepairGPT logging system

    Args:
        log_dir: Directory for log files
        log_level: Log level from environment or default to INFO
        json_format: Whether to use JSON format

    Returns:
        Configured RepairGPTLogger instance
    """
    # Get configuration from environment variables
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")

    if json_format is None:
        json_format = os.getenv("LOG_FORMAT", "text").lower() == "json"

    # Create and return logger
    logger_config = RepairGPTLogger(
        log_dir=log_dir, log_level=log_level, json_format=json_format
    )

    # Log initialization
    init_logger = logger_config.get_logger("repairgpt.logger")
    init_logger.info(
        f"RepairGPT logging system initialized - Level: {log_level}, Format: {'JSON' if json_format else 'TEXT'}"
    )

    return logger_config


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Convenience functions for common logging patterns
def log_api_call(logger: logging.Logger, endpoint: str, method: str = "GET", **kwargs):
    """Log API call"""
    logger.info(f"API call: {method} {endpoint}", extra={"extra_data": kwargs})


def log_api_error(logger: logging.Logger, endpoint: str, error: Exception, **kwargs):
    """Log API error"""
    logger.error(
        f"API error: {endpoint} - {str(error)}",
        exc_info=True,
        extra={"extra_data": kwargs},
    )


def log_user_action(logger: logging.Logger, action: str, user_id: str = None, **kwargs):
    """Log user action"""
    extra_data = {"action": action, "user_id": user_id, **kwargs}
    logger.info(f"User action: {action}", extra={"extra_data": extra_data})


def log_performance(logger: logging.Logger, operation: str, duration: float, **kwargs):
    """Log performance metrics"""
    extra_data = {"operation": operation, "duration_ms": duration * 1000, **kwargs}
    logger.info(
        f"Performance: {operation} took {duration:.3f}s",
        extra={"extra_data": extra_data},
    )


# Global logger instance (initialized by setup_logging)
_global_logger_config: Optional[RepairGPTLogger] = None


def init_global_logging(**kwargs) -> RepairGPTLogger:
    """Initialize global logging configuration"""
    global _global_logger_config
    _global_logger_config = setup_logging(**kwargs)
    return _global_logger_config


def get_global_logger_config() -> Optional[RepairGPTLogger]:
    """Get global logger configuration"""
    return _global_logger_config


# Example usage and testing
if __name__ == "__main__":
    # Test logging configuration
    print("Testing RepairGPT Logging System...")

    # Initialize logging
    logger_config = setup_logging(log_level="DEBUG", json_format=False)

    # Get logger
    test_logger = logger_config.get_logger("test")

    # Test different log levels
    test_logger.debug("Debug message - system startup")
    test_logger.info("Info message - normal operation")
    test_logger.warning("Warning message - potential issue detected")
    test_logger.error("Error message - something went wrong")

    try:
        # Test exception logging
        raise ValueError("Test exception for logging")
    except Exception as e:
        test_logger.error("Exception occurred", exc_info=True)

    # Test mixin
    class TestClass(LoggerMixin):
        def test_method(self):
            self.log_info("Testing mixin functionality")
            self.log_warning("Test warning")
            try:
                raise RuntimeError("Test error")
            except Exception as e:
                self.log_error(e, context="test_method")

    test_obj = TestClass()
    test_obj.test_method()

    print("Logging test completed! Check the logs/ directory for output files.")
