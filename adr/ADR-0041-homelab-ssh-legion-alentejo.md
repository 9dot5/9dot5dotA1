# ADR-0041: Hardened SSH between Legion and PC Alentejo

- **Status:** Proposed
- **Date:** 2026-10-31
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-30
- **Related:** ADR-0029, ADR-0033, ADR-0034, ADR-0037, ADR-0040, [operations/HOST_INVENTORY.md](../operations/HOST_INVENTORY.md), [operations/BREAK_GLASS_REGISTER.md](../operations/BREAK_GLASS_REGISTER.md), [RISK_REGISTER.md](../RISK_REGISTER.md) (R-01, R-27)

## Context

On 2026-10-31 the owner asked for SSH between the homelab machines, protected as far as possible, and authorised the change in the session ("eu autorizo e quero no meu homelab poder fazer ssh entre maquinas. quero protejer tudo ao maximo").

Facts:

- ADR-0034 decision 8 (Accepted) says agents on Legion open no SSH, remote desktop or other session to PC Alentejo. ADR-0033 rule 7 (Proposed) treats plain SSH into a node as break-glass. ADR-0040 (Proposed) covers SSH between workstations only.
- Operations MCP (ADR-0029) is not running, so there is no audited routine path to PC Alentejo. Every routine change on it has gone through Desktop Commander or SSH as break-glass (R-27).
- Before the change, PC Alentejo's sshd accepted passwords, and on both hosts the port-22 rule allowed any address on the Private profile, which includes the home LAN.
- This host's only key was `ist178938@sigma04`. The same key is used on a shared university host (`ext-sigma-01`) and was authorised on Legion.
- Both hosts run OpenSSH for Windows 9.5p2 on LibreSSL, which has no post-quantum key exchange.

## Decision

1. **Key-only SSH is allowed in both directions between `host-dev-01` (Legion) and `host-ops-01` (PC Alentejo).** It covers the owner and Claude Code sessions acting on the owner's instruction. This decision **supersedes ADR-0034 decision 8**. Until Operations MCP is admitted, this path is the routine path, not break-glass.
2. **Baseline on both sshd servers** (applied 2026-10-31):
   - public keys only (`AuthenticationMethods publickey`, ed25519 only);
   - passwords and keyboard-interactive off;
   - `AllowUsers` set to the one local account;
   - `MaxAuthTries 3` and `LoginGraceTime 30`;
   - curve25519 key exchange, AEAD ciphers and ETM MACs only;
   - agent forwarding, X11, tunnels and remote port forwarding off, with local forwarding (`-L`) allowed;
   - `LogLevel VERBOSE`, so the fingerprint of every login is logged.
3. **Network:** inbound TCP 22 is allowed only from the tailnet (`100.64.0.0/10`, `fd7a:115c:a1e0::/48`), on every profile. Other port-22 rules stay disabled. Each authorised key also carries `from="<tailnet>"`, `no-agent-forwarding` and `no-X11-forwarding`, so a key copied off the tailnet is useless.
4. **One key per source host, used only inside the homelab.** PC Alentejo uses `yau@DESKTOP-Q3GOUP4` (new, fingerprint below). The Sigma key is no longer authorised on Legion. Legion uses `rsilv@Legion-9dot5`.
5. **Recording:** agent sessions over this path are recorded through ADR-0017 once the audit hook is active. Until then, R-01 applies, and the owner accepts that residual risk with this ADR.
6. `host-ws-01` keeps its ADR-0040 restrictions. It gets **no** key on PC Alentejo.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Hardened key-only SSH over the tailnet, with key `from=` restrictions (chosen) | What the owner asked for; layered controls (Tailscale, firewall, key options, sshd); every key traceable | Agent sessions are not audited until ADR-0017 is active (R-01); routine access to a node bypasses the future gateway | 3.57 (estimate) |
| B: Keep ADR-0034 decision 8; break-glass only | Strongest separation | Not what the owner wants; in practice, routine work keeps happening off-record (R-27) | Rejected by the owner |
| C: Wait for Operations MCP | Single audited gateway | No date; blocks routine work | Deferred |

## Consequences

- Positive: routine access is possible without passwords. The LAN no longer reaches port 22 on either host, which closes the ADR-0040 decision 6 follow-up for Legion.
- Negative: a compromise of Legion gives a shell on the node. Mitigation: one user only, no forwarding of agents, tailnet only; Tailscale ACLs as a follow-up.
- Follow-up (owner, Tailscale admin console): ACL so that only `host-dev-01` and `host-ops-01` can reach `tcp:22` on each other.
- Follow-up: once ADR-0029 is admitted, review whether this path goes back to break-glass.

## Security and compliance notes

- Trust boundaries: TB-8 (Legion) to the node, bypassing TB-3 (gateway), by owner decision.
- Keys (SHA256): `yau@DESKTOP-Q3GOUP4` `3oWU1b2qCiiwQ+KmAsYpLEvT2zzZ1hdF0AXtH7B6/80`; `rsilv@Legion-9dot5` `a85j9NJJNkzncvmHDkbzYGND5Np+yKRmU5ceCdWv2/c`; `9dot5@DESKTOP-QFGSNE9` `o70xPnklcInqSHuiQzvhiMnwgdxwsujOVQIGdj91vTk` (still authorised on Legion, ADR-0040).

## Change history

| Date | Change | By |
|---|---|---|
| 2026-10-31 | Proposed. The baseline was applied on the owner's instruction before the ADR was written (exception to documentation-first, ADR-0005) | Unregistered Claude Code session on PC Alentejo (no `AGENT_ID`) |
