"""Tests for config parsing."""

import pytest

from iterm_tmuxify.config import Pane, Project, Window


class TestPane:
    def test_empty_pane(self):
        pane = Pane.from_yaml(None)
        assert pane.command is None

    def test_string_command(self):
        pane = Pane.from_yaml("echo hello")
        assert pane.command == "echo hello"

    def test_dict_command(self):
        pane = Pane.from_yaml({"command": "echo hello"})
        assert pane.command == "echo hello"


class TestWindow:
    def test_simple_window(self):
        window = Window.from_yaml({"name": "main"})
        assert window.name == "main"
        assert window.layout == "even-horizontal"
        assert len(window.panes) == 1

    def test_window_with_command(self):
        window = Window.from_yaml({
            "name": "server",
            "command": "npm start"
        })
        assert window.name == "server"
        assert len(window.panes) == 1
        assert window.panes[0].command == "npm start"

    def test_window_with_panes(self):
        window = Window.from_yaml({
            "name": "dev",
            "layout": "main-vertical",
            "panes": ["vim", None, "htop"]
        })
        assert window.name == "dev"
        assert window.layout == "main-vertical"
        assert len(window.panes) == 3
        assert window.panes[0].command == "vim"
        assert window.panes[1].command is None
        assert window.panes[2].command == "htop"


class TestProject:
    def test_minimal_project(self):
        project = Project.from_yaml({
            "name": "test",
            "root": "~/test"
        })
        assert project.name == "test"
        assert project.root == "~/test"
        assert len(project.windows) == 0

    def test_full_project(self):
        project = Project.from_yaml({
            "name": "myapp",
            "root": "~/workspace/myapp",
            "windows": [
                {"name": "main"},
                {"name": "server", "command": "npm start"}
            ]
        })
        assert project.name == "myapp"
        assert len(project.windows) == 2
        assert project.windows[0].name == "main"
        assert project.windows[1].name == "server"
