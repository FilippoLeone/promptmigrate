# API Reference

## PromptManager

The core class that manages prompt loading, saving, and migrations.

```python
from promptmigrate.manager import PromptManager
```

### Constructor

```python
def __init__(self, prompt_file: Path | None = None, state_file: Path | None = None):
    ...
```

Parameters:
- `prompt_file`: Optional path to the prompts YAML file (defaults to `Path("prompts.yaml")`)
- `state_file`: Optional path to the state JSON file (defaults to `Path(".promptmigrate_state.json")`)

### Methods

#### reload

```python
def reload(self) -> "PromptManager":
    """Reload prompts.yaml into the attribute cache and return self."""
```

#### load_prompts

```python
def load_prompts(self) -> dict[str, str]:
    """Load all prompts as a dictionary."""
```

#### save_prompts

```python
def save_prompts(self, prompts: dict[str, str]) -> None:
    """Save prompts to the YAML file."""
```

#### current_rev

```python
def current_rev(self) -> str | None:
    """Get the current revision ID or None if no migrations applied."""
```

#### set_current_rev

```python
def set_current_rev(self, rev_id: str) -> None:
    """Set the current revision ID."""
```

#### upgrade

```python
def upgrade(self, target: str | None = None) -> None:
    """Apply pending migrations up to the target or all if target is None."""
```

#### list_migrations

```python
def list_migrations(self) -> list[PromptMigration]:
    """List all registered migrations, sorted by revision ID."""
```

#### process_dynamic_value

```python
def process_dynamic_value(self, prompt: str) -> str:
    """
    Process dynamic values in a prompt string.
    
    This method finds and processes all dynamic value placeholders in the format
    {{type:options}} and replaces them with their computed values.
    """
```

#### process_date_placeholder

```python
def process_date_placeholder(self, options_str: str) -> str:
    """
    Process a date placeholder with format option.
    
    Format: {{date:format=%Y-%m-%d}}
    Returns the current date/time formatted according to the format string.
    """
```

#### process_number_placeholder

```python
def process_number_placeholder(self, options_str: str) -> str:
    """
    Process a number placeholder with min/max options.
    
    Format: {{number:min=1,max=100}}
    Returns a random integer between min and max (inclusive).
    """
```

#### process_choice_placeholder

```python
def process_choice_placeholder(self, options_str: str) -> str:
    """
    Process a choice placeholder with comma-separated options.
    
    Format: {{choice:option1,option2,option3}}
    Returns a randomly selected option from the list.
    """
```

#### process_text_placeholder

```python
def process_text_placeholder(self, options_str: str) -> str:
    """
    Process a text placeholder with a template and variables.
    
    Format: {{text:template_string,var1=value1,var2=value2}}
    Returns the template with variables substituted.
    """
```

### Attribute and Dictionary Access

```python
# Attribute access
manager.PROMPT_NAME

# Dictionary access
manager["PROMPT_NAME"]

# Both lookups are case-insensitive
manager.prompt_name  # Works the same as manager.PROMPT_NAME
```

## prompt_revision Decorator

The decorator used to register migration functions.

```python
from promptmigrate.manager import prompt_revision

@prompt_revision("001_initial", "Initial migration")
def migrate(prompts):
    prompts["KEY"] = "Value"
    return prompts
```

Parameters:
- `rev_id`: The unique revision ID (string)
- `description`: A human-readable description of the migration

## PromptMigration Class

An internal class that represents a single migration.

```python
class PromptMigration:
    """Represents a single prompt migration."""

    def __init__(self, rev_id: str, description: str, func: callable):
        self.rev_id = rev_id
        self.description = description
        self.func = func
```

## CLI Interface

The Command-Line Interface for PromptMigrate.

### Commands

#### init

Initialize a new PromptMigrate project.

```bash
promptmigrate init
```

#### current

Show the current revision.

```bash
promptmigrate current
```

#### upgrade

Apply pending migrations.

```bash
# Apply all pending migrations
promptmigrate upgrade

# Apply migrations up to a specific target
promptmigrate upgrade --to 003_dynamic
```

#### list

List all available migrations and their status.

```bash
promptmigrate list
```

## Global Instance

For convenience, a global instance of `PromptManager` is provided:

```python
from promptmigrate import promptmanager as pm

# Use the global instance in your code
system_prompt = pm.SYSTEM
```

This is the recommended way to access prompts in your application code.

Represents a single migration operation.

```python
@dataclass(slots=True, frozen=True)
class PromptMigration:
    rev_id: str
    description: str
    created_at: datetime
    fn: Callable[[dict[str, str]], dict[str, str]]
    
    def apply(self, prompts: dict[str, str]) -> dict[str, str]:
        """Apply the migration function to the prompts dict."""
```

## Global promptmanager Instance

A pre-configured singleton instance of PromptManager is available for convenience:

```python
from promptmigrate import promptmanager as pm

# Access prompts
pm.SYSTEM
```

## CLI Commands

### init

```bash
promptmigrate init [--package PKG]
```

Initialize a new revisions package.

### upgrade

```bash
promptmigrate upgrade [--to TARGET] [--package PKG]
```

Apply pending migrations.

### current

```bash
promptmigrate current
```

Show the current revision ID.

### list

```bash
promptmigrate list
```

List all available migrations and their status (applied/pending).

## Dynamic Value Placeholders

PromptMigrate supports dynamic value placeholders that can be used in your prompts. These placeholders are processed at runtime when accessing prompts.

### Format

Dynamic values use the following format:

```
{{type:options}}
```

Where:
- `type`: The type of dynamic content (date, number, choice, text)
- `options`: Configuration for the dynamic content, specific to each type

### Available Types

#### Date

```
{{date:format=%Y-%m-%d}}
```

Options:
- `format`: A strftime format string (default: "%Y-%m-%d")

Example:
```
Today is {{date:format=%B %d, %Y}}.
```

#### Number

```
{{number:min=1,max=100}}
```

Options:
- `min`: Minimum value (default: 0)
- `max`: Maximum value (default: 100)

Example:
```
Your lucky number today is {{number:min=1,max=10}}.
```

#### Choice

```
{{choice:option1,option2,option3}}
```

Options:
- A comma-separated list of options to choose from

Example:
```
I suggest trying {{choice:yoga,meditation,running}} today.
```

#### Text

```
{{text:Hello {name}!,name=World}}
```

Options:
- First part is the template with {variables}
- Remaining parts are variable assignments in format key=value

Example:
```
{{text:Welcome to {city}, {name}!,city=New York,name=traveler}}
```
