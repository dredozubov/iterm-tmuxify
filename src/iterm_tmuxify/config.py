"""YAML configuration parsing for iterm-tmuxify."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class Pane:
    """Represents a single pane in a window."""

    command: Optional[str] = None

    @classmethod
    def from_yaml(cls, data) -> "Pane":
        """Create a Pane from YAML data."""
        if data is None or data == "":
            return cls()
        if isinstance(data, str):
            return cls(command=data)
        if isinstance(data, dict):
            return cls(command=data.get("command"))
        return cls()


@dataclass
class Window:
    """Represents a window with one or more panes."""

    name: str
    layout: str = "even-horizontal"
    panes: list[Pane] = field(default_factory=list)
    command: Optional[str] = None

    @classmethod
    def from_yaml(cls, data: dict) -> "Window":
        """Create a Window from YAML data."""
        name = data.get("name", "unnamed")
        layout = data.get("layout", "even-horizontal")
        command = data.get("command")

        panes = []
        panes_data = data.get("panes", [])
        if panes_data:
            for pane_data in panes_data:
                panes.append(Pane.from_yaml(pane_data))
        elif command:
            # Single command window = single pane with that command
            panes.append(Pane(command=command))
        else:
            # Empty window = single empty pane
            panes.append(Pane())

        return cls(name=name, layout=layout, panes=panes, command=command)


@dataclass
class Project:
    """Represents a complete project configuration."""

    name: str
    root: str
    title: str = ""
    windows: list[Window] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, data: dict) -> "Project":
        """Create a Project from YAML data."""
        name = data.get("name", "unnamed")
        root = data.get("root", "~")
        title = data.get("title", "") or name  # Default to name if not set

        windows = []
        for window_data in data.get("windows", []):
            windows.append(Window.from_yaml(window_data))

        return cls(name=name, root=root, title=title, windows=windows)

    @property
    def expanded_root(self) -> Path:
        """Return the root path with ~ expanded."""
        return Path(self.root).expanduser()


def get_config_dir() -> Path:
    """Get the configuration directory."""
    config_dir = Path.home() / ".config" / "iterm-tmuxify"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def list_configs() -> list[str]:
    """List all available configuration names."""
    config_dir = get_config_dir()
    configs = []
    for path in config_dir.glob("*.yml"):
        configs.append(path.stem)
    for path in config_dir.glob("*.yaml"):
        configs.append(path.stem)
    return sorted(set(configs))


def load_config(name: str) -> Project:
    """Load a project configuration by name."""
    config_dir = get_config_dir()

    # Try .yml first, then .yaml
    config_path = config_dir / f"{name}.yml"
    if not config_path.exists():
        config_path = config_dir / f"{name}.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {name}")

    with open(config_path) as f:
        data = yaml.safe_load(f)

    return Project.from_yaml(data)


def validate_config(project: Project) -> list[str]:
    """Validate a project configuration. Returns list of warnings."""
    warnings = []

    if not project.name:
        warnings.append("Project name is empty")

    if not project.windows:
        warnings.append("Project has no windows defined")

    root_path = project.expanded_root
    if not root_path.exists():
        warnings.append(f"Root directory does not exist: {project.root}")

    return warnings
