# Threat Model

**Status:** Proposed · **Method:** STRIDE per trust boundary, with AI-specific threats · **Reference:** OWASP Top 10, OWASP LLM Top 10, NIST SP 800-207

## Assets

| Asset | Classification | Why it matters |
|---|---|---|
| Canonical documents and decisions | Internal | Integrity of decisions |
| Credentials and tokens (human, agent, service) | Secret | Access to everything |
| Personal data in knowledge or logs | Personal (GDPR) | Legal obligations |
| Backups | Secret/Personal | Contains all of the above |
| Agent tool permissions | Internal | Ability to act |

## Trust boundaries

See architecture/CONTEXT.md §Trust boundaries. Threats below are mapped to those boundaries.

## Threats

| ID | Threat (STRIDE) | Boundary | Likelihood | Impact | Treatment | Control |
|---|---|---|---|---|---|---|
| T-01 | Credential committed to Git (Information disclosure) | Repository | M | H | Reduce | Secret scanning; pre-commit hook; SECRET_MANAGEMENT |
| T-02 | Stolen agent token used for unintended actions (Spoofing, Elevation) | Agent → platform | M | H | Reduce | Scoped, expiring tokens; audit log; ADR-0010 |
| T-03 | Prompt injection through documents or tool output causes unsafe action (Tampering) | Agent input | H | H | Reduce | Read-only defaults; human confirmation for writes; untrusted-output handling |
| T-04 | Exposed admin interface on the internet (Elevation) | Edge | M | H | Reduce | Zero trust (ADR-0004); no direct exposure of admin ports |
| T-05 | Unpatched dependency (Tampering, DoS) | Services | H | M | Reduce | Dependency scanning; update policy |
| T-06 | Backup theft or unrecoverable backup (Information disclosure, DoS) | Data | M | H | Reduce | Encryption; off-site copy; restore tests |
| T-07 | Lock-in or provider outage removes access (DoS) | External | M | M | Transfer/accept | Exit paths (ADR-0006); documented export |
| T-08 | Shared host exposes data to other users (Information disclosure) | Shared hosts | M | H | Avoid | Do not store personal or secret data on hosts not owned by the platform |
| T-09 | Agent-generated code with vulnerability merged (Tampering) | Delivery | M | H | Reduce | Security review trigger; SAST in pipeline; human approval |
| T-10 | Personal data in logs or telemetry (Information disclosure) | Observability | M | M | Reduce | Redaction tests (ADR-0009) |

## Review

Re-run the model when a component is added, when a trust boundary changes, and at each phase gate.
