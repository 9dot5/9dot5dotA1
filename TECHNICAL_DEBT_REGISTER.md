# Technical and Governance Debt Register

- **Owner:** Rui Silva (`9dot5`)
- **Status:** Proposed
- **Date:** 2026-10-25
- **Review by:** 2027-01-25
- **Related:** [BACKLOG.md](BACKLOG.md), [RISK_REGISTER.md](RISK_REGISTER.md), [architecture/TARGET_ARCHITECTURE.md](architecture/TARGET_ARCHITECTURE.md)

## 1. Rules

- Debt is a known deviation: a shortcut, an inconsistency, or a design limit that is not yet fixed.
- Every item has an owner, a removal condition and a target phase. Debt without a removal condition is not allowed (ARCHITECTURE_GOVERNANCE).
- Debt already listed in TARGET_ARCHITECTURE.md is cross-referenced, not duplicated.
- **Impact**: H (a control or decision is wrong), M (a control is weaker than stated), L (a document or naming problem).

## 2. Register

| ID | Debt | Where | Why it matters | Removal condition | Impact | Target | Linked |
|---|---|---|---|---|---|---|---|
| TD-01 | Agent identity list is kept in four places by hand | `agent-identities.json`, `allowed_signers`, `ALLOWED_AGENTS` in `agent_audit.py`, `ValidateSet` in `start-agent.ps1` | A new or revoked agent can be applied in one place and not the others | One registry read by the hook and the script; a check fails when they differ | M | 00 | ADR-0017 |
| TD-02 | Host configuration is imperative | `scripts/setup-agent-runner.ps1`, `scripts/start-agent.ps1` | ADR-0001 rule 4 and the DoD (Infrastructure) require declarative configuration. No recorded exception | ADR-0025 Accepted, and either the scripts are converted or the exception has an expiry | H | 00 | B-32, B-14 |
| TD-03 | All agents share one OS account | `agent-runner`, ADR-0017 option D | Keys of one agent are readable by another. Attribution rests on the log, not on key isolation | One account or container per agent (ADR-0017 option E) | H | 08 | R-11, B-16 |
| TD-04 | The audit writer runs under the same OS user as the agent it records | `agent_audit.py` runs as `agent-runner`. The local log is under that account's profile | The writer can alter its own log. TARGET_ARCHITECTURE already records this | Audit writer under its own account, or the log exported before the agent can write | H | 08 | TARGET_ARCHITECTURE deviation 4 |
| TD-05 | The sink token is readable by the agent account | `audit-sink.token`, ADR-0018 | A compromised agent can send false records. The backend is the only control | Token scoped to write-only, rotated (SECRET_MANAGEMENT agent token rule), backend append-only | M | 00 | ADR-0018 |
| TD-06 | Dynatrace payload unverified; exit path not built | ADR-0018 follow-ups | The stated audit trail may not be received. Lock-in has no working export | Payload checked against the tenant. Scheduled JSON Lines export with head hash exists | H | 00 | B-29 |
| TD-07 | Referenced runbooks do not exist | RB-agent-audit-ship, RB-proxy-restore, RB-tls-renew, RB-backup-restore, RB-host-resources, RB-`<service>`-health (MONITORING_STRATEGY, ADR-0013, ADR-0017) | Alerts have no response procedure. Every alert must link a runbook (MONITORING_STRATEGY rule 1) | Each file exists with a test date and result | H | 00–03 | B-15 |
| TD-08 | ROI thresholds are passed on estimates | ROI_MATRIX: proxy 3.71, secret manager 3.50, portal 3.50, identity 3.43, agents 3.57, all marked estimate | Adoption decisions rest on values nobody measured | Phase 04 measurements replace the estimates and the rows are re-scored | M | 03–04 | B-35, R-17 |
| TD-09 | ROI matrix says "Accepted by default" for undecided ADRs | ROI_MATRIX register: Git hosting (ADR-0006) and knowledge base (ADR-0008) are Proposed. Agents "Adopted on Proposed ADR" (ADR-0011) | The matrix reads as a decision record. DECISION_FRAMEWORK says only the owner decides | Column changed to "Proposed" until accepted, or the ADRs are accepted | M | 00 | B-18, R-21 |
| TD-10 | Terminology drift | "Claude CLI" in ADR-0011 context, AGENT_STRATEGY and CONTEXT. "Claude Code" elsewhere. "Devin" in ADR-0010 and ADR-0011, though not used. Neither tool is in the glossary | Documents describe different tools under one name | One term, glossary entries added | L | 00 | B-46 |
| TD-11 | Internal count mismatches | CONTRIBUTING workflow has two steps numbered 5. ADR-0011 says "four subagents"; the registry lists five identities including `executor` (not a subagent) | Reviewers cannot tell which list is authoritative | Numbering fixed. ADR-0011 wording aligned with ADR-0017 | L | 00 | — |
| TD-12 | Diagram folders are placeholders | `diagrams/architecture/`, `diagrams/security/`, `diagrams/operations/` have README files only. Only `diagrams/context/` has a source | DoD and diagrams/README require a source, legend and date for each diagram | Sources added in the phase named in each README | L | 02–03 | B-41 |
| TD-13 | Phase 00 checklist is out of step with ADR status | PHASE_00: ADR-0001 to ADR-0010 unchecked (still Proposed). CHARTER criterion 1 target: end of week 2 | The gate cannot close, and the status shown is wrong | Checklist updated when each ADR is decided | M | 00 | B-33 |
| TD-14 | Restore-test timing is inconsistent | CHARTER criterion 4: "Phase 05". DISASTER_RECOVERY and BACKUP_STRATEGY: quarterly from now | Two dates for the same control | One date in CHARTER and BACKUP_STRATEGY, with a reason | M | 00 | B-05 |
| TD-15 | Retention periods conflict | SECURITY_BASELINE, ADR-0012 and ADR-0014: 90 days. ADR-0017: 12 months for agent audit, "stricter" | No single retention schedule per data class | Retention table in ADR-0019 (classification) | M | 00 | B-19 |
| TD-16 | Repository name and owner are inconsistent | GITHUB_APPS: `9dot5/9dot5dotA1` and "install on 9dot5dotA1" (organisation not created) | App installation and CODEOWNERS may point to the wrong place | One name, documented | M | 00 | B-34 |
| TD-17 | No defined mode for the owner's own sessions | ADR-0017 and CLAUDE.md: the hook blocks any call without a registered `AGENT_ID`. Owner sessions in this repo have no documented path | Once the hook is active, the owner is blocked, or is tempted to route around it. Both are wrong | A documented owner mode that is still recorded, or a rule that the owner works through an agent identity | H | 00 | B-01 |
| TD-18 | Document headers do not meet the CLAUDE.md check | 17 non-ADR documents lack a review date. 12 lack an owner | The governance-checker fails on the repository today | Headers corrected (B-38) and the check passes | L | 00 | B-38 |
| TD-19 | ADR-0017 overstates "fail closed" | `agent_audit.py post` cannot stop an action that has already run | The control is described as stronger than it is | ADR-0027 states the post-hook as an alert, with a rule | M | 00 | B-09, B-26 |
| TD-20 | Permission patterns and tools are unverified on Windows | `Edit(~/.9dot5dotA1/**)`: tilde expansion unverified. Hook command uses `python` on PATH | A deny rule may not match, or the hook may not run for the agent account | Denied-call and hook tests for each pattern, recorded in ADR-0027 | M | 00 | B-07, B-44 |
| TD-21 | Governance work is not in version control | `git status`: 10 modified tracked paths and 13 untracked paths. One commit exists (`73e6b9e`) | Changes are not reviewed or recoverable through history | Reviewed PR merged by the owner (B-20) | M | 00 | R-20 |
| TD-22 | Local audit log keeps records of blocked actions | `append()` runs before `ship()`. If shipping fails, the record stays in the local log, and a retry writes another record | The local log is not the record of truth, and it can contain entries the backend never received | Documented as local buffer (ADR-0017 says so). Backend count compared with local count in the export check | L | 00 | B-29 |

## 3. Summary

| Impact | Count | Items |
|---|---|---|
| H | 6 | TD-02, TD-03, TD-04, TD-06, TD-07, TD-17 |
| M | 11 | TD-01, TD-05, TD-08, TD-09, TD-13, TD-14, TD-15, TD-16, TD-19, TD-20, TD-21 |
| L | 5 | TD-10, TD-11, TD-12, TD-18, TD-22 |

Total: 22 items.

## 4. Change history

| Date | Change | By |
|---|---|---|
| 2026-10-25 | First version from the repository gap analysis | Architect (draft for owner review) |
