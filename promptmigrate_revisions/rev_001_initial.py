"""Initial migration to set up basic prompts."""

from promptmigrate.manager import prompt_revision


@prompt_revision("001_initial", "seed system prompt")
def migrate(prompts):
    """Add the system prompt."""
    prompts["SYSTEM"] = "You are a helpful assistant."
    return prompts
