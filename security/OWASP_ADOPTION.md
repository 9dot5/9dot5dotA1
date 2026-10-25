# OWASP Adoption

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

**Status:** Proposed · **Principle:** OWASP by Design (PRINCIPLES.md #11)

## Scope

| Reference | Applies to | Level |
|---|---|---|
| OWASP ASVS 4.0.3 | Web applications, portal, APIs | Level 2 for the portal; Level 1 for internal tools |
| OWASP Top 10 (current) | All web-facing components | Checked at design review |
| OWASP API Security Top 10 | Any API | Checked at design review |
| OWASP LLM Top 10 | AI components and agents | Checked at design review and in the threat model |
| OWASP Cheat Sheets | Developer guidance | Linked from SECURITY_BASELINE where relevant |

## How it is applied

1. **Design review:** the author completes the OWASP checklist in the ADR security section.
2. **Implementation:** ASVS controls are mapped to tests; a control without a test is recorded as a gap.
3. **Verification:** dependency and SAST scans run in the pipeline.
4. **Release:** open high-risk findings block release unless an exception is recorded.

## LLM-specific controls

- Treat all model and tool output as untrusted.
- Separate system instructions from retrieved content, and label retrieved content as data.
- Restrict tools by scope; require confirmation for destructive tools.
- Limit what retrieved documents can trigger.
- Log model inputs and tool calls, with redaction.
