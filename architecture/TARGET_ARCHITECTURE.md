# Target Architecture

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

**Status:** Proposed · Written against ADR-0001 rules. Each element names the ADR that approves it.

## Layers

```
Users (humans, agents, MCP clients)
   │  authenticated (ADR-0004)
Edge: reverse proxy + identity provider          ← Phase 04
   │
Portal (management UI, dashboards)               ← Phase 03
   │  scoped APIs
Services: knowledge, automation, AI             ← Phases 01, 04–06
   │
Data: Git (canonical), databases, backups        ← Phases 01, 05
   │
Infrastructure: hosts, storage, network          ← Phase 05 (declarative)
```

## Elements

| Element | Purpose | Approved by | Phase |
|---|---|---|---|
| Git hosting | Canonical documents and code | ADR-0008 | 00 |
| Identity provider with SSO and MFA | Single identity for humans and services | ADR-0012 (Proposed) | 04 |
| Reverse proxy with TLS | Single controlled entry point | ADR-0013 (Proposed) | 04 |
| Secret manager | Runtime secrets and scoped agent tokens | ADR-0014 (Proposed) | 04 |
| Portal | Operations and knowledge UI | ADR-0015 (Proposed, provisional) | 03 |
| Retrieval index | Search over canonical documents | ADR-0008 | 05 |
| Local models | AI capability, if approved | ADR-0007 | 04 |
| Automation engine | Scheduled and event workflows | ADR-0016 (Proposed) | 06 |
| Agents | Claude Code roles for governance and delivery | ADR-0011 (Proposed) | 00 |
| Telemetry | Health, resources, backups | ADR-0009 | 03 |

## Deviations (architecture debt)

| Deviation | Owner | Removal condition |
|---|---|---|
| Identity is local per host | Rui Silva (`9dot5`) | Identity provider live (Phase 04, ADR-0012) |
| Backups undefined per data set | Rui Silva (`9dot5`) | BACKUP_STRATEGY accepted and first restore test passed |
| Agent identities registered but pending: GitHub accounts, signing keys and audit export not yet created; agents do not run until they are | Rui Silva (`9dot5`) | Identities active, export shipping to monitoring (ADR-0017 follow-ups) |
| Agent hook and audit log run under the owner's OS user, so a process of that user can alter them | Rui Silva (`9dot5`) | Separate OS user or container for agents (ADR-0017 option D, Phase 08) |
| No secret manager; secrets live in the owner's password manager | Rui Silva (`9dot5`) | Secret manager live (Phase 04, ADR-0014) |

## Review

This document is reviewed at each phase gate. A change to any element requires its ADR to be Accepted first.
