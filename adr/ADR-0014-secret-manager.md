# ADR-0014: Secret manager

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24
- **Related:** ADR-0003, ADR-0004, ADR-0006, ADR-0011, [security/SECRET_MANAGEMENT.md](../security/SECRET_MANAGEMENT.md), [security/THREAT_MODEL.md](../security/THREAT_MODEL.md) (T-01, T-02)

## Context

SECRET_MANAGEMENT.md rule 2 says secrets are stored in a secret manager "chosen under ADR (to be
written)" and, until then, in an encrypted password manager owned by the operator. Rule 5 says
agents receive scoped, short-lived tokens. Rule 1 forbids committing secrets, including encrypted
ones in Git.

Facts: no service needs runtime secrets yet. Assumption: the number of secrets stays below a few
hundred in the next year.

## Decision

We will use an open-source secret manager that serves secrets at runtime to services and agents,
with per-secret ownership, rotation dates and audit logs. The candidate is OpenBao, a
community-maintained fork of HashiCorp Vault under an OSI-approved licence. Until it is running,
the operator's password manager remains the store, as SECRET_MANAGEMENT.md already states.

Encrypted files in Git (for example SOPS) are not used, because SECRET_MANAGEMENT rule 1 forbids
secrets in Git in any form.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: OpenBao (candidate) | Open source (MPL-2.0); audit log; dynamic and short-lived credentials | Operating cost; an extra critical service | 3.50 (estimate) |
| B: Infisical | Friendly interface; open-source core (MIT) | Some features are under a commercial licence; check before adoption | Not scored; to evaluate |
| C: Password manager only (status quo) | No new component; already in use | No runtime delivery; no short-lived agent tokens; weak audit | 3.43 (estimate) |
| D: Encrypted secrets in Git (SOPS) | Versioned with the code | Breaks SECRET_MANAGEMENT rule 1 | Rejected |

Scores are estimates. OpenBao values: value 4, frequency 3, cost 3, risk 4, reversibility 3,
learning 4. The status quo values: value 2, frequency 5, cost 5, risk 2, reversibility 5, learning 1.

## Consequences

- Positive: agents receive scoped, short-lived tokens (SECRET_MANAGEMENT rule 5).
- Positive: each secret has an owner and a rotation date in the manager.
- Negative: the secret manager becomes a critical dependency. Mitigation: backup in two copies,
  one offline (BACKUP_STRATEGY), and a restore test before first use.
- Negative: the score is exactly at threshold. Mitigation: the Phase 04 evaluation re-scores it on
  measured capacity; if it falls below 3.5, the status quo continues and this ADR is rejected.
- Follow-up: record the chosen product and the unseal procedure in a runbook before any service
  reads from it.

## Security and compliance notes

- Trust boundary: services to data stores (CONTEXT.md, boundary 3); agents to platform (boundary 4).
- Data class: Secret. Backups of the manager are encrypted, and keys are stored apart from them.
- Controls: rotation per SECRET_MANAGEMENT table; audit log retained 90 days; no secret in logs
  (ADR-0009 rule 5).
