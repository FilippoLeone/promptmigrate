"""Tests for the dynamic values feature."""

import re
from datetime import datetime
from unittest.mock import patch

import pytest

from promptmigrate.manager import PromptManager


def test_static_prompt():
    """Test that regular prompts without dynamic values work."""
    # Create a test manager with a known prompt
    manager = PromptManager()

    # Mock the _read_prompts method to return a test prompt
    with patch.object(manager, "_read_prompts", return_value={"TEST": "Static value"}):
        # Ensure the prompt value is returned exactly
        assert manager.TEST == "Static value"


def test_date_placeholder():
    """Test date placeholders in prompts."""
    manager = PromptManager()

    # Mock the _read_prompts method to return a prompt with a date placeholder
    with patch.object(
        manager, "_read_prompts", return_value={"DATE_TEST": "Today is {{date:format=%Y-%m-%d}}."}
    ):
        # Extract the date from the result
        result = manager.DATE_TEST
        assert result.startswith("Today is ")
        assert result.endswith(".")

        # Extract the date part and verify it's in the correct format
        date_match = re.search(r"Today is (\d{4}-\d{2}-\d{2})\.", result)
        assert date_match is not None

        # Try to parse the extracted date to confirm format
        date_str = date_match.group(1)
        datetime.strptime(date_str, "%Y-%m-%d")  # This will raise ValueError if format is wrong


def test_number_placeholder():
    """Test number placeholders in prompts."""
    manager = PromptManager()

    # Mock the _read_prompts method to return a prompt with a number placeholder
    with patch.object(
        manager,
        "_read_prompts",
        return_value={"NUMBER_TEST": "Your number is {{number:min=1,max=10}}."},
    ):
        # Extract the number from the result
        result = manager.NUMBER_TEST
        assert result.startswith("Your number is ")
        assert result.endswith(".")

        # Extract the number part and verify it's in the correct range
        num_match = re.search(r"Your number is (\d+)\.", result)
        assert num_match is not None

        num = int(num_match.group(1))
        assert 1 <= num <= 10


def test_choice_placeholder():
    """Test choice placeholders in prompts."""
    manager = PromptManager()

    choices = ["apple", "banana", "cherry"]

    # Mock the _read_prompts method to return a prompt with a choice placeholder
    with patch.object(
        manager,
        "_read_prompts",
        return_value={"CHOICE_TEST": f"I recommend {{{{choice:{','.join(choices)}}}}}"},
    ):
        # Get the result
        result = manager.CHOICE_TEST
        assert result.startswith("I recommend ")

        # The result should contain one of the choices
        assert any(result == f"I recommend {choice}" for choice in choices)


def test_text_placeholder():
    """Test text placeholders in prompts."""
    manager = PromptManager()

    # Mock the _read_prompts method to return a prompt with a text placeholder
    with patch.object(
        manager, "_read_prompts", return_value={"TEXT_TEST": "{{text:Hello {name}!,name=World}}"}
    ):
        # Manually test the _process_dynamic_values method
        test_value = manager._process_dynamic_values("{{text:Hello {name}!,name=World}}")
        print(f"Processed direct value: {test_value}")

        # Get the attribute value
        attr_value = manager.TEXT_TEST
        print(f"Attribute value: {attr_value}")

        # The result should be the template with the variable replaced
        assert manager.TEXT_TEST == "Hello World!"


def test_missing_variables_in_text():
    """Test text placeholders with missing variables."""
    manager = PromptManager()

    # Mock the _read_prompts method to return a prompt with a text placeholder missing a variable
    with patch.object(
        manager,
        "_read_prompts",
        return_value={"MISSING_VAR": "{{text:Hello {name}!}}"},  # No 'name' defined
    ):
        # The result should be the template unchanged
        assert manager.MISSING_VAR == "Hello {name}!"


def test_invalid_placeholder():
    """Test that invalid placeholders are left unchanged."""
    manager = PromptManager()

    # Mock the _read_prompts method to return a prompt with an invalid placeholder
    with patch.object(
        manager, "_read_prompts", return_value={"INVALID": "This is an {{invalid}} placeholder"}
    ):
        # The result should be the template with the invalid placeholder unchanged
        assert manager.INVALID == "This is an {{invalid}} placeholder"


def test_multiple_placeholders():
    """Test multiple placeholders in one prompt."""
    manager = PromptManager()

    # Mock the _read_prompts method to return a prompt with multiple placeholders
    template = "Date: {{date:format=%Y}}, Number: {{number:min=5,max=5}}, Choice: {{choice:X}}"
    with patch.object(manager, "_read_prompts", return_value={"MULTI": template}):
        result = manager.MULTI

        # Verify pattern matches what we expect
        assert re.match(r"Date: \d{4}, Number: 5, Choice: X", result) is not None
