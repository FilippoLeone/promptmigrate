# PromptMigrate

Schema-like migration manager for LLM prompt collections.

[![PyPI version](https://img.shields.io/pypi/v/promptmigrate.svg)](https://pypi.org/project/promptmigrate/)
[![Python Versions](https://img.shields.io/pypi/pyversions/promptmigrate.svg)](https://pypi.org/project/promptmigrate/)
[![Test](https://github.com/FilippoLeone/promptmigrate/actions/workflows/python-ci.yml/badge.svg)](https://github.com/FilippoLeone/promptmigrate/actions/workflows/python-ci.yml)
[![Documentation Status](https://img.shields.io/badge/docs-latest-blue.svg)](https://filippoleone.github.io/promptmigrate/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

PromptMigrate is a production-ready tool for managing LLM prompt collections with a migration system similar to database migrations. It allows developers to version, track, and evolve their prompts over time while maintaining backward compatibility.

As LLM-powered applications mature, prompt engineering becomes increasingly important. PromptMigrate provides a structured way to manage prompt changes, track versions, and ensure consistency across your application.

## Features

- **Schema-based Migration System**: Track and version prompt changes over time
- **CLI Interface**: Manage migrations from the command line
- **Ergonomic Access**: Reference prompts as attributes or dictionary keys
- **Case-insensitive Lookup**: Flexible access patterns for improved developer experience
- **Dynamic Values**: Support for runtime variables like dates, random numbers, and text templates
- **Python Integration**: Seamlessly integrate with your Python applications

## Installation

```bash
pip install promptmigrate
```

For development:

```bash
# Clone the repository
git clone https://github.com/promptmigrate/promptmigrate.git
cd promptmigrate

# Install in development mode with test dependencies
pip install -e ".[test]"
```

## Quick Start

### 1. Initialize a New Project

```bash
promptmigrate init
```

This creates a `promptmigrate_revisions` package where you can store your migrations.

### 2. Create Migrations

Create Python files in the revisions package:

```python
# promptmigrate_revisions/rev_001_initial.py
from promptmigrate.manager import prompt_revision

@prompt_revision("001_initial", "seed system prompt")
def migrate(prompts):
    prompts["SYSTEM"] = "You are a helpful assistant."
    return prompts
```

### 3. Apply Migrations

```bash
promptmigrate upgrade
```

This applies all pending migrations and creates/updates your `prompts.yaml` file.

### 4. Access Prompts in Your Code

```python
from promptmigrate import promptmanager as pm

# Attribute-style access (preferred)
system_prompt = pm.SYSTEM

# Or dictionary-style access
system_prompt = pm["SYSTEM"]

# Use in your LLM calls
response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": pm.SYSTEM},
        {"role": "user", "content": "Tell me about PromptMigrate"}
    ]
)
```

## Dynamic Values

PromptMigrate supports dynamic value placeholders that get processed at runtime:

```python
# In your migration
@prompt_revision("003_dynamic", "add dynamic prompts")
def migrate(prompts):
    # Current date with custom format
    prompts["DATE_GREETING"] = "Today is {{date:format=%B %d, %Y}}."

    # Random number between 1-10
    prompts["LUCKY_NUMBER"] = "Your lucky number is {{number:min=1,max=10}}."

    # Random choice from options
    prompts["SUGGESTION"] = "Try {{choice:yoga,meditation,running}} today."

    # Text template with variables
    prompts["WELCOME"] = "{{text:Hello {name}!,name=friend}}"

    return prompts
```

Each time you access a prompt with dynamic values, they are processed:

```python
# Each access generates fresh values
print(pm.DATE_GREETING)  # "Today is May 13, 2025."
print(pm.LUCKY_NUMBER)   # "Your lucky number is 7." (random each time)
print(pm.SUGGESTION)     # "Try meditation today." (random choice each time)
print(pm.WELCOME)        # "Hello friend!"

# You can even override text template values at runtime
welcome = pm.WELCOME.replace("friend", "valued customer")
print(welcome)  # "Hello valued customer!"
```

## Migration Commands

### Check Current Revision

```bash
promptmigrate current
```

### List All Migrations

```bash
promptmigrate list
```

### Upgrade to a Specific Version

```bash
promptmigrate upgrade --to 002_add_weather_q
```

### Use Custom Revisions Package

```bash
promptmigrate --revisions-package my_custom_package upgrade
```

## Integration with LLM Providers

PromptMigrate works with any LLM provider:

```python
# OpenAI
openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": pm.OPENAI_SYSTEM},
        {"role": "user", "content": pm.WEATHER_QUESTION}
    ]
)

# Anthropic
anthropic.messages.create(
    model="claude-3-opus-20240229",
    system=pm.ANTHROPIC_SYSTEM,
    messages=[
        {"role": "user", "content": pm.WEATHER_QUESTION}
    ]
)

# Google Gemini
genai.GenerativeModel('gemini-pro').generate_content(
    pm.WEATHER_QUESTION,
    system_instruction=pm.GEMINI_SYSTEM
)
```

```bash
promptmigrate upgrade --package my_app.prompt_revisions
```

## Why PromptMigrate?

### The Problem

As LLM applications evolve:

1. **Prompt Collections Grow**: More system prompts, user prompts, and specialized instructions
2. **Prompts Change Over Time**: Refinements and optimizations require updates
3. **Collaboration Challenges**: Teams need a structured approach for prompt engineering
4. **Version Traceability**: Understanding what version of a prompt is deployed
5. **Testing Difficulties**: No clear way to test prompt changes

### The Solution

PromptMigrate addresses these challenges by:

- Providing a familiar migration-based approach to prompt management
- Ensuring all prompt changes are versioned and tracked
- Enabling collaboration through a structured file-based system
- Supporting multiple environments (development, staging, production)
- Allowing easy rollback to previous prompt versions
- Facilitating integration with CI/CD pipelines

## Production Use

PromptMigrate v0.3.0 is production-ready and includes all the features needed for managing prompts in production environments:

- Comprehensive documentation and examples
- Full test coverage
- Efficient dynamic value processing
- Support for all major LLM providers
- Clear migration paths and version control

### Production Deployment Steps

1. Install the package: `pip install promptmigrate`
2. Initialize the project: `promptmigrate init`
3. Create your migrations following best practices in the documentation
4. Apply migrations with `promptmigrate upgrade`
5. Use the prompts in your application code
6. Track prompt versions alongside your application code in source control

## Advanced Usage

### Runtime Migrations

```python
from promptmigrate.manager import prompt_revision, PromptManager

@prompt_revision("003_custom", "Add a custom prompt")
def add_custom_prompt(prompts):
    prompts["CUSTOM"] = "This is a custom prompt added at runtime."
    return prompts

# Apply migrations
manager = PromptManager()
manager.upgrade()
```

### Attribute Access Benefits

The attribute-style access provides several benefits:

1. **IDE Autocomplete**: Your IDE can suggest available prompts
2. **Case Insensitivity**: `pm.SYSTEM` and `pm.system` work the same way
3. **Static Analysis**: Tools like mypy and pylint can check for typos

## Examples

See the `examples/` directory for complete working examples:

- `basic_usage.py`: Simple example showing attribute access
- `custom_migration.py`: How to create and apply custom migrations
- `weather_app.py`: A more complete application example

## Testing

Run the test suite with pytest:

```bash
pytest
```

Or with coverage:

```bash
coverage run -m pytest
coverage report
```

## License

MIT

## Contributing

Contributions are welcome! Please see our [Contributing Guide](./CONTRIBUTING.md) for more details.

## Documentation

For more details, check out our [comprehensive documentation](https://filippoleone.github.io/promptmigrate/):

- [Getting Started Guide](https://filippoleone.github.io/promptmigrate/usage)
- [API Reference](https://filippoleone.github.io/promptmigrate/api)
- [Working with Migrations](https://filippoleone.github.io/promptmigrate/migrations)
- [Dynamic Values](https://filippoleone.github.io/promptmigrate/dynamic_values)

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
