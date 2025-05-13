"""Pytest suite covering attribute‑style access and migration functionality."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from promptmigrate import promptmanager as pm
from promptmigrate.manager import PromptManager, prompt_revision


@prompt_revision("001_initial", "seed system prompt")
def _initial(prompts):
    prompts["SYSTEM"] = "You are a helpful assistant."
    return prompts


@prompt_revision("002_add_weather_q", "add weather question prompt")
def _weather(prompts):
    prompts["WEATHER_QUESTION"] = "What's the weather like today?"
    return prompts


def test_attribute_access(tmp_path):
    """Test attribute access works."""
    # Create a temporary prompts.yaml
    prompt_file = tmp_path / "prompts.yaml"
    state_file = tmp_path / ".promptmigrate_state.json"
    
    prompts = {
        "GREETING": "Hello, world!",
        "QUESTION_ONE": "What is your name?",
        "question_two": "How are you today?"
    }
    
    with open(prompt_file, "w") as f:
        yaml.safe_dump(prompts, f)
    
    # Create a manager instance
    manager = PromptManager(prompt_file, state_file)
    
    # Test direct attribute access
    assert manager.GREETING == "Hello, world!"
    assert manager.QUESTION_ONE == "What is your name?"
    
    # Test case-insensitive fallback
    assert manager.question_one == "What is your name?"
    assert manager.QUESTION_TWO == "How are you today?"
    
    # Test dictionary access
    assert manager["GREETING"] == "Hello, world!"
    
    # Test attribute error
    with pytest.raises(AttributeError):
        _ = manager.NONEXISTENT


def test_migration_apply(tmp_path):
    """Test applying migrations."""
    prompt_file = tmp_path / "prompts.yaml"
    state_file = tmp_path / ".promptmigrate_state.json"
    
    # Create empty files
    prompt_file.touch()
    state_file.touch()
    
    # Create manager and apply migrations
    manager = PromptManager(prompt_file, state_file)
    
    # The migrations defined above (_initial and _weather) should be registered
    manager.upgrade()
    
    # Verify migrations were applied
    assert manager.SYSTEM == "You are a helpful assistant."
    assert manager.WEATHER_QUESTION == "What's the weather like today?"
    assert manager.current_rev() == "002_add_weather_q"


def test_selective_migration(tmp_path):
    """Test applying migrations up to a specific target."""
    prompt_file = tmp_path / "prompts.yaml"
    state_file = tmp_path / ".promptmigrate_state.json"
    
    # Create empty files
    prompt_file.touch()
    state_file.touch()
    
    # Create manager and apply only the first migration
    manager = PromptManager(prompt_file, state_file)
    manager.upgrade(target="001_initial")
    
    # Verify only the first migration was applied
    assert manager.SYSTEM == "You are a helpful assistant."
    assert manager.current_rev() == "001_initial"
    
    # The WEATHER_QUESTION should not exist yet
    with pytest.raises(AttributeError):
        _ = manager.WEATHER_QUESTION
    
    # Now apply the second migration
    manager.upgrade()
    assert manager.WEATHER_QUESTION == "What's the weather like today?"
    assert manager.current_rev() == "002_add_weather_q"


def test_reload_functionality(tmp_path):
    """Test that the reload method works correctly."""
    prompt_file = tmp_path / "prompts.yaml"
    state_file = tmp_path / ".promptmigrate_state.json"
    
    # Create initial prompts
    prompts = {"TEST": "Initial value"}
    with open(prompt_file, "w") as f:
        yaml.safe_dump(prompts, f)
    
    # Create manager and check initial value
    manager = PromptManager(prompt_file, state_file)
    assert manager.TEST == "Initial value"
    
    # Modify the file directly
    new_prompts = {"TEST": "Updated value"}
    with open(prompt_file, "w") as f:
        yaml.safe_dump(new_prompts, f)
    
    # Before reload, the cached value should still be used
    assert manager.TEST == "Initial value"
    
    # After reload, the new value should be used
    manager.reload()
    assert manager.TEST == "Updated value"


def test_singleton():
    """Test the singleton instance works."""
    # This test requires temporarily changing the working directory
    original_dir = os.getcwd()
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Create a test prompts.yaml
            with open("prompts.yaml", "w") as f:
                yaml.safe_dump({"TEST_SINGLETON": "This is the singleton test"}, f)
            
            # Force reload of the singleton
            pm.reload()
            
            # Test attribute access works
            assert pm.TEST_SINGLETON == "This is the singleton test"
    finally:
        # Restore original directory
        os.chdir(original_dir)
