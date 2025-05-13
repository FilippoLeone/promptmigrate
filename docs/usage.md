# Usage Guide

## Installation

Install from PyPI:

```bash
pip install promptmigrate
```

Or install from source:

```bash
git clone https://github.com/promptmigrate/promptmigrate.git
cd promptmigrate
pip install -e .
```

## Basic Concepts

PromptMigrate manages your LLM prompts using a migration system similar to database migrations. Key concepts:

1. **Prompts**: Stored in a YAML file (`prompts.yaml`)
2. **Migrations**: Python functions that transform prompts
3. **Revisions**: Uniquely identified migrations with an ID and description

## Getting Started

### Initialize Your Project

```bash
# Create the initial revisions package
promptmigrate init
```

This creates a `promptmigrate_revisions` package where you can store your migrations.

### Create Migrations

Create Python files in the revisions package:

```python
# promptmigrate_revisions/rev_001_initial.py
from promptmigrate.manager import prompt_revision

@prompt_revision("001_initial", "seed system prompt")
def migrate(prompts):
    prompts["SYSTEM"] = "You are a helpful assistant."
    return prompts
```

### Apply Migrations

```bash
promptmigrate upgrade
```

### Check Current Revision

```bash
promptmigrate current
```

### List Available Migrations

```bash
promptmigrate list
```

## Using Prompts in Your Code

### Basic Usage

```python
from promptmigrate import promptmanager as pm

# Use attribute access
system_prompt = pm.SYSTEM

# Or dictionary access
system_prompt = pm["SYSTEM"]
```

### With OpenAI

```python
import openai
from promptmigrate import promptmanager as pm

response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": pm.SYSTEM},
        {"role": "user", "content": "Hello, how are you?"}
    ]
)
```

### With Anthropic

```python
import anthropic
from promptmigrate import promptmanager as pm

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-3-opus-20240229",
    system=pm.SYSTEM,
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)
```

## Dynamic Values

PromptMigrate supports dynamic values that are processed at runtime when accessing prompts.

### Using Dynamic Values in Migrations

```python
from promptmigrate.manager import prompt_revision

@prompt_revision("003_dynamic", "Add prompts with dynamic values")
def add_dynamic_prompts(prompts):
    # Date values with formatted output
    prompts["DATE_PROMPT"] = "Today is {{date:format=%B %d, %Y}}."

    # Random number between specific ranges
    prompts["NUMBER_PROMPT"] = "Your lucky number is {{number:min=1,max=100}}."

    # Random selection from choices
    prompts["CHOICE_PROMPT"] = "Try {{choice:yoga,meditation,running,swimming}} today."

    # Text template with variables
    prompts["TEXT_PROMPT"] = "{{text:Hello {name}, welcome to {city}!,name=traveler,city=our platform}}"

    return prompts
```

### Available Dynamic Value Types

#### Date Values

```python
# Format the current date (uses standard strftime format)
"Today is {{date:format=%Y-%m-%d}}."  # Today is 2025-05-13.
"Current month: {{date:format=%B}}"  # Current month: May
```

#### Random Numbers

```python
# Generate random integers between min and max (inclusive)
"Roll the dice: {{number:min=1,max=6}}"
"Percentage: {{number:min=0,max=100}}%"
```

#### Random Choices

```python
# Randomly select one option from a comma-separated list
"Mood today: {{choice:happy,sad,excited,calm}}"
"Color: {{choice:red,green,blue,yellow,purple}}"
```

#### Text Templates

```python
# Format text with variables (first part is template, followed by key=value pairs)
"{{text:Hello {name}!,name=World}}"
"{{text:{greeting} {name}, welcome to {place}!,greeting=Hello,name=User,place=our app}}"
```

### Example Usage

```python
from promptmigrate import promptmanager as pm

# Access a prompt with dynamic values - it gets processed on each access
greeting = pm.TEXT_PROMPT  # "Hello traveler, welcome to our platform!"

# Each access to a prompt with random values may return different results
for _ in range(3):
    print(pm.NUMBER_PROMPT)  # Different random number each time
```

## Advanced Usage

### Custom Revisions Package

```bash
promptmigrate init --package myapp.prompts.revisions
promptmigrate upgrade --package myapp.prompts.revisions
```

### Auto-Create Revisions from Manual Changes

PromptMigrate can automatically create revisions from manual changes to your `prompts.yaml` file. This allows non-technical team members to edit prompts directly and have those changes properly tracked in your migration history.

#### Using the CLI

```bash
# Detect changes and create a revision
promptmigrate auto-revision

# Preview changes without creating a revision
promptmigrate auto-revision --dry-run

# Create with custom description
promptmigrate auto-revision --description "Updated marketing prompts"
```

#### Enabling Auto-Revision in Python

```python
from promptmigrate import enable_auto_revision

# Basic auto-revision
enable_auto_revision()

# With automatic file watching (detects changes in real-time)
enable_auto_revision(watch=True)
```

#### Programmatic Usage

```python
from promptmigrate.autorevision import detect_changes, create_revision_from_changes

# Detect what has changed
added, modified, removed = detect_changes()

# Create a revision based on those changes
revision_file = create_revision_from_changes(
    description="My custom revision from manual changes"
)
```

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

### Custom Prompt and State Files

```python
from pathlib import Path
from promptmigrate.manager import PromptManager

# Use custom file locations
manager = PromptManager(
    prompt_file=Path("/path/to/custom_prompts.yaml"),
    state_file=Path("/path/to/.custom_state.json")
)
```
