"""Auto-generated migration from manual changes to prompts.yaml on 2025-05-13 14:55:02."""

from promptmigrate.manager import prompt_revision


@prompt_revision("004_auto_changes", "Update system prompt and add new prompt")
def migrate(prompts):
    """Apply changes made directly to prompts.yaml."""
    # Add new prompts
    prompts["NEW_PROMPT"] = "This is a brand new prompt"

    # Update modified prompts
    prompts["SYSTEM"] = "You are a very helpful AI assistant, updated."

    # Remove deleted prompts
    if "AUTO_TEST_PROMPT" in prompts:
        del prompts["AUTO_TEST_PROMPT"]

    return prompts
