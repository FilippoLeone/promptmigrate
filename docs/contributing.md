# Contributing

Thank you for your interest in contributing to PromptMigrate!

This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please read and follow our [Code of Conduct](https://github.com/promptmigrate/promptmigrate/blob/main/CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

If you find a bug, please report it by creating a new issue on our [GitHub repository](https://github.com/promptmigrate/promptmigrate/issues).

When reporting a bug, please include:

- A clear, descriptive title
- A detailed description of the issue
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Your environment information (Python version, OS, etc.)
- Any relevant logs or error messages

### Suggesting Enhancements

We welcome suggestions for enhancements! Please create a new issue on our [GitHub repository](https://github.com/promptmigrate/promptmigrate/issues) with the "enhancement" label.

When suggesting an enhancement, please include:

- A clear, descriptive title
- A detailed description of the proposed enhancement
- Any relevant examples or use cases
- If applicable, potential implementation approaches

### Pull Requests

We welcome pull requests for bug fixes, enhancements, or documentation improvements.

To submit a pull request:

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes
4. Run tests to ensure your changes don't break existing functionality
5. Submit a pull request to the `main` branch

#### Pull Request Guidelines

- Follow the existing code style
- Include tests for new functionality
- Update documentation as needed
- Keep pull requests focused on a single concern
- Write clear, descriptive commit messages

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/promptmigrate/promptmigrate.git
cd promptmigrate

# Install in development mode with test dependencies
pip install -e ".[test,dev]"
```

### Running Tests

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=promptmigrate
```

### Building Documentation

```bash
pip install -e ".[docs]"
mkdocs serve
```

Then visit http://localhost:8000 to see the live documentation.

## Release Process

Releases are managed by the core maintainers. The process includes:

1. Updating the version in `pyproject.toml`
2. Updating the `CHANGELOG.md`
3. Creating a new GitHub release with appropriate tags
4. Publishing to PyPI

## License

By contributing to PromptMigrate, you agree that your contributions will be licensed under the project's [MIT License](https://github.com/promptmigrate/promptmigrate/blob/main/LICENSE).
