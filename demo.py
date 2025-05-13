#!/usr/bin/env python
"""
Demo script to show how to use promptmigrate in a real-world application.

Run this script to see how the promptmigrate system works:
    python demo.py
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Ensure we can import the package
sys.path.insert(0, os.path.abspath("."))

from promptmigrate import promptmanager as pm
from promptmigrate.manager import PromptManager, prompt_revision

# Create a migration for this demo
@prompt_revision("003_llm_providers", "Add prompts for different LLM providers")
def add_llm_prompts(prompts):
    """Add prompts for various LLM providers."""
    
    # General system prompts
    prompts["SYSTEM_GENERAL"] = "You are a helpful assistant."
    prompts["SYSTEM_PROFESSIONAL"] = "You are a professional assistant with expert knowledge on various topics."
    prompts["SYSTEM_CREATIVE"] = "You are a creative assistant designed to help with brainstorming and generating ideas."
    
    # OpenAI specific prompts
    prompts["OPENAI_SYSTEM"] = "You are an AI assistant built by OpenAI. {{date:format=Today is %B %d, %Y.}}"
    prompts["OPENAI_FOLLOWUP"] = "{{choice:Is there anything else I can help you with?,Do you need more information on this topic?,Would you like me to elaborate further?}}"
    
    # Anthropic specific prompts
    prompts["ANTHROPIC_SYSTEM"] = "You are Claude, an AI assistant by Anthropic. {{date:format=Current date: %Y-%m-%d.}}"
    prompts["ANTHROPIC_THINKING"] = "{{text:I'll think through this step-by-step to ensure I give you accurate information on {topic}.,topic=the requested subject}}"
    
    # Google Gemini specific prompts
    prompts["GEMINI_SYSTEM"] = "You are Gemini, a large language model by Google. {{date:format=Today's date is %d %B %Y.}}"
    prompts["GEMINI_ASSIST"] = "I'm here to assist with {{choice:answering questions,general knowledge,creative tasks,problem-solving}}."
    
    # Weather prompts with dynamic values
    prompts["WEATHER_QUESTION"] = "What's the weather like in {{choice:New York,London,Tokyo,Sydney,Paris}} today?"
    prompts["WEATHER_RESPONSE"] = (
        "{{text:Based on my information, the weather in {location} is currently {condition} "
        "with temperatures around {temp}°C.,location=your city,condition=partly cloudy,temp=22}}"
    )    
    return prompts


# Sample LLM clients
class OpenAIClient:
    """OpenAI API client simulation."""
    
    def complete(self, messages):
        """Simulate completion API."""
        print("\n--- OpenAI API Call ---")
        for msg in messages:
            print(f"[{msg['role']}]: {msg['content']}")
        return {
            'choices': [{
                'message': {
                    'role': 'assistant',
                    'content': f"Response from OpenAI to your query. (Using system: {messages[0]['content'][:30]}...)"
                }
            }]
        }


class AnthropicClient:
    """Anthropic API client simulation."""
    
    def messages(self, system, messages):
        """Simulate messages API."""
        print("\n--- Anthropic API Call ---")
        print(f"[system]: {system}")
        for msg in messages:
            print(f"[{msg['role']}]: {msg['content']}")
        return {
            'content': [{
                'text': f"Response from Claude to your query. (Using system: {system[:30]}...)"
            }]
        }


class GeminiClient:
    """Google Gemini API client simulation."""
    
    def generate_content(self, prompt, system_instruction=None):
        """Simulate content generation."""
        print("\n--- Google Gemini API Call ---")
        if system_instruction:
            print(f"[system]: {system_instruction}")
        print(f"[prompt]: {prompt}")
        return {
            'text': f"Response from Gemini to your query. (Using system: {system_instruction[:30] if system_instruction else 'None'}...)"
        }


def setup():
    """Ensure migrations are applied."""
    print("🔄 Setting up promptmigrate...")
    manager = PromptManager()
    
    # Check current revision
    current = manager.current_rev()
    print(f"📝 Current revision: {current or '<none>'}")
    
    # Apply migrations
    print("🔄 Applying migrations...")
    manager.upgrade()
    print(f"✅ New revision: {manager.current_rev()}")
      # List all prompts
    print("\n📋 Available prompts:")
    prompts = manager.load_prompts()
    print(f"Total: {len(prompts)} prompts")
    
    # Show some example prompts
    print("\n📝 Example prompts:")
    categories = {
        "General": ["SYSTEM_GENERAL"],
        "OpenAI": ["OPENAI_SYSTEM", "OPENAI_FOLLOWUP"],
        "Anthropic": ["ANTHROPIC_SYSTEM", "ANTHROPIC_THINKING"],
        "Gemini": ["GEMINI_SYSTEM", "GEMINI_ASSIST"],
        "Weather": ["WEATHER_QUESTION", "WEATHER_RESPONSE"]
    }
    
    for category, prompt_keys in categories.items():
        print(f"\n{category} prompts:")
        for key in prompt_keys:
            if key in prompts:
                print(f"  {key}: {prompts[key]}")


def demo_openai():
    """Demonstrate using prompts with OpenAI."""
    client = OpenAIClient()
    
    # Create messages for chat completion
    messages = [
        {"role": "system", "content": pm.OPENAI_SYSTEM},
        {"role": "user", "content": pm.WEATHER_QUESTION}
    ]
    
    # Get completion
    response = client.complete(messages)
    
    # Show response
    print(f"\nResponse: {response['choices'][0]['message']['content']}")
    print(f"\nFollow-up: {pm.OPENAI_FOLLOWUP}")


def demo_anthropic():
    """Demonstrate using prompts with Anthropic."""
    client = AnthropicClient()
    
    # Create message for Claude
    system = pm.ANTHROPIC_SYSTEM
    messages = [
        {"role": "user", "content": pm.WEATHER_QUESTION}
    ]
    
    # Add thinking placeholder
    thinking = pm.ANTHROPIC_THINKING.replace("the requested subject", "weather patterns")
    messages.insert(0, {"role": "assistant", "content": thinking})
    
    # Get response
    response = client.messages(system, messages)
    
    # Show response
    print(f"\nResponse: {response['content'][0]['text']}")


def demo_gemini():
    """Demonstrate using prompts with Google Gemini."""
    client = GeminiClient()
    
    # Create prompt and system instruction
    system = pm.GEMINI_SYSTEM
    user_prompt = f"{pm.WEATHER_QUESTION}\n\n{pm.GEMINI_ASSIST}"
    
    # Get response
    response = client.generate_content(user_prompt, system_instruction=system)
    
    # Show response
    print(f"\nResponse: {response['text']}")
      # Show weather response
    weather_response = pm.WEATHER_RESPONSE.replace("your city", "Paris")
    print(f"\nCustomized Weather: {weather_response}")


def main():
    """Run the demo."""
    print("=" * 50)
    print("PromptMigrate Demo")
    print("=" * 50)
    
    # Set up and apply migrations
    setup()
    
    # Ask user which demo to run
    print("\n🔄 Select a demo to run:")
    print("1. OpenAI")
    print("2. Anthropic")
    print("3. Gemini")
    print("4. All demos")
    print("q. Quit")
    
    choice = input("\nYour choice (1-4 or q): ").strip().lower()
    
    if choice == '1':
        demo_openai()
    elif choice == '2':
        demo_anthropic()
    elif choice == '3':
        demo_gemini()
    elif choice == '4':
        demo_openai()
        demo_anthropic()
        demo_gemini()
    else:
        print("Exiting demo.")
        return
    
    print("\n✅ Demo completed!")


if __name__ == "__main__":
    main()
