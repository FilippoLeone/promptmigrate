"""Example showing how to use auto-revision to create migrations from manual changes."""

import argparse
import os
import time
from pathlib import Path

import yaml

from promptmigrate import enable_auto_revision
from promptmigrate import promptmanager as pm
from promptmigrate.autorevision import create_revision_from_changes, detect_changes


def main():
    """Demonstrate auto-revision functionality."""
    parser = argparse.ArgumentParser(description="Auto-revision example")
    parser.add_argument("--enable", action="store_true", help="Enable auto-revision")
    parser.add_argument("--watch", action="store_true", help="Enable file watching")
    parser.add_argument("--edit", action="store_true", help="Simulate manual edits to prompts.yaml")
    parser.add_argument(
        "--create", action="store_true", help="Create revision from current changes"
    )
    args = parser.parse_args()

    if args.enable:
        # Enable auto-revision with optional file watching
        enable_auto_revision(watch=args.watch)
        print(f"✅ Auto-revision enabled (watch mode: {args.watch})")

    if args.edit:
        # Simulate a manual edit to prompts.yaml
        prompt_file = Path("prompts.yaml")

        # Read current prompts
        if prompt_file.exists():
            with open(prompt_file, "r") as f:
                prompts = yaml.safe_load(f) or {}
        else:
            prompts = {}

        # Make changes
        prompts["MANUAL_EDIT"] = (
            f"This prompt was manually added at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        if "SYSTEM" in prompts:
            prompts["SYSTEM"] = "Updated system prompt via manual edit"
        else:
            prompts["SYSTEM"] = "New system prompt via manual edit"

        # Write back to file
        with open(prompt_file, "w") as f:
            yaml.dump(prompts, f)

        print("✅ Made manual edits to prompts.yaml")

    if args.create:
        # Detect and show changes
        added, modified, removed = detect_changes()

        # Display changes
        if added:
            print("\n➕ Added prompts:")
            for key in added:
                print(f"  - {key}")

        if modified:
            print("\n📝 Modified prompts:")
            for key in modified:
                print(f"  - {key}")

        if removed:
            print("\n❌ Removed prompts:")
            for key in removed:
                print(f"  - {key}")

        if not (added or modified or removed):
            print("No changes detected")
            return

        # Create revision
        rev_file = create_revision_from_changes(description="Created from manual edits example")
        if rev_file:
            print(f"\n✅ Created new revision at {rev_file}")
            print("Run 'promptmigrate upgrade' to apply this revision")
        else:
            print("\n❌ No revision created")


if __name__ == "__main__":
    main()
