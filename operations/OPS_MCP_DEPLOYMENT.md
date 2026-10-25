# Operations MCP: Deployment Guide

**Owner:** Rui Silva (`9dot5`) · **Status:** Proposed · **Review by:** 2027-01-25
**Related:** [ADR-0029](../adr/ADR-0029-operations-mcp.md), [ops-mcp/README.md](../ops-mcp/README.md), [security/OPS_MCP_THREAT_MODEL.md](../security/OPS_MCP_THREAT_MODEL.md), [BACKUP_STRATEGY.md](BACKUP_STRATEGY.md)

## 0. Status

**This service must not be deployed yet.** It becomes deployable only when ADR-0029 is Accepted, the threat-model addendum has its residual risks decided, and the Phase 03 gate is closed. Until then this guide is the plan, and it is written so that the steps can be checked against reality.

Preconditions that are not yet met:

| Precondition | Source | State (2026-10-25) |
|---|---|---|
| ADR-0029 to ADR-0033 Accepted | ADR-0010, ADR-0031 gate | Proposed (all five) |
| Owner review of threat model and permission matrix recorded in `config/gate.json` | ADR-0031 Part B | Not recorded |
| Identity provider live | ADR-0012 | Proposed, not deployed |
| Secret broker live | ADR-0014 | Proposed, not deployed |
| Audit sink decided | ADR-0018, C-5 | Dynatrace unconfirmed |
| Approval audit-before-change (R-22) | threat T-OPS-09, ADR-0032 | Fixed in code, pending security review |
| Persistent approval journal (R-23) | ADR-0032 | Fixed in code, pending security review |
| Control node measured | ADR-0015, B-35 | Not measured |
| LSD2 identified | M2M Q1 | Unknown |
| Sigma role decided | C-5, C-6 | Monitoring centre; options open |

## 1. Target layout

- One control node, owner-controlled. It hosts Authentik, the reverse proxy (ADR-0013), the secret broker, Operations MCP and the audit store.
- Operations MCP runs as its own service account, with no interactive login.
- Nodes are reached only by the adapters, through restricted accounts with forced commands (M2M §4.3).

## 2. Install (when preconditions are met)

Not yet written. Each step will be a declarative definition in Git, applied through the pipeline (DEPLOYMENT_STRATEGY), with a rollback step. Version 0.1 has no installer by design: the package is run as Python from the repository, and nothing is installed on a host.

## 3. Configuration

| Setting | Source | Content |
|---|---|---|
| Signing key | secret broker, environment variable `OPS_MCP_KEY` | At least 32 bytes. Never in a file |
| Client token | issued by Authentik, environment variable `OPS_MCP_TOKEN` | Per client process |
| Audit file | environment variable `OPS_MCP_AUDIT` | Path outside the repository, on owner-controlled storage |
| Nodes | `config/nodes.json` | Reviewed in Git. Enabling a node needs a recorded access decision |
| Roles | `config/policy.json` | Reviewed in Git. Only the owner's role has `may_approve` |

## 4. Verification

1. Run the test suite: `python -m unittest discover -s tests -v` from `ops-mcp/`. All tests must pass.
2. Start the server with a test token and call `get_nodes`. It must return the registry and write two audit records.
3. Run `python -m ops_mcp verify`. It must print `OK`.
4. Call `restart_service` as an agent. It must return `approval_required` and must not reach an adapter.
5. Approve from the owner's terminal. The repeated call must run once, and a third call must need a new approval.
6. Edit one line of the audit file and run `verify` again. It must fail. Restore the file from backup afterwards.

## 5. Rollback

- Stop the process. Clients get no response and no action is taken.
- Revert the commit that enabled a node in `config/nodes.json`.
- Keep the audit file. It is evidence, not state (ADR-0017).

## 6. Recovery

Recovery material for the signing key and the audit file is covered by BACKUP_STRATEGY (data sets to add, B-08). A restore is tested before the first real use. The key-loss procedure is in the runbook RB-ops-mcp-recovery, which is not yet written.

## 7. Monitoring

- Alerts: process down for 5 minutes; audit verification failed; any `denied` record for a write capability; approval flood (more than 20 pending per hour, proposed).
- Owner of alerts: the owner. Runbook links: RB-ops-mcp-recovery (to write), RB-agent-audit-ship (B-15).

## 8. Not allowed

- Running it on Sigma or on a lab PC. Sigma is a monitoring centre and a shared host (C-5). Lab PCs are outside the owner's control.
- Exposing the MCP server on a network address. It is a stdio process for local clients. A network transport needs its own ADR.
- Storing node credentials in `config/`, in environment variables of agents, or in the repository.
