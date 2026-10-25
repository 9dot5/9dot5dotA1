# Access Control

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

**Status:** Proposed · **Control:** A.5.15, A.5.18, A.8.2, A.8.5 · **Principle:** ADR-0004

## Roles

| Role | Who | Can | Cannot |
|---|---|---|---|
| Owner | Human, one | Everything, including risk acceptance | — (keep an offline recovery path) |
| Maintainer | Human, delegated | Merge after review; operate services per runbook | Accept risk; change security baseline |
| Contributor | Human | Propose changes; read | Merge to `main` |
| Operator | Human or service | Run approved runbook steps | Change access rules |
| Agent (per agent type) | AI agent | Actions in AGENT_STRATEGY.md; on GitHub, everything except deleting a repository, including merge after checks (ADR-0036) | Delete a repository; accept risk; set an ADR status other than Proposed |
| Service | Software identity | Its documented interfaces | Anything not in its role |

## Rules

1. Access is granted per role, recorded in the identity provider (when live) or in the access register below.
2. Access is reviewed quarterly; removal is immediate on role change.
3. Administrative actions require MFA and are logged.
4. Elevated access is time-bound and requested per action.
5. Shared accounts are not permitted.

## Access register

| Identity | Role | Granted | Review date | Notes |
|---|---|---|---|---|
| Rui Silva (`9dot5`) | Owner | 2026-10-24 | 2027-01-24 | Quarterly review. Recovery path to be recorded offline. |
| `architect` (agent) | Agent | pending | 2027-01-24 | Identity pending: GitHub account and signing key not created. See operations/AGENT_IDENTITIES.md. |
| `governance-checker` (agent) | Agent | pending | 2027-01-24 | As above. Read-only. |
| `security-reviewer` (agent) | Agent | pending | 2027-01-24 | As above. Read-only. |
| `docs-maintainer` (agent) | Agent | pending | 2027-01-24 | As above. |
| `executor` (agent) | Agent | pending | 2027-01-24 | As above. May merge after checks (ADR-0036). |

## Repository protection

- `main` requires a pull request, at least one approval, passing checks, and no direct pushes.
- Owners of the paths in CODEOWNERS must approve changes to those paths.
- Force pushes and branch deletion on `main` are disabled.
