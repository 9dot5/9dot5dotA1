# Incident Response

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

**Status:** Proposed · **Control:** A.5.24–A.5.28 · **Reference:** NIST SP 800-61r2

## Severity

| Level | Definition | Example | Response time |
|---|---|---|---|
| S1 | Confirmed exposure of secrets or personal data; loss of integrity of decisions | Credential in public repository | Start within 1 hour |
| S2 | Service compromise or outage with security impact | Unauthorised access to a service | Start within 4 hours |
| S3 | Control failure without confirmed impact | Backup job silently failing | Next working day |
| S4 | Near miss or suspicious event | Failed login attempts from unknown origin | Weekly review |

## Steps

1. **Detect and report.** Anyone, human or agent, reports to the owner immediately. Agents do not investigate beyond collecting logs.
2. **Contain.** Revoke the credential, isolate the service, or stop the agent. Containment comes before diagnosis.
3. **Assess.** Determine scope, data affected, and whether personal data is involved.
4. **Notify.** For personal data breaches, the GDPR requires notification to the supervisory authority within 72 hours where it is likely to result in a risk to individuals. Record the decision either way.
5. **Eradicate and recover.** Remove the cause; restore from a verified backup if needed.
6. **Review.** A blameless post-incident review within 10 working days. Output: actions with owners, and any ADR or baseline change.

## Records

Each incident has a record with timeline, decisions, evidence locations (not evidence contents), and closure date. Records are stored in the restricted section of the repository.

## Agent-caused incidents

An incident caused by an agent action is reviewed like any other. The agent's permissions are reviewed under AGENT_STRATEGY.md.
