# Contributing to Linkglys

**Last Updated:** April 9, 2026

Thank you for your interest in contributing to Linkglys! This document provides guidelines and instructions for contributing to the project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Code Standards](#code-standards)
- [Documentation Standards](#documentation-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Component Ownership](#component-ownership)

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

---

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, check existing issues. When creating a bug report:

1. **Use a clear, descriptive title**
2. **Describe the exact steps to reproduce**
3. **Include expected vs actual behavior**
4. **Provide environment details** (Python version, OS, etc.)
5. **Include logs or error messages**

Example:
```
**Steps to Reproduce:**
1. Start API server: `cd src && python3 main.py`
2. Call POST /api/v2/auth/login with invalid credentials
3. Observe 500 error instead of expected 401

**Expected:** 401 Unauthorized
**Actual:** 500 Internal Server Error
**Environment:** Python 3.11, macOS 14.0
```

### Suggesting Enhancements

1. **Check existing issues** to avoid duplicates
2. **Describe the current behavior** and desired change
3. **Explain why this would be useful**
4. **Consider implementation approach**

### Pull Requests

We welcome PRs for:
- Bug fixes
- New features (discuss in issue first for large changes)
- Documentation improvements
- Performance optimizations
- Test coverage improvements

---

## Development Setup

See [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md) for complete setup instructions.

**Quick setup:**
```bash
git clone https://github.com/NeuralBlitz/opencode-lrs-agents-nbx
cd opencode-lrs-agents-nbx
pip install -e ".[dev]"
```

---

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

**Branch naming conventions:**
- `feature/` — New features
- `fix/` — Bug fixes
- `docs/` — Documentation changes
- `refactor/` — Code refactoring
- `test/` — Test additions/improvements
- `chore/` — Maintenance tasks

### 2. Make Your Changes

- Follow existing code style
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Verify Your Changes

```bash
# Run all tests
pytest tests/ -v

# Check code quality
ruff check src/ tests/
black --check src/ tests/
mypy src/

# Check coverage
pytest --cov=src --cov-fail-under=80
```

---

## Submitting a Pull Request

1. **Fork the repository** and create your branch
2. **Make changes** following guidelines above
3. **Run tests** — ensure all pass
4. **Update documentation** — README, API docs, etc.
5. **Push to your fork** and open a PR
6. **Describe your changes** in the PR description

### PR Description Template

```markdown
## Summary
Brief description of what this PR does.

## Changes
- Added X feature
- Fixed Y bug
- Updated Z documentation

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Coverage above 80%

## Documentation
- [ ] README updated (if needed)
- [ ] API docs updated (if needed)
- [ ] CHANGELOG entry added

## Related Issues
Closes #123
```

---

## Code Standards

### Python Style

- **Black** for formatting (line length: 100)
- **Ruff** for linting
- **Type hints** for all public APIs
- **Docstrings** for all public classes and functions

```python
def calculate_score(base: float, multiplier: float = 1.0) -> float:
    """Calculate weighted score.

    Args:
        base: Base score value.
        multiplier: Weight multiplier. Defaults to 1.0.

    Returns:
        Weighted score.
    """
    return base * multiplier
```

### Code Organization

- One class per file (or related small classes)
- Keep files under 500 lines when possible
- Use meaningful variable names
- Add comments for complex logic only

### Imports

```python
# Standard library
import os
import json
from typing import Dict, List

# Third party
import numpy as np
from fastapi import FastAPI

# Local
from src.middleware.auth import get_current_user
```

---

## Documentation Standards

### README Files

Every component directory should have a README with:
- **Overview** — What this component does
- **Quick Start** — How to use it in 5 minutes
- **Architecture** — How it works (diagram if helpful)
- **API Reference** — Classes, functions, endpoints
- **Examples** — Working code examples
- **Testing** — How to run tests

### Docstrings

Use Google-style docstrings:

```python
class AuthService:
    """Handles authentication and token management.

    This service manages user authentication, token generation,
    and role-based access control.
    """

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password.

        Args:
            username: User's username.
            password: User's password (plaintext).

        Returns:
            User object if authentication succeeds, None otherwise.
        """
```

---

## Testing Guidelines

### Test Types

| Type | Location | Purpose |
|------|----------|---------|
| **Unit** | `tests/unit/` | Test individual functions/classes |
| **Integration** | `tests/integration/` | Test component interactions |
| **E2E** | `tests/e2e/` | Test full user workflows |
| **Performance** | `tests/performance/` | Benchmark critical paths |

### Writing Tests

- Test public APIs first
- Cover happy path and edge cases
- Use fixtures for common setup
- Mark slow tests: `@pytest.mark.slow`
- Mock external services (databases, APIs)

```python
class TestAuthService:
    @pytest.fixture
    def service(self):
        return AuthService()

    def test_authenticate_success(self, service):
        user = service.authenticate("admin", "password")
        assert user is not None
        assert user.username == "admin"

    def test_authenticate_invalid_password(self, service):
        user = service.authenticate("admin", "wrong")
        assert user is None
```

---

## Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
```

**Types:**
- `feat` — New feature
- `fix` — Bug fix
- `docs` — Documentation only
- `style` — Code style (formatting, no logic change)
- `refactor` — Code refactor
- `test` — Adding or updating tests
- `chore` — Maintenance tasks

**Examples:**
```
feat(auth): add API key generation
fix(ml): resolve training data shape mismatch
docs(src): add middleware README
test(agents): add orchestrator unit tests
refactor(governance): simplify charter validation
chore(deps): update pytest to 7.4
```

---

## Component Ownership

| Component | Primary Language | Key Files |
|-----------|-----------------|-----------|
| **src/** | Python | FastAPI application |
| **lrs_agents/** | Python | Active inference framework |
| **neuralblitz-v50/** | Python, Go, Rust | Cognitive engine |
| **neuralblitz-dashboard/** | JavaScript/React | Web dashboard |
| **neuralblitz-mobile/** | TypeScript/React Native | Mobile app |
| **vs-code/** | TypeScript | VS Code extension |

When contributing to a component, check its README for specific guidelines.

---

## Review Process

1. **Automated checks** — CI must pass (tests, linting, types)
2. **Code review** — At least one maintainer approves
3. **Documentation review** — Changes documented appropriately
4. **Merge** — Squash merge with descriptive commit message

---

## Getting Help

- **GitHub Issues** — Bug reports, feature requests
- **GitHub Discussions** — Questions, ideas
- **Component READMEs** — Component-specific guidance
- **ARCHITECTURE.md** — System overview
- **DEVELOPMENT_SETUP.md** — Setup instructions

---

## License

By contributing, you agree that your contributions will be licensed under the project's license.
