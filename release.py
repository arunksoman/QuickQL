import argparse
from pathlib import Path
import re
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
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print("Error output:", e.stderr.strip())
        return None
    except FileNotFoundError:
        print(f"Error: Command not found: {command[0]}")
        return None


def get_current_version():
    """Get current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found")
        return None

    content = pyproject_path.read_text()
    match = re.search(r'version = "([^"]+)"', content)
    if match:
        return match.group(1)

    print("Error: Could not find version in pyproject.toml")
    return None


def update_version(new_version):
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    # Update version - only the main project version in [project] section
    updated_content = re.sub(
        r'(\[project\].*?)^version = "[^"]+"',
        rf'\1version = "{new_version}"',
        content,
        flags=re.MULTILINE | re.DOTALL
    )

    if content == updated_content:
        print("Error: Could not update version in pyproject.toml")
        return False

    pyproject_path.write_text(updated_content)
    print(f"Updated version to {new_version} in pyproject.toml")
    return True


def validate_version(version):
    """Validate version format."""
    # Simple semantic version validation
    pattern = r"^\d+\.\d+\.\d+(?:rc\d+)?$"
    return re.match(pattern, version) is not None


def check_git_status():
    """Check if git working directory is clean."""
    result = run_command(
        ["git", "status", "--porcelain"], "Checking git status", check=False
    )
    if result is None:
        return False

    if result.stdout.strip():
        print(
            "Error: Git working directory is not clean. Please commit or stash changes."
        )
        return False

    return True


def create_release(version, dry_run=False):
    """Create a release."""
    if not validate_version(version):
        print(f"Error: Invalid version format: {version}")
        print("Version should be in format: X.Y.Z or X.Y.ZrcN")
        return False

    current_version = get_current_version()
    if not current_version:
        return False

    print(f"Current version: {current_version}")
    print(f"New version: {version}")

    if not check_git_status():
        return False

    if dry_run:
        print("DRY RUN MODE - No changes will be made")
        print("Steps that would be performed:")
        print(f"1. Update version to {version}")
        print("2. Commit version update")
        print(f"3. Create git tag v{version}")
        print("4. Push tag to origin")
        return True

    # Update version
    if not update_version(version):
        return False

    # Commit version update
    result = run_command(["git", "add", "pyproject.toml"], "Staging pyproject.toml")
    if not result:
        return False

    result = run_command(
        ["git", "commit", "-m", f"Bump version to {version}"],
        "Committing version update",
    )
    if not result:
        return False

    # Create tag
    tag_name = f"{version}"
    result = run_command(
        ["git", "tag", "-a", tag_name, "-m", f"Release {version}"],
        f"Creating tag {tag_name}",
    )
    if not result:
        return False

    # Push tag
    result = run_command(["git", "push", "origin", tag_name], f"Pushing tag {tag_name}")
    if not result:
        return False

    # Also push the commit
    result = run_command(["git", "push"], "Pushing version update commit")
    if not result:
        print("Warning: Failed to push version update commit")

    print("✅ Release {version} created successfully!")
    print("🚀 GitHub Actions will now build and publish to PyPI")
    print("📦 Check the Actions tab: https://github.com/yourusername/quickql/actions")

    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Create a QuickQL release")
    parser.add_argument("version", help="Version to release (e.g., 0.1.1, 0.2.0rc1)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("QuickQL Release Script")
    print("=" * 60)

    success = create_release(args.version, args.dry_run)

    if not success:
        print("❌ Release creation failed!")
        sys.exit(1)

    if not args.dry_run:
        print("\n" + "=" * 60)
        print("Release created successfully! 🎉")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Monitor GitHub Actions for build and publish status")
        print("2. Check PyPI for the new release")
        print("3. Update documentation if needed")
        print("4. Announce the release!")


if __name__ == "__main__":
    main()
