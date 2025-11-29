# PyPI Publishing Setup Guide

This guide helps you set up PyPI publishing for QuickQL using GitHub Actions and trusted publishing.

## Prerequisites

1. A PyPI account (create one at [pypi.org](https://pypi.org))
2. GitHub repository with admin access
3. The package name should be available on PyPI

## Setup Steps

### 1. Register the Package on PyPI

First, you need to register your package name on PyPI:

1. Go to [pypi.org](https://pypi.org) and sign in
2. You have two options:
   - **Option A**: Use the web interface to create a new project
   - **Option B**: Do an initial manual upload (recommended for first-time setup)

#### Option B: Initial Manual Upload

```bash
# Install build tools
uv pip install build twine

# Build the package
uv run python -m build

# Upload to PyPI (you'll be prompted for credentials)
uv run twine upload dist/*
```

### 2. Set Up Trusted Publishing on PyPI

This allows GitHub Actions to publish without storing API tokens:

1. Go to [pypi.org](https://pypi.org) and sign in
2. Navigate to your project (quickql)
3. Go to "Manage" → "Publishing"
4. Click "Add a new pending publisher"
5. Fill in the details:
   - **PyPI Project Name**: `quickql`
   - **Owner**: `yourusername` (your GitHub username)
   - **Repository name**: `quickql`
   - **Workflow filename**: `ci.yml`
   - **Environment name**: `pypi`
6. Click "Add"

### 3. Set Up GitHub Repository Environments

1. Go to your GitHub repository
2. Navigate to "Settings" → "Environments"
3. Create a new environment called `pypi`
4. Optionally, add protection rules:
   - Required reviewers
   - Deployment branches (e.g., only tags matching `v*`)

### 4. Optional: Set Up TestPyPI

For testing releases with release candidates:

1. Go to [test.pypi.org](https://test.pypi.org) and sign in
2. Follow the same trusted publishing setup as above, but:
   - Environment name: `testpypi`
   - This will be used for release candidates (tags containing 'rc')

## Usage

### Creating a Release

Use the provided release script:

```bash
# Dry run to see what would happen
python release.py 0.1.1 --dry-run

# Create actual release
python release.py 0.1.1
```

### Release Types

- **Regular release**: `python release.py 0.1.1`
  - Creates tag `v0.1.1`
  - Publishes to PyPI
  - Creates GitHub release
  
- **Release candidate**: `python release.py 0.2.0rc1`
  - Creates tag `v0.2.0rc1`
  - Publishes to TestPyPI (if configured)
  - Does not publish to main PyPI

### Manual Release Process

If you prefer manual control:

```bash
# 1. Update version in pyproject.toml
# 2. Commit the change
git add pyproject.toml
git commit -m "Bump version to 0.1.1"

# 3. Create and push tag
git tag -a v0.1.1 -m "Release 0.1.1"
git push origin v0.1.1

# 4. GitHub Actions will automatically build and publish
```

## Workflow Overview

When you push a tag:

1. **CI runs**: Tests run on all supported Python versions
2. **Build**: Package is built (wheel and source distribution)
3. **Publish to PyPI**: Uses trusted publishing (no tokens needed)
4. **GitHub Release**: Creates a release with signed artifacts
5. **TestPyPI**: For release candidates, also publishes to TestPyPI

## Troubleshooting

### Common Issues

1. **Package name already exists on PyPI**
   - Choose a different name in `pyproject.toml`
   - Update the trusted publishing configuration

2. **Trusted publishing not working**
   - Verify the repository name, owner, and workflow filename exactly match
   - Check that the environment name in the workflow matches PyPI configuration

3. **Build fails**
   - Ensure all tests pass before creating a tag
   - Check the GitHub Actions logs for detailed error messages

4. **Permission denied on PyPI**
   - Verify trusted publishing is set up correctly
   - Check that you're the owner/maintainer of the PyPI project

### Useful Commands

```bash
# Check what would be built
uv run python -m build --help

# Test the package locally
uv pip install dist/quickql-0.1.0-py3-none-any.whl
python -c "from quickql import Query; print('Success!')"

# Check package metadata
uv run twine check dist/*
```

## Security Notes

- Never store PyPI API tokens in your repository
- Use trusted publishing instead of API tokens
- Regularly review who has access to your GitHub repository
- Consider requiring reviews for the `pypi` environment

## Next Steps

After setting up:

1. Test the workflow with a release candidate
2. Monitor the first few releases closely
3. Consider setting up release notes automation
4. Add badges to your README showing PyPI version and download stats