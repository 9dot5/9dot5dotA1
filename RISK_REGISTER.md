# Risk Register

- **Owner:** Rui Silva (`9dot5`)
- **Status:** Proposed
- **Date:** 2026-10-25
- **Review by:** 2027-01-25
- **Related:** [security/THREAT_MODEL.md](security/THREAT_MODEL.md), [governance/SECURITY_GOVERNANCE.md](governance/SECURITY_GOVERNANCE.md), [BACKLOG.md](BACKLOG.md), [TECHNICAL_DEBT_REGISTER.md](TECHNICAL_DEBT_REGISTER.md)

## 1. Scales

- **Likelihood (L)** and **Impact (I)**: 1 (low) to 5 (high). All values are architect estimates.
- **Score** = L × I.
- **Rating**: Critical 20 to 25; High 12 to 19; Medium 6 to 11; Low 1 to 5.
- **Treatment**: Avoid, Reduce, Transfer or Accept (SECURITY_GOVERNANCE).

**No risk in this register is accepted.** Agents may propose treatments. They never accept a risk on their own; they may record an acceptance only when the owner names it and confirms it in the session (ADR-0010 rule 3, ADR-0037, CLAUDE.md rule 2). Each "Accept" below is a proposal for the owner. An accepted risk expires after six months (SECURITY_GOVERNANCE).

## 2. Register

| ID | Risk | Cause and evidence | L | I | Score | Rating | Treatment | Control or backlog | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-01 | Owner-session actions are not recorded | `~/.9dot5dotA1/audit` absent. ADR-0017 Verification: workspace trust not accepted. Deny rules not verified | 5 | 5 | 25 | Critical | Reduce | B-01 | Open |
| R-02 | An agent merges a harmful change into `main` | Owner decision 2026-10-25 (ADR-0036): agents may merge after required checks. The risk is no longer an unauthorised merge but a harmful authorised one | 3 | 5 | 15 | High | Reduce | Required checks on `main`, alert on each merge, revert (ADR-0036). B-03 | Open, owner decision |
| R-03 | Owner GitHub account is taken over | Sole approver and key holder. No threat entry. Recovery path not recorded | 2 | 5 | 10 | Medium | Reduce | B-02, B-13 | Open |
| R-04 | A credential is committed to Git | `.gitignore` exists (secret patterns, `.env`, `*.pem`, `*.key`, `*.token`, audit sink files; checked 2026-10-25). No secret scanning, no push protection, no pre-commit scan | 3 | 5 | 15 | High | Reduce | B-04 | Open (`.gitignore` done; scanning missing) |
| R-05 | The agent-account password is exposed | `scripts/setup-agent-runner.ps1` starts a transcript in `%TEMP%` (line 44) and prints the new password with `Write-Host` (lines 82 and 91), so the password is written to the transcript. Checked 2026-10-25: the existing `agent-runner-setup.log` holds only the header, no password. The fix (pause the transcript while the password is shown, delete the transcript at the end) is applied to `scripts/setup-agent-runner.ps1` on 2026-10-25 under an owner-authorised exception to CLAUDE.md. It parses; it has not been run as administrator | 5 | 3 | 15 | High | Reduce | B-17 | Mitigated in code, pending a run and owner review |
| R-06 | Prompt injection makes an agent take an unsafe action (T-03) | Agents read web and document content. `WebFetch` and `WebSearch` not denied. No injection tests | 4 | 4 | 16 | High | Reduce | B-07, B-10 | Open |
| R-07 | Agent sink token is sent over plain HTTP | `agent_audit.py` accepts any URL scheme | 2 | 4 | 8 | Medium | Reduce | B-11 | Open |
| R-08 | Shell commands bypass the deny rules | ADR-0011 negative consequence: rules are advisory for shell arguments. `gh api` and `--no-verify` not denied | 3 | 4 | 12 | High | Reduce | B-07, B-09 | Open |
| R-09 | Audit log or agent keys are lost | Not in BACKUP_STRATEGY. Keys have no passphrase and no key-loss procedure | 2 | 4 | 8 | Medium | Reduce | B-08 | Open |
| R-10 | A backup cannot be restored when needed | No restore has ever been tested. DR objectives are proposals | 4 | 4 | 16 | High | Reduce | B-05 | Open |
| R-11 | All agent keys are readable by one account | ADR-0017 option D, accepted by the owner as a known limit, but no expiry recorded | 3 | 3 | 9 | Medium | Accept (proposed, expiry needed) | B-16 | Open, owner decision |
| R-12 | The audit sink is down and all agents stop | ADR-0018 is fail-closed. Dynatrace is a SaaS dependency. RB-agent-audit-ship missing | 3 | 3 | 9 | Medium | Reduce | B-15, B-29 | Open |
| R-13 | The sole owner is unavailable and work stops | One person holds all roles. No delegate, on-call or break-glass record | 3 | 4 | 12 | High | Reduce | B-24 | Open |
| R-14 | Governance documents contradict each other | Approval count (ACCESS_CONTROL vs CONTRIBUTING), retention (90 days vs 12 months), repository name, header gaps | 4 | 3 | 12 | High | Reduce | B-22, B-34, B-38 | Open |
| R-15 | Hosted AI or SaaS processes repository content without a recorded decision | ADR-0011 says content "may be processed by a hosted model". ADR-0007 rule 3 decision missing | 3 | 3 | 9 | Medium | Reduce | B-21 | Open |
| R-16 | Personal data is processed without a ROPA or DPIA | "Personal" class defined nowhere. Audit log holds tool inputs that may contain personal data | 2 | 4 | 8 | Medium | Reduce | B-30 | Open |
| R-17 | Adoption decisions rest on unmeasured estimates | ROI rows for proxy, secret manager, portal and identity are estimates. Two sit at exactly 3.50 | 3 | 3 | 9 | Medium | Reduce | B-35 | Open |
| R-18 | An agent merges a defect or a wrong governance statement | T-09 and T-12. No evaluation set. No pipeline checks yet | 3 | 3 | 9 | Medium | Reduce | B-06, B-10 | Open |
| R-19 | A lost or stolen device exposes keys and logs | Keys and audit log on local disk. Encryption status not recorded | 2 | 4 | 8 | Medium | Reduce | B-12, B-13 | Open |
| R-20 | Governance changes are not in version control | 10 modified and 13 untracked paths in `git status` | 4 | 2 | 8 | Medium | Reduce | B-20 | Open |
| R-21 | Agents act under a decision that is not binding | ADR-0011 is Proposed. ROI_MATRIX says "Adopted on Proposed ADR" | 4 | 3 | 12 | High | Reduce | B-18 | Open |
| R-22 | Approval is recorded before its audit write; a failed write leaves an approval with no record | `ops-mcp/ops_mcp/approval.py` and `gateway.approve()`, threat T-OPS-09 | 2 | 4 | 8 | Medium | Reduce | Fixed in code: audit before each state change (ADR-0032). Pending security review | Mitigated, pending review |
| R-23 | Approvals and the audit cursor are in memory; a restart loses pending approvals | `ops-mcp/ops_mcp/approval.py`, ops-mcp README known limits | 3 | 2 | 6 | Medium | Reduce | Fixed in code: journal with replay (ADR-0032). Pending security review | Mitigated, pending review |
| R-24 | Sigma (shared university host, now the monitoring centre) holds data about the owner's nodes | Owner decision 2026-10-25; T-08; M2M C-5 | 3 | 3 | 9 | Medium | Reduce | Health and metrics only (ADR-0030) | Open, owner decision |
| R-25 | Hops from Sigma to CSHP lab PCs widen the attack path to machines with no owner | Owner note 2026-10-25; TB-4 default deny; M2M C-6; ADR-0007 "not ours to load" | 3 | 4 | 12 | High | Avoid | No hop until ADR-0031 Part C names each host; gate closed | Open, owner decision |
| R-26 | Shared HMAC key for tokens during development | `ops-mcp/ops_mcp/identity.py`; threat T-OPS-02 | 2 | 4 | 8 | Medium | Reduce | Authentik before any real node | Open |
| R-27 | Routine work is done through an unregistered out-of-band path (plain SSH from a personal session, as on 2026-10-25) | Threat T-OPS-17; R-01; ADR-0033 | 4 | 4 | 16 | High | Reduce | Break-glass register and per-session record (ADR-0033) | Open, owner decision |
| R-28 | An orchestrator agent, steered by prompt injection, activates other agents | ADR-0034 lets the orchestrator activate registered identities. T-03 | 3 | 4 | 12 | High | Reduce | Separate OS account, owner ceiling per identity, alert on each activation (ADR-0034) | Open, owner decision |
| R-29 | Internal data is published in the public repository | `9dot5/9dot5dotA1` is public. Node addresses were in M2M_ARCHITECTURE and were removed before the first push (2026-10-25). Issues and pull requests are public too | 3 | 4 | 12 | High | Reduce | Make the repository private, or scan each change for Internal data before push (B-04) | Open, owner decision |
| R-30 | A Sigma user or a stolen Grafana Viewer credential reads the infrastructure metrics | ADR-0035 flow F-9 gives Sigma read access to a metrics-only Grafana on PC Alentejo. T-08 | 2 | 3 | 6 | Medium | Reduce | Metrics-only organisation, Viewer role, overlay only, no audit data (ADR-0035) | Open, owner decision |
| R-31 | A merge made by an agent reaches every host through ansible-pull | ADR-0036 lets agents merge; ADR-0025 makes `main` the host configuration source. T-03, T-09 | 3 | 4 | 12 | High | Reduce | ansible-pull applies only after `ansible-lint` and `--check` pass; alert on each merge; revert and re-run (ADR-0025, ADR-0036) | Open, owner decision |
| R-32 | An agent records an ADR acceptance the owner did not make | ADR-0037 lets agents write a status change on owner permission. Injected or misread permission (T-03, T-12) | 2 | 5 | 10 | Medium | Reduce | Named permission, automatic check, final owner confirmation, separate commit, alert (ADR-0037) | Open, owner decision |

## 3. Summary

| Rating | Count | Items |
|---|---|---|
| Critical | 1 | R-01 |
| High | 14 | R-02, R-04, R-05, R-06, R-08, R-10, R-13, R-14, R-21, R-25, R-27, R-28, R-29, R-31 |
| Medium | 17 | R-03, R-07, R-09, R-11, R-12, R-15, R-16, R-17, R-18, R-19, R-20, R-22, R-23, R-24, R-26, R-30, R-32 |
| Low | 0 | — |

Scores are estimates. The first-week items in [PRIORITY_MATRIX.md](PRIORITY_MATRIX.md) reduce R-01, R-04, R-05 and part of R-06. R-21 needs an owner decision, not more work.

## 4. Needs owner decision

- **R-11**: accept the shared agent-account risk with an expiry date, or fund per-agent accounts in Phase 08.
- **R-21**: accept, reject or revise ADR-0011 to ADR-0018. Until then, the agents' decisions are not binding.
- **R-12**: accept Dynatrace as a dependency for agent availability (ADR-0018 exception), or choose a self-hosted backend.

## 5. Change history

| Date | Change | By |
|---|---|---|
| 2026-10-25 | First version from the repository gap analysis | Architect (draft for owner review) |
| 2026-10-25 | R-04 and R-05 re-checked against the working tree. Line references corrected (the script has 162 lines). R-05 patch drafted outside the repository for owner review | Session draft, not a registered agent identity (see CLAUDE.md). Owner to review |
| 2026-10-25 | R-28 (orchestrator, ADR-0034) and R-29 (public repository) added | Session draft, not a registered agent identity. Owner to review |
| 2026-10-25 | R-30 (Sigma read access to Grafana, ADR-0035) added. R-12 now depends on PC Alentejo instead of Dynatrace if ADR-0035 is accepted | Session draft. Owner to review |
| 2026-10-25 | R-02 restated after ADR-0036 (agents may merge after checks). R-31 added | Session draft. Owner to review |
| 2026-10-25 | R-32 added (ADR-0037, agents record owner decisions). The note in section 1 that agents never accept a risk now reads with ADR-0037 | Session draft. Owner to review |
