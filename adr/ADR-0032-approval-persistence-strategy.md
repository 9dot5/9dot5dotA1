# ADR-0032: Approval persistence and the ordering of state changes

- **Status:** Proposed
- **Date:** 2026-10-25
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-25
- **Related:** ADR-0010, ADR-0017, ADR-0018, ADR-0029, ADR-0031, [security/OPS_MCP_THREAT_MODEL.md](../security/OPS_MCP_THREAT_MODEL.md) (T-OPS-05, T-OPS-06, T-OPS-09), RISK_REGISTER R-22, R-23

## Context

Operations MCP approvals are the record that a human allowed a change. Two defects were found on review (2026-10-25):

- **R-22.** The approval was recorded as granted before its audit record was written. If the audit write failed, the approval existed with no record, so a human's decision could not be shown afterwards.
- **R-23.** Approvals were held in memory. A restart lost pending requests, and it also lost the fact that an approval had been used, which allowed a replay after restart.

## Decision

1. **Every state change is preceded by its audit record.** The order is: check (no change), audit record, journal entry, commit (in memory). If the audit record cannot be written, nothing changes and no action runs.
2. **Consumption is also audited before it happens.** An approval is used through an `approval_used` audit record, and only then marked used. The action follows. So at any point where an action has run, its authorisation is recorded.
3. **The approval state is persisted in an append-only journal.** The file is JSON Lines, one entry per change (request, approve, use). Each entry is fsynced. On start, the journal is replayed, and pending, approved and used states are restored.
4. **A journal write failure refuses the change.** It raises `store_unavailable`, and the state stays as it was.
5. **The journal is not a second audit log.** It holds approval state only. The audit log (ADR-0017) remains the record of evidence. The journal location is beside the audit log, on owner-controlled storage, outside the repository.
6. **Expiry and single use are checked again at commit,** so an approval that expires between check and commit is refused.
7. **No external database is introduced.** A file journal is enough for one owner. A database is considered only when more than one control node exists (ADR-0033 and the portability section of M2M).

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Check, audit, journal, commit, with replay (chosen) | No state without a record; survives restart; no new service | Replay time grows with the journal; the journal needs rotation later | 4.00 (estimate) |
| B: Keep approvals in memory and accept the loss | Simplest | A restart lets an approved action be re-run or lost silently; no evidence | Rejected |
| C: Store approvals in a database | Scales; queries | New service to run and secure before any need; adds a credential | Deferred until a second control node |
| D: Record the approval after the action, and roll it back on failure | Looks simple | Cannot roll back a physical action; a failed record leaves an action with no approval | Rejected |

Score for A is an estimate. Values: value 4, frequency 4, cost 4, risk 4, reversibility 4, learning 4. Weighted sum: 12 + 8 + 12 + 12 + 8 + 4 = 56, divided by 14 = 4.00. The score does not include journal rotation, which is not built yet; that is a follow-up, not a gain.

## Consequences

- Positive: a granted approval always has a record first. A restart cannot re-use an approval, and cannot forget a pending one.
- Negative: a failed audit or journal write makes the service refuse work. This is intended (fail closed).
- Negative: an action can still fail after its authorisation was recorded. The authorisation record shows the approval and the action result shows the failure. Recovery is manual.
- Follow-up: write journal rotation and a restore test (BACKUP_STRATEGY, B-08).
- Follow-up: the journal and the audit log need the same retention class.

## Security and compliance notes

- Data classes: approval records are Internal, with the requester's identifier. No credential is stored.
- Controls: fsync on every write; replay; single use; the check-then-commit double test; the journal outside the repository.
- Residual: a deleted journal removes pending approvals (they expire anyway) and loses the used flags. A deletion would be visible in the audit log, because each request and use has its own record. Threat T-OPS-06 covers this.
