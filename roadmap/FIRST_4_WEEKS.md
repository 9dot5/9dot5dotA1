# First four weeks — execution order

**Owner:** Rui Silva (`9dot5`)

**Review by:** 2027-01-25

**Status:** Proposed. Each step names what must be done before the next begins.

## Week 1 — Foundations

1. **Name the owner** in PROJECT_CHARTER.md and CODEOWNERS. Nothing else is accepted until this is done.
2. **Choose the licence** and record the decision in ADR-0006.
3. **Create the GitHub organisation** `9dot5dotA1` and the repository. Enable branch protection on `main`: pull request, one approval, no force push.
4. **Enable secret scanning** and dependency scanning on the repository.
5. **Review ADR-0001 to ADR-0005** (rules, governance, security first, zero trust, documentation first). Accept or revise each.

## Week 2 — Governance decisions

6. **Review ADR-0006 to ADR-0010** (open source, AI strategy, knowledge, observability, human in the loop). Accept or revise. ADR-0007 may stay Proposed until Phase 04.
7. **Fill the ROI matrix** for the components already named: Git hosting, knowledge store, identity provider, local models, retrieval.
8. **Write the Definition of Done** (docs/standards.md) and adopt it for the next pull requests.

## Week 3 — Security and architecture

9. **Complete the threat model** for the components in TARGET_ARCHITECTURE.md. Each threat has a treatment.
10. **Accept SECURITY_BASELINE**, SECRET_MANAGEMENT and ACCESS_CONTROL. Replace the access-register placeholders.
11. **Write the missing ADRs** referenced in TARGET_ARCHITECTURE.md: identity provider, reverse proxy, secret manager, portal hosting, automation engine.

## Week 4 — Operations and knowledge

12. **Accept INCIDENT_RESPONSE and DISASTER_RECOVERY.** Set the first restore-test date.
13. **Create the Confluence space** and publish one governance document from Git, recording the publication method in an ADR.
14. **Create the Jira epic PLAT-GOV** with one Story per Phase 00 deliverable, each linked to its document.
15. **Close Phase 00** with the owner's gate sign-off in a pull request.

## Not in the first four weeks

Installing any service, host or container. Those start in Phase 03 or later, after the gates above.
