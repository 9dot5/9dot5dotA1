# Monitoring Strategy

**Status:** Proposed · **Related:** ADR-0009

## Signals (from Phase 03)

| Signal | Measured | Alert when | Owner | Runbook |
|---|---|---|---|---|
| Service health | Endpoint or process check | Down for 5 minutes | Operator | RB-<service>-health |
| Resource use | RAM, CPU, disk | Disk above 85%; RAM above 90% for 15 minutes | Operator | RB-host-resources |
| Backup status | Last successful backup age | Older than the RPO | Operator | RB-backup-restore |
| Certificate expiry | Days remaining | Under 21 days | Operator | RB-tls-renew |

## Rules

1. Every alert has an owner, a threshold, and a runbook. An alert without these is removed.
2. Alerts go to the owner's notification channel, not to a shared public channel.
3. Dashboards show the three signals per service before any other view.
4. Thresholds are reviewed after each incident.

## Measurement evidence

Capacity claims in the ROI matrix cite a measurement from this monitoring or from a documented
test. Estimates are labelled as estimates.
