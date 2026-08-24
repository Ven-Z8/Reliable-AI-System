"""Adversarial tests: workspace escapes and command-policy bypass attempts."""

import sys
from typing import ClassVar

import pytest

from reliable_agent_platform.harness.policy import CommandPolicy
from reliable_agent_platform.harness.workspace import PathEscapeError, Workspace

pytestmark = pytest.mark.adversarial


class TestWorkspaceEscapeBattery:
    """Every escape vector must be blocked before any file op happens."""

    ESCAPES: ClassVar[list[str]] = [
        "../escape.txt",
        "a/b/../../../escape.txt",
        "..\\windows-escape.txt",
        "/absolute/escape.txt",
        "C:/Windows/system32/config",
        "./../escape.txt",
        "sub/../../escape.txt",
    ]

    @pytest.mark.parametrize("attempt", ESCAPES)
    def test_escape_vectors_rejected(self, tmp_path, attempt):
        ws = Workspace(tmp_path)
        with pytest.raises(PathEscapeError):
            ws.resolve(attempt)

    def test_symlink_inside_pointing_outside_rejected(self, tmp_path):
        if sys.platform == "win32":
            pytest.skip("symlink creation requires elevated privileges on Windows")

        outside = tmp_path / "outside"
        outside.mkdir()
        secret = outside / "secret.txt"
        secret.write_text("top secret")

        ws_root = tmp_path / "ws"
        ws_root.mkdir()
        link = ws_root / "innocent.txt"
        link.symlink_to(secret)
        (ws_root / "sub").mkdir()

        ws = Workspace(ws_root)
        with pytest.raises(PathEscapeError):
            ws.resolve("innocent.txt")
        with pytest.raises(PathEscapeError):
            ws.resolve("sub/../innocent.txt")


class TestPolicyBypassAttempts:
    def test_multi_space_injection_still_denied(self):
        policy = CommandPolicy(allowed_commands=None, denied_commands=["rm -rf /"])
        assert not policy.decide("rm \t -rf \t /").allowed

    def test_case_bypass_denied(self):
        policy = CommandPolicy(allowed_commands=None, denied_commands=["curl"])
        assert not policy.decide("CURL http://evil.example").allowed

    def test_allowlisted_binary_with_denied_subcommand_blocked(self):
        policy = CommandPolicy(
            allowed_commands=["git"],
            denied_commands=["git push"],
        )
        assert policy.decide("git status").allowed
        assert not policy.decide("git push origin main").allowed

    def test_empty_command_never_runs(self):
        policy = CommandPolicy(allowed_commands=None, denied_commands=[])
        assert not policy.decide("").allowed
        assert not policy.decide(" \t ").allowed
