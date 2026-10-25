# Security Baseline

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

**Status:** Proposed · **Reference:** ISO/IEC 27001:2022 Annex A (controls cited as A.x), OWASP ASVS, CIS Controls v8

Every service and repository must meet this baseline. Exceptions follow SECURITY_GOVERNANCE.md.

## Identity and access

- MFA for every administrative account (A.5.17, A.8.5).
- Least privilege; roles documented in ACCESS_CONTROL.md (A.5.15, A.8.2).
- No shared accounts; service accounts have a named owner (A.5.16).
- Credentials rotated at least yearly, and immediately on suspected exposure.

## Secrets

- No secrets in Git, documents, logs or chat (A.8.24). See SECRET_MANAGEMENT.md.
- Secret scanning enabled on every repository.

## Software and configuration

- Dependencies pinned and scanned on each change (A.8.8, A.8.25 for secure development).
- Default credentials removed before a service starts.
- Services bind to the smallest interface they need.
- Automatic security updates enabled where the platform supports it.

## Logging and monitoring

- Authentication, authorisation and administrative actions are logged (A.8.15, A.8.16).
- Logs retained for at least 90 days, unless a stricter legal need applies.
- Logs do not contain secrets or unredacted personal data.

## Backup and recovery

- Each data set has a backup entry in BACKUP_STRATEGY.md (A.8.13).
- A restore test is recorded at least quarterly.

## Pipeline checks (DevSecOps)

| Check | When | Blocks merge when |
|---|---|---|
| Secret scan | Every push | Any finding |
| Dependency scan | Every pull request | Critical or high, without exception |
| Static analysis (SAST) | Every pull request | Critical or high, without exception |
| Markdown lint and link check | Every pull request | Broken link or invalid metadata |
| Infrastructure policy check | Every infrastructure change (Phase 05+) | Policy violation |

## Compliance mapping

Each control above is listed in the ISO/IEC 27001 Statement of Applicability when the
platform is formally assessed. Until then, this table is the working mapping.
