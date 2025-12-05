# Contributing to YoungLion

Thank you for your interest in contributing to YoungLion! This document provides guidelines and instructions for contributing.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)

---

## Code of Conduct

Please treat all contributors with respect. We aim to maintain a welcoming, inclusive community.

### Expected Behavior
- Be respectful and constructive
- Accept criticism gracefully
- Focus on what's best for the community
- Show empathy and understanding

### Unacceptable Behavior
- Harassment, discrimination, or offensive comments
- Trolling or insulting language
- Personal attacks
- Any form of abuse

---

## Getting Started

### Prerequisites
- Git
- Python 3.7 or higher
- pip

### Fork & Clone

1. Fork the repository on GitHub
2. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/YoungLion.git
cd YoungLion
```

3. Add upstream remote:
```bash
git remote add upstream https://github.com/cavanshirpro/YoungLion.git
```

---

## Development Setup

### 1. Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 2. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- pytest - Testing framework
- pytest-cov - Coverage reporting
- black - Code formatting
- pylint - Code linting
- mypy - Type checking
- build, twine - Build tools

### 3. Verify Installation

```bash
python -c "import YoungLion; print(YoungLion.__version__)"
# Should output: 0.0.9.9
```

---

## Making Changes

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
# OR
git checkout -b bugfix/issue-description
# OR
git checkout -b docs/documentation-improvement
```

### 2. Make Your Changes

Follow these guidelines:

#### Code Style
- Use **black** for formatting (100 char line limit)
- Use **snake_case** for functions/variables
- Use **PascalCase** for classes
- Use **UPPER_CASE** for constants

#### Type Hints
```python
# Good
def process_data(data: Dict[str, Any]) -> List[str]:
    return list(data.keys())

# Also good - for complex types
from typing import Dict, List, Any

def handle_items(items: List[Dict]) -> None:
    pass
```

#### Documentation
```python
def calculate_average(numbers: List[float]) -> float:
    """
    Calculate the arithmetic mean of numbers.
    
    Args:
        numbers: List of numeric values
        
    Returns:
        The average value
        
    Example:
        >>> calculate_average([1, 2, 3, 4, 5])
        3.0
        
    Raises:
        ValueError: If list is empty
    """
    if not numbers:
        raise ValueError("List cannot be empty")
    return sum(numbers) / len(numbers)
```

### 3. Commit Messages

Write clear, descriptive commit messages:

```bash
# Good
git commit -m "feat: Add SmartCache ultra-fast completion system"
git commit -m "fix: Resolve path-based access edge cases in DDM"
git commit -m "docs: Update README with new examples"
git commit -m "test: Add comprehensive tests for Range class"

# Avoid
git commit -m "fixes stuff"
git commit -m "update"
git commit -m "WIP"
```

### 4. Keep Commits Atomic

Each commit should represent one logical change:
- Don't mix multiple features
- Don't mix refactoring with new features
- Don't include unrelated fixes

---

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test
```bash
pytest tests/test_datamodel.py -v
pytest tests/test_datamodel.py::TestDDM::test_clone -v
```

### Run with Coverage
```bash
pytest tests/ --cov=src/YoungLion --cov-report=html
# Coverage report will be in htmlcov/index.html
```

### Writing Tests

```python
import pytest
from YoungLion import DDM, SmartCache

class TestDDM:
    """Test cases for DDM class."""
    
    def test_clone(self):
        """Test that clone creates deep copy."""
        ddm = DDM({"name": "Alice", "age": 30})
        cloned = ddm.clone()
        
        # Modify clone
        cloned.name = "Bob"
        
        # Original unchanged
        assert ddm.name == "Alice"
        assert cloned.name == "Bob"
    
    def test_path_access(self):
        """Test path-based nested access."""
        ddm = DDM({"user": {"address": {"city": "NY"}}})
        
        assert ddm.get_path("user.address.city") == "NY"
        assert ddm.has_path("user.address")
        
        ddm.set_path("user.address.zip", "10001")
        assert ddm.get_path("user.address.zip") == "10001"
    
    @pytest.mark.parametrize("value,expected", [
        ([], []),
        ([1, 2, 3], [1, 2, 3]),
        ([{"name": "test"}], [{"name": "test"}]),
    ])
    def test_list_handling(self, value, expected):
        """Test handling of list values."""
        ddm = DDM({"items": value})
        assert ddm.items == expected
```

---

## Code Quality

### 1. Format Code
```bash
black src/YoungLion/ --line-length 100
```

### 2. Check Linting
```bash
pylint src/YoungLion/
# Fix issues with:
pylint src/YoungLion/ --disable=all --enable=E,F
```

### 3. Type Checking
```bash
mypy src/YoungLion/ --ignore-missing-imports
```

### 4. Full Quality Check
```bash
# Run all checks
black --check src/YoungLion/
pylint src/YoungLion/
mypy src/YoungLion/ --ignore-missing-imports
pytest tests/ -v --cov=src/YoungLion
```

---

## Submitting Changes

### 1. Keep Branch Updated

```bash
git fetch upstream
git rebase upstream/main
```

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. Go to GitHub repository
2. Click "Compare & pull request"
3. Fill in PR description:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Related Issue
Fixes #123

## Testing
- [x] Added tests
- [x] All tests pass
- [x] Coverage: XX%

## Checklist
- [x] Code follows style guidelines
- [x] Documentation updated
- [x] No breaking changes
- [x] All tests pass
```

### 4. Review Process

- Maintainer will review code
- May request changes or improvements
- Once approved, PR will be merged

---

## Reporting Bugs

### Before Reporting
- Check if bug already reported in Issues
- Update to latest version
- Verify the issue is reproducible

### Bug Report Template

```markdown
## Description
Brief description of the bug

## Environment
- Python Version: 3.10
- OS: Windows 10
- YoungLion Version: 0.0.9.9

## Steps to Reproduce
1. First step
2. Second step
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Error Message
```
Paste full error traceback here
```

## Additional Context
Any other relevant information
```

---

## Requesting Features

### Feature Request Template

```markdown
## Description
Clear description of the requested feature

## Motivation
Why this feature is needed

## Proposed Solution
How should this work (if you have ideas)

## Examples
Code examples of how it would be used

## Alternative Solutions
Any alternative approaches considered
```

---

## Documentation Guidelines

### README.md
- Keep updated with new features
- Include examples for major classes
- Update installation instructions if needed

### Docstrings
```python
def function_name(param1: str, param2: int) -> bool:
    """
    One-line summary.
    
    Longer description if needed. Explain what it does,
    why it's useful, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
        TypeError: When param2 is wrong type
        
    Example:
        >>> function_name("test", 42)
        True
        
    Note:
        Any important notes about usage
    """
    pass
```

### Changelog
Add entry to Releases.md for significant changes:
```markdown
## Version X.X.X - Date

### Added
- New feature description

### Changed
- Changed behavior description

### Fixed
- Bug fix description
```

---

## Build & Packaging

### Local Build Testing

```bash
# Build wheels locally
python -m build --wheel

# Install locally built wheel
pip install dist/YoungLion-*.whl --force-reinstall

# Verify installation
python -c "import YoungLion; print(YoungLion.__version__)"
```

### Cross-Platform Testing

We use GitHub Actions for automated testing on:
- Windows
- Linux
- macOS

With Python versions: 3.7, 3.8, 3.9, 3.10, 3.11, 3.12

---

## Questions or Need Help?

- 📧 Email: cavanshirpro@gmail.com
- 🐛 Issues: https://github.com/cavanshirpro/YoungLion/issues
- 💬 Discussions: https://github.com/cavanshirpro/YoungLion/discussions

---

## Recognition

Contributors who have made significant contributions are recognized in:
- README.md Contributors section
- Release notes
- GitHub Contributors page

Thank you for contributing to YoungLion! 🦁
