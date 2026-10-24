# Security Governance

**Status:** Proposed · **Reference:** ISO/IEC 27001:2022 Annex A, OWASP ASVS 4.0.3, NIST SP 800-207 (Zero Trust)

## Accountability

| Role | Responsibility |
|---|---|
| Owner | Accepts residual risk; approves security exceptions; signs the security baseline |
| Security reviewer | Performs security review for changes listed in §Review triggers |
| Architect | Keeps the threat model aligned with the architecture |
| Operator | Applies baseline controls, rotates credentials, runs restore tests |
| Agents | Run automated checks; never accept a risk and never approve their own change |

## Review triggers

A change requires a security review when it:

- adds or changes an external interface, authentication flow or authorisation rule;
- stores or processes personal data or secrets;
- introduces a component with network access, or a new dependency with privileges;
- changes a control listed in [SECURITY_BASELINE.md](../security/SECURITY_BASELINE.md).

## Risk acceptance

Risks are recorded with: description, likelihood, impact, owner, treatment (avoid, reduce,
transfer, accept), expiry date. Accepted risks expire after 6 months and must be
re-approved. No risk may be accepted silently.

## Exceptions

An exception to the baseline is an ADR with status Accepted, a stated expiry, and a
compensating control. Expired exceptions are treated as violations.

## Metrics reviewed monthly

- Open critical and high findings from scanners.
- Secrets detected in commits (must be zero).
- Services without a current runbook.
- Overdue restore tests.
