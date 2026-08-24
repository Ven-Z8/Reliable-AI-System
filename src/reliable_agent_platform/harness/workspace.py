"""Sandboxed workspace path resolution.

Every file path a worker wants to touch passes through :meth:`Workspace.resolve`
*before* any I/O. Resolution rejects non-normalized inputs outright (absolute,
drive-letter, backslash forms), collapses ``.``/``..`` segments, follows real
symlinks, and verifies the result stays inside the workspace root - so neither
lexical tricks nor symlink indirection can escape the sandbox.
"""

import re
from pathlib import Path, PurePosixPath


class PathEscapeError(Exception):
    """Raised when a requested path leaves the workspace boundary."""


_DRIVE_LETTER = re.compile(r"^[A-Za-z]:")


class Workspace:
    """A filesystem sandbox rooted at one directory."""

    def __init__(self, root: Path | str) -> None:
        root_path = Path(root)
        root_path.mkdir(parents=True, exist_ok=True)
        self._root = root_path.resolve()

    @property
    def root(self) -> Path:
        return self._root

    def resolve(self, relative: str) -> Path:
        """Resolve a workspace-relative path, refusing anything that escapes."""
        if not relative or not relative.strip():
            raise PathEscapeError("empty path")

        if "\\" in relative:
            raise PathEscapeError(
                f"path must use forward slashes, got backslash form: {relative!r}"
            )
        posix = PurePosixPath(relative)
        if posix.is_absolute() or relative.startswith("/") or _DRIVE_LETTER.match(relative):
            raise PathEscapeError(
                f"path must be workspace-relative, got absolute form: {relative!r}"
            )

        resolved = (self._root / Path(*posix.parts)).resolve()
        if not resolved.is_relative_to(self._root):
            raise PathEscapeError(f"path escapes the workspace: {relative!r} -> {resolved!r}")
        return resolved

    def validate_paths(self, relatives: list[str]) -> None:
        """Check every path; raise on the first violation (all-or-nothing gate)."""
        for relative in relatives:
            self.resolve(relative)
