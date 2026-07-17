# ADR-0001: Build a Fresh Modular Monorepo

Status: Accepted  
Date: 2026-07-17

## Decision

Create a new repository with independently testable packages and deployable applications.

Do not use AgentOps Harness or ContextIQ as source, dependencies, submodules, or migration inputs.

## Consequences

The project gains coherent contracts and naming, but must re-implement only the differentiated outer reliability layer.
