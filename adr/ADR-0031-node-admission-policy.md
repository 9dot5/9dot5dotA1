# ADR-0031: Node admission policy and the security gate

- **Status:** Proposed
- **Date:** 2026-10-25
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-25
- **Related:** ADR-0004, ADR-0010, ADR-0011, ADR-0029, ADR-0030, ADR-0032, ADR-0033, [architecture/M2M_ARCHITECTURE.md](../architecture/M2M_ARCHITECTURE.md) (C-6, Q1), [security/OPS_MCP_THREAT_MODEL.md](../security/OPS_MCP_THREAT_MODEL.md) (T-OPS-12, T-OPS-13)

## Context

Operations MCP can reach nodes. Before this ADR, the only control on a node was a flag in `config/nodes.json`, which anyone with write access to the repository could change. Nothing required a recorded decision to admit a node, or the governance conditions that must hold before the first contact.

The owner has three candidate nodes and one unknown:

- PC Alentejo (`DESKTOP-Q3GOUP4`, user `yau`): reached by SSH. Ownership of the user account is not recorded.
- Sigma: shared university server, now the monitoring centre (ADR-0030).
- CSHP lab PCs: more machines behind Sigma. Not owned. ADR-0007 says "not ours to load".
- LSD2: not identified (M2M Q1).

## Decision

### Part A. Admission of a node

A node may be enabled for Operations MCP only when all of these hold, recorded in `config/nodes.json` and in a dated line of this ADR's change history:

1. **Identity.** The node has a name, an owner, and a statement of who controls the host.
2. **Ownership class.** One of: `owned` (the owner controls the host and its user accounts), `shared` (other users have access), `external` (controlled by someone else).
3. **Data class allowed.** Each node has the highest data class it may hold. `external` nodes hold nothing above Public.
4. **Access record.** The access path is written down (account, key type, forced command, source address), and the key is in the secret broker (ADR-0014), not on disk in the repository.
5. **Capacity or purpose.** A measured capacity (ADR-0015) or a stated purpose, for the capability set that is enabled.
6. **Manual-only setting.** Shared and external nodes are `manual_only` until ADR-0030 or a later ADR says otherwise.
7. **Review date.** Each admission has a review date no more than 6 months away (SECURITY_GOVERNANCE).

Admission of a new node is a Risk-bearing decision (DECISION_FRAMEWORK). It is the owner's decision only.

### Part B. The security gate

Operations MCP cannot communicate with any node while any of these is false:

1. ADR-0029, ADR-0030, ADR-0031, ADR-0032 and ADR-0033 have status **Accepted**. The gate reads this from the ADR files.
2. The threat model addendum (`security/OPS_MCP_THREAT_MODEL.md`) has been reviewed. The owner records the reviewer and the date in `config/gate.json`.
3. The permission matrix (M2M_ARCHITECTURE §6) has been approved. The owner records the approver and the date in `config/gate.json`.

The gate is enforced in code (`ops_mcp/gate.py`). A gated call is refused and audited, and no approval is created for it. Local capabilities (`get_nodes`, `search_adr`) and external knowledge sources are not gated. Reading `get_alerts` or `get_incidents` is gated, because those sources read from nodes.

An agent cannot open the gate: the ADR status is accepted only by the owner, and `config/gate.json` is part of the owner's review.

### Part C. Lab PCs behind Sigma

Each lab PC is a separate node under Part A. None is discovered automatically. A lab PC is admitted only with an explicit owner decision recorded here, and a hop through Sigma is recorded as its access path. Until then, no lab PC is in the registry.

### Part D. Q1 (LSD2)

LSD2 is not admitted. It stays out of the registry until its identity, owner and access path are recorded under Part A.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Admission conditions and a code gate (chosen) | No node is reached by accident; the record exists before the first contact | Slower onboarding; the owner must write the admission record each time | 3.64 (estimate) |
| B: Registry flag only (status quo before this ADR) | Quick to change | Anyone with repository write can enable a node; no decision record | Rejected |
| C: Automatic discovery of hosts on the overlay | Less manual work | Overlay membership is not authorisation (ADR-0004 rule 1); finds machines nobody approved | Rejected |
| D: Trust the lab PCs as owned because they are reachable | Simple | Wrong for shared and external hosts (T-08) | Rejected |

Score for A is an estimate. Values: value 4, frequency 3, cost 3, risk 4, reversibility 4, learning 4. Weighted sum: 12 + 6 + 9 + 12 + 8 + 4 = 51, divided by 14 = 3.64. The estimate is close to the threshold; the owner should re-score it after the first admission.

## Consequences

- Positive: every node has a recorded reason to be in scope, and nothing reaches a node before the governance conditions hold.
- Negative: the first contact with any node waits for the owner's review. This is intended.
- Negative: the gate reads ADR status from files. A file edit by someone with repository write access could change a status. Mitigation: status changes are reviewed in pull requests, CODEOWNERS covers `adr/`, and the owner's review record is in a separate file.
- Follow-up: add the admission record as a template in `docs/templates/` (B-39).
- Follow-up: record the first admission (PC Alentejo) only after its ownership class is confirmed by the owner.

## Security and compliance notes

- Trust boundaries: TB-3 (gateway to nodes), TB-4 (node to node, denied), TB-7 (shared host).
- Controls: enabled flag and manual-only flag in the registry; the security gate in code; audit of every refused call.
- Threats: T-OPS-12 (lab hop), T-OPS-13 (node re-enabled without a record), T-OPS-16 (gate bypass), added to the threat model.
