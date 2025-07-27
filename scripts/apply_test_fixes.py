#!/usr/bin/env python3
"""
Apply automatic fixes for common test failures.
"""
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple


class TestFixApplier:
    """Apply automatic fixes for identified test failures."""

    def __init__(self):
        self.fixes_applied = []
        self.analysis_file = "test_failure_analysis.json"

    def load_analysis(self) -> Dict:
        """Load test failure analysis results."""
        if not os.path.exists(self.analysis_file):
            print("No analysis file found")
            return {}

        with open(self.analysis_file, "r") as f:
            return json.load(f)

    def fix_missing_import(self, file_path: str, import_name: str, module_name: str) -> bool:
        """Fix missing import errors."""
        if not os.path.exists(file_path):
            return False

        with open(file_path, "r") as f:
            content = f.read()

        # Check if import already exists
        import_pattern = f"from {module_name} import.*{import_name}"
        if re.search(import_pattern, content):
            return False

        # Find the right place to add import
        lines = content.split("\n")
        import_line = f"from {module_name} import {import_name}"

        # Find last import line
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith(("import ", "from ")):
                last_import_idx = i

        # Insert new import after last import
        lines.insert(last_import_idx + 1, import_line)

        # Write back
        with open(file_path, "w") as f:
            f.write("\n".join(lines))

        return True

    def fix_missing_module(self, file_path: str, module_name: str) -> bool:
        """Fix missing module errors by adjusting import paths."""
        if not os.path.exists(file_path):
            return False

        with open(file_path, "r") as f:
            content = f.read()

        # Common fixes for module not found
        fixes = [
            # Try relative import
            (f"import {module_name}", f"from . import {module_name}"),
            (f"from {module_name}", f"from .{module_name}"),
            # Try src prefix
            (f"import {module_name}", f"from src import {module_name}"),
            (f"from {module_name}", f"from src.{module_name}"),
        ]

        fixed = False
        for old_pattern, new_pattern in fixes:
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                fixed = True
                break

        if fixed:
            with open(file_path, "w") as f:
                f.write(content)

        return fixed

    def fix_none_type_error(self, file_path: str, line_number: Optional[int] = None) -> bool:
        """Add null checks for None type errors."""
        if not os.path.exists(file_path):
            return False

        with open(file_path, "r") as f:
            lines = f.readlines()

        # Simple heuristic: look for variable access without null check
        fixed = False
        for i in range(len(lines)):
            line = lines[i]

            # Pattern: variable[...] or variable.method()
            if re.search(r"(\w+)(\[|\.\w+\()", line):
                # Check if there's already a null check
                if i > 0 and "if " in lines[i - 1] and "is not None" in lines[i - 1]:
                    continue

                # Add null check
                indent = len(line) - len(line.lstrip())
                var_match = re.search(r"(\w+)(\[|\.\w+\()", line)
                if var_match:
                    var_name = var_match.group(1)
                    if var_name not in ["self", "cls", "True", "False", "None"]:
                        lines[i] = f"{' ' * indent}if {var_name} is not None:\n{' ' * (indent + 4)}{line.lstrip()}"
                        fixed = True

        if fixed:
            with open(file_path, "w") as f:
                f.writelines(lines)

        return fixed

    def fix_missing_fixture(self, file_path: str, fixture_name: str) -> bool:
        """Add missing pytest fixtures."""
        if not os.path.exists(file_path):
            return False

        with open(file_path, "r") as f:
            content = f.read()

        # Check if fixture already exists
        if f"def {fixture_name}" in content:
            return False

        # Add basic fixture
        fixture_code = f"""
@pytest.fixture
def {fixture_name}():
    \"\"\"Auto-generated fixture for {fixture_name}.\"\"\"
    # TODO: Implement proper fixture logic
    return None
"""

        # Find a good place to add fixture (after imports)
        lines = content.split("\n")
        import_end = 0
        for i, line in enumerate(lines):
            if line.startswith(("import ", "from ")):
                import_end = i

        # Insert fixture after imports
        lines.insert(import_end + 2, fixture_code)

        # Make sure pytest is imported
        if "import pytest" not in content:
            lines.insert(import_end + 1, "import pytest")

        with open(file_path, "w") as f:
            f.write("\n".join(lines))

        return True

    def fix_async_conflict(self, file_path: str) -> bool:
        """Fix async event loop conflicts."""
        if not os.path.exists(file_path):
            return False

        with open(file_path, "r") as f:
            content = f.read()

        # Add pytest-asyncio marker if missing
        if "@pytest.mark.asyncio" not in content:
            # Find async test functions
            async_pattern = r"async def (test_\w+)"
            matches = re.finditer(async_pattern, content)

            for match in reversed(list(matches)):
                pos = match.start()
                # Find the line start
                line_start = content.rfind("\n", 0, pos) + 1
                indent = pos - line_start

                # Insert decorator
                decorator = " " * indent + "@pytest.mark.asyncio\n"
                content = content[:line_start] + decorator + content[line_start:]

        # Ensure pytest is imported
        if "import pytest" not in content:
            content = "import pytest\n" + content

        with open(file_path, "w") as f:
            f.write(content)

        return True

    def fix_async_plugin_missing(self, file_path: str) -> bool:
        """Fix missing async plugin by adding pytest.ini configuration."""
        # Create or update pytest.ini
        pytest_ini_path = "pytest.ini"

        if os.path.exists(pytest_ini_path):
            with open(pytest_ini_path, "r") as f:
                content = f.read()

            # Check if asyncio mode is already configured
            if "asyncio_mode" not in content:
                # Add to existing pytest.ini
                if "[tool:pytest]" in content:
                    content = content.replace("[tool:pytest]", "[tool:pytest]\nasyncio_mode = auto")
                else:
                    content += "\n\n[tool:pytest]\nasyncio_mode = auto\n"

                with open(pytest_ini_path, "w") as f:
                    f.write(content)
                return True
        else:
            # Create new pytest.ini
            with open(pytest_ini_path, "w") as f:
                f.write("[tool:pytest]\nasyncio_mode = auto\n")
            return True

        return False

    def fix_mock_configuration(self, file_path: str) -> bool:
        """Fix mock configuration errors."""
        if not os.path.exists(file_path):
            return False

        with open(file_path, "r") as f:
            content = f.read()

        # Common mock fixes
        fixes_applied = False

        # Replace Mock() with MagicMock() for better attribute handling
        if "Mock()" in content:
            content = content.replace("Mock()", "MagicMock()")
            fixes_applied = True

        # Ensure proper imports
        if "MagicMock" in content and "from unittest.mock import" in content:
            if "MagicMock" not in content.split("from unittest.mock import")[1].split("\n")[0]:
                content = content.replace("from unittest.mock import", "from unittest.mock import MagicMock, ")
                fixes_applied = True

        if fixes_applied:
            with open(file_path, "w") as f:
                f.write(content)

        return fixes_applied

    def apply_fixes(self) -> Tuple[int, List[str]]:
        """Apply all identified fixes."""
        analysis = self.load_analysis()
        if not analysis:
            return 0, []

        fixed_count = 0
        fixed_issues = []

        for issue in analysis.get("fixable_issues", []):
            file_path = issue["file"]
            fix_type = issue["fix_type"]

            fixed = False

            if fix_type == "missing_import" and len(issue["match_groups"]) >= 2:
                fixed = self.fix_missing_import(file_path, issue["match_groups"][0], issue["match_groups"][1])
            elif fix_type == "missing_module" and issue["match_groups"]:
                fixed = self.fix_missing_module(file_path, issue["match_groups"][0])
            elif fix_type == "none_type_error":
                fixed = self.fix_none_type_error(file_path)
            elif fix_type == "missing_fixture" and issue["match_groups"]:
                fixed = self.fix_missing_fixture(file_path, issue["match_groups"][0])
            elif fix_type == "async_conflict":
                fixed = self.fix_async_conflict(file_path)
            elif fix_type == "async_plugin_missing":
                fixed = self.fix_async_plugin_missing(file_path)
            elif fix_type == "mock_configuration":
                fixed = self.fix_mock_configuration(file_path)

            if fixed:
                fixed_count += 1
                fixed_issues.append(f"{fix_type} in {file_path}")
                self.fixes_applied.append({"file": file_path, "fix_type": fix_type, "test": issue["test"]})

        return fixed_count, fixed_issues

    def generate_fix_summary(self) -> str:
        """Generate a summary of fixes applied."""
        if not self.fixes_applied:
            return "No fixes were applied"

        summary = []
        fix_counts = {}

        for fix in self.fixes_applied:
            fix_type = fix["fix_type"]
            if fix_type not in fix_counts:
                fix_counts[fix_type] = 0
            fix_counts[fix_type] += 1

        for fix_type, count in fix_counts.items():
            summary.append(f"- {fix_type}: {count} fixes")

        return "\n".join(summary)


def main():
    """Main function to apply fixes."""
    fixer = TestFixApplier()

    # Apply fixes
    fixed_count, fixed_issues = fixer.apply_fixes()

    # Generate summary
    fix_summary = fixer.generate_fix_summary()

    # Set GitHub Actions outputs
    print(f"::set-output name=fixed::{'true' if fixed_count > 0 else 'false'}")
    print(f"::set-output name=fixed_count::{fixed_count}")
    print(f"::set-output name=fix_summary::{fix_summary}")
    print(f"::set-output name=fixed_issues::{', '.join(fixed_issues)}")

    # Print summary
    print("\n=== Test Fix Summary ===")
    print(f"Total fixes applied: {fixed_count}")
    if fixed_count > 0:
        print("\nFixes applied:")
        print(fix_summary)
        print("\nFixed issues:")
        for issue in fixed_issues:
            print(f"  - {issue}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
