# Phase 02 — Security

**Status:** Proposed · **Duration:** 3 weeks · **Related:** ADR-0003, ADR-0004

## Objective

Complete the security foundation before any service is deployed: threat model, baseline,
secret management, access control, incident and recovery procedures.

## Deliverables

- [ ] THREAT_MODEL.md reviewed with STRIDE and AI-specific threats
- [ ] SECURITY_BASELINE.md accepted by the owner
- [ ] SECRET_MANAGEMENT.md, ACCESS_CONTROL.md accepted
- [ ] INCIDENT_RESPONSE.md and DISASTER_RECOVERY.md accepted
- [ ] Secret scanning and dependency scanning enabled on the repository
- [ ] Pre-commit secret scan documented and installed on each developer machine

## Exit criteria

- No open critical or high finding in the repository's scans.
- Threat model covers every component in the planned target architecture.
- Owner accepts or rejects each identified residual risk in writing.

## Dependencies

Phase 01 (repository and branch protection).
