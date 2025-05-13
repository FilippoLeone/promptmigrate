"""Example showing how to create and apply custom migrations."""

import argparse
from datetime import datetime
from pathlib import Path

from promptmigrate.manager import PromptManager, prompt_revision


@prompt_revision("003_custom", "Add a custom prompt")
def add_custom_prompt(prompts):
    """Add a custom prompt to the collection."""
    prompts["CUSTOM"] = "This is a custom prompt added at runtime."
    return prompts


def main():
    parser = argparse.ArgumentParser(description="Custom migration example")
    parser.add_argument("--apply", action="store_true", help="Apply the migration")
    args = parser.parse_args()
    
    # Create a manager pointing to the current directory
    manager = PromptManager()
    
    if args.apply:
        # Apply all migrations including our custom one
        manager.upgrade()
        print(f"Current revision: {manager.current_rev()}")
        
        # Print all prompts
        manager.reload()  # Ensure we have latest prompts
        prompts = manager.load_prompts()
        
        print("\nCurrent prompts:")
        for key, value in prompts.items():
            print(f"- {key}: {value}")
    else:
        print("Run with --apply to apply the migration")


if __name__ == "__main__":
    main()
