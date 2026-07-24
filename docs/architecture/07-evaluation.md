# Evaluation Strategy

## Hierarchy

1. schema and invariant checks;
2. deterministic behavior checks;
3. ground-truth task checks;
4. trajectory checks;
5. model-judge checks;
6. human review.

Deterministic checks remain authoritative for policy, files, commands, calculations, and persisted evidence.

## Reproducibility record

Every evaluation records:

- Git commit;
- dataset version;
- schema version;
- worker;
- model;
- prompt and skill hashes;
- configuration;
- environment;
- timestamp;
- raw artifact location.
