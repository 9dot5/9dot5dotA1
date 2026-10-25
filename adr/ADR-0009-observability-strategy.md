# ADR-0009: Observability strategy

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24

## Context

Without observability, the platform's health is known only when something fails. Full
observability stacks are expensive to run, so the scope must match value.

## Decision

1. Three signals are collected from phase 03 onwards: service health, resource use and backup status.
2. Each signal has an owner, an alert threshold and a runbook link (see [operations/MONITORING_STRATEGY.md](../operations/MONITORING_STRATEGY.md)).
3. Tracing and log analytics are added only when a named question cannot be answered by the three signals.
4. Telemetry is open-standard (OpenTelemetry where applicable) so backends can change.
5. Telemetry must not contain personal data or secrets; redaction is tested.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Staged, standards-based | Cost matched to value | Later depth | — |
| B: Full commercial suite from day one | Rich dashboards | Cost; lock-in | — |

## Consequences

- Positive: alerts map to decisions someone can act on.
- Negative: deeper diagnosis waits until a need is proven.

## Security and compliance notes

Access to dashboards follows ACCESS_CONTROL.md. Logs of access decisions are retained per the security baseline.
