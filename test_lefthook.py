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


if __name__ == "__main__":
    print("Testing lefthook...")
    result = test_function(1, 2)
    print(f"Test completed with result: {result}")
