"""Core implementation: manages the *prompts.yaml* model file, revision state
and exposes *attribute access* to individual prompt strings for ergonomic use
in application code.
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from logging import getLogger
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Protocol, Union, cast, runtime_checkable

import yaml

STATE_FILE = Path(".promptmigrate_state.json")
PROMPT_FILE = Path("prompts.yaml")
REVISION_ATTR = "__pm_revision__"

# Logger for this module
logger = getLogger(__name__)

# Dynamic value placeholders pattern
DYNAMIC_VALUE_PATTERN = r"\{\{(.*?)\}\}"


# ---------------------
@dataclass(slots=True, frozen=True)
class PromptMigration:
    """Metadata describing a single migration step."""

    rev_id: str
    description: str
    created_at: datetime
    fn: Callable[[dict[str, str]], dict[str, str]]

    def apply(self, prompts: dict[str, str]) -> dict[str, str]:  # noqa: D401
        """Apply the migration function to the *prompts* dict and return a new mapping."""
        return self.fn(prompts)


@runtime_checkable
class _RevisionModuleProto(Protocol):
    """A runtime interface used for static type‑checking revision modules."""

    __name__: str
    __pm_revision__: PromptMigration  # type: ignore[override]


# ---------------------
# Registry helpers
_migrations: list[PromptMigration] = []

def prompt_revision(
    rev_id: str,
    description: str = "",
) -> Callable[[Callable[[dict[str, str]], dict[str, str]]], Callable[[dict[str, str]], dict[str, str]]]:
    """Decorator registering *func* as a prompt‑migration."""

    def decorator(func: Callable[[dict[str, str]], dict[str, str]]) -> Callable[[dict[str, str]], dict[str, str]]:
        migration = PromptMigration(rev_id, description, datetime.now(timezone.utc), func)
        setattr(func, REVISION_ATTR, migration)
        _migrations.append(migration)
        return func

    return decorator


# ---------------------
class PromptManager:
    """Facade for applying prompt migrations **and** ergonomic prompt lookup.

    After importing :data:`promptmigrate.promptmanager` or instantiating the
    class directly, prompts can be referenced as attributes instead of dict
    keys::

        from promptmigrate import promptmanager as pm
        print(pm.QUESTION_EN_WEATHER)
    """

    # ‑‑‑ Construction & helpers ‑‑‑
    def __init__(self, prompt_file: Path | None = None, state_file: Path | None = None):
        self.prompt_file = prompt_file or PROMPT_FILE
        self.state_file = state_file or STATE_FILE
        self.prompt_file.touch(exist_ok=True)
        self.state_file.touch(exist_ok=True)
        self._cache: dict[str, str] | None = None  # lazy‑loaded prompts

    # Private: ensure cache is populated
    def _ensure_loaded(self) -> None:
        if self._cache is None:
            self._cache = self._read_prompts()

    # Internal YAML IO separated so *reload()* can bypass attribute cache
    def _read_prompts(self) -> dict[str, str]:
        if self.prompt_file.read_bytes():
            return yaml.safe_load(self.prompt_file.read_text()) or {}
        return {}

    def _write_prompts(self, prompts: dict[str, str]) -> None:
        self.prompt_file.write_text(yaml.safe_dump(prompts, sort_keys=False))

    # ‑‑‑ User‑facing API ‑‑‑
    def reload(self) -> "PromptManager":
        """Reload *prompts.yaml* into the attribute cache and return *self*."""
        self._cache = self._read_prompts()
        return self
        
    # Dictionary‑style access
    def __getitem__(self, key: str) -> str:
        self._ensure_loaded()
        assert self._cache is not None  # noqa: S101 – for mypy
        return self._process_dynamic_values(self._cache[key])

    # Attribute‑style access (case‑insensitive)
    def __getattr__(self, name: str) -> str:  # noqa: D401
        if name.startswith("__"):
            raise AttributeError(name)
        self._ensure_loaded()
        assert self._cache is not None
        # direct match or case‑insensitive fallback
        if name in self._cache:
            return self._process_dynamic_values(self._cache[name])
        lowered = name.lower()
        for k, v in self._cache.items():
            if k.lower() == lowered:
                return self._process_dynamic_values(v)
        raise AttributeError(f"Prompt {name!r} not found in prompts.yaml")

    # Legacy public helpers kept for backwards‑compat
    def load_prompts(self) -> dict[str, str]:  # deprecated in docs, kept for API
        self.reload()
        assert self._cache is not None
        return self._cache.copy()

    def save_prompts(self, prompts: dict[str, str]) -> None:
        self._write_prompts(prompts)
        self.reload()

    # Migration helpers
    def current_rev(self) -> str | None:
        if self.state_file.read_bytes():
            return json.loads(self.state_file.read_text()).get("rev")
        return None

    def set_current_rev(self, rev_id: str) -> None:
        self.state_file.write_text(json.dumps({"rev": rev_id}))

    def upgrade(self, target: str | None = None) -> None:
        applied = self.current_rev()
        prompts = self._read_prompts()

        pending = self._pending(applied, target)
        for mig in pending:
            prompts = mig.apply(prompts)
            self._write_prompts(prompts)
            self.set_current_rev(mig.rev_id)
            logger.info("Applied prompt revision %s – %s", mig.rev_id, mig.description)
        # refresh cache
        self.reload()
        
    def list_migrations(self) -> list[PromptMigration]:
        return sorted(_migrations, key=lambda m: m.rev_id)
        
    # ‑‑‑ Internal helpers ‑‑‑
    def _pending(self, current: str | None, target: str | None) -> list[PromptMigration]:
        ordered = self.list_migrations()
        if current:
            ordered = [m for m in ordered if m.rev_id > current]
        if target:
            ordered = [m for m in ordered if m.rev_id <= target]
        return ordered
        
    def _process_dynamic_values(self, text: str) -> str:
        """Process dynamic value placeholders in the prompt text.
        
        Placeholders use the format {{type:options}} where:
        - type: The type of dynamic content (date, number, choice, etc.)
        - options: Configuration for the dynamic content
        
        Examples:
            - {{date:format=%Y-%m-%d}} - Current date in specified format
            - {{number:min=1,max=100}} - Random number between min and max
            - {{choice:one,two,three}} - Random choice from a list
            - {{text:Hello {name}!,name=World}} - Formatted text with variables
        """
        if not text or "{{" not in text:
            return text
            
        def _replace_match(match: re.Match) -> str:
            directive = match.group(1).strip()
            
            if ":" not in directive:
                return match.group(0)  # Return unchanged if no format specifier
                
            value_type, options = directive.split(":", 1)
            
            # Handle different dynamic value types
            if value_type == "date":
                return self._process_date(options)
            elif value_type == "number":
                return self._process_number(options)
            elif value_type == "choice":
                return self._process_choice(options)
            elif value_type == "text":
                return self._process_text(options)
            
            # Unknown type, return unchanged
            return match.group(0)
            
        return re.sub(DYNAMIC_VALUE_PATTERN, _replace_match, text)
    
    def _process_date(self, options: str) -> str:
        """Process date dynamic values with optional format."""
        format_str = "%Y-%m-%d"
        
        # Extract format if specified
        if "format=" in options:
            format_match = re.search(r"format=([^,]+)", options)
            if format_match:
                format_str = format_match.group(1)
                
        return datetime.now().strftime(format_str)
    
    def _process_number(self, options: str) -> str:
        """Process number dynamic values with optional min/max."""
        min_val = 0
        max_val = 100
        
        # Extract min if specified
        if "min=" in options:
            min_match = re.search(r"min=([^,]+)", options)
            if min_match:
                try:
                    min_val = int(min_match.group(1))
                except ValueError:
                    pass
        
        # Extract max if specified
        if "max=" in options:
            max_match = re.search(r"max=([^,]+)", options)
            if max_match:
                try:
                    max_val = int(max_match.group(1))
                except ValueError:
                    pass
                    
        return str(random.randint(min_val, max_val))
    
    def _process_choice(self, options: str) -> str:
        """Process choice dynamic values by selecting from a list."""
        choices = options.split(",")
        return random.choice(choices).strip() if choices else ""
    
    def _process_text(self, options: str) -> str:
        """Process text with variables for template formatting."""
        # First part is the template, rest are variable assignments
        parts = options.split(",")
        template = parts[0]
        
        # Extract variables
        variables = {}
        for part in parts[1:]:
            if "=" in part:
                key, value = part.split("=", 1)
                variables[key.strip()] = value.strip()
                
        # Format the template with variables
        try:
            return template.format(**variables)
        except (KeyError, ValueError):
            # If there are no variables or formatting fails, return the template string
            return template


# ---------------------
# Convenience API for dynamic module discovery

def load_revision_module(module: str | ModuleType) -> _RevisionModuleProto:
    import importlib

    mod = importlib.import_module(module) if isinstance(module, str) else module
    migration: PromptMigration | None = getattr(mod, REVISION_ATTR, None)
    if migration is None:
        raise AttributeError(f"{mod.__name__!r} does not define a PromptMigrate migration")
    return mod  # type: ignore[return‑value]
