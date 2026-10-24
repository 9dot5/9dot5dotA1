# System Context

**Status:** Proposed · **Owner:** Rui Silva (`9dot5`) · **Review:** each phase gate

## Actors

| Actor | Kind | Interaction |
|---|---|---|
| Owner | Human | Administers, approves, owns risk |
| Collaborators | Human | Read and contribute to knowledge; limited operations rights |
| Claude CLI | AI agent | Architect, reviewer, documenter, via MCP and terminal |
| Devin | AI agent | Executor: implements, tests, opens pull requests |
| MCP clients | Software | Expose platform capabilities to agents under scoped tokens |
| Upstream providers | External | Git hosting, Atlassian suite, model APIs, DNS, backup targets |

## The platform in one sentence

A governed system where knowledge, decisions and operations are stored once, and
humans and agents reach them through explicit, authenticated interfaces.

## Context diagram

The diagram source is `diagrams/context/system-context.md` (Mermaid). Keep it aligned with
the table above; a mismatch is a documentation defect.

## Trust boundaries

1. Internet to edge (reverse proxy, identity provider): untrusted.
2. Edge to platform services: authenticated and authorised per request.
3. Platform services to data stores: service identities, least privilege.
4. Agents to platform: scoped MCP tokens, no administrative rights by default.
5. Platform to external providers: outbound only, recorded in the service catalogue.

## Assumptions

- Hosts are not shared with untrusted users.
- The owner controls the identity provider.
- Backups leave the primary host to a separate location.
