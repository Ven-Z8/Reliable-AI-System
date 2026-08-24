"""Pre-execution command policy.

Semantics (documented contract, enforced identically everywhere):

- Commands are compared as whitespace-token sequences, case-insensitively;
  a deny rule matches when its tokens are a *word-aligned prefix* of the
  command's tokens (so ``git push`` denies ``git push origin main`` but not
  ``git pusher``).
- Deny rules are evaluated first and always win over the allowlist.
- ``allowed_commands=None`` means default-open (still subject to denies);
  an empty allowlist means nothing may run; a non-empty allowlist permits a
  command only when some entry matches as a word-aligned prefix.
"""

import re
from typing import Self

from pydantic import BaseModel, ConfigDict


class CommandDeniedError(Exception):
    """Raised when a command is refused before execution."""


_TOKEN_SPLIT = re.compile(r"\s+")

Tokens = tuple[str, ...]


class PolicyDecision(BaseModel):
    """Result of evaluating one command against the policy."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    allowed: bool
    reason: str | None = None
    matched_rule: str | None = None


def _tokenize(command: str) -> Tokens:
    stripped = command.strip().lower()
    if not stripped:
        return ()
    return tuple(_TOKEN_SPLIT.split(stripped))


def _rule_matches(rule: Tokens, command_tokens: Tokens) -> bool:
    if len(rule) > len(command_tokens):
        return False
    return all(r == c for r, c in zip(rule, command_tokens, strict=False))


class CommandPolicy:
    """Decides whether a proposed command line may execute."""

    def __init__(
        self,
        allowed_commands: list[str] | None,
        denied_commands: list[str] | None,
    ) -> None:
        self._denied: tuple[Tokens, ...] = tuple(
            _tokenize(entry) for entry in (denied_commands or [])
        )
        self._allowed: tuple[Tokens, ...] | None = (
            None if allowed_commands is None else tuple(_tokenize(e) for e in allowed_commands)
        )

    @classmethod
    def from_contract_fields(
        cls,
        allowed_commands: list[str] | None,
        denied_commands: list[str] | None,
    ) -> Self:
        """Build directly from RunContract field values."""
        return cls(allowed_commands=allowed_commands, denied_commands=denied_commands)

    def decide(self, command: str) -> PolicyDecision:
        command_tokens = _tokenize(command)
        if not command_tokens:
            return PolicyDecision(allowed=False, reason="empty command")

        for rule in self._denied:
            if _rule_matches(rule, command_tokens):
                return PolicyDecision(
                    allowed=False,
                    reason=f"denied by rule {' '.join(rule)!r}",
                    matched_rule=" ".join(rule),
                )

        if self._allowed is None:
            return PolicyDecision(allowed=True)

        for entry in self._allowed:
            if _rule_matches(entry, command_tokens):
                return PolicyDecision(allowed=True, matched_rule=" ".join(entry))

        return PolicyDecision(allowed=False, reason="not permitted by allowlist")

    def ensure_allowed(self, command: str) -> None:
        decision = self.decide(command)
        if not decision.allowed:
            raise CommandDeniedError(f"command not allowed: {command!r} ({decision.reason})")
