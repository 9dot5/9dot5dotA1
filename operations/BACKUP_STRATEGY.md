# Backup Strategy

**Status:** Proposed · **Control:** A.8.13 · **Related:** security/DISASTER_RECOVERY.md

## Principles

1. **3-2-1:** three copies, two media types, one copy off-site.
2. **Immutable or offline copy** for at least one copy, to resist ransomware.
3. **Encrypted** at rest and in transit. Keys are stored separately from the backup.
4. **Tested.** A backup that has not been restored is not counted.

## Data sets

| Data set | Source | Frequency | Retention | Copies | Restore test |
|---|---|---|---|---|---|
| Git repositories | Hosting platform | Continuous (remote is authoritative) | Per hosting terms | Remote + local clone | Quarterly |
| Documents and exports | Knowledge store | Daily | 90 days daily, 12 months monthly | 3 | Quarterly |
| Secrets store | Secret manager | On every change, plus daily | 12 months | 2 (one offline) | Yearly |
| Identity provider configuration | Identity service | Daily | 12 months | 2 | Quarterly (Phase 04+) |
| Service data | Each service | Per service runbook | Per classification | 3 | Quarterly |

## Procedures

- Backup jobs report success or failure to the monitoring system (see MONITORING_STRATEGY).
- A failing job is an S3 incident if not fixed within one working day.
- Restore tests are recorded with date, data set, duration, and result.

## Exclusions

Backups are not stored on hosts that are not controlled by the platform owner (see THREAT_MODEL T-08).
