# Priority Matrix

- **Owner:** Rui Silva (`9dot5`)
- **Status:** Proposed
- **Date:** 2026-10-25
- **Review by:** 2027-01-25
- **Related:** [BACKLOG.md](BACKLOG.md), [RISK_REGISTER.md](RISK_REGISTER.md), [TECHNICAL_DEBT_REGISTER.md](TECHNICAL_DEBT_REGISTER.md), [governance/ROI_MATRIX.md](governance/ROI_MATRIX.md)

## 1. Ranking rule

Items are ranked by four criteria, in this order:

1. **Security risk (S)**, 1 to 5. The worst credible outcome of leaving the gap open, with the likelihood it occurs.
2. **Business value (B)**, 1 to 5. What the owner gets from closing it: a gate passed, a decision made, a capability unlocked.
3. **ROI (R)**, 1 to 5, where 5 is best. Value delivered per unit of effort, the same idea as the ROI_MATRIX inverted cost.
4. **Complexity (C)**, 1 to 5, where 1 is simplest. Used last, so that of two equal items the simpler one comes first.

The sort is lexicographic: S descending, then B descending, then R descending, then C ascending. The backlog ID is the rank.

All scores are architect estimates. They are not measurements. Changing a score changes the order, so a score change is recorded in the change history of this file.

## 2. Quadrants

| Quadrant | Rule | Meaning |
|---|---|---|
| **Quick win** | S ≥ 4 and C ≤ 2 | Do first. Cheap and reduces a high risk |
| **Major project** | S ≥ 4 and C ≥ 3 | Plan it. Needs an ADR and sustained effort |
| **Hygiene** | S ≤ 3 and C ≤ 2 | Do in the normal flow of Phase 00 and 01 |
| **Plan** | S ≤ 3 and C ≥ 3 | Schedule against a phase gate |

## 3. Ranked matrix

| Rank | ID | Item | S | B | R | C | Quadrant | Phase |
|---|---|---|---|---|---|---|---|---|
| 1 | B-01 | Audit owner sessions (hook not active) | 5 | 5 | 5 | 1 | Quick win | 00 |
| 2 | B-02 | Owner account takeover controls | 5 | 5 | 5 | 1 | Quick win | 00 |
| 3 | B-03 | Enforce merge authority (ADR-0020) | 5 | 5 | 4 | 3 | Major project | 00 |
| 4 | B-04 | `.gitignore`, secret scanning, push protection | 5 | 4 | 5 | 1 | Quick win | 00 |
| 5 | B-05 | First restore test | 4 | 4 | 4 | 2 | Quick win | 00 |
| 6 | B-06 | Documentation pipeline (DevSecOps checks) | 4 | 4 | 4 | 2 | Quick win | 01 |
| 7 | B-07 | Extend deny rules, restrict subagent tools | 4 | 4 | 4 | 2 | Quick win | 00 |
| 8 | B-08 | Back up audit log and agent keys (ADR-0022) | 4 | 4 | 4 | 2 | Quick win | 00 |
| 9 | B-09 | Agent runtime hardening (ADR-0027) | 4 | 4 | 4 | 2 | Quick win | 00 |
| 10 | B-10 | Prompt-injection controls and evaluation set | 4 | 4 | 3 | 3 | Major project | 00 |
| 11 | B-11 | HTTPS-only audit sink | 4 | 3 | 5 | 1 | Quick win | 00 |
| 12 | B-12 | Verify disk encryption on key and log hosts | 4 | 3 | 5 | 1 | Quick win | 00 |
| 13 | B-13 | Threat-model additions (TM-01 to TM-05) | 4 | 3 | 5 | 1 | Quick win | 00 |
| 14 | B-14 | Security review of setup scripts | 4 | 3 | 4 | 2 | Quick win | 00 |
| 15 | B-15 | Runbook RB-agent-audit-ship | 4 | 3 | 4 | 2 | Quick win | 01 |
| 16 | B-16 | Formal acceptance of shared agent-account risk | 4 | 3 | 2 | 4 | Major project | 08 |
| 17 | B-17 | Remove password from setup transcript | 4 | 2 | 5 | 1 | Quick win | 00 |
| 18 | B-18 | Owner decision on ADR-0011 to ADR-0018 | 3 | 5 | 5 | 1 | Hygiene | 00 |
| 19 | B-19 | Data classification standard (ADR-0019) | 3 | 4 | 5 | 2 | Hygiene | 00 |
| 20 | B-20 | Commit governance baseline through PR | 3 | 4 | 4 | 1 | Hygiene | 00 |
| 21 | B-21 | Third-party and hosted-AI data handling (ADR-0021) | 3 | 4 | 4 | 2 | Hygiene | 00 |
| 22 | B-22 | Align approval rules across documents | 3 | 3 | 5 | 1 | Hygiene | 00 |
| 23 | B-23 | Add `SECURITY.md` | 3 | 3 | 5 | 1 | Hygiene | 00 |
| 24 | B-24 | Sole-owner break-glass and continuity record | 3 | 3 | 4 | 1 | Hygiene | 00 |
| 25 | B-25 | Incident contacts and restricted record store | 3 | 3 | 4 | 1 | Hygiene | 00 |
| 26 | B-26 | Alerting for post-hook failures | 3 | 3 | 4 | 2 | Hygiene | 00 |
| 27 | B-27 | Platform logging standard | 3 | 3 | 4 | 2 | Hygiene | 02 |
| 28 | B-28 | Vulnerability and dependency management | 3 | 3 | 4 | 2 | Hygiene | 02 |
| 29 | B-29 | Audit head-hash export and Dynatrace payload check | 3 | 3 | 4 | 2 | Hygiene | 00 |
| 30 | B-30 | GDPR record of processing and DPIA trigger (ADR-0026) | 3 | 3 | 3 | 2 | Hygiene | 00 |
| 31 | B-31 | Access model for portal and knowledge store | 3 | 3 | 3 | 3 | Plan | 03 |
| 32 | B-32 | Host configuration method (ADR-0025) | 3 | 3 | 3 | 3 | Plan | 00 |
| 33 | B-33 | Phase 00 gate: accept ADR-0001 to ADR-0010 | 2 | 5 | 5 | 1 | Hygiene | 00 |
| 34 | B-34 | Decide repository owner and organisation name | 2 | 4 | 5 | 1 | Hygiene | 00 |
| 35 | B-35 | Measure control-plane host capacity | 2 | 4 | 5 | 2 | Hygiene | 03 |
| 36 | B-36 | Confluence publication method (ADR-0023) | 2 | 4 | 4 | 2 | Hygiene | 01 |
| 37 | B-37 | Portal architecture and hosting (ADR-0024) | 2 | 4 | 3 | 4 | Plan | 03 |
| 38 | B-38 | Document headers to the CLAUDE.md standard | 2 | 3 | 5 | 1 | Hygiene | 00 |
| 39 | B-39 | PR, change, risk and incident templates | 2 | 3 | 5 | 1 | Hygiene | 00 |
| 40 | B-40 | Interface contract standard | 2 | 3 | 4 | 2 | Hygiene | 02 |
| 41 | B-41 | Trust-boundary diagram with threat IDs | 2 | 3 | 4 | 2 | Hygiene | 02 |
| 42 | B-42 | Asset and third-party inventory | 2 | 3 | 4 | 2 | Hygiene | 01 |
| 43 | B-43 | Environments and promotion (ADR) | 2 | 3 | 3 | 3 | Plan | 05 |
| 44 | B-44 | `python` available to the agent account | 2 | 2 | 4 | 1 | Hygiene | 00 |
| 45 | B-45 | Work-tracking model (ADR-0028) | 1 | 3 | 3 | 2 | Hygiene | 01 |
| 46 | B-46 | Terminology: Claude Code, Devin | 1 | 2 | 5 | 1 | Hygiene | 00 |

## 4. Act now

These items carry a current risk. Do them before anything else in the table, whatever their rank:

1. **B-17**: check for `%TEMP%\agent-runner-setup.log`, delete it, and reset the agent-account password.
2. **B-01**: accept the workspace trust dialog and run the denied-call test. Until this is done, no owner-session action is recorded.
3. **B-02**: confirm MFA on the GitHub owner account and store recovery codes offline.
4. **B-04**: add `.gitignore` and enable secret scanning before any further commit.
5. **B-11**: refuse non-HTTPS audit sinks before any real token is stored in the sink file.

## 5. Mapping to the first four weeks

Source: [roadmap/FIRST_4_WEEKS.md](roadmap/FIRST_4_WEEKS.md). Step numbers are from that file.

| Week | Items | Why here |
|---|---|---|
| 1 | B-17, B-01, B-02, B-04, B-11, B-12, B-34, B-20 | Act-now items, and FIRST_4_WEEKS steps 1 to 4 (owner, repository, scanning) |
| 2 | B-33, B-18, B-22, B-23, B-38, B-44, B-46 | Gate decisions (steps 5 and 6), and document fixes that depend on them |
| 3 | B-03, B-07, B-09, B-13, B-19, B-21, B-29, B-30 | FIRST_4_WEEKS step 9 to 11: threat model, baselines, missing ADRs |
| 4 | B-05, B-08, B-15, B-24, B-25, B-39, B-14 | Step 12: accept incident and DR procedures, first restore test |

Items B-06, B-10 and B-16 need an owner decision on the CI start and on the evaluation threshold. They are scheduled after week 4.

## 6. Change history

| Date | Change | By |
|---|---|---|
| 2026-10-25 | First version, from the gap analysis of the whole repository | Architect (draft for owner review) |
