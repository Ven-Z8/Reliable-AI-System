"""Unit tests for the sandboxed workspace abstraction - TDD red."""

from pathlib import Path

import pytest

from reliable_agent_platform.harness.workspace import PathEscapeError, Workspace


class TestConstruction:
    def test_root_is_created_and_resolved(self, tmp_path):
        root = tmp_path / "workspace"
        ws = Workspace(root)
        assert root.exists()
        assert ws.root == root.resolve()
        assert Path(ws.root).is_absolute()

    def test_existing_directory_accepted(self, tmp_path):
        ws = Workspace(tmp_path)
        assert ws.root == tmp_path.resolve()


class TestResolution:
    def test_relative_file_resolves_under_root(self, tmp_path):
        ws = Workspace(tmp_path / "ws")
        resolved = ws.resolve("src/module.py")
        assert resolved.is_absolute()
        assert resolved.is_relative_to(ws.root)
        assert resolved.name == "module.py"

    def test_uncreated_nested_paths_resolve_fine(self, tmp_path):
        ws = Workspace(tmp_path)
        resolved = ws.resolve("deep/never/seen/before.txt")
        assert resolved.parent == ws.root / "deep" / "never" / "seen"

    def test_dot_segments_collapse(self, tmp_path):
        ws = Workspace(tmp_path)
        assert ws.resolve("a/./b.txt") == ws.root / "a" / "b.txt"

    def test_plain_filename_at_root(self, tmp_path):
        ws = Workspace(tmp_path)
        assert ws.resolve("README.md") == ws.root / "README.md"


class TestBasicRejections:
    """The workspace never returns a path outside its root."""

    def test_absolute_input_rejected(self, tmp_path):
        ws = Workspace(tmp_path)
        with pytest.raises(PathEscapeError):
            ws.resolve("/etc/passwd")

    def test_parent_traversal_rejected(self, tmp_path):
        ws = Workspace(tmp_path)
        with pytest.raises(PathEscapeError):
            ws.resolve("../outside.txt")
