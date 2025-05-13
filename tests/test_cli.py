"""Test suite for CLI functionality."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from promptmigrate.cli import cli


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


def test_version(runner):
    """Test the version command works."""
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "promptmigrate" in result.output


def test_init_command(runner, tmp_path):
    """Test the init command creates a revisions package."""
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        assert "Created revisions package" in result.output
        
        # Check the package was created
        assert os.path.exists(os.path.join(td, "promptmigrate_revisions"))
        assert os.path.exists(os.path.join(td, "promptmigrate_revisions", "__init__.py"))


def test_current_command(runner, tmp_path):
    """Test the current command shows the current revision."""
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        # With no state file, should show <none>
        result = runner.invoke(cli, ["current"])
        assert result.exit_code == 0
        assert "<none>" in result.output


@patch("promptmigrate.cli.load_revision_module")
def test_upgrade_command_package_not_found(mock_load, runner, tmp_path):
    """Test the upgrade command handles missing package."""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Test with non-existent package
        result = runner.invoke(cli, ["upgrade", "--package", "nonexistent_package"])
        assert result.exit_code != 0
        assert "not found" in result.output
        # The load_revision_module should not be called
        mock_load.assert_not_called()
