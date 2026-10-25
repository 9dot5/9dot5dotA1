# ADR-0030: Sigma monitoring boundary

- **Status:** Proposed
- **Date:** 2026-10-25
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-25
- **Related:** ADR-0004, ADR-0007, ADR-0009, ADR-0015, ADR-0017, ADR-0018, ADR-0029, ADR-0031, [architecture/M2M_ARCHITECTURE.md](../architecture/M2M_ARCHITECTURE.md) (C-5, C-6), THREAT_MODEL T-08, T-11

## Context

Sigma is `sigma04.ist.utl.pt`, a university server shared with other users. The owner has no root on it and cannot install system services. The owner has decided that Sigma will be the monitoring centre, and that it is the bridge to the CSHP lab PCs, which are more machines of the same kind.

Facts:

- THREAT_MODEL T-08: data on hosts the platform does not control can be exposed to other users. Mitigation: no personal or secret data there.
- ADR-0015 rejected the shared lab server for the portal.
- ADR-0018 keeps the audit record outside the agent hosts and under owner control.
- ADR-0007: lab machines are "not ours to load".
- The owner cannot install system-level software on Sigma. Any monitoring there runs as a user process, or uses what the university already provides.

Assumption: the university administrators can read files and processes owned by any user on Sigma. Not verified.

## Decision

1. **Sigma receives health and metrics only.** Nodes push availability and resource measurements to Sigma (ADR-0009 signals). Sigma holds no audit record, no credential, no configuration of Operations MCP, and no personal data.
2. **Audit records stay on owner-controlled storage** (ADR-0017, ADR-0018). Sigma is never their store, not even as a replica.
3. **Sigma is not a write target.** Operations MCP never changes Sigma. Every write on Sigma is manual, performed by the owner (ADR-0031, `manual_only`).
4. **Sigma is not a gateway.** Nothing reaches a node through Sigma. Sigma pushes data outward. It does not accept connections that open access to another node.
5. **Hops from Sigma to lab PCs are out of scope of this ADR.** They are governed by ADR-0031: each lab PC is admitted by name, one at a time, and is disabled until admitted.
6. **Sigma's monitoring is user-space and uses no privilege.** If a monitoring tool needs root or a system service, it is not installed on Sigma and the signal is taken from the node instead.
7. **Revocation.** If the university changes the terms of use, or an administrator objects, the owner stops the push and removes Sigma from the registry in one commit. No other component depends on Sigma.
8. **Sigma may read one metrics-only Grafana view on PC Alentejo** (flow F-10, [ADR-0035](ADR-0035-alentejo-monitoring-stack.md), added 2026-10-25). It is read-only, over the private overlay, with a Viewer account, and holds no audit data. It opens no path from Sigma to any other service or node, so rule 4 still holds.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Sigma holds health and metrics only (chosen) | Gets the monitoring the owner wants; no audit or secret exposed to a shared host | Metrics on a shared host still show the owner's infrastructure to others | 3.57 (estimate) |
| B: Sigma holds the audit record too, as an exception | Redundant copy | Breaks ADR-0018 control and T-08; audit evidence on a host the owner does not control | Rejected |
| C: Sigma as the single monitoring store and the bridge to all nodes | Less infrastructure to run | Turns a shared host into a path to every node; violates TB-4 and ADR-0004 rule 1 | Rejected |
| D: No Sigma; monitoring on the control node | Full control | The control node is not yet measured or hosted (ADR-0015) | Kept as fallback |

Score for A is an estimate. Values: value 4, frequency 4, cost 4, risk 3, reversibility 5, learning 3. Weighted sum: 12 + 8 + 12 + 9 + 10 + 3 = 54, divided by 14 = 3.86. The risk value (3) assumes that only health and metrics are on Sigma. Changing that assumption re-scores the option to rejected.

## Consequences

- Positive: the owner gets monitoring without installing system services on a host it does not own.
- Negative: the metrics show the owner's infrastructure to the host's administrators. Mitigation: metrics carry node names and levels, not addresses, credentials or service configuration.
- Negative: if Sigma is unavailable, monitoring is lost. Mitigation: nodes keep their own health checks, and the alert path goes to the owner without Sigma.
- Follow-up: decide with the owner which metrics leave the node (write the list in MONITORING_STRATEGY).
- Follow-up: check the university's terms of use for a personal monitoring process on a shared server. Not verified.

## Security and compliance notes

- Trust boundary: TB-7 (Sigma, shared, hostile by assumption) and TB-5 (nodes to telemetry, push only), as in M2M_ARCHITECTURE §7.
- Data classes: health and metrics are Internal. Node names are Internal. Nothing Personal or Secret is allowed on Sigma. Restricted material is excluded (ADR-0019 once accepted).
- Controls: push-only network rule (ADR-0032 zones, to be written); no credential on Sigma; `manual_only` on the registry entry; monthly review of what is stored there.
- The residual risk that a shared-host administrator reads the metrics is recorded in the risk register (R-24) and needs the owner's acceptance.
