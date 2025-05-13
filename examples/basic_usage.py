"""Basic usage example showing how to access prompts."""

from promptmigrate import promptmanager as pm

# First, make sure migrations are applied
# In a real-world application, you would handle this during setup or startup

def simulate_llm_call(system_prompt, user_prompt):
    """Simulate calling an LLM API."""
    print(f"Using system prompt: {system_prompt}")
    print(f"Using user prompt: {user_prompt}")
    print("LLM response: This is a simulated response")


def main():
    # Use attribute-style access (case-insensitive)
    system = pm.SYSTEM
    
    # Or use dict-style access
    # system = pm["SYSTEM"]
    
    # Access the weather question prompt
    weather_q = pm.WEATHER_QUESTION
    
    # Simulate an LLM call
    simulate_llm_call(system, weather_q)


if __name__ == "__main__":
    main()
