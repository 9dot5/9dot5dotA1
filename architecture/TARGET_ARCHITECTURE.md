# Target Architecture

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
| Identity provider with SSO and MFA | Single identity for humans and services | ADR-0004 (to be written) | 04 |
| Reverse proxy with TLS | Single controlled entry point | ADR-0004 | 04 |
| Portal | Operations and knowledge UI | ADR-0002 (to be written) | 03 |
| Retrieval index | Search over canonical documents | ADR-0008 | 05 |
| Local models | AI capability, if approved | ADR-0007 | 04 |
| Automation engine | Scheduled and event workflows | ADR-0002 (to be written) | 06 |
| Telemetry | Health, resources, backups | ADR-0009 | 03 |

## Deviations (architecture debt)

| Deviation | Owner | Removal condition |
|---|---|---|
| Identity is local per host | Rui Silva (`9dot5`) | Identity provider live (Phase 04) |
| Backups undefined per data set | Rui Silva (`9dot5`) | BACKUP_STRATEGY accepted and first restore test passed |

## Review

This document is reviewed at each phase gate. A change to any element requires its ADR to be Accepted first.
