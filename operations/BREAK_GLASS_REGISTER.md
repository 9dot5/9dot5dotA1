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
| 2026-10-31 | PC Alentejo | SSH from Legion (key added for the occasion) | Claude Code session on PC Alentejo (no `AGENT_ID`) | Owner asked for the access; it was not checked against ADR-0034 decision 8 first | Owner asked that Legion can SSH to the host. One test session (`hostname`, `whoami`) | To be written by the owner, `break-glass/2026-10-31-alentejo-ssh-from-legion.md` | Reverted the same day at the owner's choice. Later replaced by the hardened path of ADR-0041, on explicit owner instruction |
| 2026-10-31 | PC Alentejo | Local session on the node (not through Operations MCP) | Claude Code session on PC Alentejo (no `AGENT_ID`) | Owner, in the session ("eu autorizo") | `wsl --update` (no-op, already latest); fix of the k3s monitoring stack (Elasticsearch probe, Kibana token, Grafana mount); sshd hardening | To be written by the owner, `break-glass/2026-10-31-alentejo-k3s-and-ssh.md` | k3s manifest moved to Git (homelab-gitops PR #4, Argo CD); SSH change recorded in ADR-0041 and HOST_INVENTORY |
| 2026-10-30 to 2026-10-31 | PC Alentejo | SSH from Legion (owner's key) | Devin CLI session on Legion (no `AGENT_ID`, tool not registered) | Owner, in the session | Status survey; ADR-0035 bootstrap with Podman (stopped: starting Elasticsearch or Grafana reset the WSL VM); monitoring stack moved to k3s; Elasticsearch, Kibana and Grafana scaled to zero; pod `sigma-tunnel` added | To be written by the owner, `break-glass/2026-10-31-alentejo-devin.md` | Changes made directly with `kubectl`, not through Git; to reconcile with the k3s manifest in homelab-gitops |
| 2026-10-31 | Sigma | SSH, user account (owner's key) | Devin CLI session on Legion (no `AGENT_ID`, tool not registered) | Owner, in the session | Prometheus and Grafana installed in user space for metrics from PC Alentejo; tunnel key authorised | To be written by the owner, `break-glass/2026-10-31-sigma-devin.md` | Exception to ADR-0030 rule 3, recorded in ADR-0042 decision 9; owner to keep or remove |
| 2026-10-31 | Sigma and PC Alentejo | SSH, user account; SSH from Legion | Claude Code session on Legion (no `AGENT_ID`) | Owner, in the session | Read-only review; tunnel key restricted to one forward; `sigma-tunnel` restarted to check the forward | To be written by the owner, `break-glass/2026-10-31-sigma-key-restriction.md` | Backup of the key file kept on Sigma; forward checked working |
