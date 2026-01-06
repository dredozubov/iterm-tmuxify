"""CLI for iterm-tmuxify."""

import sys

import click

from . import __version__
from .config import get_config_dir, list_configs, load_config, validate_config
from .tmux import attach_session, kill_session, list_sessions, session_exists, start_or_attach


@click.group()
@click.version_option(version=__version__)
def main():
    """Native iTerm panes with tmux session persistence."""
    pass


@main.command()
@click.argument("name")
def start(name: str):
    """Start a project session (or attach if already running).

    NAME is the project configuration name (without .yml extension).
    """
    try:
        project = load_config(name)
    except FileNotFoundError:
        click.echo(f"Error: Config not found: {name}", err=True)
        click.echo(f"Config directory: {get_config_dir()}", err=True)
        sys.exit(1)

    warnings = validate_config(project)
    for warning in warnings:
        click.echo(f"Warning: {warning}", err=True)

    start_or_attach(project)


@main.command()
@click.argument("name")
def attach(name: str):
    """Attach to an existing tmux session.

    NAME is the tmux session name.
    """
    if not session_exists(name):
        click.echo(f"Error: Session not found: {name}", err=True)
        click.echo("Running sessions:", err=True)
        for session in list_sessions():
            click.echo(f"  - {session}", err=True)
        sys.exit(1)

    attach_session(name, control_mode=True)


@main.command()
@click.argument("name")
def stop(name: str):
    """Stop a tmux session.

    NAME is the tmux session name.
    """
    if not session_exists(name):
        click.echo(f"Session not found: {name}", err=True)
        sys.exit(1)

    if kill_session(name):
        click.echo(f"Stopped session: {name}")
    else:
        click.echo(f"Failed to stop session: {name}", err=True)
        sys.exit(1)


@main.command("list")
@click.option("--configs", "-c", is_flag=True, help="List available configs instead of sessions")
def list_cmd(configs: bool):
    """List tmux sessions or available configs."""
    if configs:
        config_names = list_configs()
        if not config_names:
            click.echo(f"No configs found in {get_config_dir()}")
        else:
            click.echo("Available configs:")
            for name in config_names:
                click.echo(f"  - {name}")
    else:
        sessions = list_sessions()
        if not sessions:
            click.echo("No tmux sessions running")
        else:
            click.echo("Running sessions:")
            for session in sessions:
                click.echo(f"  - {session}")


@main.command()
@click.argument("name")
def edit(name: str):
    """Open a config file in your editor.

    NAME is the project configuration name.
    Creates a new config if it doesn't exist.
    """
    import os

    config_dir = get_config_dir()
    config_path = config_dir / f"{name}.yml"

    if not config_path.exists():
        # Create a template config
        template = f"""name: {name}
root: ~/workspace/{name}

windows:
  - name: main
    layout: main-vertical
    panes:
      -   # empty terminal
      -   # empty terminal

  - name: server
    command: echo "Add your server command here"
"""
        config_path.write_text(template)
        click.echo(f"Created new config: {config_path}")

    editor = os.environ.get("EDITOR", "vim")
    os.execvp(editor, [editor, str(config_path)])


@main.command()
@click.argument("name")
def show(name: str):
    """Show details of a project configuration.

    NAME is the project configuration name.
    """
    try:
        project = load_config(name)
    except FileNotFoundError:
        click.echo(f"Error: Config not found: {name}", err=True)
        sys.exit(1)

    click.echo(f"Project: {project.name}")
    click.echo(f"Root: {project.root}")
    click.echo(f"Windows: {len(project.windows)}")

    for i, window in enumerate(project.windows, 1):
        click.echo(f"\n  [{i}] {window.name}")
        click.echo(f"      Layout: {window.layout}")
        click.echo(f"      Panes: {len(window.panes)}")
        for j, pane in enumerate(window.panes, 1):
            cmd = pane.command or "(empty)"
            click.echo(f"        {j}. {cmd}")

    warnings = validate_config(project)
    if warnings:
        click.echo("\nWarnings:")
        for warning in warnings:
            click.echo(f"  - {warning}")


if __name__ == "__main__":
    main()
