# Phase 04 — AI Platform

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

**Status:** Proposed · **Duration:** to be sized after Phase 03 · **Related:** ADR-0007, ADR-0010

## Objective

Decide whether and how to run AI components, based on measured capacity and the ROI matrix.

## Deliverables

- [ ] Identity provider evaluated under ROI matrix (SSO, MFA, RBAC) and ADR accepted
- [ ] Hardware capacity measured on each candidate host: RAM, CPU, disk, power
- [ ] Model serving evaluated: at least two open-source options, with measured throughput
- [ ] Data-handling decision for hosted APIs, per data class
- [ ] ADR accepted naming the AI components approved for deployment

## Exit criteria

- Each approved component has an ROI row with a score at or above threshold.
- Capacity test results are recorded before any service is documented as available.

## Dependencies

Phase 02 (threat model covers AI threats), Phase 03 (portal to present results).
