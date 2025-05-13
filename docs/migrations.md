# Migration Guide

This guide explains best practices for creating and managing prompt migrations.

## Migration Naming

Use a consistent naming pattern for your revision IDs:

```
XXX_descriptive_name
```

Where `XXX` is a numeric prefix that ensures migrations are applied in the correct order.

Examples:
- `001_initial_system`
- `002_add_weather_questions`
- `010_refactor_system_prompt`

## Writing Migration Functions

Migrations should be pure functions that take a prompts dictionary and return a modified dictionary:

```python
@prompt_revision("001_initial", "Add system prompt")
def migrate(prompts):
    # Add new prompts
    prompts["SYSTEM"] = "You are a helpful assistant."

    # Or modify existing ones (if you know they exist)
    if "USER_GREETING" in prompts:
        prompts["USER_GREETING"] = "Updated greeting"

    return prompts
```

## Migration Best Practices

### 1. Make Migrations Idempotent

Migrations should be safe to run multiple times:

```python
@prompt_revision("002_fix_typo", "Fix typo in system prompt")
def fix_typo(prompts):
    if "SYSTEM" in prompts and "assisstant" in prompts["SYSTEM"]:
        prompts["SYSTEM"] = prompts["SYSTEM"].replace("assisstant", "assistant")
    return prompts
```

### 2. Keep Migrations Small and Focused

Each migration should do one logical change:

```python
# Good: Focused on one type of prompt
@prompt_revision("003_add_weather", "Add weather prompts")
def add_weather(prompts):
    prompts["WEATHER_QUESTION"] = "What's the weather like today?"
    prompts["WEATHER_FOLLOW_UP"] = "Would you like a detailed forecast?"
    return prompts

# Instead of combining unrelated changes
```

### 3. Document Your Changes

Add clear descriptions to your migrations:

```python
@prompt_revision(
    "004_format_change",
    "Changed format of response prompts to include variable placeholders"
)
def update_format(prompts):
    # Implementation
    return prompts
```

### 4. Testing Migrations

Test your migrations to ensure they work as expected:

```python
# test_migrations.py
from promptmigrate.manager import PromptManager, prompt_revision

def test_migration():
    # Create a test migration
    @prompt_revision("test_001", "Test migration")
    def test_migrate(prompts):
        prompts["TEST"] = "Test value"
        return prompts

    # Apply it to an empty prompts dict
    manager = PromptManager(prompt_file=Path("test_prompts.yaml"))
    manager.upgrade()

    # Verify it worked
    assert manager.TEST == "Test value"
```

## Organizing Migrations

### Option 1: Chronological Files

```
promptmigrate_revisions/
  ├── __init__.py
  ├── rev_001_initial.py
  ├── rev_002_add_weather.py
  └── rev_003_refactor.py
```

### Option 2: Module-Based Organization

```
myapp/
  ├── __init__.py
  └── prompts/
      ├── __init__.py
      └── revisions/
          ├── __init__.py
          ├── core.py  # Core prompts
          ├── weather.py  # Weather-related prompts
          └── user.py  # User interaction prompts
```

With module loading in your application:

```python
# Load all revision modules
import importlib
import pkgutil

pkg = "myapp.prompts.revisions"
pkg_mod = importlib.import_module(pkg)

for _, name, _ in pkgutil.walk_packages(pkg_mod.__path__, f"{pkg_mod.__name__}."):
    importlib.import_module(name)
```

## Advanced Migration Patterns

### 1. Conditional Migrations

Apply changes only if certain conditions are met:

```python
@prompt_revision("005_conditional", "Update prompts based on condition")
def conditional(prompts):
    # Only update if we have the old format
    if "SYSTEM" in prompts and not prompts["SYSTEM"].startswith("You are"):
        prompts["SYSTEM"] = "You are " + prompts["SYSTEM"]
    return prompts
```

### 2. Renaming Prompts

When renaming prompts, create a migration that handles both keys:

```python
@prompt_revision("006_rename", "Rename GREETING to WELCOME")
def rename_greeting(prompts):
    if "GREETING" in prompts:
        prompts["WELCOME"] = prompts["GREETING"]
        del prompts["GREETING"]
    return prompts
```

### 3. Marking Prompts as Deprecated

Instead of removing prompts, mark them as deprecated:

```python
@prompt_revision("007_deprecate", "Mark old prompts as deprecated")
def deprecate_prompts(prompts):
    if "OLD_PROMPT" in prompts:
        prompts["OLD_PROMPT_DEPRECATED"] = prompts["OLD_PROMPT"]
        prompts["OLD_PROMPT"] = "[DEPRECATED] Please use NEW_PROMPT instead. " + prompts["OLD_PROMPT"]
    return prompts
```

## Auto-Generated Migrations

PromptMigrate supports automatically creating migrations from manual changes to your `prompts.yaml` file.

### Using the Auto-Revision Command

```bash
# Detect changes and create a revision
promptmigrate auto-revision
```

The system will automatically:
1. Compare the current prompts.yaml with the state after the last applied migration
2. Identify added, modified, and removed prompts
3. Generate a new migration file with appropriate code
4. Register the migration so it can be applied with `promptmigrate upgrade`

### Example Auto-Generated Migration

Here's an example of what an auto-generated migration might look like:

```python
"""Auto-generated migration from manual changes to prompts.yaml on 2025-05-13 14:22:45."""

from promptmigrate.manager import prompt_revision


@prompt_revision("005_auto_changes", "Auto-generated from manual changes to prompts.yaml")
def migrate(prompts):
    """Apply changes made directly to prompts.yaml."""
    # Add new prompts
    prompts["NEW_PROMPT"] = "This is a new prompt added manually"

    # Update modified prompts
    prompts["SYSTEM"] = "Updated system prompt with better instructions"

    # Remove deleted prompts
    if "OLD_PROMPT" in prompts:
        del prompts["OLD_PROMPT"]

    return prompts
```

### Best Practices for Auto-Revision

1. **Review Before Upgrading**: Always review auto-generated migrations before applying them
2. **Update Descriptions**: Consider editing the auto-generated description to be more specific
3. **Combine with Manual Edits**: You can modify auto-generated migrations to improve them
4. **Add Tests**: Consider adding tests for important prompt changes
