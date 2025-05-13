"""Add weather-related prompts."""

from promptmigrate.manager import prompt_revision


@prompt_revision("002_add_weather_q", "add weather question prompt")
def migrate(prompts):
    """Add the weather question prompt."""
    prompts["WEATHER_QUESTION"] = "What's the weather like today?"
    return prompts
