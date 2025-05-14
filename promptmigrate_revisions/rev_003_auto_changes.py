"""Auto-generated migration from manual changes to prompts.yaml on 2025-05-13 17:49:48."""

from promptmigrate.manager import prompt_revision


@prompt_revision("003_auto_changes", "Auto-generated from manual changes to prompts.yaml")
def migrate(prompts):
    """Apply changes made directly to prompts.yaml."""

    # Update modified prompts
    prompts["SYSTEM"] = "Initial system prompt"

    return prompts
