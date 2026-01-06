"""tmux session management for iterm-tmuxify."""

import os
import subprocess
import sys
from typing import Optional

from .config import Project, Window
from .layouts import get_split_commands


def run_tmux(*args: str, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a tmux command."""
    cmd = ["tmux"] + list(args)
    return subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
    )


def session_exists(name: str) -> bool:
    """Check if a tmux session exists."""
    result = run_tmux("has-session", "-t", name)
    return result.returncode == 0


def list_sessions() -> list[str]:
    """List all tmux sessions."""
    result = run_tmux("list-sessions", "-F", "#{session_name}")
    if result.returncode != 0:
        return []
    return [s.strip() for s in result.stdout.strip().split("\n") if s.strip()]


def kill_session(name: str) -> bool:
    """Kill a tmux session."""
    result = run_tmux("kill-session", "-t", name)
    return result.returncode == 0


def create_session(project: Project) -> bool:
    """
    Create a tmux session from a project configuration.

    Returns True if session was created successfully.
    """
    if session_exists(project.name):
        return False

    root_dir = str(project.expanded_root)

    # Create the session with the first window
    first_window = project.windows[0] if project.windows else None
    # Use project title for the tab name
    tab_name = project.title

    result = run_tmux(
        "new-session",
        "-d",  # Detached
        "-s", project.name,
        "-n", tab_name,
        "-c", root_dir,
    )

    if result.returncode != 0:
        print(f"Failed to create session: {result.stderr}", file=sys.stderr)
        return False

    # Enable titles and set format to use window name
    run_tmux("set-option", "-t", project.name, "set-titles", "on")
    run_tmux("set-option", "-t", project.name, "set-titles-string", "#W")  # #W = window name
    run_tmux("set-option", "-t", project.name, "automatic-rename", "off")
    run_tmux("set-option", "-t", project.name, "allow-rename", "off")

    # Configure the first window
    if first_window:
        _setup_window(project.name, tab_name, first_window, root_dir)

    # Create additional windows
    for window in project.windows[1:]:
        _create_window(project.name, window, root_dir)

    # Force rename the first window to override any shell title changes
    run_tmux("rename-window", "-t", f"{project.name}:0", tab_name)

    return True


def _create_window(session: str, window: Window, root_dir: str) -> None:
    """Create a new window in the session."""
    run_tmux(
        "new-window",
        "-t", session,
        "-n", window.name,
        "-c", root_dir,
    )
    _setup_window(session, window.name, window, root_dir)


def _setup_window(session: str, window_name: str, window: Window, root_dir: str) -> None:
    """Set up panes and commands in a window."""
    target = f"{session}:{window_name}"
    num_panes = len(window.panes)

    # Create additional panes
    split_commands = get_split_commands(num_panes, window.layout)
    for cmd_args in split_commands:
        # Add target and directory to split-window commands
        if cmd_args[0] == "split-window":
            run_tmux(*cmd_args, "-t", target, "-c", root_dir)
        else:
            run_tmux(*cmd_args, "-t", target)

    # Set pane titles and send commands to each pane
    for i, pane in enumerate(window.panes):
        pane_target = f"{target}.{i}"
        # Set pane title to window name (this is what iTerm displays)
        run_tmux("select-pane", "-t", pane_target, "-T", window_name)
        if pane.command:
            run_tmux("send-keys", "-t", pane_target, pane.command, "Enter")


def attach_session(name: str, control_mode: bool = True) -> None:
    """
    Attach to a tmux session.

    Args:
        name: Session name to attach to
        control_mode: If True, use -CC for iTerm2 integration
    """
    if control_mode:
        # Create a new tab that runs tmux -CC directly
        # After tmux exits, check if session still exists:
        # - If yes (user detached): keep tab open with shell
        # - If no (user closed windows): exit cleanly
        applescript = f'''
            tell application "iTerm"
                tell current window
                    create tab with default profile command "/bin/zsh -l -c 'tmux -CC attach-session -t {name}; tmux has-session -t {name} 2>/dev/null && exec $SHELL'"
                end tell
            end tell
        '''
        subprocess.run(
            ["osascript", "-e", applescript],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        args = ["tmux", "attach-session", "-t", name]
        os.execvp("tmux", args)


def start_or_attach(project: Project) -> None:
    """
    Start a new session or attach to existing one.

    If the session doesn't exist, creates it and attaches.
    If it exists, just attaches.
    """
    if not session_exists(project.name):
        if not create_session(project):
            print(f"Failed to create session: {project.name}", file=sys.stderr)
            sys.exit(1)

    attach_session(project.name, control_mode=True)
