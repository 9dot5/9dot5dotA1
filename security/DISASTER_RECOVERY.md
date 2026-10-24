# Disaster Recovery

**Status:** Proposed · **Control:** A.5.29, A.5.30, A.8.13, A.8.14

## Objectives

| Data or service | RTO (time to restore) | RPO (data loss accepted) |
|---|---|---|
| Git repositories | 1 day | 0 (remote is authoritative) |
| Knowledge and documents | 1 day | 24 hours |
| Management portal | 3 days | 24 hours |
| Identity provider (Phase 04+) | 4 hours | 1 hour |
| Secrets store | 4 hours | Last change |

These objectives are proposals until the first restore test is recorded.

## Scenarios

1. **Host failure.** Rebuild from declarative configuration in Git; restore data from backup.
2. **Ransomware or data corruption.** Restore from an offline or immutable backup copy; never from a copy that is continuously writable from the host.
3. **Loss of an account or identity provider.** Use the owner's offline recovery codes; document the procedure in a runbook.
4. **Loss of a provider.** Use the documented exit path (ADR-0006).
5. **Loss of the operator.** An access continuity note, kept in the password manager's recovery section, lists the owner's recovery path.

## Testing

- Restore test quarterly for one data set, rotating through all data sets each year.
- Results recorded with date, duration achieved against RTO, and data loss against RPO.
- A failed test opens an S3 incident.
