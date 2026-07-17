"""Worker capabilities - boolean flags only, no permissions."""

from dataclasses import dataclass, field


@dataclass
class WorkerCapabilities:
    """Worker capabilities - flags only, do NOT grant permissions.

    Capabilities describe what a worker CAN do; the control plane
    policy engine decides what it MAY do.
    """

    filesystem: bool = False
    shell: bool = False
    streaming: bool = False
    cancellation: bool = False
    checkpoints: bool = False
    context_compaction: bool = False
    sub_agents: bool = False
    mcp: bool = False
    human_approval: bool = False
    sandbox: bool = False
    cost_reporting: bool = False
    token_reporting: bool = False

    # Allow future extension without breaking
    extra: dict[str, bool] = field(default_factory=dict)
