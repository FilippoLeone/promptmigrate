"""Tests to verify proper installation and imports work."""

import importlib
import subprocess
import sys

import pytest


def test_import_package():
    """Test that the package can be imported."""
    try:
        import promptmigrate

        assert promptmigrate.__version__ is not None
    except ImportError:
        pytest.fail("Failed to import promptmigrate")


def test_import_submodules():
    """Test that all submodules can be imported."""
    submodules = ["manager", "cli"]
    for module in submodules:
        try:
            importlib.import_module(f"promptmigrate.{module}")
        except ImportError as e:
            pytest.fail(f"Failed to import promptmigrate.{module}: {e}")


def test_cli_availability():
    """Test that the CLI command is available."""
    try:
        result = subprocess.run(
            ["promptmigrate", "--help"], capture_output=True, text=True, check=False
        )
        assert result.returncode == 0
        assert "Prompt schema migrations for LLM applications" in result.stdout
    except FileNotFoundError:
        # If we're running tests in dev mode, the CLI might not be installed
        if "site-packages" in sys.modules["promptmigrate"].__file__:
            pytest.fail("CLI command not found despite being installed")
        else:
            # Skip if we're in development mode
            pytest.skip("CLI not installed, skipping test")
