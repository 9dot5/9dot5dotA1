# ADR-0013: Reverse proxy with TLS

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24
- **Related:** ADR-0004, ADR-0006, ADR-0012, [architecture/TARGET_ARCHITECTURE.md](../architecture/TARGET_ARCHITECTURE.md), [security/THREAT_MODEL.md](../security/THREAT_MODEL.md) (T-04), Phase 04

## Context

TARGET_ARCHITECTURE.md requires a single controlled entry point for every service, with TLS.
ADR-0004 forbids implicit trust from network location, and T-04 names an exposed admin interface
as a high-impact threat. No reverse proxy exists today.

Facts: no services are deployed before Phase 04. Assumption: most services will be reached from
the owner's devices, not the public internet.

## Decision

We will place one open-source reverse proxy in front of every service that has a web or API
interface. It terminates TLS, forwards only to named upstreams, and does not expose admin
ports. The candidate is Caddy; the choice is confirmed by the Phase 04 capacity test.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Caddy (candidate) | Automatic TLS; short configuration; Apache-2.0 | Smaller plugin ecosystem than nginx | 3.71 (estimate) |
| B: Traefik | Automatic discovery from containers; MIT | More moving parts; configuration complexity | Not scored; similar |
| C: nginx | Mature; widely known | Manual TLS management; more configuration | Not scored; similar |
| Do nothing: services bind to LAN addresses | No component | Trust by location (ADR-0004 rule 1); T-04 | Not scored; rejected |

Scores are estimates. Values: value 4, frequency 3, cost 4, risk 3, reversibility 5, learning 3.

## Consequences

- Positive: a single place to enforce TLS, headers and access checks.
- Negative: the proxy is a single point of failure. Mitigation: its configuration is in Git and
  its restore is a runbook step (Phase 04).
- Negative: certificate issuance depends on a DNS name the owner controls. Mitigation: recorded in
  SERVICE_CATALOG when the first service is added.
- Follow-up: write the runbook RB-proxy-restore.md before the first service is exposed.

## Security and compliance notes

- Trust boundary: internet to edge (CONTEXT.md, boundary 1). Treats T-04 as Reduce.
- Controls: TLS for every external interface; no admin interface on the public address; access
  logs without secrets (SECURITY_BASELINE).
- Exposure to the internet is decided per service in its own ADR, not by this one.
