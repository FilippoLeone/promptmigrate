"""Example showing how to use dynamic values in prompts."""

from promptmigrate import promptmanager as pm
from promptmigrate.manager import PromptManager, prompt_revision


@prompt_revision("003_dynamic_values", "Add prompts with dynamic values")
def add_dynamic_prompts(prompts):
    """Add prompts that demonstrate dynamic value functionality."""
    # Date example
    prompts["DATE_GREETING"] = "Today is {{date:format=%B %d, %Y}}. How can I help you?"
    
    # Number example
    prompts["LUCKY_NUMBER"] = "Your lucky number today is {{number:min=1,max=100}}."
    
    # Choice example
    prompts["MOOD_SUGGESTION"] = "I notice you're feeling down. Have you tried {{choice:meditation,deep breathing,going for a walk,listening to music}} today?"
    
    # Text example with variable substitution
    prompts["PERSONALIZED_GREETING"] = "{{text:Hello {name}! Welcome to {service}.,name=valued customer,service=our AI assistant}}"
    
    return prompts


def main():
    """Run the example to demonstrate dynamic values."""
    # Create a manager and apply our migration
    manager = PromptManager()
    print("Current revision:", manager.current_rev() or "<none>")
    
    # Apply our migration with dynamic values
    manager.upgrade()
    print("New revision:", manager.current_rev())
    
    # Access the prompts multiple times to show that dynamic values
    # are processed on each access
    print("\nDynamic Values Examples:")
    print("-" * 50)
    
    # Date example - changes based on current date
    print("Date Example:")
    print("  First access:", pm.DATE_GREETING)
    print("  Second access:", pm.DATE_GREETING)
    print()
    
    # Number example - random number each time
    print("Number Example:")
    print("  First access:", pm.LUCKY_NUMBER)
    print("  Second access:", pm.LUCKY_NUMBER)
    print()
    
    # Choice example - random choice each time
    print("Choice Example:")
    print("  First access:", pm.MOOD_SUGGESTION)
    print("  Second access:", pm.MOOD_SUGGESTION)
    print()
    
    # Text example - template with variables
    print("Text Example:")
    print("  Default:", pm.PERSONALIZED_GREETING)
    
    # You can also load all prompts at once
    # Note that this gives you the raw templates, not the processed values
    all_prompts = pm.load_prompts()
    print("\nRaw prompt templates:")
    for key, value in all_prompts.items():
        if "{{" in value:
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()