"""Top‑level package for *promptmigrate*.

Exports the public API and attaches package metadata in ``__all__`` for
static‑analysis friendliness and provides a convenience *singleton* so users
can reference prompts via **attribute access**, e.g. ``promptmanager.GREETING``.
"""

from importlib import metadata as _metadata
from logging import getLogger

from .manager import get_auto_revision_setting  # MODIFIED
from .manager import (  # noqa: E402  pylint: disable=wrong‑import‑position
    AUTO_REVISION_WATCH,
    PromptManager,
    PromptMigration,
    prompt_revision,
)

try:
    from .autorevision import create_revision_from_changes, detect_changes
except ImportError:
    # These might not be available during initial import
    detect_changes = None
    create_revision_from_changes = None

__all__ = [
    "PromptMigration",
    "PromptManager",
    "prompt_revision",
    "promptmanager",  # convenience singleton
    "create_revision_from_changes",
    "detect_changes",
    "enable_auto_revision",
]

try:
    __version__ = _metadata.version(__name__)
except _metadata.PackageNotFoundError:  # local, editable install
    __version__ = "0.4.3"

logger = getLogger(__name__)

# ‑‑‑ Public singleton for ergonomic access ‑‑‑
#: A *lazy* PromptManager automatically reading *prompts.yaml* when the first
#: attribute is accessed.  Typical usage::
#:
#:     from promptmigrate import promptmanager as pm
#:     reply = openai.ChatCompletion.create(
#:         model="gpt‑4o",
#:         messages=[{"role": "system", "content": pm.SYSTEM}]
#:     )


# Helper to enable auto-revision functionality
def enable_auto_revision(watch: bool = False):
    """
    Enable automatic revision creation from manual changes to prompts.yaml.

    Args:
        watch: If True, starts a file watcher to detect changes in real-time
    """
    import os

    os.environ["PROMPTMIGRATE_AUTO_REVISION"] = "1"
    # The PromptManager now internally uses AUTO_REVISION_WATCH based on this env var
    if watch:
        os.environ["PROMPTMIGRATE_AUTO_REVISION_WATCH"] = "1"
    else:
        # Ensure it's disabled if watch is False
        os.environ["PROMPTMIGRATE_AUTO_REVISION_WATCH"] = "0"

    # Re-create the singleton with auto-revision enabled/disabled
    # The PromptManager will pick up the environment variables.
    # We pass skip_manual_check=False to ensure the watcher is started if env vars are set.
    global promptmanager
    promptmanager = PromptManager(skip_manual_check=False)


# Default singleton instance
# Initialize with skip_manual_check=False to allow watcher to start if env vars are set
promptmanager = PromptManager(skip_manual_check=False)
