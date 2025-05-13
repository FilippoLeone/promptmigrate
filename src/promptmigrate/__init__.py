"""Top‑level package for *promptmigrate*.

Exports the public API and attaches package metadata in ``__all__`` for
static‑analysis friendliness and provides a convenience *singleton* so users
can reference prompts via **attribute access**, e.g. ``promptmanager.GREETING``.
"""

from importlib import metadata as _metadata
from logging import getLogger

from .manager import PromptManager, prompt_revision, PromptMigration  # noqa: E402  pylint: disable=wrong‑import‑position

__all__ = [
    "PromptMigration",
    "PromptManager",
    "prompt_revision",
    "promptmanager",  # convenience singleton
]

try:
    __version__ = _metadata.version(__name__)
except _metadata.PackageNotFoundError:  # local, editable install
    __version__ = "0.3.0"

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
promptmanager = PromptManager()
