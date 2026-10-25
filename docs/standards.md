# Standards

**Review by:** 2027-01-25

**Owner:** Rui Silva (`9dot5`)

**Status:** Proposed · Applies to every repository in the organisation.

## 1. Responsibilities

| Area | Owns | Reviews | Approves |
|---|---|---|---|
| Governance | Charter, principles, ROI matrix, decision framework | Owner | Owner |
| Security | Threat model, baseline, risk register, reviews | Security reviewer | Owner (risk acceptance) |
| Architecture | ADRs, architecture documents, target state | Architecture reviewer | Owner, or delegate in writing |
| Knowledge | Document standards, glossary, publication to Confluence | Maintainer | Maintainer |
| Operations | Service catalogue, runbooks, backups, incidents | Operator | Owner for production changes |
| AI | Agent permissions, MCP servers, evaluations | Owner | Owner (per ADR-0010) |

## 2. Architecture Review Process

Defined in [governance/ARCHITECTURE_GOVERNANCE.md](../governance/ARCHITECTURE_GOVERNANCE.md). Summary: ADR Proposed → reviewed within 5 working days (10 if a trust boundary changes) → Accepted, Rejected or Returned.

## 3. Security Review Process

1. Triggered by the review triggers in [governance/SECURITY_GOVERNANCE.md](../governance/SECURITY_GOVERNANCE.md).
2. The author adds a threat model entry (security/THREAT_MODEL.md) and the security checklist to the pull request.
3. A security reviewer checks authentication, authorisation, data handling, logging, and the applicable baseline controls.
4. Findings are fixed, or accepted by the owner with an expiry date. Findings are never silently closed.
5. The review result is recorded in the pull request before merge.

## 4. Change Management Process

| Change type | Examples | Approval | Lead time |
|---|---|---|---|
| Standard | Documentation fix, link repair, typo | One reviewer | Same day |
| Normal | New document, new automation, config change in staging | Reviewer plus owner for production | 2 working days |
| Significant | New component, new trust boundary, data-store change | ADR Accepted, security review, owner | Per ADR review |
| Emergency | Restoring service after an incident | Owner, after containment | Immediate; reviewed within 2 working days |

Each change records: the Jira key, the ADR (if any), the rollback step, and the test evidence.
Changes to production are made from Git, not by hand; a manual emergency change is written up within 2 working days and brought back into Git.

## 5. Definition of Done

A change is Done when every criterion for its type is met.

### Documentation
- Owner, status and review date set in the document header.
- Links resolve; terms follow the glossary.
- Reviewed by a second person (or the owner for single-author work).
- Linked to an ADR or Jira key where it records a decision.

### Infrastructure
- Defined declaratively in Git.
- Applied through the pipeline, not by hand.
- Capacity measured on its host, result recorded.
- Rollback step documented and, for production, tested once.
- Service entry in the service catalogue; monitoring and backup entries in place.
- Security baseline checks pass, or exceptions are recorded.

### Applications
- Tests cover the change, including denied-access cases where authentication applies.
- Dependency and static analysis pass with no open critical or high finding.
- No secrets in code, configuration or logs.
- OWASP ASVS controls mapped for the changed functions.
- Documentation of user-facing behaviour and of the API contract updated.
- Accessibility checked for user interfaces (WCAG 2.2 AA).

### AI components
- An ADR accepted for the component, with its ROI row.
- Data classes handled documented; hosted-API use recorded in ADR-0007 terms.
- Tool permissions scoped; destructive tools require confirmation.
- Prompt-injection tests pass against retrieved and tool-returned content.
- An evaluation set exists and the component passes it; results recorded.
- Monitoring of inputs and tool calls, with redaction, is in place.
- Owner approval recorded.
