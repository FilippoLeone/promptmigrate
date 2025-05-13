"""Command‑line interface powered by *click*."""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import Optional

import click

from . import __version__, logger
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
