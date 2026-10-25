# ADR-0039: One-off agent bootstrap of PC Alentejo through Desktop Commander

- **Status:** Proposed
- **Date:** 2026-10-25
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2026-11-25
- **Related:** ADR-0025, ADR-0029, ADR-0033, ADR-0034, ADR-0035, ADR-0037, [operations/BREAK_GLASS_REGISTER.md](../operations/BREAK_GLASS_REGISTER.md), [RISK_REGISTER.md](../RISK_REGISTER.md) (R-27, R-35)

## Context

The owner asked a Claude Code session on Legion to run the first monitoring bootstrap on PC Alentejo and to watch it, while the owner worked on GitHub (2026-10-25: "mas podes que eu deixo!"). The owner also told the session to stop non-essential applications on PC Alentejo to free memory.

Facts:

- ADR-0025 decision 8 (Accepted): the first `ansible-pull` on a host is started by the owner on that host and recorded under ADR-0033.
- ADR-0034 decision 8 (Accepted): agents on Legion open no SSH, remote desktop or other session to PC Alentejo.
- ADR-0033 rule 6 (Proposed): no agent holds or uses a break-glass path.
- PC Alentejo is reachable from the session through Desktop Commander, a remote shell on the `yau` account. It is not covered by the agent audit hook, which is not active yet (R-01).

## Decision

1. **A one-off exception, for 2026-10-25 only.** A Claude Code session may use the Desktop Commander path to PC Alentejo to: survey the host read-only, stop non-essential desktop applications that the owner named as stoppable, start the Podman machine, clone this repository, run `ansible/bootstrap/run-ansible-pull.ps1`, and check the four monitoring services.
2. **Everything applied comes from Git.** The session changes configuration only through the bootstrap script and the `monitoring` role on `main`. A fix found on the host goes through a pull request first.
3. **The session is a break-glass session.** It is listed in BREAK_GLASS_REGISTER and recorded in the owner's restricted store (ADR-0033 rules 2 and 3).
4. **Afterwards the accepted rules apply again.** Later runs are started by the owner or by the host's own schedule (ADR-0025). Agents do not use the Desktop Commander path for routine work (ADR-0029, ADR-0033 rule 7). Any further agent use needs a new decision.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: One-off agent bootstrap, recorded as break-glass (chosen) | The owner keeps working; the bootstrap is watched and fixed as it runs | An agent with a full shell on a node, without the audit hook | 3.36 (estimate) |
| B: Owner runs the bootstrap (ADR-0025 decision 8) | Matches the accepted rules | The owner asked for this work to be done for them | Rejected by the owner |
| C: Standing agent access to PC Alentejo through Desktop Commander | Convenient | Every routine action bypasses the gateway and the audit (R-27) | Rejected |

Score for A is an estimate. Values: value 4, frequency 1, cost 5, risk 2, reversibility 4, learning 4. Weighted sum: 12 + 2 + 15 + 6 + 8 + 4 = 47, divided by 14 = 3.36. It is below the 3.5 threshold; the owner accepts it as an exception, as ADR-0033 allows for a break-glass path.

## Consequences

- Positive: the first run happens now, and a defect in the bootstrap script was found and fixed before it ran (PR #6).
- Negative: a remote shell with the owner's account was used by an agent without the audit hook. Mitigation: the session record, and the register entry. Recorded as R-35.
- Negative: desktop applications were force-stopped because the workstation was locked. Mitigation: they were named by the owner; browser sessions are restored on next start.

## Security and compliance notes

- Trust boundaries: TB-8 (Legion, developer host) to PC Alentejo, bypassing TB-3 (gateway to nodes).
- Data classes: the session saw process lists and file paths on PC Alentejo (Internal). No secret value was printed or copied.
- Threats: T-OPS-17 (routine work through an unregistered path). This ADR keeps the path registered and limited to one day.
