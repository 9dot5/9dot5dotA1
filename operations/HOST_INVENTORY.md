# Host Inventory

**Owner:** Rui Silva (`9dot5`) · **Status:** Proposed · **Review by:** 2027-01-25
**Related:** [docs/naming-conventions.md](../docs/naming-conventions.md), [architecture/SYSTEM_LANDSCAPE.md](../architecture/SYSTEM_LANDSCAPE.md), [SERVICE_CATALOG.md](SERVICE_CATALOG.md), [BREAK_GLASS_REGISTER.md](BREAK_GLASS_REGISTER.md), [ADR-0031](../adr/ADR-0031-node-admission-policy.md), [ADR-0040](../adr/ADR-0040-workstation-ssh-over-tailscale.md)

The single list of the owner's machines. Every other document names a host by its **ID** from this table. IDs follow the naming convention (role-based, no personal names); the Windows host name and the nickname are kept so that people and tools can find the machine. This repository is public: no addresses, ports or passwords here.

## Hosts

| ID | Host name | Nickname | Class | Ownership (ADR-0031) | Hardware (measured 2026-10-25) | OS | Roles | Status |
|---|---|---|---|---|---|---|---|---|
| `host-dev-01` | `Legion-9dot5` | Legion | Workstation | Owned | Laptop, 6C/12T, 7.9 GB RAM | Windows 11 Home (build 26300) | Development, agent sessions (`agent-runner`), course work | Active |
| `host-ops-01` | `DESKTOP-Q3GOUP4` | PC Alentejo | Node (candidate) | Owned, account `yau` | Desktop, Ryzen 7 3700X, 16 GB RAM, NVIDIA GPU (8 GB VRAM, stated in agent-sandbox, not measured), 465 GB disk | Windows (version not recorded yet) | Monitoring stack (ADR-0035), Ollama, k3s in WSL, second agent host (ADR-0034) | Active; not admitted to Operations MCP |
| `host-ws-01` | `DESKTOP-QFGSNE9` | maindesktop | Workstation | Owned (to confirm), account `9dot5` | Laptop Toshiba Satellite L50-A, i7-4700MQ, 3.2 GB RAM, GT 740M, 930 GB disk | **Windows 10 Home 1903 (build 18362), out of support** | SSH client and target for the owner | Active; restricted (see below) |
| `ext-sigma-01` | `sigma04.ist.utl.pt` | Sigma | External shared host | Shared (university) | 8 vCPU, 15 GB (SERVICE_CATALOG) | Debian 12 | Course work, monitoring centre (ADR-0030) | Active, not owned |

Classes: a **node** is a host that Operations MCP may reach once admitted (ADR-0031). A **workstation** is an owner's machine used by people and agent sessions; it is a developer client (TB-8), not a node.

## Access between hosts

| From | To | Method | Credential | Allowed by |
|---|---|---|---|---|
| `host-dev-01` | `host-ws-01` | SSH over Tailscale, key only | `rsilv@Legion-9dot5` ed25519 key | ADR-0040 |
| `host-ws-01` | `host-dev-01` | SSH over Tailscale, key only | `9dot5@DESKTOP-QFGSNE9` ed25519 key | ADR-0040 |
| `host-dev-01` | `host-ops-01` | SSH or Desktop Commander | Owner | Break-glass only (ADR-0033, ADR-0039) |
| `host-dev-01` | `ext-sigma-01` | SSH, user account | Owner's key | Course work; ADR-0030 for monitoring |

Key fingerprints are recorded so that an unexpected key can be spotted:

| Key | Fingerprint (SHA256) | Authorised on |
|---|---|---|
| `rsilv@Legion-9dot5` (ed25519) | `a85j9NJJNkzncvmHDkbzYGND5Np+yKRmU5ceCdWv2/c` | `host-ws-01` (`administrators_authorized_keys` and the user file) |
| `9dot5@DESKTOP-QFGSNE9` (ed25519) | `o70xPnklcInqSHuiQzvhiMnwgdxwsujOVQIGdj91vTk` | `host-dev-01` (`administrators_authorized_keys`) |

## Baseline for SSH servers on workstations (ADR-0040)

- Key-only: `PasswordAuthentication no`, `ChallengeResponseAuthentication no` (or `KbdInteractiveAuthentication no`).
- Firewall: inbound TCP 22 allowed only from the Tailscale range; no rule open on all profiles.
- Members of Administrators use `C:\ProgramData\ssh\administrators_authorized_keys`, readable by SYSTEM and Administrators only, UTF-8 without BOM.

| Host | Key-only | Tailscale-only firewall | Checked |
|---|---|---|---|
| `host-dev-01` | Yes | Rule is on the Private profile; the Tailscale and Wi-Fi interfaces are both Private, so the LAN can reach port 22 too | 2026-10-25 |
| `host-ws-01` | Yes (from 2026-10-25) | Yes (`sshd-tailscale`; the all-profiles rule disabled 2026-10-25) | 2026-10-25 |

## Restrictions for `host-ws-01`

Windows 10 1903 receives no security updates. Until it is upgraded or retired: no agent identity, no signing key, no repository write credential and no secret is stored on it, and it holds no node role (R-36).
