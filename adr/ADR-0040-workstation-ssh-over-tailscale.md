# ADR-0040: SSH between owner workstations over Tailscale

- **Status:** Proposed
- **Date:** 2026-10-25
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-25
- **Related:** ADR-0004, ADR-0029, ADR-0031, ADR-0033, ADR-0039, [operations/HOST_INVENTORY.md](../operations/HOST_INVENTORY.md), [operations/BREAK_GLASS_REGISTER.md](../operations/BREAK_GLASS_REGISTER.md), [RISK_REGISTER.md](../RISK_REGISTER.md) (R-01, R-36)

## Context

On 2026-10-25 the owner set up SSH in both directions between Legion (`host-dev-01`) and a third machine, `DESKTOP-QFGSNE9` (`host-ws-01`), and asked that Claude Code sessions on Legion can connect to it on their own.

Facts:

- ADR-0029 and ADR-0033 govern access to **nodes**. ADR-0033 rule 7 treats plain SSH into a node as break-glass. Neither ADR covers SSH between the owner's workstations, which are developer clients (TB-8), not nodes.
- `host-ws-01` runs Windows 10 Home 1903, out of support since December 2020, with OpenSSH 7.7 for Windows and 3.2 GB of RAM.
- Before 2026-10-25 its SSH server accepted passwords, and one firewall rule allowed TCP 22 on all network profiles. Both were changed that day: key-only, and a Tailscale-only rule.
- Legion's SSH server is key-only. Its firewall rule is on the Private profile, and both its Tailscale and Wi-Fi interfaces are Private, so hosts on the home LAN can also reach port 22.
- Agent sessions on Legion are not yet audited (R-01).

## Decision

1. **SSH is allowed between owner workstations** listed in HOST_INVENTORY as class *workstation*, in both directions, for the owner and for Claude Code sessions acting on the owner's instruction. It is not break-glass, because no node is involved.
2. **Nodes are excluded.** SSH from a workstation to a node (`host-ops-01`, Sigma) stays under ADR-0029 and ADR-0033 (break-glass only).
3. **Baseline on every workstation SSH server:** key-only authentication; inbound TCP 22 allowed only from the Tailscale range; the authorised key files readable only by their owner, SYSTEM and Administrators; UTF-8 without BOM. HOST_INVENTORY records the baseline per host and the fingerprints of every authorised key.
4. **One key per source host**, named `user@host`. A key is added to a workstation only with its fingerprint recorded in HOST_INVENTORY, and removed when the source host is retired.
5. **Hosts out of vendor support hold nothing of value.** `host-ws-01` keeps no agent identity, signing key, repository write credential or secret, and holds no node role, until it is upgraded or retired.
6. **Legion's firewall rule is narrowed to the Tailscale range** as a follow-up, so that the LAN no longer reaches its port 22. This is an owner action on Legion (administrator).

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Key-only SSH between workstations over Tailscale, with a recorded baseline (chosen) | What the owner asked for; no passwords on the wire; every key traceable | Agent SSH between workstations is not yet audited (R-01); an unsupported OS stays on the tailnet | 3.57 (estimate) |
| B: Treat workstation SSH as break-glass (ADR-0033 rule 7 applied to workstations) | One rule for every SSH session | Every routine connection needs a session record; not what the owner wants | Rejected |
| C: Keep password authentication as a fallback | Easy recovery | Passwords guessable on an unsupported OS; the server was reachable from every network | Rejected |

Score for A is an estimate. Values: value 4, frequency 3, cost 4, risk 3, reversibility 4, learning 3. Weighted sum: 12 + 6 + 12 + 9 + 8 + 3 = 50, divided by 14 = 3.57. Risk is 3 because one of the two hosts runs an unsupported Windows build.

## Consequences

- Positive: the owner and the agent session can reach `host-ws-01` with a key, and the passwords path is closed.
- Negative: `host-ws-01` is an unsupported Windows build on the tailnet. Mitigation: decision 5 and R-36; upgrade or retire it.
- Negative: an agent session can run commands on `host-ws-01` without an audit record until ADR-0017 is active. Mitigation: R-01 work; nothing of value on that host.
- Follow-up: narrow Legion's SSH firewall rule to the Tailscale range (owner, decision 6).
- Follow-up: upgrade `host-ws-01` to a supported Windows version, or retire it; then update OpenSSH there.

## Security and compliance notes

- Trust boundaries: TB-8 (workstations). No node boundary is crossed.
- Data classes: none stored on `host-ws-01` beyond Public (decision 5).
- Threats: compromise of an unsupported workstation used as a stepping stone to Legion. Mitigation: key-only, Tailscale-only, no secrets there, R-36.
