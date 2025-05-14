"""Tests for the dynamic values feature."""

import re
import tempfile  # Added
from datetime import datetime
from pathlib import Path  # Added
from unittest.mock import patch

import pytest
import yaml  # Added

from promptmigrate.manager import PromptManager


def test_static_prompt(tmp_path: Path):  # Added tmp_path
    """Test that regular prompts without dynamic values work."""
    prompt_file = tmp_path / "prompts.yaml"
    state_file = tmp_path / ".state.json"

    prompts_content = {"TEST": "Static value"}
    with open(prompt_file, "w") as f:
        yaml.dump(prompts_content, f)

    # Create a test manager with a known prompt, pointing to the temp file
    manager = PromptManager(prompt_file=prompt_file, state_file=state_file, skip_manual_check=True)
    # manager.reload(force_reload=True) # Ensure it loads from the temp file

    # Ensure the prompt value is returned exactly
    assert manager.TEST == "Static value"


def test_date_placeholder(tmp_path: Path):  # Added tmp_path
    """Test date placeholders in prompts."""
    prompt_file = tmp_path / "prompts.yaml"
    state_file = tmp_path / ".state.json"

    prompts_content = {"DATE_TEST": "Today is {{date:format=%Y-%m-%d}}."}
    with open(prompt_file, "w") as f:
        yaml.dump(prompts_content, f)

    manager = PromptManager(prompt_file=prompt_file, state_file=state_file, skip_manual_check=True)
    # manager.reload(force_reload=True)

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


def test_number_placeholder(tmp_path: Path):  # Added tmp_path
    """Test number placeholders in prompts."""
    prompt_file = tmp_path / "prompts.yaml"
    state_file = tmp_path / ".state.json"

    prompts_content = {"NUMBER_TEST": "Your number is {{number:min=1,max=10}}."}
    with open(prompt_file, "w") as f:
        yaml.dump(prompts_content, f)

    manager = PromptManager(prompt_file=prompt_file, state_file=state_file, skip_manual_check=True)
    # manager.reload(force_reload=True)

    # Extract the number from the result
    result = manager.NUMBER_TEST
    assert result.startswith("Your number is ")
    assert result.endswith(".")

    # Extract the number part and verify it's in the correct range
    num_match = re.search(r"Your number is (\d+)\.", result)
    assert num_match is not None

    num = int(num_match.group(1))
    assert 1 <= num <= 10


def test_choice_placeholder(tmp_path: Path):  # Added tmp_path
    """Test choice placeholders in prompts."""
    prompt_file = tmp_path / "prompts.yaml"
    state_file = tmp_path / ".state.json"

    choices = ["apple", "banana", "cherry"]
    prompts_content = {"CHOICE_TEST": f"I recommend {{{{choice:{','.join(choices)}}}}}"}  # noqa
    with open(prompt_file, "w") as f:
        yaml.dump(prompts_content, f)

    manager = PromptManager(prompt_file=prompt_file, state_file=state_file, skip_manual_check=True)
    # manager.reload(force_reload=True)

    # Get the result
    result = manager.CHOICE_TEST
    assert result.startswith("I recommend ")

    # The result should contain one of the choices
    assert any(result == f"I recommend {choice}" for choice in choices)


def test_text_placeholder(tmp_path: Path):  # Added tmp_path
    """Test text placeholders in prompts."""
    prompt_file = tmp_path / "prompts.yaml"
    state_file = tmp_path / ".state.json"

    prompts_content = {"TEXT_TEST": "{{text:Hello {name}!,name=World}}"}
    with open(prompt_file, "w") as f:
        yaml.dump(prompts_content, f)

    manager = PromptManager(prompt_file=prompt_file, state_file=state_file, skip_manual_check=True)
    # manager.reload(force_reload=True)

    # Manually test the _process_dynamic_values method
    # This part of the test might need to be re-evaluated as _process_dynamic_values is internal.
    # For now, we focus on the external behavior (attribute access).
    # test_value = manager._process_dynamic_values("{{text:Hello {name}!,name=World}}")
    # print(f"Processed direct value: {test_value}")

    # Get the attribute value
    attr_value = manager.TEXT_TEST
    print(f"Attribute value: {attr_value}")

    # The result should be the template with the variable replaced
    assert manager.TEXT_TEST == "Hello World!"


def test_missing_variables_in_text(tmp_path: Path):  # Added tmp_path
    """Test text placeholders with missing variables."""
    prompt_file = tmp_path / "prompts.yaml"
    state_file = tmp_path / ".state.json"

    prompts_content = {"MISSING_VAR": "{{text:Hello {name}!}}"}  # No 'name' defined
    with open(prompt_file, "w") as f:
        yaml.dump(prompts_content, f)

    manager = PromptManager(prompt_file=prompt_file, state_file=state_file, skip_manual_check=True)
    # manager.reload(force_reload=True)

    # The result should be the template unchanged
    assert manager.MISSING_VAR == "Hello {name}!"


def test_invalid_placeholder(tmp_path: Path):  # Added tmp_path
    """Test that invalid placeholders are left unchanged."""
    prompt_file = tmp_path / "prompts.yaml"
    state_file = tmp_path / ".state.json"

    prompts_content = {"INVALID": "This is an {{invalid}} placeholder"}
    with open(prompt_file, "w") as f:
        yaml.dump(prompts_content, f)

    manager = PromptManager(prompt_file=prompt_file, state_file=state_file, skip_manual_check=True)
    # manager.reload(force_reload=True)

    # The result should be the template with the invalid placeholder unchanged
    assert manager.INVALID == "This is an {{invalid}} placeholder"


def test_multiple_placeholders(tmp_path: Path):  # Added tmp_path
    """Test multiple placeholders in one prompt."""
    prompt_file = tmp_path / "prompts.yaml"
    state_file = tmp_path / ".state.json"

    template = "Date: {{date:format=%Y}}, Number: {{number:min=5,max=5}}, Choice: {{choice:X}}"
    prompts_content = {"MULTI": template}
    with open(prompt_file, "w") as f:
        yaml.dump(prompts_content, f)

    manager = PromptManager(prompt_file=prompt_file, state_file=state_file, skip_manual_check=True)
    # manager.reload(force_reload=True)

    result = manager.MULTI

    # Verify pattern matches what we expect
    assert re.match(r"Date: \\d{4}, Number: 5, Choice: X", result) is not None
