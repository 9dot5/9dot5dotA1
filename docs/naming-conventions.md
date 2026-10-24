# Naming conventions

**Status:** Proposed

| Object | Convention | Example |
|---|---|---|
| Governance and architecture documents | `UPPER_SNAKE.md` | `ROI_MATRIX.md` |
| ADRs | `ADR-NNNN-kebab-title.md`, four-digit sequence, never reused | `ADR-0004-zero-trust.md` |
| Phase documents | `PHASE_NN_TOPIC.md` | `PHASE_02_SECURITY.md` |
| Runbooks | `RB-<service>-<topic>.md` | `RB-backup-restore.md` |
| Diagrams | `<area>/<kebab-name>.md` (Mermaid source) and exported image beside it | `architecture/target-overview.md` |
| Git branches | `<type>/<kebab-topic>` where type is `docs`, `feat`, `fix`, `sec`, `ops`, `chore` | `docs/adr-0004-zero-trust` |
| Jira keys | `PLAT-<n>` for platform work | `PLAT-12` |
| Services in the catalogue | `<component>-<host>`, lowercase | `knowledge-core-01` |
| Hosts | Role-based, no personal names | `host-control-01` |
| Secrets | `<service>/<purpose>` in the secret manager; never in names of files | `git/agent-readonly` |

Dates are ISO 8601 (`YYYY-MM-DD`). Time is UTC in logs and records.
