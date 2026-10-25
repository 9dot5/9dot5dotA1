# Monitoring Strategy

**Owner:** Rui Silva (`9dot5`)

**Review by:** 2027-01-25

**Status:** Proposed · **Related:** ADR-0009

## Signals (from Phase 03)

| Signal | Measured | Alert when | Owner | Runbook |
|---|---|---|---|---|
| Service health | Endpoint or process check | Down for 5 minutes | Operator | RB-<service>-health |
| Resource use | RAM, CPU, disk | Disk above 85%; RAM above 90% for 15 minutes | Operator | RB-host-resources |
| Backup status | Last successful backup age | Older than the RPO | Operator | RB-backup-restore |
| Certificate expiry | Days remaining | Under 21 days | Operator | RB-tls-renew |
| Agent audit chain | Verification result and head hash, per export | Chain broken, head missing for more than 24 hours, or export failed | Operator | RB-agent-audit-ship (to be written) |
| Agent identity use | Sessions started without an active identity; tool calls blocked by the audit hook | Any occurrence | Operator | RB-agent-audit-ship (to be written) |
| Agent actions on protected paths | Tool calls that touch CODEOWNERS, LICENSE, `.claude/**`, `scripts/**` | Any attempt, even if denied | Owner | RB-agent-audit-ship (to be written) |

The three agent signals come from the audit log described in [ADR-0017](../adr/ADR-0017-agent-audit-logging.md).
They are monitored from the moment the first agent identity is active.

## Rules

1. Every alert has an owner, a threshold, and a runbook. An alert without these is removed.
2. Alerts go to the owner's notification channel, not to a shared public channel.
3. Dashboards show the three signals per service before any other view.
4. Thresholds are reviewed after each incident.

## Measurement evidence

Capacity claims in the ROI matrix cite a measurement from this monitoring or from a documented
test. Estimates are labelled as estimates.
