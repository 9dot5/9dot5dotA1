# Operations MCP

**Owner:** Rui Silva (`9dot5`) · **Status:** Proposed · **Review by:** 2027-01-25
**Decision:** [ADR-0029](../adr/ADR-0029-operations-mcp.md) · **Version:** 0.1.0

**Not deployed. Inert until ADR-0029 is accepted.** Version 0.1 connects to no node, holds no credential, and answers every infrastructure capability with `not_configured`. What works: the authentication, RBAC, approval and audit logic, the MCP protocol surface, and the search of ADRs in this repository.

## What it is

The single gateway through which humans, Claude CLI, workflows and future agents reach infrastructure (M2M_ARCHITECTURE, ADR-0029). Agents never hold node credentials and never open a connection to a node.

## Layout

| Path | Purpose |
|---|---|
| `ops_mcp/capabilities.py` | The public API: names, tiers, argument schemas |
| `ops_mcp/identity.py` | Signed, short-lived tokens (development verifier; Authentik in production, ADR-0012) |
| `ops_mcp/policy.py` | RBAC by role, node scope, manual-only nodes. Default deny |
| `ops_mcp/approval.py` | Approval records: bound to one request, one approver, one use, 15-minute expiry. Journal with replay (ADR-0032) |
| `ops_mcp/gate.py` | Security gate: closed unless the ADRs are Accepted and both owner reviews are recorded (ADR-0031) |
| `ops_mcp/audit.py` | Hash-chained audit log, fsynced, fail closed |
| `ops_mcp/gateway.py` | The one path every call takes |
| `ops_mcp/adapters/` | Adapters. Built in: not-configured, node registry, ADR search |
| `ops_mcp/server.py` | MCP over stdio (initialize, tools/list, tools/call) |
| `config/nodes.json` | Node registry. No addresses, keys or credentials |
| `config/policy.json` | Roles. Only the owner's role can approve |
| `docs/API.md` | API contract, one section per capability |
| `tests/` | Security tests: authentication, RBAC, approval rules, audit chain, API contract |

## Run the tests

From `ops-mcp/`:

    python -m unittest discover -s tests -v

The suite covers forged, expired and tampered tokens; unknown capabilities, arguments and nodes; reader and workflow limits; approval by an agent, by the requester, for different content, after expiry, and reuse; audit chain editing and deletion; fail-closed audit writes; and the API contract.

## Known limits of version 0.1

- Approvals are persisted in `approvals.jsonl` beside the audit file and replayed at start (ADR-0032, R-23). Fixed in code on 2026-10-25, pending security review.
- Every state change is preceded by its audit record. A failed audit write changes nothing (ADR-0032, R-22, T-OPS-09). Fixed in code on 2026-10-25, pending security review.
- The security gate (ADR-0031 Part B) is closed in the shipped configuration. Node-touching calls are refused and audited until ADR-0029 to ADR-0033 are Accepted and the owner records the two reviews in `config/gate.json`.
- Tokens use a shared HMAC key. Production uses Authentik-issued tokens (ADR-0012).
- There is no rate limit on approval requests (threat T-OPS-07).
- Adapters for infrastructure are not written. Each one needs admission under ADR-0031 Part A, an adapter decision, and tests.

## Not included, by design

- No generic shell capability.
- No credentials in the repository or in configuration.
- No automatic discovery of hosts. Each node is added by hand to `config/nodes.json`, disabled until its access is recorded.

See [docs/API.md](docs/API.md), [architecture](../architecture/OPS_MCP_ARCHITECTURE.md), [threat model](../security/OPS_MCP_THREAT_MODEL.md) and [deployment guide](../operations/OPS_MCP_DEPLOYMENT.md).
