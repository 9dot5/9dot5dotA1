# ADR-0029: Operations MCP as the single gateway to infrastructure

- **Status:** Proposed
- **Date:** 2026-10-25
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-25
- **Related:** ADR-0004, ADR-0006, ADR-0007, ADR-0008, ADR-0009, ADR-0010, ADR-0011, ADR-0012, ADR-0013, ADR-0014, ADR-0016, ADR-0017, ADR-0018, [architecture/M2M_ARCHITECTURE.md](../architecture/M2M_ARCHITECTURE.md), [architecture/OPS_MCP_ARCHITECTURE.md](../architecture/OPS_MCP_ARCHITECTURE.md), [MCP_STRATEGY](../architecture/MCP_STRATEGY.md), [ops-mcp/](../ops-mcp/README.md)

## Context

Humans, Claude CLI sessions, Devin (if approved, see ADR-0011), Rovo, MCP clients, workflows and future agents need to inspect and change infrastructure on the owner's nodes: PC Alentejo, Sigma (a shared university host) and LSD2 (not yet identified). Without a single gateway, each client would need its own path to each node, and nothing would show who did what.

Facts:

- ADR-0011 forbids agents from holding administrative credentials. ADR-0017 requires a registered identity and a hash-chained audit record for every tool call.
- ADR-0010 requires a named human to approve consequential actions.
- ADR-0016 rejects n8n for licence reasons. ADR-0011 says Devin is not in use. Both are open conflicts in M2M_ARCHITECTURE §2.
- The 2026-10-25 session connected by SSH to PC Alentejo and copied the repository there without an audit record. This is recorded as risk R-01 and must not repeat.
- No identity provider, reverse proxy or secret manager is deployed yet (ADR-0012, ADR-0013, ADR-0014 are Proposed).

Assumption: the owner accepts the Operations MCP design in M2M_ARCHITECTURE before any node is connected. This ADR does not connect any node.

## Decision

1. **One gateway.** All infrastructure reads and changes go through the Operations MCP (OPS-MCP). Agents, humans, workflows and future clients never open an SSH, API or console session to a node themselves.
2. **Typed capabilities, no shell.** OPS-MCP exposes a fixed set of named capabilities. It has no tool that runs an arbitrary command (MCP_STRATEGY rule 1).
3. **Default deny.** A principal can call a capability only when its role lists it. Unknown capabilities, unknown fields and unknown nodes are refused.
4. **Three tiers.** *Read* runs directly. *Write* (start, stop, restart, deploy) requires an approval record that a different human has granted for that exact request. *Manual* is never executed by OPS-MCP; it is reserved for changes listed as manual in M2M_ARCHITECTURE §6.
5. **Audit first.** Each call writes a record before it runs and a record after. If the record cannot be written, the call is refused (fail closed, ADR-0017 rule 5).
6. **Attribution.** Each record names the human, agent or workflow, the MCP client, the run id and the capability. Records are hash-chained and shipped to the sink (ADR-0018).
7. **Adapters are separate.** Each node type has its own adapter. Only adapters hold node credentials, and those credentials come from the secret broker (ADR-0014), not from configuration files.
8. **Stable API, replaceable backends.** Capability names and their schemas are the public contract. A new node type (Kubernetes, cloud VM, customer installation) adds an adapter and changes no capability.
9. **Phased activation.** The code in `ops-mcp/` is inert until the owner accepts this ADR. Activation then needs: ADR-0012 (identity), ADR-0014 (secrets), ADR-0017 (audit) active, and the Phase 03 gate closed.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: One Operations MCP gateway with typed capabilities, RBAC, approvals and audit (chosen) | One place to enforce and to audit; agents get no credentials; replaceable adapters | Build and operate one more component; single point of failure (mitigated by a runbook) | 3.86 (estimate) |
| B: Each client connects to nodes directly over SSH | No new component | No single audit point; keys spread across clients; violates ADR-0004 and the request | Rejected |
| C: Generic shell MCP with allow-listed commands | Flexible | Allow-lists are bypassed by arguments; hard to review; violates MCP_STRATEGY rule 1 | Rejected |
| D: Off-the-shelf automation platform (n8n or similar) as the gateway | Connectors ready | Licence (ADR-0016); workflow logic outside Git; approvals and audit not native | Not adopted; see C-1 |
| E: Do nothing; the owner runs every change by hand | No risk from new code | No audit; owner is the bottleneck; does not scale to agents | Rejected |

Score for A is an estimate. Values: value 5, frequency 4, cost 3, risk 3, reversibility 4, learning 5. Weighted sum: 15 + 8 + 9 + 9 + 8 + 5 = 54, divided by 14 = 3.86. Its risk value (3) is conditional on the controls in [security/OPS_MCP_THREAT_MODEL.md](../security/OPS_MCP_THREAT_MODEL.md).

## Consequences

- Positive: every infrastructure action is attributable, approved where required, and recorded.
- Positive: new node types and new clients do not change the agent-facing API.
- Negative: OPS-MCP becomes a critical dependency. Mitigation: a recovery runbook and a tested restore (BACKUP_STRATEGY).
- Negative: approvals add latency. Mitigation: read tier is direct; approvals are per request and expire after 15 minutes.
- Negative: sole-owner mode means the owner approves their own agents' requests. Mitigation: approval is a separate MFA step bound to the request hash; agents cannot approve; a second approver is required when a second maintainer joins.
- Follow-up: write the threat model addendum (done with this ADR, for review); deployment guide (`operations/OPS_MCP_DEPLOYMENT.md`); runbook RB-ops-mcp-recovery.
- Follow-up: record LSD2's identity and Sigma's ownership before any adapter for them is enabled (M2M_ARCHITECTURE §13).

## Security and compliance notes

- Trust boundaries: TB-1 (actors to Ops zone), TB-2 (Ops zone internal), TB-3 (gateway to nodes), TB-4 (node to node, denied). Defined in M2M_ARCHITECTURE §7.
- Data classes: the audit log is Internal with personal data possible in arguments (12-month retention, ADR-0017). Node credentials are Secret and never leave the broker.
- Controls: RBAC and policy in `ops-mcp/`, approvals bound to request hash, hash-chained audit, fail-closed writes, redaction before return. Threats T-02, T-03, T-11, T-12, T-16 and the new threats in the addendum apply.
- Security review: triggered (new interface, privileged access, authentication). Review by the `security-reviewer` role is read-only, so the owner performs the review and records it here before acceptance.
