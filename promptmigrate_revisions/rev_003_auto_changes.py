"""Auto-generated migration from manual changes to prompts.yaml on 2025-05-13 14:54:01."""

from promptmigrate.manager import prompt_revision


@prompt_revision("003_auto_changes", "Add initial prompts")
def migrate(prompts):
    """Apply changes made directly to prompts.yaml."""
    # Add new prompts
    prompts["ANTHROPIC_SYSTEM"] = (
        "You are Claude, an AI assistant by Anthropic. {{date:format=Current date: %Y-%m-%d.}}"
    )
    prompts["AUTO_TEST_PROMPT"] = "This is a test prompt added at 14:53:17"
    prompts["DATE_GREETING"] = "Today is {{date:format=%B %d, %Y}}. How can I help you?"
    prompts["GEMINI_SYSTEM"] = (
        "You are Gemini, a large language model by Google. {{date:format=Today's date is %d %B %Y.}}"
    )
    prompts["LUCKY_NUMBER"] = "Your lucky number today is {{number:min=1,max=100}}."
    prompts["MOOD_SUGGESTION"] = (
        "I notice you're feeling down. Have you tried {{choice:meditation,deep breathing,going for a walk,listening to music}} today?"
    )
    prompts["NEW_TEST_PROMPT"] = "This is a new test prompt for auto-revision"
    prompts["OPENAI_SYSTEM"] = (
        "You are an AI assistant built by OpenAI. {{date:format=Today is %B %d, %Y.}}"
    )
    prompts["PERSONALIZED_GREETING"] = (
        "{{text:Hello {name}! Welcome to {service}.,name=valued customer,service=our AI assistant}}"
    )
    prompts["SYSTEM"] = "You are a helpful assistant."
    prompts["WEATHER_FOLLOW_UP"] = "Would you like to know the forecast for tomorrow as well?"
    prompts["WEATHER_QUESTION"] = "What's the weather like today?"

    return prompts
