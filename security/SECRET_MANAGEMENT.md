# Secret Management

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

**Status:** Proposed · **Control:** A.5.17, A.8.24

## What counts as a secret

Passwords, API keys, tokens, private keys, session cookies, recovery codes, connection strings with credentials, and any value that grants access.

## Rules

1. Secrets are never committed to Git, including in history, examples or test fixtures. Use placeholders such as `<REDACTED>` or `example-value`.
2. Secrets are stored in a secret manager chosen under ADR (to be written). Until then, they are stored in an encrypted password manager owned by the human operator.
3. Services read secrets at runtime from the manager; secrets are not baked into images or configuration files.
4. Each secret has an owner, a purpose, a creation date and a rotation date.
5. Agents receive scoped, short-lived tokens; long-lived credentials are never passed to an agent.
6. A suspected exposure is treated as an incident (INCIDENT_RESPONSE.md): revoke first, investigate second.

## Prevention

- Pre-commit secret scanning on every developer machine.
- Secret scanning on the hosting platform, with alerts to the owner.
- Documents and logs are reviewed for secrets before publication.

## Rotation

| Secret type | Maximum age |
|---|---|
| Human passwords | Per the password manager policy; rotate on exposure |
| API tokens | 90 days |
| Agent tokens | 30 days, or per session where supported |
| Service credentials | 365 days, and on staff or host change |
