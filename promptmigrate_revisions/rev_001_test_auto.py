"""Auto-generated migration from manual changes to prompts.yaml on 2025-05-13 15:10:59."""

from promptmigrate.manager import prompt_revision


@prompt_revision("001_test_auto", "Auto-generated from manual changes")
def migrate(prompts):
    """Apply changes made directly to prompts.yaml."""
    # Add new prompts
    prompts["SYSTEM"] = "You are a helpful assistant."
    prompts["OPENAI_SYSTEM"] = (
        "You are an AI assistant built by OpenAI. {{date:format=Today is %B %d, %Y.}}"
    )
    prompts["ANTHROPIC_SYSTEM"] = (
        "You are Claude, an AI assistant by Anthropic. {{date:format=Current date: %Y-%m-%d.}}"
    )
    prompts["GEMINI_SYSTEM"] = (
        "You are Gemini, a large language model by Google. {{date:format=Today's date is %d %B %Y.}}"
    )
    prompts["DATE_GREETING"] = "Today is {{date:format=%B %d, %Y}}. How can I help you?"
    prompts["WEATHER_QUESTION"] = "What's the weather like today?"
    prompts["WEATHER_FOLLOW_UP"] = "Would you like to know the forecast for tomorrow as well?"
    prompts["PERSONALIZED_GREETING"] = (
        "{{text:Hello {name}! Welcome to {service}.,name=valued customer,service=our AI assistant}}"
    )
    prompts["LUCKY_NUMBER"] = "Your lucky number today is {{number:min=1,max=100}}."
    prompts["MOOD_SUGGESTION"] = (
        "I notice you're feeling down. Have you tried {{choice:meditation,deep breathing,going for a walk,listening to music}} today?"
    )

    return prompts
