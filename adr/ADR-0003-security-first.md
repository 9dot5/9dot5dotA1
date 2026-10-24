# ADR-0003: Security first

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24

## Context

Systems that are made to work first and secured later accumulate exposed services,
default credentials and undocumented access. Retrofitting controls is expensive and often
incomplete.

## Decision

Security is a design input from the first ADR of each component:

1. A threat model entry exists before a component is accepted (see [security/THREAT_MODEL.md](../security/THREAT_MODEL.md)).
2. Controls from [security/SECURITY_BASELINE.md](../security/SECURITY_BASELINE.md) apply by default.
3. Security findings in pipelines block merges when they are critical or high and have no accepted exception.
4. Shift left: the same checks run locally, in pull requests and in the pipeline.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Security first | Lower total risk; cheaper changes | Slower initial design | — |
| B: Security as a final gate | Faster start | Gate is always under pressure to pass | — |

## Consequences

- Positive: fewer exceptions over time.
- Negative: the first phase delivers documents, not services, by design.

## Security and compliance notes

This ADR governs all others. An ADR that cannot show its threat model entry is incomplete.
