#!/usr/bin/env python3
"""
Test runner script for QuickQL.

This script provides easy commands to run tests with different configurations.
"""

from pathlib import Path
import subprocess
import sys


def run_command(command, description):
    """Run a command and print results."""
    print(f"\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print("=" * 60)

    result = subprocess.run(command, capture_output=False, text=True)
    return result.returncode == 0


def main():
    """Main test runner function."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [command]")
        print("\nAvailable commands:")
        print("  all       - Run all tests")
        print("  basic     - Run basic functionality tests")
        print("  building  - Run query building tests")
        print("  edge      - Run edge case tests")
        print("  integration - Run integration tests")
        print("  coverage  - Run tests with coverage report")
        print("  verbose   - Run tests with verbose output")
        print("  help      - Show this help message")
        return

    command = sys.argv[1].lower()

    # Ensure we're in the project root
    project_root = Path(__file__).parent

    if command == "help":
        main()
        return
    elif command == "all":
        success = run_command(["python", "-m", "pytest", "tests/", "-v"], "All Tests")
    elif command == "basic":
        success = run_command(
            ["python", "-m", "pytest", "tests/test_query_basic.py", "-v"],
            "Basic Functionality Tests",
        )
    elif command == "building":
        success = run_command(
            ["python", "-m", "pytest", "tests/test_query_building.py", "-v"],
            "Query Building Tests",
        )
    elif command == "edge":
        success = run_command(
            ["python", "-m", "pytest", "tests/test_edge_cases.py", "-v"],
            "Edge Case Tests",
        )
    elif command == "integration":
        success = run_command(
            ["python", "-m", "pytest", "tests/test_integration.py", "-v"],
            "Integration Tests",
        )
    elif command == "coverage":
        success = run_command(
            [
                "python",
                "-m",
                "pytest",
                "tests/",
                "--cov=src",
                "--cov-report=html",
                "--cov-report=term",
            ],
            "Tests with Coverage Report",
        )
        if success:
            print("\nCoverage report generated in htmlcov/index.html")
    elif command == "verbose":
        success = run_command(
            ["python", "-m", "pytest", "tests/", "-v", "-s", "--tb=short"],
            "Verbose Test Output",
        )
    else:
        print(f"Unknown command: {command}")
        print("Run 'python run_tests.py help' for available commands")
        return

    if success:
        print(f"\n✅ {command.title()} tests passed!")
    else:
        print(f"\n❌ {command.title()} tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
