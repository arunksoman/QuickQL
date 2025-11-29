#!/usr/bin/env python3
"""
Development setup script for QuickQL.

This script sets up the development environment using uv.
"""

import subprocess
import sys


def run_command(command, description, check=True):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")

    try:
        result = subprocess.run(command, check=check, capture_output=True, text=True)
        if result.stdout:
            print("Output:", result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print("Error output:", e.stderr.strip())
        return False
    except FileNotFoundError:
        print(f"Error: Command not found: {command[0]}")
        return False


def check_uv_installed():
    """Check if uv is installed."""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        print(f"Found uv: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print("QuickQL Development Environment Setup")
    print("=" * 60)

    # Check if uv is installed
    if not check_uv_installed():
        print("\n❌ uv is not installed!")
        print("Please install uv first:")
        print('  Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"')
        print("  Linux/macOS: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("  Or visit: https://docs.astral.sh/uv/getting-started/installation/")
        return False

    print("\n✅ uv is installed")

    # Create virtual environment
    print("\n" + "=" * 40)
    success = run_command(["uv", "venv"], "Creating virtual environment")
    if not success:
        print("❌ Failed to create virtual environment")
        return False

    # Install package in development mode with dev dependencies
    print("\n" + "=" * 40)
    success = run_command(
        ["uv", "pip", "install", "-e", ".[dev]"],
        "Installing package in development mode",
    )
    if not success:
        print("❌ Failed to install package")
        return False

    # Run a quick test to make sure everything works
    print("\n" + "=" * 40)
    success = run_command(
        [
            "uv",
            "run",
            "python",
            "-c",
            "from quickql import Query; print('✅ QuickQL imported successfully')",
        ],
        "Testing installation",
    )
    if not success:
        print("❌ Package installation test failed")
        return False

    # Run ruff check
    print("\n" + "=" * 40)
    success = run_command(
        ["uv", "run", "ruff", "check", "."],
        "Running ruff linting check",
        check=False,  # Don't fail if there are lint errors
    )

    # Run ruff format check
    print("\n" + "=" * 40)
    success = run_command(
        ["uv", "run", "ruff", "format", "--check", "."],
        "Checking code formatting",
        check=False,  # Don't fail if there are format issues
    )

    # Run tests
    print("\n" + "=" * 40)
    success = run_command(["uv", "run", "pytest", "tests/", "-v"], "Running test suite")
    if not success:
        print("⚠️ Some tests failed, but setup is complete")

    print("\n" + "=" * 60)
    print("🎉 Development environment setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print(
        "1. Activate the environment: source .venv/bin/activate (Linux/macOS) or .venv\\Scripts\\activate (Windows)"
    )
    print("2. Or use 'uv run' prefix for commands")
    print("\nCommon commands:")
    print("  uv run pytest tests/                    # Run all tests")
    print("  uv run pytest tests/ --cov=src         # Run tests with coverage")
    print("  uv run ruff check .                    # Lint code")
    print("  uv run ruff format .                   # Format code")
    print("  uv run python run_tests.py all         # Run tests with custom script")
    print("\nHappy coding! 🚀")

    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
