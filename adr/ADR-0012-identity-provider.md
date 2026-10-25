# ADR-0012: Identity provider

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24
- **Related:** ADR-0004, ADR-0006, ADR-0011, [security/ACCESS_CONTROL.md](../security/ACCESS_CONTROL.md), [architecture/TARGET_ARCHITECTURE.md](../architecture/TARGET_ARCHITECTURE.md), Phase 04

## Context

Each host currently keeps its own local identities, which TARGET_ARCHITECTURE.md records as
architecture debt. ADR-0004 requires every request to be authenticated and every administrative
action to use MFA. A single identity source is needed before Phase 04 services are deployed.

Facts: no identity service runs today. The ROI row is already in the register
(governance/ROI_MATRIX.md) with a score of 3.43, below the 3.5 threshold. Assumption: the
platform's identity needs are small (one owner, a few agents and services).

## Decision

We will use one open-source identity provider for humans and services, providing SSO and
MFA for administrative access. The product is selected in Phase 04 from measured capacity
on the control-plane host, not from preference.

No product is adopted by this ADR. The component stays at "To evaluate" in the ROI matrix until
the Phase 04 evaluation lowers its risk or raises its value enough to pass the threshold.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Open-source IdP with SSO and MFA (candidates: Keycloak, Authentik, Authelia) | One identity for humans, services and agents; standards-based | Operating cost; a critical dependency (ADR-0004) | 3.43 (estimate, register values) |
| B: Local accounts per host (status quo) | No new component | Unmanaged identities; the debt already recorded | Not scored; debt |
| C: Managed identity service | Low operating cost | Lock-in; data about the owner leaves the platform (ADR-0006 item 3) | Not scored; needs its own ADR |

## Consequences

- Positive: one place to revoke an identity (ADR-0004 item 4).
- Negative: the identity provider becomes a critical dependency. Mitigation: an offline recovery
  path for the owner (ACCESS_CONTROL, Owner row), and a tested restore (BACKUP_STRATEGY).
- Negative: the score is below threshold. Mitigation: the Phase 04 evaluation measures RAM and
  CPU before any adoption.
- Follow-up: capacity measurement on the control-plane candidate host (Phase 04).
- Follow-up: record the chosen product in a new ADR that supersedes this one.

## Security and compliance notes

- Trust boundary: internet to edge, and edge to services (CONTEXT.md, boundaries 1 and 2).
- Data classes: credentials (Secret) and identity attributes (Personal). Both must be backed up
  under BACKUP_STRATEGY.md.
- Controls: MFA for administrative accounts (SECURITY_BASELINE); access logs retained 90 days;
  service identities separate from human identities.
