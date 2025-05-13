"""Tests for auto-revision functionality."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest
import yaml

from promptmigrate import enable_auto_revision
from promptmigrate import promptmanager as pm
from promptmigrate.autorevision import create_revision_from_changes, detect_changes
from promptmigrate.manager import PromptManager


def test_detect_changes(tmp_path):
    """Test detecting changes to prompts.yaml file."""
    # Create temporary files
    prompt_file = tmp_path / "prompts.yaml"
    state_file = tmp_path / ".promptmigrate_state.json"

    # Set up initial state
    prompts = {"SYSTEM": "Initial prompt"}
    with open(prompt_file, "w") as f:
        yaml.dump(prompts, f)

    # Create manager
    manager = PromptManager(prompt_file=prompt_file, state_file=state_file)

    # Apply initial state
    manager.save_prompts(prompts)

    # Modify prompts.yaml directly
    modified_prompts = {"SYSTEM": "Updated prompt", "NEW_PROMPT": "Brand new prompt"}
    with open(prompt_file, "w") as f:
        yaml.dump(modified_prompts, f)

    # Detect changes
    added, modified, removed = detect_changes()

    # Verify detection
    assert "NEW_PROMPT" in added
    assert "SYSTEM" in modified
    assert not removed


def test_create_revision_from_changes(tmp_path):
    """Test creating a revision from changes to prompts.yaml."""
    # Set up temporary environment
    os.environ["PROMPTMIGRATE_AUTO_REVISION"] = "1"

    # Create temporary files
    prompt_file = tmp_path / "prompts.yaml"
    state_file = tmp_path / ".promptmigrate_state.json"
    revisions_dir = tmp_path / "promptmigrate_revisions"
    revisions_dir.mkdir()
    (revisions_dir / "__init__.py").touch()

    # Create initial state
    manager = PromptManager(prompt_file=prompt_file, state_file=state_file)
    initial_prompts = {"SYSTEM": "Initial system prompt"}
    manager.save_prompts(initial_prompts)

    # Directly modify prompts.yaml
    modified_prompts = {"SYSTEM": "Updated system prompt", "USER": "New user prompt"}
    with open(prompt_file, "w") as f:
        yaml.dump(modified_prompts, f)

    # Create revision
    revision_file = create_revision_from_changes(rev_id="001_test_auto")

    # Verify revision was created
    assert revision_file is not None
    assert Path(revision_file).exists()

    # Check content of revision file
    with open(revision_file, "r") as f:
        content = f.read()
        assert 'prompt_revision("001_test_auto"' in content
        assert 'prompts["SYSTEM"] = "Updated system prompt"' in content
        assert 'prompts["USER"] = "New user prompt"' in content


def test_auto_revision_enabled(monkeypatch, tmp_path):
    """Test that auto-revision can be enabled via environment variable."""
    # Set up temporary environment
    monkeypatch.setenv("PROMPTMIGRATE_AUTO_REVISION", "1")

    # Create temporary files
    prompt_file = tmp_path / "prompts.yaml"
    state_file = tmp_path / ".promptmigrate_state.json"

    # Create manager
    manager = PromptManager(prompt_file=prompt_file, state_file=state_file)

    # Verify auto-revision is enabled
    assert hasattr(manager, "_check_for_manual_changes")

    # Test enable_auto_revision function
    enable_auto_revision()
    assert os.environ.get("PROMPTMIGRATE_AUTO_REVISION") == "1"
