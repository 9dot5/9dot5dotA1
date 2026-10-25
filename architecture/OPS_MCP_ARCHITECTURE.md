# Operations MCP: System Architecture (Phase 1)

**Owner:** Rui Silva (`9dot5`) · **Status:** Proposed · **Review by:** 2027-01-25
**Related:** [ADR-0029](../adr/ADR-0029-operations-mcp.md), [M2M_ARCHITECTURE.md](M2M_ARCHITECTURE.md), [MCP_STRATEGY.md](MCP_STRATEGY.md), [security/OPS_MCP_THREAT_MODEL.md](../security/OPS_MCP_THREAT_MODEL.md)

Phase 1 deliverables: system context, components, sequences, permissions, trust boundaries and risks. The permission matrix and the trust-boundary table are maintained in [M2M_ARCHITECTURE.md](M2M_ARCHITECTURE.md) §6 and §7 and are not repeated here. Risks are in [RISK_REGISTER.md](../RISK_REGISTER.md) (R-22 to R-26 added below).

## 1. System context

```mermaid
flowchart LR
  owner([Owner]) -->|OIDC + MFA| idp[Authentik]
  owner -->|approve, local terminal| ops
  human([Human operator]) --> idp
  claude[Claude CLI session] -->|MCP stdio, agent token| ops
  devin[Devin - only if approved, C-2] -.-> ops
  rovo[Rovo] -.->|read-only, if approved| ops
  wf[Automation workflow] -->|workflow token| ops
  future[Future agents, clients] -.-> ops

  subgraph ctrl[Control zone - to be hosted]
    ops[Operations MCP]
    idp
    audit[(Audit store)]
    secrets[Secret broker]
  end

  ops --> audit
  ops --> secrets
  ops -->|restricted SSH, forced command| alentejo[PC Alentejo]
  ops -->|health and metrics only, C-5| sigma[Sigma - monitoring centre]
  sigma -.->|named hop only, C-6| lab[CSHP lab PCs]
  ops -.->|disabled until identified| lsd2[LSD2 - Q1]
  ops -.->|API token, future| pve[Proxmox - future]
  ops -.->|future adapters| k8s[Kubernetes / cloud - future]
```

Version 0.1 contains only the MCP server, the gateway and the adapters that need no network. The arrows to nodes are the target design, not code.

## 2. Components

| Component | Responsibility | Module | State in 0.1 |
|---|---|---|---|
| MCP server | Protocol surface. Reads one token per process | `server.py` | Implemented |
| Gateway | Single path for all calls. Orders the checks | `gateway.py` | Implemented |
| Capability registry | Public names, tiers, schemas | `capabilities.py` | Implemented, 21 capabilities |
| Token verifier | Authentication | `identity.py` | Development verifier. Authentik is the target (ADR-0012) |
| Policy engine | RBAC, node scope, manual-only | `policy.py` | Implemented |
| Approval engine | One-time, bound, expiring approvals | `approval.py` | Implemented, in memory |
| Audit log | Hash chain, fail closed | `audit.py` | Implemented, local file. Sink to ADR-0018 later |
| Adapters | Execute against a node or a source | `adapters/` | Not-configured, node registry, ADR search |
| Secret broker | Node credentials, short-lived | ADR-0014 | Not present |

## 3. Sequence: read call

```mermaid
sequenceDiagram
  participant C as Claude CLI
  participant S as MCP server
  participant G as Gateway
  participant A as Audit log
  participant P as Policy
  participant D as Adapter
  C->>S: tools/call get_nodes
  S->>G: call(token, get_nodes)
  G->>G: validate schema, unknown fields refused
  G->>G: verify token (signature, expiry)
  G->>A: attempt (fail closed)
  G->>P: decide(principal, capability, node)
  P-->>G: allow
  G->>D: execute
  D-->>G: result
  G->>A: result
  G-->>S: result
  S-->>C: text result
```

## 4. Sequence: write call with approval

```mermaid
sequenceDiagram
  participant C as Agent (executor)
  participant G as Gateway
  participant A as Audit log
  participant O as Owner (terminal)
  participant D as Adapter
  C->>G: restart_service(alentejo, qdrant)
  G->>A: attempt
  G->>G: policy: write tier, approval needed
  G->>G: no approval for this requester and hash
  G->>A: approval_requested (request_id, hash)
  G-->>C: approval_required (request_id)
  O->>G: approve(request_id), owner MFA token
  G->>G: checks: human, may_approve, not requester, unused, unexpired
  G->>A: approval_granted
  C->>G: restart_service(alentejo, qdrant) again
  G->>G: consume approval (one use)
  G->>D: execute
  D-->>G: result
  G->>A: result
  G-->>C: result
```

## 5. Sequence: refusal

Refusals (bad token, unknown capability, unknown argument, disabled node, manual-only node, role not granted) write an audit record and return an error. No adapter is called. The refusal reason is recorded so that repeated refusals can be reviewed.

## 6. Sigma as monitoring centre

Decided by the owner on 2026-10-25. Sigma is a shared university host, so its role is limited:

- It receives health and metrics pushed by nodes (TB-5). It is not where audit records or secrets are stored (C-5, recommendation a).
- It is not a write target. Writes to Sigma are refused (`manual_only`).
- A hop from Sigma to a CSHP lab PC is a separate, named, disabled-by-default entry in the node registry, after ADR-0031 Part C admits that host (C-6). Discovery of lab machines is not automatic.

## 7. Trust boundaries

Defined in [M2M_ARCHITECTURE.md](M2M_ARCHITECTURE.md) §7 (TB-1 to TB-8). The boundaries relevant to version 0.1 are TB-1 (actor to gateway) and TB-2 (inside the control zone). Everything beyond the gateway is not yet connected.

## 8. New risks (added to RISK_REGISTER)

| ID | Risk | L | I | Score | Treatment |
|---|---|---|---|---|---|
| R-22 | Approval is recorded after state change; a failed audit write leaves an approval without a record | 2 | 4 | 8 | Reduce. Reverse the order before activation |
| R-23 | Approvals and audit cursor are in memory; a restart loses pending approvals | 3 | 2 | 6 | Reduce. Persist in Phase 03 |
| R-24 | Sigma (shared) holds monitoring data about the owner's nodes | 3 | 3 | 9 | Reduce. Health and metrics only (C-5) |
| R-25 | Hops from Sigma to lab PCs widen the attack path to machines with no owner | 3 | 4 | 12 | Avoid until ADR-0031 Part C. Named entries only (C-6) |
| R-26 | Shared HMAC key for tokens in development use | 2 | 4 | 8 | Reduce. Authentik before any real node |
