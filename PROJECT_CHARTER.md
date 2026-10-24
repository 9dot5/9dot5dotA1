# Project Charter — 9dot5dotA1

**Status:** Proposed · **Owner:** Rui Silva (`9dot5`), sole owner · **Review cycle:** every 6 months

## 1. Purpose

Build a single operating platform where humans, AI agents, MCP servers and clients
work on the same knowledge, under explicit governance, with security designed in from
the start.

## 2. Problem statement

Personal and small-team infrastructure tends to grow by adding services without
documented decisions. The result is unmanaged credentials, undocumented dependencies
and no way to answer "why is it built this way". This project exists to prevent that
pattern, not to add services.

## 3. Scope

**In scope (first 12 months):**
- Governance, architecture and security documentation (Phase 00–02).
- Knowledge management and a management portal (Phase 01, 03).
- A self-hosted AI platform, if the ROI matrix approves it (Phase 04–05).
- Automation and observability for the platform itself (Phase 06–07).
- Agent-assisted operations under human approval (Phase 08).

**Out of scope:**
- Hosting third-party production workloads for other organisations.
- Building proprietary AI models.
- Any component that cannot be operated, backed up and removed by the owner.

## 4. Success criteria

| # | Criterion | Measure | Target date |
|---|---|---|---|
| 1 | Governance baseline accepted | ADR-0001 to ADR-0010 at status Accepted | End of week 2 |
| 2 | Every running service documented | Entries in `operations/SERVICE_CATALOG.md` = running services | Phase 03 |
| 3 | No plaintext secrets in any repository | Secret-scanning alerts = 0 open | Continuous |
| 4 | Backups restored successfully | One restore test per quarter, logged | Phase 05 |
| 5 | Each phase closes with a review | Phase document updated to Done | Each phase |

## 5. Constraints

- **Hardware:** no single host is assumed to be dedicated. Capacity decisions must
  cite measured resource use (see [ROI_MATRIX.md](governance/ROI_MATRIX.md)).
- **Budget:** prefer free and open-source tools; any paid service needs a recorded
  ROI justification.
- **Regulation:** GDPR applies to personal data; ISO/IEC 27001:2022 controls are the
  reference for the security baseline.

## 6. Stakeholders and roles

| Role | Holder | Responsibility |
|---|---|---|
| Sponsor and owner | Rui Silva (`9dot5`), sole owner of a single-member company (ENI) | Final decisions, risk acceptance, all roles until delegated in writing |
| Architecture | Rui Silva (`9dot5`) (delegable) | ADR approval, target architecture |
| Security | Rui Silva (`9dot5`) (delegable) | Threat model, security review |
| Operations | Rui Silva (`9dot5`) | Runbooks, backups, incidents |
| AI agents | Devin, Claude CLI | Execution and review under human approval |

## 7. Governing documents

[VISION](governance/VISION.md) · [MISSION](governance/MISSION.md) ·
[PRINCIPLES](governance/PRINCIPLES.md) · [ROI_MATRIX](governance/ROI_MATRIX.md) ·
[SECURITY_GOVERNANCE](governance/SECURITY_GOVERNANCE.md) ·
[ARCHITECTURE_GOVERNANCE](governance/ARCHITECTURE_GOVERNANCE.md) ·
[DECISION_FRAMEWORK](governance/DECISION_FRAMEWORK.md)

## 8. Approval

Accepting this charter requires the owner's sign-off recorded in the first commit that
changes its status to Accepted.
