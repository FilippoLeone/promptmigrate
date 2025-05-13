"""Command‑line interface powered by *click*."""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import Optional

import click

from . import __version__, logger
from .autorevision import create_revision_from_changes, detect_changes
from .manager import PromptManager, load_revision_module

_pkg_name = "promptmigrate_revisions"


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="promptmigrate")
def cli() -> None:
    """Prompt schema migrations for LLM applications."""


@cli.command("init")
@click.option("--package", "pkg", default=_pkg_name, help="Package where revisions live.")
def init_cmd(pkg: str) -> None:
    path = Path(pkg.replace(".", "/"))
    path.mkdir(parents=True, exist_ok=True)
    (path / "__init__.py").touch(exist_ok=True)
    click.echo(f"✅ Created revisions package at {path}")


@cli.command("upgrade")
@click.option("--to", "target", help="Target revision (inclusive)")
@click.option("--package", "pkg", default=_pkg_name, help="Revisions package")
def upgrade_cmd(target: Optional[str], pkg: str) -> None:
    try:
        pkg_mod = importlib.import_module(pkg)
    except ModuleNotFoundError as exc:
        raise click.ClickException(f"Revisions package {pkg!r} not found") from exc

    for _, name, _ in pkgutil.walk_packages(pkg_mod.__path__, f"{pkg_mod.__name__}."):
        load_revision_module(name)

    mgr = PromptManager()
    mgr.upgrade(target)
    click.echo("🎉 Prompt migrations complete.")


@cli.command("current")
def current_cmd() -> None:
    mgr = PromptManager()
    click.echo(mgr.current_rev() or "<none>")


@cli.command("list")
def list_cmd() -> None:
    """List all available migrations."""
    mgr = PromptManager()
    migrations = mgr.list_migrations()
    current = mgr.current_rev()

    if not migrations:
        click.echo("No migrations found.")
        return

    click.echo("Available migrations:")
    for migration in migrations:
        if current and migration.rev_id <= current:
            status = "[applied]"
        else:
            status = "[pending]"

        click.echo(f"{migration.rev_id}: {migration.description} {status}")


@cli.command("auto-revision")
@click.option("--description", "-d", help="Custom description for the auto-generated revision")
@click.option("--package", "pkg", default=_pkg_name, help="Package where revision will be created")
@click.option("--dry-run", is_flag=True, help="Only show changes without creating a revision")
def auto_revision_cmd(description: Optional[str], pkg: str, dry_run: bool) -> None:
    """Detect manual changes to prompts.yaml and create a revision automatically."""
    # Ensure package exists
    path = Path(pkg.replace(".", "/"))
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        (path / "__init__.py").touch(exist_ok=True)
        click.echo(f"✅ Created revisions package at {path}")

    # Get changes
    added, modified, removed = detect_changes()

    if not any([added, modified, removed]):
        click.echo("No changes detected in prompts.yaml compared to the current revision state.")
        return

    # Show changes
    click.echo("Changes detected in prompts.yaml:")

    if added:
        click.echo("\n✨ Added prompts:")
        for key in added:
            click.echo(f"  - {key}")

    if modified:
        click.echo("\n📝 Modified prompts:")
        for key in modified:
            click.echo(f"  - {key}")

    if removed:
        click.echo("\n🗑️ Removed prompts:")
        for key in removed:
            click.echo(f"  - {key}")

    if dry_run:
        click.echo(
            "\n🔍 Dry run - no revision created. Run without --dry-run to create the revision."
        )
        return

    # Create revision
    desc = description or "Auto-generated from manual changes to prompts.yaml"
    rev_file = create_revision_from_changes(description=desc)

    if rev_file:
        click.echo(f"\n✅ Created new revision at {rev_file}")
        click.echo("Run 'promptmigrate upgrade' to apply this revision.")
    else:
        click.echo("\n❌ Failed to create revision file.")
