# Security Threat Model

## Trust boundaries

- human to control plane;
- control plane to worker;
- worker to workspace;
- worker to tool or MCP server;
- MCP server to downstream system;
- application to telemetry;
- retrieval system to source document.

## Principal threats

- prompt injection;
- path or shell escape;
- secret leakage;
- forged evidence;
- worker self-approval;
- test manipulation;
- infinite loops;
- duplicated side effects;
- token passthrough;
- malicious MCP metadata;
- poisoned memory;
- cross-tenant retrieval.

## Completion standard

A safety feature is complete only when a negative test proves that forbidden behavior is blocked.
