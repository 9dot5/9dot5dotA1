# ADR-0015: Portal hosting

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24
- **Related:** ADR-0007, ADR-0009, ADR-0013, [roadmap/PHASE_03_PORTAL.md](../roadmap/PHASE_03_PORTAL.md), [operations/SERVICE_CATALOG.md](../operations/SERVICE_CATALOG.md) (Hosts)

## Context

The management portal is the platform's first product (Phase 03). Its hosting location must be
named in an accepted ADR before Phase 03 closes. PHASE_03 says the choice is made by capacity
measurements, not preference.

Facts: SERVICE_CATALOG lists three hosts. The laptop (6C/12T, 8 GB) is development-only and is
not a production host. The shared lab server is shared and holds no personal data. The control-plane
candidate is a desktop with 8C/16T, 16 GB and a discrete GPU, not yet measured. No capacity
measurement has been recorded.

## Decision

We will host the portal on the control-plane candidate host, once its capacity measurement shows
headroom for the portal, the identity provider (ADR-0012) and the reverse proxy (ADR-0013) together.
Until that measurement exists, this decision is provisional and no service on that host is
documented as available.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Control-plane candidate host | Owner-controlled; hosts identity and proxy; spare capacity likely | Power cost while on; single host | 3.50 (estimate) |
| B: Laptop | Already owned | Not a production host (SERVICE_CATALOG); sleeps and moves | Rejected |
| C: Shared lab server | Already available | Shared with other users (T-08); not ours to load | Rejected |
| D: Managed cloud hosting | High availability | Data leaves the platform; lock-in (ADR-0006) | Not scored; needs its own ADR |

Scores are estimates. Values: value 4, frequency 4, cost 3, risk 3, reversibility 4, learning 3.

## Consequences

- Positive: the portal sits beside the services it shows.
- Negative: one host carries several roles. Mitigation: capacity measured first; the portal is
  moved to another host if the measurement fails, by a new ADR.
- Negative: the decision depends on a measurement not yet taken. Mitigation: the Phase 03 exit
  criterion requires the measurement to be recorded.
- Follow-up: capacity measurement on the control-plane candidate host (RAM, CPU, disk, watts).
- Follow-up: update SERVICE_CATALOG hosts table with measured values.

## Security and compliance notes

- Trust boundary: internet to edge, then portal (CONTEXT.md, boundaries 1 and 2). The portal is an
  external interface and triggers the security review (governance/SECURITY_GOVERNANCE.md).
- Controls: exposure through the reverse proxy only; authentication through the identity provider;
  no personal data on the portal beyond what the Domain Model requires.
- Hosts not owned by the platform are excluded (T-08).
