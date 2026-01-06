"""Layout definitions and calculations for tmux panes."""

# tmux built-in layouts that we support
TMUX_LAYOUTS = {
    "even-horizontal": "Panes spread evenly left to right",
    "even-vertical": "Panes spread evenly top to bottom",
    "main-horizontal": "Large pane on top, others below",
    "main-vertical": "Large pane on left, others on right",
    "tiled": "Panes arranged in grid pattern",
}

# Default layout if none specified
DEFAULT_LAYOUT = "even-horizontal"


def is_valid_layout(layout: str) -> bool:
    """Check if a layout name is valid."""
    return layout in TMUX_LAYOUTS


def get_layout_description(layout: str) -> str:
    """Get the description of a layout."""
    return TMUX_LAYOUTS.get(layout, "Unknown layout")


def get_split_commands(num_panes: int, layout: str) -> list[list[str]]:
    """
    Generate tmux split commands to create the required number of panes.

    Args:
        num_panes: Number of panes to create
        layout: The tmux layout to apply

    Returns:
        List of tmux command arg lists to execute
    """
    if num_panes <= 1:
        return []

    commands: list[list[str]] = []

    if layout == "main-vertical":
        # Left pane (main) | right pane(s) stacked vertically
        # First split: horizontal to create left and right (65% left, 35% right)
        commands.append(["split-window", "-h", "-p", "35"])
        # Additional panes split the right side vertically
        for _ in range(num_panes - 2):
            commands.append(["split-window", "-v", "-t", "1"])
        commands.append(["select-pane", "-t", "0"])

    elif layout == "main-horizontal":
        # Top pane (main) | bottom pane(s) side by side
        commands.append(["split-window", "-v", "-p", "50"])
        for _ in range(num_panes - 2):
            commands.append(["split-window", "-h", "-t", "1"])
        commands.append(["select-pane", "-t", "0"])

    elif layout == "even-horizontal":
        # All panes side by side
        for _ in range(num_panes - 1):
            commands.append(["split-window", "-h"])
        commands.append(["select-layout", "even-horizontal"])
        commands.append(["select-pane", "-t", "0"])

    elif layout == "even-vertical":
        # All panes stacked
        for _ in range(num_panes - 1):
            commands.append(["split-window", "-v"])
        commands.append(["select-layout", "even-vertical"])
        commands.append(["select-pane", "-t", "0"])

    else:  # tiled or unknown
        for _ in range(num_panes - 1):
            commands.append(["split-window"])
        commands.append(["select-layout", "tiled"])
        commands.append(["select-pane", "-t", "0"])

    return commands
