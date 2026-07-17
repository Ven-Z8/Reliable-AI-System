# Third-Party Policy

No third-party source code is included in this starter.

Planned categories of dependencies:

| Capability | Preferred approach |
|---|---|
| Inner agent worker | Optional DeepAgents adapter |
| Durable execution | Optional LangGraph integration |
| PDF parsing | Optional Docling integration |
| Retrieval storage | Adapter for Qdrant or PostgreSQL |
| Telemetry | OpenTelemetry |
| MCP | Official MCP SDK |
| Sandboxing | Existing maintained runtime |
| Models | Provider-neutral adapters |

Before adding or copying code:

1. verify the exact license;
2. prefer dependency or subprocess integration over copying;
3. preserve required notices;
4. record the dependency and purpose here;
5. add an architecture decision when the dependency creates lock-in.
