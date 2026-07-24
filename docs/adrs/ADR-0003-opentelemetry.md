# ADR-0003: Use OpenTelemetry as the Portable Telemetry Standard

Status: Accepted  
Date: 2026-07-17

## Decision

All subsystems will emit OpenTelemetry-compatible spans and metrics.

Raw sensitive content is opt-in. Default telemetry uses identifiers, hashes, lengths, categories, and redacted summaries.
