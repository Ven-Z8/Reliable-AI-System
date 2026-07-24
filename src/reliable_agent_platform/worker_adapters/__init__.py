"""Worker-neutral adapter protocol and implementations."""

from reliable_agent_platform.worker_adapters.capabilities import WorkerCapabilities
from reliable_agent_platform.worker_adapters.mock_worker import MockWorker
from reliable_agent_platform.worker_adapters.protocol import (
    WorkerAdapter,
    WorkerEventSink,
    WorkerRequest,
    WorkerResult,
)

__all__ = [
    "MockWorker",
    "WorkerAdapter",
    "WorkerCapabilities",
    "WorkerEventSink",
    "WorkerRequest",
    "WorkerResult",
]
