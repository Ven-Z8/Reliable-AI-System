"""Unit tests for the pre-execution command policy - TDD red."""

import pytest

from reliable_agent_platform.harness.policy import (
    CommandDeniedError,
    CommandPolicy,
)


def _policy(allowed=None, denied=None):
    return CommandPolicy(allowed_commands=allowed, denied_commands=denied)


class TestDefaultOpen:
    """No allowlist means unknown commands run unless denied."""

    def test_unknown_command_allowed(self):
        decision = _policy().decide("python -V")
        assert decision.allowed

    def test_denied_list_only_blocks_matches(self):
        policy = _policy(denied=["rm -rf /"])
        assert policy.decide("ls -la").allowed
        assert not policy.decide("rm -rf /").allowed


class TestDenyMatching:
    def test_exact_deny(self):
        assert not _policy(denied=["git push"]).decide("git push").allowed

    def test_deny_covers_extra_arguments(self):
        assert not _policy(denied=["git push"]).decide("git push origin main --force").allowed

    def test_word_boundary_no_false_positive(self):
        decision = _policy(denied=["git push"]).decide("git pusher status")
        assert decision.allowed
        assert _policy(denied=["git push"]).decide("gitpush").allowed

    def test_case_insensitive_deny(self):
        assert not _policy(denied=["git push"]).decide("Git Push --force").allowed

    def test_whitespace_variations_still_match(self):
        assert not _policy(denied=["rm -rf /"]).decide("   rm   -rf   /  ").allowed


class TestAllowlistMode:
    def test_unlisted_command_blocked(self):
        policy = _policy(allowed=["pytest", "ruff"])
        decision = policy.decide("mypy src")
        assert not decision.allowed
        assert decision.reason is not None

    def test_listed_command_with_args_allowed(self):
        assert _policy(allowed=["pytest", "ruff"]).decide("pytest -q tests/").allowed

    def test_empty_allowlist_blocks_everything(self):
        policy = _policy(allowed=[])
        assert not policy.decide("echo hi").allowed


class TestDenyPrecedence:
    def test_denied_wins_over_allowlist(self):
        policy = _policy(allowed=["pytest"], denied=["pytest"])
        assert not policy.decide("pytest -q").allowed


class TestMalformed:
    @pytest.mark.parametrize("command", ["", "   ", "\t\n"])
    def test_blank_commands_denied(self, command):
        decision = _policy().decide(command)
        assert not decision.allowed


class TestEnsureAllowed:
    def test_passes_for_allowed(self):
        _policy(denied=["git push"]).ensure_allowed("make lint")

    def test_raises_structured_error(self):
        policy = _policy(allowed=["pytest"])
        with pytest.raises(CommandDeniedError) as excinfo:
            policy.ensure_allowed("curl evil.example")
        assert "not allowed" in str(excinfo.value)
