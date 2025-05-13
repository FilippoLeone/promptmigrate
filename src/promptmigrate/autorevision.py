"""Auto-generate revisions from changes to prompts.yaml."""

from __future__ import annotations

import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

from .manager import PROMPT_FILE, PromptManager


def detect_changes() -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
    """
    Detect changes between current prompts.yaml and the state after last migration.

    Returns:
        Tuple containing (added, modified, removed) prompts
    """
    manager = PromptManager()

    # Load the current prompts from file
    current_prompts = {}
    if PROMPT_FILE.exists():
        with open(PROMPT_FILE, "r") as f:
            current_yaml_content = f.read()
            current_prompts = yaml.safe_load(current_yaml_content) or {}

    # Get the last migrated state by applying all migrations
    # We need to create a temporary copy of the prompts file to avoid overwriting
    # the current prompts that may include manual changes
    temp_file = Path(f"temp_prompts_{int(time.time())}.yaml")
    temp_state = Path(f"temp_state_{int(time.time())}.json")

    try:
        # Create a temporary manager that doesn't affect the real files
        temp_manager = PromptManager(prompt_file=temp_file, state_file=temp_state)

        # Apply all existing migrations to get what should be the current state
        temp_manager.upgrade()

        # Get the prompts after all migrations applied
        migrated_prompts = temp_manager.load_prompts()

        # Find differences
        added_prompts = {}
        modified_prompts = {}
        removed_prompts = {}

        # Find added and modified prompts
        for key, value in current_prompts.items():
            if key not in migrated_prompts:
                added_prompts[key] = value
            elif migrated_prompts[key] != value:
                modified_prompts[key] = value

        # Find removed prompts
        for key in migrated_prompts:
            if key not in current_prompts:
                removed_prompts[key] = migrated_prompts[key]

        return added_prompts, modified_prompts, removed_prompts

    finally:
        # Clean up temporary files
        if temp_file.exists():
            temp_file.unlink()
        if temp_state.exists():
            temp_state.unlink()


def create_revision_from_changes(
    rev_id: str = None, description: str = "Auto-generated from manual changes"
) -> str:
    """
    Create a new revision file based on detected changes to prompts.yaml.

    Args:
        rev_id: Optional revision ID. If not provided, one will be auto-generated.
        description: Description of the revision.

    Returns:
        Path to the created revision file.
    """
    added_prompts, modified_prompts, removed_prompts = detect_changes()

    # Only proceed if there are actual changes
    if not (added_prompts or modified_prompts or removed_prompts):
        return None

    # Generate a revision ID if not provided
    if not rev_id:
        # Find the latest revision ID and increment it
        manager = PromptManager()
        migrations = manager.list_migrations()

        if migrations:
            # Extract the numeric part of the latest revision ID
            latest_id = migrations[-1].rev_id
            match = re.match(r"(\d+)_", latest_id)
            if match:
                next_num = int(match.group(1)) + 1
                rev_id = f"{next_num:03d}_auto_changes"
            else:
                rev_id = "001_auto_changes"
        else:
            rev_id = "001_auto_changes"

    # Create the revision file content
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"rev_{rev_id}.py"

    # Generate the migration code
    migration_code = f'''"""Auto-generated migration from manual changes to prompts.yaml on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}."""

from promptmigrate.manager import prompt_revision


@prompt_revision("{rev_id}", "{description}")
def migrate(prompts):
    """Apply changes made directly to prompts.yaml."""
'''

    # Add code for added prompts
    if added_prompts:
        migration_code += f"    # Add new prompts\n"
        for key, value in added_prompts.items():
            # Properly escape quotes in the value
            escaped_value = str(value).replace('"', '\\"')
            migration_code += f'    prompts["{key}"] = "{escaped_value}"\n'

    # Add code for modified prompts
    if modified_prompts:
        migration_code += f"\n    # Update modified prompts\n"
        for key, value in modified_prompts.items():
            # Properly escape quotes in the value
            escaped_value = str(value).replace('"', '\\"')
            migration_code += f'    prompts["{key}"] = "{escaped_value}"\n'

    # Add code for removed prompts
    if removed_prompts:
        migration_code += f"\n    # Remove deleted prompts\n"
        for key in removed_prompts:
            migration_code += f'    if "{key}" in prompts:\n'
            migration_code += f'        del prompts["{key}"]\n'

    migration_code += "\n    return prompts\n"

    # Write the file to the revisions package
    package_path = Path("promptmigrate_revisions")
    if not package_path.exists():
        package_path.mkdir(parents=True)
        (package_path / "__init__.py").touch()

    file_path = package_path / file_name
    with open(file_path, "w") as f:
        f.write(migration_code)

    return str(file_path)
