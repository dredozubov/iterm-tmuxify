# iterm-tmuxify

Native iTerm panes with tmux session persistence.

## Installation

```bash
pip install iterm-tmuxify
```

## Usage

Create a config at `~/.config/iterm-tmuxify/<project>.yml`:

```yaml
name: myproject
root: ~/workspace/myproject

windows:
  - name: dev
    layout: main-vertical
    panes:
      - claude
      -   # empty terminal
      -   # empty terminal

  - name: docker
    command: docker compose up

  - name: logs
    command: docker compose logs -f
```

Then start your session:

```bash
# Start or attach to session
iterm-tmuxify start myproject

# List sessions
iterm-tmuxify list

# Stop session
iterm-tmuxify stop myproject
```

## Commands

- `start <name>` - Start a project session (or attach if already running)
- `attach <name>` - Attach to an existing tmux session
- `stop <name>` - Stop a tmux session
- `list` - List running sessions
- `list --configs` - List available configs
- `edit <name>` - Edit a config file
- `show <name>` - Show config details

## Layouts

Supports tmux built-in layouts:

- `even-horizontal` - Panes spread evenly left to right
- `even-vertical` - Panes spread evenly top to bottom
- `main-horizontal` - Large pane on top, others below
- `main-vertical` - Large pane on left, others on right
- `tiled` - Panes arranged in grid pattern
