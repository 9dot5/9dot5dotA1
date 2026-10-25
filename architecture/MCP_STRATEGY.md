# MCP Strategy

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

**Status:** Proposed · **Related:** ADR-0007, ADR-0010, [security/ACCESS_CONTROL.md](../security/ACCESS_CONTROL.md)

## Purpose

MCP servers expose platform capabilities to AI agents in a uniform way. They also widen
the attack surface: each tool is an action an agent can take. The strategy keeps
capabilities useful and bounded.

## Planned servers

| Server | Capability | Access | Phase |
|---|---|---|---|
| Knowledge | Read and search canonical documents | Read-only | 05 |
| Governance | Read ADRs, principles, standards; list open decisions | Read-only | 01 |
| Security | Read threat model, baseline, findings | Read-only; write requires review | 02 |
| Architecture | Read landscape and target; draft ADRs as pull requests | Draft only | 02 |
| Operations | Read service catalogue and status; run approved runbook steps | Read by default; write requires human confirmation | 06 |

## Rules

1. One server, one purpose. No general-purpose "shell" server.
2. Read-only by default. Write capabilities are listed explicitly and need an ADR.
3. Each server authenticates with a scoped token that expires. Tokens are never stored in documents.
4. Each tool call is logged with the calling identity and arguments (redacting secrets).
5. Tool descriptions are reviewed like API contracts.
6. Output from tools is treated as untrusted input to the agent; prompt-injection
   defences apply (see THREAT_MODEL).

## Acceptance criteria for a new MCP server

- ADR accepted, with a threat model entry.
- Token scope documented.
- Tests cover denied access, not only allowed access.
- Runbook entry exists for its failure modes.
