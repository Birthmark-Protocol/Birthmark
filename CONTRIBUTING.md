# Contributing to Birthmark Protocol

Thank you for your interest in contributing to Birthmark Protocol! We're building open authentication infrastructure for digital media to combat the deepfake crisis, and we welcome contributions from developers, security researchers, photographers, and anyone passionate about media authenticity.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Submitting Contributions](#submitting-contributions)
- [Coding Standards](#coding-standards)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project adheres to the Contributor Covenant [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [samryan.pdx@proton.me](mailto:samryan.pdx@proton.me).

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, screenshots, etc.)
- **Describe the behavior you observed and what you expected**
- **Include your environment details** (OS, Python version, dependencies)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description of the proposed functionality**
- **Explain why this enhancement would be useful**
- **List any potential drawbacks or considerations**

### Areas Where We Need Help

**Technical Development:**
- Camera app prototype (Python/mobile integration)
- Blockchain integration (zkRollup, smart contracts)
- Cryptographic implementation (secure element simulation, hashing)
- Verification client (hash checking tool)
- Server infrastructure (load balancing, API design)
- Testing and security auditing

**Documentation:**
- Technical specification writing
- Architecture documentation
- Tutorial creation
- API documentation
- Use case examples

**Domain Expertise:**
- Photojournalism workflows
- Legal evidence requirements
- Security and cryptography review
- Privacy considerations
- UX design for authentication

**Community Building:**
- Answering questions in issues/discussions
- Writing blog posts about authentication challenges
- Presenting at conferences
- Building partnerships

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of cryptography concepts (helpful but not required)
- Familiarity with blockchain concepts (helpful but not required)

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/birthmark.git
   cd birthmark
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/birthmark-protocol/birthmark.git
   ```

4. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

6. **Run tests to verify setup:**
   ```bash
   pytest
   ```

## Development Process

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates

### Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Write tests** for new functionality

4. **Run tests locally:**
   ```bash
   pytest
   ```

5. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```
   
   Follow [conventional commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Adding or updating tests
   - `refactor:` Code refactoring
   - `chore:` Maintenance tasks

6. **Keep your branch updated:**
   ```bash
   git fetch upstream
   git rebase upstream/develop
   ```

7. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Submitting Contributions

### Pull Request Process

1. **Open a Pull Request** against the `develop` branch (not `main`)

2. **Fill out the PR template** with:
   - Description of changes
   - Related issue numbers (#123)
   - Testing performed
   - Breaking changes (if any)

3. **Ensure all checks pass:**
   - Tests pass
   - Code style compliant
   - Documentation updated

4. **Request review** from maintainers

5. **Address feedback** through additional commits

6. **Squash commits** if requested before merge

### What Happens Next?

- Maintainers will review your PR within 7 days
- You may be asked to make changes
- Once approved, your PR will be merged
- Your contribution will be acknowledged in release notes

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length:** 100 characters (not 79)
- **Imports:** Organized (standard library, third-party, local)
- **Type hints:** Encouraged for function signatures
- **Docstrings:** Required for public functions (Google style)

### Code Formatting

We use automated formatting tools:

```bash
# Format code with black
black src/

# Sort imports with isort
isort src/

# Check with flake8
flake8 src/
```

### Example Code Style

```python
from typing import Optional, Tuple
import hashlib
from datetime import datetime


def compute_image_hash(
    image_data: bytes,
    algorithm: str = "sha256"
) -> Tuple[str, datetime]:
    """
    Compute cryptographic hash of image data.
    
    Args:
        image_data: Raw image bytes
        algorithm: Hash algorithm to use (default: sha256)
        
    Returns:
        Tuple of (hash_string, timestamp)
        
    Raises:
        ValueError: If algorithm is not supported
    """
    if algorithm not in hashlib.algorithms_available:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    hasher = hashlib.new(algorithm)
    hasher.update(image_data)
    
    return hasher.hexdigest(), datetime.utcnow()
```

### Testing Standards

- **Write tests** for all new functionality
- **Aim for >80% code coverage**
- **Use pytest** for test framework
- **Name tests clearly:** `test_function_name_expected_behavior`

```python
def test_compute_image_hash_returns_valid_sha256():
    """Test that hash computation returns valid SHA256."""
    test_data = b"test image data"
    hash_value, timestamp = compute_image_hash(test_data)
    
    assert len(hash_value) == 64  # SHA256 is 64 hex characters
    assert isinstance(timestamp, datetime)
```

## Documentation

### Code Documentation

- **Docstrings required** for all public functions, classes, and modules
- **Use Google style** docstrings
- **Include examples** for complex functions
- **Document exceptions** that can be raised

### Project Documentation

- Update `README.md` for user-facing changes
- Update `/docs` for technical specifications
- Add examples to `/examples` for new features
- Update `CHANGELOG.md` for notable changes

### Writing Style

- **Be clear and concise**
- **Use active voice**
- **Include code examples**
- **Explain the "why" not just the "what"**

## Community

### Communication Channels

- **GitHub Issues:** Bug reports, feature requests, technical discussions
- **GitHub Discussions:** General questions, ideas, community chat
- **Email:** [samryan.pdx@proton.me](mailto:samryan.pdx@proton.me) for sensitive matters

### Getting Help

- **Check existing issues and documentation** first
- **Ask questions in GitHub Discussions**
- **Tag issues with "question" or "help wanted"**
- **Be patient and respectful** - maintainers are volunteers

### Recognition

We value all contributions! Contributors will be:

- Listed in `CONTRIBUTORS.md`
- Acknowledged in release notes
- Given credit in related publications/presentations
- Invited to join the advisory board (for significant contributions)

## License

By contributing to Birthmark Protocol, you agree that your contributions will be licensed under the Apache License 2.0. This ensures your work remains open and freely usable while protecting against patent trolling.

## Questions?

Don't hesitate to reach out if you have questions about contributing. We're here to help!

- Open a [GitHub Discussion](../../discussions)
- Email the project lead: [samryan.pdx@proton.me](mailto:samryan.pdx@proton.me)
- Check our [documentation](/docs)

---

**Thank you for contributing to Birthmark Protocol! Together we're building authentication infrastructure that will help preserve trust in digital media.**
