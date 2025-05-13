# PromptMigrate

> Schema-like migration manager for LLM prompt collections

[![PyPI version](https://img.shields.io/pypi/v/promptmigrate.svg)](https://pypi.org/project/promptmigrate/)
[![Python Versions](https://img.shields.io/pypi/pyversions/promptmigrate.svg)](https://pypi.org/project/promptmigrate/)
[![Test](https://github.com/promptmigrate/promptmigrate/actions/workflows/python-ci.yml/badge.svg)](https://github.com/promptmigrate/promptmigrate/actions/workflows/python-ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

PromptMigrate is a production-ready tool for managing LLM prompt collections with a migration system similar to database migrations. It allows developers to version, track, and evolve their prompts over time while maintaining backward compatibility.

As LLM-powered applications mature, prompt engineering becomes increasingly important. PromptMigrate provides a structured way to manage prompt changes, track versions, and ensure consistency across your application.

## Key Features

- **Schema-based Migration System**: 
  Track and version prompt changes over time, just like database migrations

- **CLI Interface**:
  Manage migrations from the command line with intuitive commands

- **Ergonomic Access**:
  Reference prompts as attributes or dictionary keys for cleaner code

- **Case-insensitive Lookup**:
  Flexible access patterns for improved developer experience

- **Dynamic Values**:
  Support for runtime variables like dates, random numbers, and text templates

- **Python Integration**:
  Seamlessly integrate with your Python applications

## Installation

```bash
pip install promptmigrate
```

## Quick Example

Define your prompt migrations:

```python
# promptmigrate_revisions/rev_001_initial.py
from promptmigrate.manager import prompt_revision

@prompt_revision("001_initial", "Initial prompts")
def migrate(prompts):
    prompts["SYSTEM"] = "You are a helpful assistant."
    prompts["GREETING"] = "{{choice:Hello,Hi,Hey}}! How can I help you today?"
    prompts["DATE_AWARE"] = "Today is {{date:format=%B %d, %Y}}."
    return prompts
```

Apply migrations:

```bash
promptmigrate upgrade
```

Use in your application:

```python
from promptmigrate import promptmanager as pm

response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": pm.SYSTEM},
        {"role": "assistant", "content": pm.GREETING},
        {"role": "user", "content": "Tell me about PromptMigrate"}
    ]
)
```

## Why PromptMigrate?

As LLM applications evolve:

1. **Prompts Change**: Evolution of prompts is a standard part of LLM app development
2. **Version Control**: Tracking changes helps understand application behavior
3. **Collaboration**: Teams need a structured way to manage prompt engineering
4. **Testing**: Versioned prompts enable better testing and validation

PromptMigrate solves these challenges with a familiar migration-based approach.

## Documentation

- [Getting Started](usage.md)
- [API Reference](api.md)
- [Working with Migrations](migrations.md)
- [Dynamic Values](dynamic_values.md)