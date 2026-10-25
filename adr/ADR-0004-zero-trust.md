# ADR-0004: Zero trust

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24

## Context

A home or lab network is often treated as trusted. Devices, VPNs and agents then gain
access to services by location alone. Agents and remote clients make that assumption
unsafe.

## Decision

Follow NIST SP 800-207 principles:

1. No implicit trust from network location, subnet or VPN membership.
2. Every request to a service is authenticated, and authorised against a stated policy.
3. Least privilege for humans, agents and services, with time-bound elevated rights.
4. Devices and agents are identified; their identity is revoked on loss or misuse.
5. Logs of access decisions are retained and reviewed.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Zero trust principles | Limits lateral movement; fits agents | More setup for identity | — |
| B: Perimeter trust | Simple | One breach exposes everything | — |

## Consequences

- Positive: access can be reasoned about per identity.
- Negative: identity provider becomes a critical dependency (see ADR-0002 risk and Phase 02).

## Security and compliance notes

Relates to ACCESS_CONTROL.md. Requires MFA for administrative access.
