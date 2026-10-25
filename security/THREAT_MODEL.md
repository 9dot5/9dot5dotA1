# Threat Model

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

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
| T-11 | Agent acts with the owner's credentials, or its actions cannot be attributed or denied afterwards (Spoofing, Repudiation) | Agent → platform | M | H | Reduce | Registered identity per agent; signed commits; hash-chained audit log exported to monitoring; fail-closed hook (ADR-0017). Residual: hook and log share the owner's OS user until Phase 08 option D |
| T-12 | Agent edits an accepted decision, a protected file or a status field (Tampering) | Delivery | M | H | Reduce | CLAUDE.md rules; deny rules on CODEOWNERS and LICENSE; `governance-checker` review; owner approval (ADR-0010) |
| T-13 | Secret manager compromise exposes all runtime secrets (Information disclosure, Elevation) | Data | L | H | Reduce | Audit log; short-lived agent tokens; unseal keys stored apart from backups (ADR-0014) |
| T-14 | Reverse proxy misconfiguration exposes an admin interface (Elevation) | Edge | M | H | Reduce | No admin port on the public address; configuration in Git; review per service (ADR-0013) |
| T-15 | Identity provider outage or compromise blocks or grants access (Spoofing, DoS) | Edge | M | H | Reduce | MFA for administrators; offline recovery path; tested restore (ADR-0012) |
| T-16 | Automation script runs a consequential action without approval (Tampering) | Automation | M | H | Reduce | Classification read-only / reversible / consequential; approval record before run (ADR-0016, ADR-0010) |

## Review

Re-run the model when a component is added, when a trust boundary changes, and at each phase gate.
