# Contributing to PromptMigrate

We love your input! We want to make contributing to PromptMigrate as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Pull Requests

1. Update the README.md and documentation with details of changes if applicable
2. Update the tests to reflect your changes
3. The PR should work for Python 3.9 and above
4. Ensure all tests pass before submitting

## Development Setup

```bash
# Clone your fork
git clone https://github.com/FilippoLeone/promptmigrate.git
cd promptmigrate

# Install development dependencies
pip install -e ".[test]"

# Run tests
pytest
```

## Testing

We use pytest for testing. All tests should be in the `tests/` directory:

```bash
# Run all tests
pytest

# Run with coverage
coverage run -m pytest
coverage report

# Run specific test file
pytest tests/test_manager.py
```

## Coding Style

We follow the PEP 8 style guide for Python. Please ensure your code follows this standard.

```bash
# Install linting tools
pip install flake8 black isort

# Run linters
flake8 src tests
black src tests
isort src tests
```

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

## References

This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/master/CONTRIBUTING.md).
