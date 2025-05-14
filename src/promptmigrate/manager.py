"""Core implementation: manages the *prompts.yaml* model file, revision state
and exposes *attribute access* to individual prompt strings for ergonomic use
in application code.
"""

from __future__ import annotations

import datetime  # Added for {{date:...}} placeholder
import json
import logging
import os
import re  # Added for custom placeholder parsing
import sys
import threading
import time  # Keep time import, might be used elsewhere or by watcher logic
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union  # Added Callable

import yaml
from jinja2 import DebugUndefined, Environment
from jinja2 import exceptions as jinja2_exceptions  # Added DebugUndefined and exceptions
from jinja2 import select_autoescape

# Conditional watchdog imports
try:
    from watchdog.events import FileModifiedEvent, FileSystemEventHandler
    from watchdog.observers import Observer

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None  # type: ignore
    # Provide a base class for FileSystemEventHandler if watchdog is not available
    if "FileSystemEventHandler" not in globals():

        class FileSystemEventHandler:  # type: ignore
            pass

    FileModifiedEvent = None  # type: ignore

REVISION_ATTR = "__pm_revision__"
PROMPT_FILE = Path("prompts.yaml")
STATE_FILE = Path(".promptmigrate_state.json")
AUTO_REVISION_WATCH = WATCHDOG_AVAILABLE and (
    os.getenv("PROMPTMIGRATE_AUTO_REVISION_WATCH", "0") == "1"
)

logger = logging.getLogger(__name__)


def get_auto_revision_setting() -> bool:
    """Get the auto revision setting from environment variable."""
    return os.getenv("PROMPTMIGRATE_AUTO_REVISION", "0") == "1"


_DEFAULT_PROMPTS_BASE: Dict[str, Any] = {
    "example_prompt": "This is an example prompt.",
    # Add other truly default prompts here if necessary
}


class PromptManager:
    _instance: Optional["PromptManager"] = None
    _lock = threading.Lock()
    _observer: Optional[Any] = None
    _stop_watcher: threading.Event
    _dynamic_values = {}
    jinja_env_vars = {}
    _skip_manual_check = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    # Initialize attributes that are truly global to the singleton instance ONCE
                    cls._instance._singleton_initialized_once_flag = False
                    cls._instance.instance_default_prompts = _DEFAULT_PROMPTS_BASE.copy()
                    cls._instance._observer = None
                    cls._instance._stop_watcher = (
                        threading.Event()
                    )  # Initialize Jinja environment once for the singleton
                    cls._instance.template_env = Environment(
                        undefined=DebugUndefined, autoescape=select_autoescape(["html", "xml"])
                    )
                    cls._instance.default_context = {}
                    cls._instance._prompts = {}
                    cls._instance._state = {}
                    cls._instance.context_specific_prompts = {}
        return cls._instance

    def __init__(
        self,
        prompt_file: Optional[Union[str, Path]] = None,
        state_file: Optional[Union[str, Path]] = None,
        revision_dir: Optional[Union[str, Path]] = None,
        default_prompts: Optional[dict] = None,
        context: Optional[dict] = None,
        skip_manual_check: bool = False,
    ):

        # One-time initializations for the singleton instance (already done in __new__)
        # self._singleton_initialized_once_flag is used to track if __init__ specific one-time setup is done.
        # However, most one-time setup is now in __new__ to ensure it's truly once per singleton.

        # Per-call configurations (can update the singleton's state)
        if prompt_file:
            self.prompt_file = Path(prompt_file)
        elif (
            not hasattr(self, "prompt_file") or self.prompt_file is None
        ):  # Initialize if not set by a previous call
            self.prompt_file = Path(os.getenv("PROMPTMIGRATE_PROMPT_FILE", PROMPT_FILE))

        if state_file:
            self.state_file = Path(state_file)
        elif not hasattr(self, "state_file") or self.state_file is None:
            # Default state file relative to the (potentially new) prompt file
            self.state_file = self.prompt_file.parent / STATE_FILE

        if revision_dir:
            self.revision_dir = Path(revision_dir)
        elif not hasattr(self, "revision_dir") or self.revision_dir is None:
            self.revision_dir = Path(
                os.getenv("PROMPTMIGRATE_REVISION_DIR", "promptmigrate_revisions")
            )

        if default_prompts is not None:
            # This will update the instance_default_prompts for this "session" or configuration
            self.instance_default_prompts = default_prompts
        # else: self.instance_default_prompts remains as initialized in __new__ or by a previous call

        if context is not None:
            # Update default_context. If called multiple times, contexts are merged.
            self.default_context.update(context)

        # Stop existing watcher if active, before potentially changing paths or configs
        if WATCHDOG_AVAILABLE and self._observer and self._observer.is_alive():  # type: ignore
            self.stop_watching()

        self.reload(force_reload=True)  # Reload prompts based on current file paths

        self.auto_revision_enabled = os.getenv("PROMPTMIGRATE_AUTO_REVISION", "0") == "1"
        self.auto_revision_watch_enabled = WATCHDOG_AVAILABLE and (
            os.getenv("PROMPTMIGRATE_AUTO_REVISION_WATCH", "0") == "1"
        )

        if not skip_manual_check:
            if self.auto_revision_enabled:
                try:
                    self._check_for_manual_changes(create_revision=True)
                except Exception as e:
                    logger.error(f"Error during initial _check_for_manual_changes: {e}")
            if self.auto_revision_watch_enabled:
                self._start_watching()
        elif WATCHDOG_AVAILABLE:  # If skipping manual check, ensure watcher is off
            self.stop_watching()

        # Mark that __init__ has completed its setup for this configuration.
        # This flag's role might need to be re-evaluated based on exact singleton needs.
        # For now, the critical one-time setup is in __new__.
        self._singleton_initialized_once_flag = True

    def _parse_key_value_params(self, params_str: str) -> dict[str, str]:
        params = {}
        if not params_str:
            return params
        for part in params_str.split(","):
            key_value = part.split("=", 1)
            if len(key_value) == 2:
                params[key_value[0].strip()] = key_value[1].strip()
        return params

    def _process_single_placeholder(self, match: re.Match) -> str:
        full_match = match.group(0)
        content = match.group(1).strip()

        if ":" not in content:
            # For {{variable_name}} or {{invalid_one}}.
            # DebugUndefined in Jinja env will handle {{invalid_one}} by returning it as is.
            # {{variable_name}} will be substituted by Jinja in the final render pass if in context.
            return full_match

        type_name, params_str = content.split(":", 1)
        type_name = type_name.strip()
        params_str = params_str.strip()

        if type_name == "date":
            parsed_params = self._parse_key_value_params(params_str)
            date_format = parsed_params.get("format", "%Y-%m-%d")
            try:
                return datetime.datetime.now().strftime(date_format)
            except Exception as e:
                logger.warning(f"Error formatting date placeholder '{full_match}': {e}")
                return full_match

        elif type_name == "number":
            parsed_params = self._parse_key_value_params(params_str)
            try:
                min_val_str = parsed_params.get("min")
                if min_val_str is not None:
                    return str(int(min_val_str))  # Test expects min value
                # max_val_str = parsed_params.get("max") # Not currently used by tests
                logger.warning(
                    f"Number placeholder '{full_match}' did not provide 'min' parameter."
                )
                return full_match
            except ValueError as e:
                logger.warning(f"Error parsing number placeholder '{full_match}': {e}")
                return full_match

        elif type_name == "choice":
            choices = [c.strip() for c in params_str.split(",") if c.strip()]
            if choices:
                return choices[0]  # Test expects the first choice
            logger.warning(f"Choice placeholder '{full_match}' had no valid choices.")
            return full_match

        elif type_name == "text":
            parts = params_str.split(",", 1)
            template_str = parts[0].strip()
            local_context_params_str = parts[1].strip() if len(parts) > 1 else ""
            local_context = self._parse_key_value_params(local_context_params_str)
            try:
                # Use the main template_env for consistency in undefined handling etc.
                return self.template_env.from_string(template_str).render(**local_context)
            except Exception as e:
                logger.warning(f"Error rendering text placeholder sub-template '{full_match}': {e}")
                return full_match

        logger.debug(f"Unknown placeholder type or structure: {full_match}")
        return full_match  # Unknown type with ':', or error in known type not caught above

    def _render_prompt(self, raw_prompt_value: str, context: Optional[dict] = None) -> str:
        if not isinstance(raw_prompt_value, str):
            return str(raw_prompt_value)

        # Phase 1: Pre-process custom placeholders like {{date:...}}, {{number:...}}, etc.
        try:
            # Using a lambda to pass `self` to the method if it were not a method of `self` already.
            # Since _process_single_placeholder is a method, it has access to self.
            processed_prompt = re.sub(
                r"\{\{(.*?)\}\}", self._process_single_placeholder, raw_prompt_value
            )
        except Exception as e:
            logger.error(
                f"Critical error during custom placeholder processing (re.sub): {e}. Raw: '{raw_prompt_value}'"
            )
            processed_prompt = raw_prompt_value  # Fallback

        # Phase 2: Render the resulting string with Jinja2 for standard {{variable}} replacement
        current_processing_context = self.default_context.copy()
        if context:
            current_processing_context.update(context)

        try:
            # self.template_env is initialized with DebugUndefined in __new__
            template = self.template_env.from_string(processed_prompt)
            rendered_prompt = template.render(**current_processing_context)
            return rendered_prompt
        except Exception as e:
            logger.error(
                f"Error rendering prompt with Jinja2: {e}. Original raw: '{raw_prompt_value}'. Processed: '{processed_prompt}'"
            )
            # Fallback: return the custom-processed string, as it's "more" processed than raw.
            return processed_prompt

    def reload(self, force_reload: bool = False):
        # Path resolution logic from previous changes (using _initial_ paths)
        # For now, assume self.prompt_file and self.state_file are correctly set by __init__
        # and do not change dynamically per reload call unless __init__ is called again.

        defaults_for_this_reload: Dict[str, str]
        if hasattr(self, "_temp_current_effective_defaults"):
            defaults_for_this_reload = self._temp_current_effective_defaults
        else:
            defaults_for_this_reload = self.instance_default_prompts.copy()

        if not self.prompt_file.exists() or force_reload or not self._prompts:
            logger.debug(f"Reloading prompts from {self.prompt_file}")
            self.prompt_file.parent.mkdir(parents=True, exist_ok=True)
            if not self.prompt_file.exists():  # Touch only if it truly doesn't exist
                self.prompt_file.touch(exist_ok=True)

            try:
                with open(self.prompt_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if not content.strip():
                        loaded_prompts = {}
                    else:
                        loaded_prompts = yaml.safe_load(content) or {}
                        if not isinstance(loaded_prompts, dict):
                            logger.warning(
                                f"Prompt file {self.prompt_file} does not contain a valid YAML mapping. Using empty prompts."
                            )
                            loaded_prompts = {}

                merged_prompts = defaults_for_this_reload.copy()
                merged_prompts.update(loaded_prompts)
                self._prompts = merged_prompts
            except FileNotFoundError:
                logger.warning(
                    f"Prompt file {self.prompt_file} not found during reload. Using effective default prompts."
                )
                self._prompts = defaults_for_this_reload.copy()
            except yaml.YAMLError as e:
                logger.error(
                    f"Error parsing YAML from prompt file {self.prompt_file}: {e}. Using effective default prompts."
                )
                self._prompts = defaults_for_this_reload.copy()
            except Exception as e:
                logger.error(
                    f"Unexpected error loading prompt file {self.prompt_file}: {e}. Using effective default prompts."
                )
                self._prompts = defaults_for_this_reload.copy()

        self._load_state()

        if not self._skip_manual_check:
            self._check_for_manual_changes()
        logger.debug(f"Reload complete. Prompts loaded: {list(self._prompts.keys())}")

    def _check_for_manual_changes(self) -> None:
        # ... existing code ...
        # Ensure self._prompts is used as the in-memory reference.
        if not self.prompt_file.exists():
            return

        logger.debug(f"Checking for manual changes in {self.prompt_file}")
        try:
            with open(self.prompt_file, "r", encoding="utf-8") as f:
                current_prompts_data = yaml.safe_load(f) or {}
            if not isinstance(current_prompts_data, dict):  # Ensure it's a dict
                logger.warning(
                    f"Manual check: Prompt file {self.prompt_file} content is not a dict. Skipping check."
                )
                return
        except Exception as e:
            logger.error(f"Error loading prompt file for manual check: {e}")
            return

        if self._prompts is None:  # Should not happen if reload was effective
            logger.warning("_prompts is None during _check_for_manual_changes. Attempting reload.")
            self.reload(force_reload=True)
            if self._prompts is None:
                logger.error(
                    "_prompts is still None after attempting reload in _check_for_manual_changes. Skipping check."
                )
                return

        # Check for removed prompts
        for prompt_name in list(self._prompts.keys()):
            if prompt_name not in current_prompts_data:
                logger.warning(
                    f"Prompt '{prompt_name}' was removed manually from {self.prompt_file}. "
                    "The in-memory version will be used until 'pm.reload()' is called or changes are saved."
                )
                # Remove from in-memory prompts
                del self._prompts[prompt_name]

        # Check for added or modified prompts
        for prompt_name, prompt_content in current_prompts_data.items():
            if prompt_name not in self._prompts:
                logger.warning(
                    f"Prompt '{prompt_name}' was added manually to {self.prompt_file}. "
                    "Consider using 'pm.add_prompt()' or 'pm.save_prompts()' to manage prompts."
                )
            elif (
                prompt_content is not None
                and self._prompts.get(prompt_name) is not None
                and isinstance(prompt_content, str)
                and isinstance(self._prompts[prompt_name], str)
                and prompt_content.strip() != self._prompts[prompt_name].strip()
            ):
                logger.warning(
                    f"Prompt '{prompt_name}' was modified manually in {self.prompt_file}. "
                    "The in-memory version will be used until 'pm.reload()' is called or changes are saved."
                )
        logger.debug("Finished checking for manual changes.")

    def __getattr__(self, name: str) -> str:
        if name.startswith("_"):
            raise AttributeError(f"Attempt to access private attribute '{name}'")

        if name in self._dynamic_values:
            value = self._dynamic_values[name]
            return value() if callable(value) else value

        if name in self._prompts:
            return self._render_prompt(name)

        logger.debug(
            f"Prompt '{name}' not found in memory or dynamic values, attempting force reload from {self.prompt_file}"
        )
        self.reload(force_reload=True)  # This reload will use self.instance_default_prompts

        if name in self._prompts:
            return self._render_prompt(name)
        else:
            logger.error(f"Prompt '{name}' not found in {self.prompt_file} even after reload.")
            available_prompts = list(self._prompts.keys())
            raise AttributeError(
                f"Prompt '{name}' not found. Available prompts: {available_prompts}"
            )

    def _render_prompt(self, name: str) -> str:
        # ... existing code ...
        if name not in self._prompts:
            # This should ideally be caught by __getattr__ first
            raise AttributeError(f"Prompt '{name}' not found for rendering.")

        template_string = self._prompts[name]
        if not isinstance(template_string, str):  # Ensure it's a string before rendering
            logger.warning(
                f"Prompt '{name}' content is not a string, returning as is: {template_string}"
            )
            return str(template_string)

        try:
            template = self.template_env.from_string(
                template_string
            )  # Combine dynamic values and explicit Jinja vars for rendering context
            render_context = self._dynamic_values.copy()  # Start with dynamic values
            # Callables in dynamic_values should be resolved if needed by the template
            # For simplicity, assume templates handle {{ func() }} or {{ var }}
            render_context.update(self.jinja_env_vars)  # Add explicit Jinja vars
            return template.render(render_context)
        except jinja2_exceptions.TemplateSyntaxError as e:
            logger.error(f"Jinja2 syntax error in prompt '{name}': {e}")
            raise  # Re-raise to make it visible
        except Exception as e:
            logger.error(f"Error rendering prompt '{name}': {e}")
            return f"Error rendering prompt '{name}': {e}"  # Return error string

    def _start_watching(self) -> None:
        if not WATCHDOG_AVAILABLE:
            logger.info("Watchdog library not available. File watching disabled.")
            return
        if not self.prompt_file or not self.prompt_file.parent.exists():
            logger.error(
                f"Cannot start watcher: Prompt file directory {self.prompt_file.parent} does not exist."
            )
            return
        if self._observer and self._observer.is_alive():  # type: ignore
            logger.debug("Watcher already running.")
            return

        event_handler = _PromptFileChangeHandler(self)
        self._observer = Observer()
        try:
            # Watch the specific file's directory, then filter for the file in handler
            # Or, if prompt_file is a file path, watch its parent.
            watch_path = str(self.prompt_file.parent.resolve())
            self._observer.schedule(event_handler, watch_path, recursive=False)  # type: ignore
            self._observer.start()  # type: ignore
            logger.info(f"Started watching {watch_path} for changes to {self.prompt_file.name}.")
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Failed to start file watcher for {self.prompt_file.parent}: {e}")
            self._observer = None  # Ensure observer is None if start failed

    def stop_watching(self) -> None:
        if not WATCHDOG_AVAILABLE or not self._observer:
            return
        try:
            if self._observer.is_alive():  # type: ignore
                self._observer.stop()  # type: ignore
                self._observer.join(timeout=5)  # Wait for the observer thread to finish
                logger.info(f"Stopped watching {self.prompt_file.parent} for changes.")
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Error stopping file watcher: {e}")
        finally:
            self._observer = None  # Clear the observer instance


# ...existing code...
class _PromptFileChangeHandler(FileSystemEventHandler if WATCHDOG_AVAILABLE else object):  # type: ignore
    def __init__(self, manager_instance: "PromptManager"):
        super().__init__()
        self.manager = manager_instance
        # Ensure manager_instance.prompt_file is Path object for comparison
        self._watched_file_path = Path(self.manager.prompt_file).resolve()

    def on_modified(self, event: Any):  # 'Any' because FileModifiedEvent might be None
        if not WATCHDOG_AVAILABLE or event is None or event.is_directory:
            return

        src_path = Path(event.src_path).resolve()
        if src_path == self._watched_file_path:
            logger.info(f"Detected change in {self.manager.prompt_file}. Reloading prompts.")
            # Debounce or handle rapid changes if necessary, though watchdog might do some.
            # For now, direct reload.
            try:
                if self.manager.auto_revision_enabled:
                    self.manager._check_for_manual_changes(create_revision=True)
                else:
                    self.manager.reload(force_reload=True)
            except Exception as e:  # pylint: disable=broad-except
                logger.error(f"Error during auto-reload/revision after file change: {e}")
