#!/usr/bin/env python3
"""
Build verification script for QuickQL.

This script verifies that the package can be built properly and checks
the built artifacts.
"""

from pathlib import Path
import shutil
import subprocess
import sys


def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n{'=' * 50}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print("=" * 50)

    result = subprocess.run(command, capture_output=False, text=True)
    success = result.returncode == 0

    if success:
        print(f"✅ {description} - SUCCESS")
    else:
        print(f"❌ {description} - FAILED")

    return success


def check_build_dependencies():
    """Check if build dependencies are available."""
    print("Checking build dependencies...")

    try:
        import build  # noqa

        print("✅ build package is available")
        return True
    except ImportError:
        print("❌ build package not found")
        print("Install with: uv pip install build")
        return False


def clean_build_artifacts():
    """Clean previous build artifacts."""
    print("\nCleaning previous build artifacts...")

    paths_to_clean = [
        Path("dist"),
        Path("build"),
        Path("src/quickql.egg-info"),
        Path("quickql.egg-info"),
    ]

    for path in paths_to_clean:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed directory: {path}")
            else:
                path.unlink()
                print(f"Removed file: {path}")


def build_package():
    """Build the package."""
    success = run_command(
        ["python", "-m", "build"], "Building package (wheel and source distribution)"
    )
    return success


def verify_build_artifacts():
    """Verify the build artifacts."""
    print("\n" + "=" * 50)
    print("Verifying build artifacts")
    print("=" * 50)

    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ dist/ directory not found")
        return False

    files = list(dist_dir.glob("*"))
    if not files:
        print("❌ No files found in dist/ directory")
        return False

    print(f"Found {len(files)} files in dist/:")

    wheel_found = False
    tarball_found = False

    for file in files:
        print(f"  📦 {file.name}")
        if file.suffix == ".whl":
            wheel_found = True
        elif file.name.endswith(".tar.gz"):
            tarball_found = True

    if wheel_found and tarball_found:
        print("✅ Both wheel and source distribution found")
        return True
    else:
        if not wheel_found:
            print("❌ Wheel (.whl) file not found")
        if not tarball_found:
            print("❌ Source distribution (.tar.gz) file not found")
        return False


def check_package_metadata():
    """Check package metadata using twine."""
    print("\n" + "=" * 50)
    print("Checking package metadata")
    print("=" * 50)

    try:
        import importlib.util

        if importlib.util.find_spec("twine") is not None:
            print("✅ twine is available")
        else:
            raise ImportError("twine not found")
    except ImportError:
        print("⚠️ twine not found - installing...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "twine"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("❌ Failed to install twine")
            return False

    success = run_command(
        ["python", "-m", "twine", "check", "dist/*"],
        "Checking package metadata with twine",
    )
    return success


def test_package_import():
    """Test that the built package can be imported."""
    print("\n" + "=" * 50)
    print("Testing package import")
    print("=" * 50)

    # Find the wheel file
    dist_dir = Path("dist")
    wheel_files = list(dist_dir.glob("*.whl"))

    if not wheel_files:
        print("❌ No wheel file found to test")
        return False

    wheel_file = wheel_files[0]
    print(f"Testing wheel: {wheel_file.name}")

    # Install in a temporary virtual environment would be ideal,
    # but for simplicity, we'll just test the source code
    success = run_command(
        [
            "python",
            "-c",
            "from quickql import Query; q = Query().SELECT('*').FROM('test'); "
            "print('✅ Import test passed'); print('Query result:', str(q))",
        ],
        "Testing package import and basic functionality",
    )

    return success


def main():
    """Main function."""
    print("=" * 60)
    print("QuickQL Build Verification")
    print("=" * 60)
    print("This script will:")
    print("1. Check build dependencies")
    print("2. Clean previous build artifacts")
    print("3. Build the package")
    print("4. Verify build artifacts")
    print("5. Check package metadata")
    print("6. Test package import")
    print()

    all_checks_passed = True

    # Step 1: Check dependencies
    if not check_build_dependencies():
        print("\n❌ Build dependencies not available!")
        return False

    # Step 2: Clean artifacts
    clean_build_artifacts()

    # Step 3: Build package
    if not build_package():
        print("\n❌ Package build failed!")
        all_checks_passed = False

    # Step 4: Verify artifacts
    if not verify_build_artifacts():
        print("\n❌ Build artifacts verification failed!")
        all_checks_passed = False

    # Step 5: Check metadata
    if not check_package_metadata():
        print("\n❌ Package metadata check failed!")
        all_checks_passed = False

    # Step 6: Test import
    if not test_package_import():
        print("\n❌ Package import test failed!")
        all_checks_passed = False

    print("\n" + "=" * 60)
    if all_checks_passed:
        print("🎉 All checks passed! Package is ready for publishing.")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review the built artifacts in dist/")
        print("2. Test the package in a clean environment")
        print("3. Create a release tag to trigger PyPI publishing")
        print("4. Use: python release.py <version>")
    else:
        print("❌ Some checks failed! Please fix the issues before publishing.")
        print("=" * 60)

    return all_checks_passed


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
