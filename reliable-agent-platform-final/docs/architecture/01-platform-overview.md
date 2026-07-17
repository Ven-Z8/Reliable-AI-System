# Platform Architecture

## Layered model

```mermaid
flowchart TB
    Human[Human / CI / Scheduler] --> Loop[Loop Engine]
    Human --> Harness[Harness Control Plane]
    Loop --> Harness

    Harness --> Contract[Contracts]
    Harness --> Policy[Policy and Budgets]
    Harness --> Workspace[Workspace / Sandbox]
    Harness --> Adapter[Worker Adapter]
    Adapter --> Worker[DeepAgents / Other Worker]
    Worker --> Workspace

    Workspace --> Verifier[Independent Verification]
    Verifier --> Evidence[Evidence Bundle]
    Evidence --> Human

    RAG[Multimodal RAG] --> Evidence
    MCP[Secure MCP Servers] --> Worker

    Harness --> OTel[OpenTelemetry]
    Loop --> OTel
    RAG --> OTel
    MCP --> OTel
    OTel --> TraceBench[TraceBench]
```

## Stable platform interfaces

- `RunContract`
- `WorkerCapabilities`
- `WorkerRequest`
- `WorkerEvent`
- `WorkerResult`
- `PolicyDecision`
- `VerificationResult`
- `EvidenceBundle`
- `EvaluationResult`
- `TraceEvent`

## Ownership rule

Contracts may be imported by every package.

Contracts must not import application, framework, model-provider, database, or UI packages.
