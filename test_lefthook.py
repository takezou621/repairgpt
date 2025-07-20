#!/usr/bin/env python3
"""
Test file for lefthook functionality
This file tests the lefthook pre-commit hooks
"""


def test_function(x, y):
    """A simple test function for lefthook validation"""
    result = x + y
    print(f"Result is {result}")
    return result


def test_formatting():
    """Test that demonstrates lefthook auto-formatting"""
    values = [1, 2, 3, 4, 5]
    for value in values:
        print(f"Processing value: {value}")
    return sum(values)


if __name__ == "__main__":
    print("Testing lefthook...")
    result = test_function(1, 2)
    print(f"Test completed with result: {result}")

    formatting_result = test_formatting()
    print(f"Formatting test result: {formatting_result}")
