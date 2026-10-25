# Phase 06 — Automation

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

**Status:** Proposed · **Duration:** to be sized · **Related:** ADR-0010, AGENT_STRATEGY.md

## Objective

Automate recurring work — backups verification, documentation checks, scheduled reports —
with each automation owned, logged and reversible.

## Deliverables

- [ ] Automation engine decided under ROI matrix and recorded in ADR
- [ ] Inventory of recurring tasks, each with owner and frequency
- [ ] Automations classified: read-only, reversible write, or consequential (human approval required)
- [ ] Logging and alerting for every automation
- [ ] Each automation has a runbook and a stop procedure

## Exit criteria

- Every automation in production appears in the service catalogue.
- No automation performs a consequential action without recorded approval.

## Dependencies

Phase 03 (portal to show status), Phase 02 (controls).
