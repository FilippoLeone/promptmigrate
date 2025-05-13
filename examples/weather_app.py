"""Advanced example demonstrating prompt migration in an LLM application context."""

import argparse
import json
from typing import Dict, List, Any

from promptmigrate import promptmanager as pm
from promptmigrate.manager import PromptManager


class LLMClient:
    """Mock LLM client to simulate API calls to OpenAI, Anthropic, etc."""
    
    def chat_completion(self, system: str, prompt: str) -> Dict[str, Any]:
        """Simulate a chat completion call."""
        print(f"[LLM] System: {system}")
        print(f"[LLM] User: {prompt}")
        return {
            "response": f"This is a simulated response to: {prompt[:30]}...",
            "tokens": len(prompt) + len(system),
            "model": "gpt-simulation-4"
        }


class WeatherApp:
    """Example application using prompts to interact with LLMs."""
    
    def __init__(self):
        # Ensure migrations are applied first
        manager = PromptManager()
        manager.upgrade()
        
        # Initialize the LLM client
        self.llm = LLMClient()
    
    def get_weather_forecast(self, location: str, date: str = "today") -> Dict[str, Any]:
        """Get a weather forecast for the specified location."""
        # Use the system prompt 
        system = pm.SYSTEM
        
        # Customize the weather question prompt with the location
        prompt = pm.WEATHER_QUESTION.replace("today", date)
        prompt = f"{prompt} in {location}"
        
        # Call the LLM
        return self.llm.chat_completion(system, prompt)


def main():
    parser = argparse.ArgumentParser(description="PromptMigrate Weather App Example")
    parser.add_argument("--location", default="New York", help="Location for weather forecast")
    parser.add_argument("--date", default="today", help="Date for forecast (today, tomorrow, etc.)")
    args = parser.parse_args()
    
    app = WeatherApp()
    result = app.get_weather_forecast(args.location, args.date)
    
    print("\nForecasting result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
