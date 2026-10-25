# Phase 07 — Observability

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

**Status:** Proposed · **Duration:** to be sized · **Related:** ADR-0009, MONITORING_STRATEGY.md

## Objective

Make platform health visible through the three signals defined in ADR-0009, and add deeper
tooling only where a named question remains unanswered.

## Deliverables

- [ ] Health, resource and backup-status signals for every service in the catalogue
- [ ] Alert thresholds and owners recorded
- [ ] Redaction tests for logs and telemetry
- [ ] Tracing or log analytics ADR, only if a question requires it

## Exit criteria

- Each alert links to a runbook.
- A simulated failure is detected within the agreed time.

## Dependencies

Phase 03 (portal), Phase 05 (platform services running).
