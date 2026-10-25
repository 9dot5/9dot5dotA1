# ADR-0033: Out-of-band access policy

- **Status:** Proposed
- **Date:** 2026-10-25
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-25
- **Related:** ADR-0004, ADR-0010, ADR-0017, ADR-0029, ADR-0031, [security/SECRET_MANAGEMENT.md](../security/SECRET_MANAGEMENT.md), [security/DISASTER_RECOVERY.md](../security/DISASTER_RECOVERY.md), [operations/AGENT_IDENTITIES.md](../operations/AGENT_IDENTITIES.md)

## Context

Out-of-band access is any way into a node that does not go through Operations MCP: a local console, a remote-desktop session, a manual SSH login, a physical visit, a vendor portal, or a recovery account. Such paths are needed. A node that can only be reached through the gateway fails when the gateway fails. But each one bypasses the controls of ADR-0029, and today nothing governs them.

Facts:

- Today the owner reaches PC Alentejo by SSH from a personal session. That session is not audited (R-01).
- Sigma has no root for the owner, so out-of-band access there is limited to the user account.
- The CSHP lab machines are not owned, so out-of-band access to them is not the owner's to grant.

## Decision

1. **Out-of-band access is allowed only as a break-glass path.** It is used when the gateway or its audit cannot be used, and for recovery, never for routine change.
2. **Each break-glass path is listed** in the access register: node, method, account, who holds the credential, and where the recovery material is kept. A path not in the register is not permitted.
3. **Every break-glass session is recorded by hand** in a dated record: time, reason, what was done, who approved, and the outcome. The record is written within 24 hours, in the restricted incident store (INCIDENT_RESPONSE).
4. **Break-glass changes are reconciled with the gateway afterwards.** Any change made out of band is brought back into Git or into the registry, or reverted, within two working days (standards §4, emergency change).
5. **Credentials for break-glass paths** are held by the owner in the password manager, with an offline copy of the recovery material. Each is rotated at least yearly and at once after use by anyone other than the owner.
6. **No agent holds or uses a break-glass path.** An agent that needs one stops and asks the owner (ADR-0010 rule 4).
7. **Routine remote access to a node is not break-glass.** Routine access goes through Operations MCP (ADR-0029) or it is not permitted. Remote desktop, plain SSH sessions and vendor portals are break-glass by this rule.
8. **Out-of-band access to a shared or external node** (Sigma, lab PCs) is not permitted without a recorded decision under ADR-0030 or ADR-0031.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Break-glass only, registered, recorded, reconciled (chosen) | Recovery remains possible; every bypass is listed and reviewed | Manual record-keeping; slower routine change for the owner | 3.64 (estimate) |
| B: No out-of-band access at all | Strongest control | A gateway failure locks the owner out of nodes; no recovery | Rejected |
| C: Out-of-band access allowed for routine work | Convenient | Every routine action bypasses the audit; this is the current practice that R-01 records | Rejected |
| D: Out-of-band access logged by the operating system only | Automatic | Not attributable to an approval; the logs sit on the node that is being changed | Rejected as the only control |

Score for A is an estimate. Values: value 4, frequency 2, cost 3, risk 4, reversibility 4, learning 3. Weighted sum: 12 + 4 + 9 + 12 + 8 + 3 = 48, divided by 14 = 3.43. This is below the threshold of 3.5. The rule is kept because it is a control and not a service, and the owner must accept the score explicitly.

## Consequences

- Positive: each bypass is listed, dated and reconciled, so an unrecorded change becomes visible.
- Negative: the owner records each break-glass session by hand. Mitigation: a template in `docs/templates/`.
- Negative: the current practice of plain SSH to PC Alentejo is non-compliant from the date of acceptance. Mitigation: the access register is written before the policy is accepted, and the 2026-10-25 connection is recorded there.
- Follow-up: create the access register table (`operations/BREAK_GLASS_REGISTER.md`).
- Follow-up: write the break-glass runbook RB-break-glass (not yet written).

## Security and compliance notes

- Trust boundaries: TB-1 and TB-3 are bypassed by break-glass access, so the policy compensates with registration and reconciliation.
- Controls: access register; per-session record; reconciliation within two working days; credential rotation; no agent use.
- Threats: T-OPS-17 (routine work through an unregistered path), added to the threat model. Residual: the owner can misuse a break-glass path. Mitigation: the reconciliation record makes a misuse visible afterwards. The owner accepts this residual risk.
