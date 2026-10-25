# Break-glass Register

**Owner:** Rui Silva (`9dot5`) · **Status:** Proposed · **Review by:** 2027-01-25
**Related:** [ADR-0033](../adr/ADR-0033-out-of-band-access-policy.md), [ADR-0039](../adr/ADR-0039-agent-bootstrap-pc-alentejo.md), [security/INCIDENT_RESPONSE.md](../security/INCIDENT_RESPONSE.md), [RISK_REGISTER.md](../RISK_REGISTER.md) (R-27)

The list of out-of-band paths into each node (ADR-0033 rule 2). A path not listed here is not permitted. This repository is public, so the register names paths and holders only: no addresses, ports, passwords or keys. Each session's record is kept outside the repository, in the owner's restricted store (ADR-0033 rule 3).

SSH between the owner's workstations (`host-dev-01`, `host-ws-01`) is not break-glass and is not listed here: it is governed by [ADR-0040](../adr/ADR-0040-workstation-ssh-over-tailscale.md) and recorded in [HOST_INVENTORY.md](HOST_INVENTORY.md).

## Paths

| Node | Method | Account | Credential held by | Recovery material | Status |
|---|---|---|---|---|---|
| PC Alentejo | Local console | `yau` | Owner | Owner's password manager | Listed |
| PC Alentejo | SSH from the owner's session | `yau` | Owner | Owner's password manager | Listed. Used 2026-10-25 without a record (R-27); recorded below |
| PC Alentejo | Desktop Commander remote shell | `yau` | Owner (Desktop Commander account) | Desktop Commander device management | Listed. Agent use only under ADR-0039 |
| Sigma | SSH, user account | personal IST account | Owner | Owner's password manager | Listed. No root (ADR-0030) |

## Sessions

| Date | Node | Path | Who acted | Approved by | Reason | Record | Reconciled |
|---|---|---|---|---|---|---|---|
| 2026-10-25 | PC Alentejo | SSH from the owner's session | Claude Code session (no `AGENT_ID`) | Not recorded | Repository copied to the host | Not written at the time (R-27) | Copy left at its path; not used |
| 2026-10-25 | PC Alentejo | Desktop Commander remote shell | Claude Code session (no `AGENT_ID`) | Owner, in the session | First monitoring bootstrap (ADR-0035), freeing memory for it | Owner's restricted store, `break-glass/2026-10-25-alentejo-monitoring-bootstrap.md` | Configuration applied from `main`; ADR-0039 records the exception |
