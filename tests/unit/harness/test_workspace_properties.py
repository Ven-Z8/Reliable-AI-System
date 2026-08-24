"""Property-based tests for workspace path resolution (hypothesis)."""

import string

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from reliable_agent_platform.harness.workspace import PathEscapeError, Workspace

# Windows reserves device names; trailing dots/spaces are stripped by Win32 -
# both would make cross-platform resolution semantics murky, so exclude them.
_RESERVED = (
    {"con", "prn", "aux", "nul"}
    | {f"com{i}" for i in range(1, 10)}
    | {f"lpt{i}" for i in range(1, 10)}
)
_SAFE_CHARS = string.ascii_letters + string.digits + "_-"

_components = (
    st.text(alphabet=_SAFE_CHARS, min_size=1, max_size=12)
    .filter(lambda s: s.lower() not in _RESERVED and not s.endswith("."))
    .map(str)
)
_safe_relative_paths = st.lists(_components, min_size=1, max_size=5, unique=True).map(
    lambda parts: "/".join(parts)
)


@settings(deadline=None)
@given(relative=_safe_relative_paths)
def test_clean_paths_always_stay_under_root(tmp_path_factory, relative):
    root = tmp_path_factory.mktemp("prop-ws")
    ws = Workspace(root)
    assert ws.resolve(relative).is_relative_to(ws.root)


@settings(deadline=None)
@given(relative=_safe_relative_paths, extra_ups=st.integers(min_value=1, max_value=8))
def test_excess_parent_segments_always_escape(tmp_path_factory, relative, extra_ups):
    depth = len(relative.split("/"))
    malicious = "/".join([".."] * (depth + extra_ups)) + "/" + relative
    root = tmp_path_factory.mktemp("prop-ws-esc")
    ws = Workspace(root)
    with pytest.raises(PathEscapeError):
        ws.resolve(malicious)


@settings(deadline=None)
@given(relative=st.lists(_components, min_size=2, max_size=5, unique=True).map("/".join))
def test_leading_absolute_forms_always_rejected(tmp_path_factory, relative):
    root = tmp_path_factory.mktemp("prop-ws-abs")
    ws = Workspace(root)
    for attempt in (f"/{relative}", f"C:/{relative}", relative.replace("/", "\\")):
        with pytest.raises(PathEscapeError):
            ws.resolve(attempt)
