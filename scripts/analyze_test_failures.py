#!/usr/bin/env python3
"""
Analyze test failures from GitHub Actions logs and identify fixable issues.
"""
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class TestFailureAnalyzer:
    """Analyze test failures and identify patterns that can be automatically fixed."""

    def __init__(self):
        self.failures = []
        self.fixable_patterns = {
            "import_error": {
                "pattern": r"ImportError: cannot import name '(\w+)' from '([\w\.]+)'",
                "fix_type": "missing_import",
                "description": "Missing import statement",
            },
            "module_not_found": {
                "pattern": r"ModuleNotFoundError: No module named '([\w\.]+)'",
                "fix_type": "missing_module",
                "description": "Missing module or incorrect import path",
            },
            "attribute_error": {
                "pattern": r"AttributeError: '(\w+)' object has no attribute '(\w+)'",
                "fix_type": "missing_attribute",
                "description": "Missing attribute or method",
            },
            "type_error_none": {
                "pattern": r"TypeError: 'NoneType' object is not (subscriptable|iterable|callable)",
                "fix_type": "none_type_error",
                "description": "None type error - missing null check",
            },
            "assertion_error": {
                "pattern": r"AssertionError: assert (.*?) (==|!=|is|is not) (.*)",
                "fix_type": "assertion_failure",
                "description": "Test assertion failure",
            },
            "fixture_not_found": {
                "pattern": r"fixture '(\w+)' not found",
                "fix_type": "missing_fixture",
                "description": "Pytest fixture not found",
            },
            "async_error": {
                "pattern": (
                    r"RuntimeError: (This event loop is already running|"
                    r"Cannot run the event loop while another loop is running)"
                ),
                "fix_type": "async_conflict",
                "description": "Async event loop conflict",
            },
            "async_plugin_missing": {
                "pattern": r"async def functions are not natively supported.*You need to install a suitable plugin",
                "fix_type": "async_plugin_missing",
                "description": "Async test plugin missing",
            },
            "mock_error": {
                "pattern": r"AttributeError: .*Mock.* object has no attribute",
                "fix_type": "mock_configuration",
                "description": "Mock object configuration error",
            },
        }

    def parse_logs(self, log_dir: str = "workflow_logs") -> List[Dict]:
        """Parse workflow logs to extract test failures."""
        failures = []

        # Parse log files
        if os.path.exists(log_dir):
            # Include both .txt and .log files
            for log_file in Path(log_dir).rglob("*.[tl][xo][tg]"):
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                    # Extract pytest failures - multiple patterns
                    patterns = [
                        # Standard pytest output
                        r"FAILED (.*?) - (.*?)(?=(?:FAILED|PASSED|===|$))",
                        # Alternative format
                        r"FAILED (.*?)\n(.*?)(?=(?:FAILED|PASSED|===|$))",
                        # Short format
                        r"FAILED (.*?)$",
                    ]

                    for pattern in patterns:
                        failure_blocks = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                        if failure_blocks:
                            break

                    # Also look for async function errors
                    if "async def functions are not natively supported" in content:
                        test_match = re.search(r"(test_\w+)", content)
                        if test_match:
                            failures.append(
                                {
                                    "test": test_match.group(1),
                                    "error": (
                                        "async def functions are not natively supported. "
                                        "You need to install a suitable plugin"
                                    ),
                                    "file": "unknown",
                                }
                            )

                    for test_name, error_msg in failure_blocks:
                        failures.append(
                            {
                                "test": test_name.strip(),
                                "error": error_msg.strip(),
                                "file": self._extract_file_from_test_name(test_name),
                            }
                        )

        # Also check for direct pytest output
        if os.path.exists("pytest.log"):
            with open("pytest.log", "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                # Similar parsing logic

        self.failures = failures
        return failures

    def _extract_file_from_test_name(self, test_name: str) -> str:
        """Extract file path from test name."""
        match = re.match(r"(.*?)::.*", test_name)
        if match:
            return match.group(1)
        return ""

    def identify_fixable_issues(self) -> Tuple[List[Dict], int]:
        """Identify which failures can be automatically fixed."""
        fixable_issues = []

        for failure in self.failures:
            error_msg = failure["error"]

            for pattern_name, pattern_info in self.fixable_patterns.items():
                match = re.search(pattern_info["pattern"], error_msg)
                if match:
                    fixable_issues.append(
                        {
                            "test": failure["test"],
                            "file": failure["file"],
                            "error": error_msg,
                            "fix_type": pattern_info["fix_type"],
                            "pattern": pattern_name,
                            "match_groups": match.groups(),
                            "description": pattern_info["description"],
                        }
                    )
                    break

        return fixable_issues, len(fixable_issues)

    def generate_report(self) -> Dict:
        """Generate analysis report."""
        fixable_issues, fixable_count = self.identify_fixable_issues()

        report = {
            "total_failures": len(self.failures),
            "fixable_count": fixable_count,
            "fixable_percentage": (fixable_count / len(self.failures) * 100) if self.failures else 0,
            "fixable_issues": fixable_issues,
            "fix_types": {},
        }

        # Count fix types
        for issue in fixable_issues:
            fix_type = issue["fix_type"]
            if fix_type not in report["fix_types"]:
                report["fix_types"][fix_type] = 0
            report["fix_types"][fix_type] += 1

        return report

    def save_analysis(self, output_file: str = "test_failure_analysis.json"):
        """Save analysis results to file."""
        report = self.generate_report()

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        return report


def main():
    """Main function to run the analyzer."""
    analyzer = TestFailureAnalyzer()

    # Parse logs
    failures = analyzer.parse_logs()
    print(f"Found {len(failures)} test failures")

    # Generate report
    report = analyzer.generate_report()

    # Save analysis
    analyzer.save_analysis()

    # Set GitHub Actions outputs
    print(f"::set-output name=total_failures::{report['total_failures']}")
    print(f"::set-output name=fixable_count::{report['fixable_count']}")
    print(f"::set-output name=fixable::{'true' if report['fixable_count'] > 0 else 'false'}")

    # Print summary
    print("\n=== Test Failure Analysis Summary ===")
    print(f"Total failures: {report['total_failures']}")
    print(f"Fixable issues: {report['fixable_count']} ({report['fixable_percentage']:.1f}%)")

    if report["fix_types"]:
        print("\nFixable issue types:")
        for fix_type, count in report["fix_types"].items():
            print(f"  - {fix_type}: {count}")

    return 0 if report["fixable_count"] > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
