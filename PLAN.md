# Plan: iterm-tmuxify - Native iTerm Panes with Session Persistence

## Problem Statement

User wants a tmuxinator-like experience but with:
1. **Native iTerm panes** (not tmux-drawn panes)
2. **Session persistence** (survives iTerm restarts)
3. **YAML configuration** (like tmuxinator)

**Current trade-off in existing tools:**
- Native panes (itermocil, itomate) = No persistence
- Session persistence (tmuxinator, tmuxifier) = tmux panes (not truly native)

---

## Research Findings

### Existing Tools Comparison

| Tool | Native iTerm Panes | Session Persistence | YAML Config | Maintained |
|------|-------------------|---------------------|-------------|------------|
| tmuxinator | No (tmux -CC converts) | Yes | Yes | **Yes** |
| tmuxifier | No (tmux -CC converts) | Yes | No (shell) | **Yes** |
| itermocil | **Yes** (AppleScript) | No | Yes | No (2022) |
| itomate | **Yes** (Python API) | No | Yes | No (2020) |

### iTerm2 Native Features

1. **Arrangements** - Save/restore layouts, but not running processes
2. **Session Restoration** - Survives crashes, but NOT reboots or Cmd+Q
3. **Python API** - Full programmatic control over windows/tabs/panes
4. **tmux -CC mode** - Maps tmux to native-looking UI, full persistence

### Key Insight

**Process persistence requires a session server.** That's what tmux provides. Without tmux (or similar), processes die when the terminal closes.

The `tmux -CC` mode is close - panes LOOK native but are tmux underneath. This is actually the right trade-off for persistence.

---

## Recommended Solution

### Approach: Enhanced tmux -CC Wrapper

Build **iterm-tmuxify** - a Python CLI that:
1. Reads YAML config (like tmuxinator)
2. Creates tmux session with layout
3. Automatically attaches with `-CC` for native iTerm UI
4. Handles edge cases better than tmuxinator's -CC bolt-on

**Why this approach:**
- Full session persistence (tmux server)
- Native-looking iTerm panes via -CC mode
- YAML configuration
- Relatively simple to implement
- Designed for -CC from the start (not added later)

---

## Implementation Plan

### Phase 1: MVP

**Config format:**
```yaml
# ~/.config/iterm-tmuxify/directoryresearch.yml
name: directoryresearch
root: ~/workspace/directoryresearch/directoryresearch.com

windows:
  - name: dev
    layout: main-vertical  # left 60%, right split top/bottom
    panes:
      - claude
      -   # empty terminal
      -   # empty terminal

  - name: docker
    command: docker compose up

  - name: api
    command: docker compose logs -f api

  - name: prefect
    command: docker compose logs -f prefect

  - name: worker
    command: docker compose logs -f worker
```

**CLI:**
```bash
# Creates tmux session, attaches with -CC
iterm-tmuxify start directoryresearch

# Reattach after iTerm restart
iterm-tmuxify attach directoryresearch

# List sessions
iterm-tmuxify list

# Stop session
iterm-tmuxify stop directoryresearch
```

### Phase 2: Polish

- Auto-detect existing session (attach vs create)
- Better pane sizing in -CC mode
- Shell completion (zsh, bash)
- Validation of config files

### Phase 3: (Optional) iTerm2 Contributions

Submit PRs for quality-of-life improvements:
- Per-pane "send text at start" in arrangements
- Fix tab name restoration bug (#2692)
- Better directory preservation

---

## Project Structure

```
~/workspace/iterm-tmuxify/
├── README.md
├── PLAN.md                 # This plan
├── pyproject.toml
├── src/
│   └── iterm_tmuxify/
│       ├── __init__.py
│       ├── cli.py          # Click CLI
│       ├── config.py       # YAML parsing
│       ├── tmux.py         # tmux session management
│       └── layouts.py      # Layout calculations
├── configs/
│   └── example.yml
└── tests/
    └── test_config.py
```

---

## Key Differences from tmuxinator

| Feature | tmuxinator | iterm-tmuxify |
|---------|------------|---------------|
| -CC mode | Bolt-on (hooks) | Native design |
| Attach behavior | Separate command | Auto-detect |
| Config complexity | Many options | Focused on common cases |
| Ruby dependency | Yes | No (Python) |
| iTerm-specific | No | Yes |

---

## Next Steps

1. Create project at `~/workspace/iterm-tmuxify`
2. Implement basic YAML → tmux -CC flow
3. Test with directoryresearch project
4. Iterate based on actual usage

---

## Research Sources

- [tmuxinator GitHub](https://github.com/tmuxinator/tmuxinator)
- [tmuxifier GitHub](https://github.com/jimeh/tmuxifier)
- [itermocil GitHub](https://github.com/TomAnthony/itermocil)
- [itomate GitHub](https://github.com/kamranahmedse/itomate)
- [iTerm2 tmux Integration](https://iterm2.com/documentation-tmux-integration.html)
- [iTerm2 Python API](https://iterm2.com/python-api/)
- [iTerm2 Arrangements](https://iterm2.com/documentation-preferences-arrangements.html)
- [iTerm2 GitLab Issues](https://gitlab.com/gnachman/iterm2/-/issues)
