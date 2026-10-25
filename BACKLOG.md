# Governance Gap Backlog

- **Owner:** Rui Silva (`9dot5`)
- **Status:** Proposed
- **Date:** 2026-10-25
- **Review by:** 2027-01-25
- **Related:** [PRIORITY_MATRIX.md](PRIORITY_MATRIX.md), [RISK_REGISTER.md](RISK_REGISTER.md), [TECHNICAL_DEBT_REGISTER.md](TECHNICAL_DEBT_REGISTER.md), [roadmap/FIRST_4_WEEKS.md](roadmap/FIRST_4_WEEKS.md)

## 1. Method

The whole repository was read on 2026-10-25: every Markdown file (69 outside `.claude/`), the subagent definitions, `.claude/settings.json`, `.claude/agent-identities.json`, `.claude/hooks/agent_audit.py` and both PowerShell scripts. Checks were run on the working tree:

- relative links: no broken link found;
- document headers: 17 non-ADR documents have no review date and 12 have no owner, which breaks the check in `CLAUDE.md`;
- hygiene: no `.gitignore`, no `.github/`, no `SECURITY.md`;
- runtime evidence: `~/.9dot5dotA1/audit` does not exist, so the audit hook has recorded nothing under the owner's profile.

Ranking and scores are defined in [PRIORITY_MATRIX.md](PRIORITY_MATRIX.md). Scores are architect estimates. Nothing here is accepted. Every item is a proposal for the owner to decide.

## 2. Gap summary by category

### 2.1 Missing ADRs

The next free number is ADR-0019. The numbers below are proposals.

| Proposed ADR | Gap it closes | Item |
|---|---|---|
| ADR-0019 Data classification and handling | Classes Internal, Personal, Secret and Restricted are used in ADRs and the threat model, but no standard defines them | B-19 |
| ADR-0020 Merge authority enforcement | "Owner-only merge" is a convention. Branch protection and app permissions do not yet prove it | B-03 |
| ADR-0021 Third-party services and hosted AI data handling | ADR-0007 rule 3 requires a recorded data-handling decision, which does not exist. ADR-0006 item 2 requires one ADR per proprietary service (GitHub, Atlassian, Dynatrace, Anthropic), and none exists | B-21 |
| ADR-0022 Backup platform and key custody | BACKUP_STRATEGY names no tool. The audit log and agent keys are not in any data set | B-08 |
| ADR-0023 Confluence publication method | Phase 01 deliverable, recorded as "to be written" | B-36 |
| ADR-0024 Portal architecture and hosting | Phase 03 exit criterion. ADR-0015 is provisional | B-37 |
| ADR-0025 Host configuration method | ADR-0001 rule 4 and DEPLOYMENT_STRATEGY principle 1 require declarative configuration. `scripts/setup-agent-runner.ps1` is imperative, with no recorded exception | B-32 |
| ADR-0026 Personal data governance (GDPR) | "Personal" is a data class with no record of processing and no DPIA trigger | B-30 |
| ADR-0027 Agent runtime hardening (amends ADR-0017) | ADR-0017 says "fail closed", but the post-hook cannot block. The HTTPS requirement is not enforced. The deny list is incomplete | B-09 |
| ADR-0028 Work tracking and traceability | README names Jira as the execution source. No ADR defines keys, workflow or linking rules | B-45 |

Also pending: owner decisions on ADR-0001 to ADR-0010 (B-33) and ADR-0011 to ADR-0018 (B-18). Agents already run under ADR-0011, which is still Proposed.

### 2.2 Missing security controls

- **Identity of the owner.** No threat-model entry for takeover of the owner's GitHub account. The owner is the only approver, and the recovery path is "to be recorded offline" (B-02, B-13).
- **Secret hygiene.** No `.gitignore`, no secret scanning, no push protection, no pre-commit scan (B-04). The setup script writes the agent password to a transcript (B-17).
- **Enforcement of agent limits.** The deny list does not cover `WebFetch`, `WebSearch`, `gh api` or `--no-verify`. The post-hook is not a gate (B-07, B-09, B-26).
- **Transport.** The audit sink accepts plain `http://` while sending a bearer token (B-11).
- **Disk protection.** Agent keys and the audit log sit on disk without a recorded encryption status (B-12).
- **Pipeline checks.** SECURITY_BASELINE lists secret, dependency and SAST checks on every change. No pipeline exists (B-06).
- **Disclosure route.** No `SECURITY.md`. CONTRIBUTING sends reporters to the internal incident procedure (B-23).
- **Prompt injection (T-03, High/High).** The control is listed as "Reduce", but no test or evaluation set exists (B-10).
- **Backups.** No backup of the audit log or agent keys (B-08). No restore test recorded (B-05).

### 2.3 Missing architecture decisions

- Data classification and handling rules (B-19).
- Access model: how the RBAC roles in ACCESS_CONTROL map to portal and knowledge permissions (B-31).
- Host configuration method (B-32).
- Interface contract standard. ADR-0001 rule 2 requires one, and no template exists (B-40).
- Environments and promotion. DEPLOYMENT_STRATEGY defers staging to Phase 05 (B-43).
- Logging standard covering all services, not only agents: fields, UTC, redaction, retention (B-27).
- Trust-boundary diagram with threat IDs. `diagrams/security/` has a README only (B-41).
- Capacity evidence for the control-plane host. Four ROI rows depend on it and all are estimates (B-35).
- Work tracking model (B-45).

### 2.4 Missing operational processes

- **Runbooks.** Only the template exists. At least six runbooks are referenced and missing: RB-agent-audit-ship, RB-proxy-restore, RB-tls-renew, RB-backup-restore, RB-host-resources and RB-`<service>`-health (B-15, B-42).
- **Restore testing.** No restore has ever been run (B-05).
- **Incident contacts.** No contact or escalation list. The "restricted section" of the repository that INCIDENT_RESPONSE names does not exist (B-25).
- **Continuity of the sole owner.** No break-glass path, no delegate, no on-call arrangement (B-24).
- **Asset and third-party inventory.** SERVICE_CATALOG is empty. External SaaS is not listed (B-42).
- **Vulnerability and dependency management.** No process behind the baseline (B-28).
- **Agent evaluation.** The DoD for AI components requires an evaluation set. None exists, and the monthly evaluation is Phase 08 only (B-10).
- **Audit export.** The head hash is not exported on a schedule. The Dynatrace payload is unchecked (B-29).
- **Templates.** Missing PR, change, risk and incident templates (B-39).

## 3. Ranked backlog

Order: Security Risk (S), then Business Value (B), then ROI (R), then Complexity (C, lower first). The ID is the rank. Scales and definitions are in [PRIORITY_MATRIX.md](PRIORITY_MATRIX.md).

| ID | Gap | Evidence | Action | Done when | Phase |
|---|---|---|---|---|---|
| B-01 | Owner sessions are not audited. S5 B5 R5 C1 | `~/.9dot5dotA1/audit` absent. ADR-0017 Verification: workspace trust not accepted, so project `allow`/`deny` rules were not verified | Accept the workspace trust dialog. Run the denied-call test (`git push origin main`) and record it. Document how the owner works in this repo without an agent identity (see TD-17) | `agent_audit.py verify` returns OK for an owner session. Denied test recorded in ADR-0017 | 00 |
| B-02 | Owner account takeover is not modelled or controlled. S5 B5 R5 C1 | ACCESS_CONTROL owner row: "recovery path to be recorded offline". THREAT_MODEL has no owner-account entry. Owner is the sole approver | Enable phishing-resistant MFA on the GitHub owner account. Store recovery codes offline. Add threat TM-01 (see B-13) | MFA status recorded (no codes in repo). Recovery steps in DISASTER_RECOVERY scenario 3 | 00 |
| B-03 | Merge authority is not enforced technically. S5 B5 R4 C3 | GITHUB_APPS: `architect`, `docs-maintainer`, `executor` have Contents write and Pull requests write. CONTRIBUTING: 0 required approvals. Whether branch protection stops an app-token merge is unverified | Write ADR-0020. Test with a throwaway branch: an app token must not merge into `main`. Reduce app permissions where possible | ADR-0020 Accepted. Test merge refused and recorded | 00 |
| B-04 | No secret protection in the repository. S5 B4 R5 C1 | No `.gitignore` at the root. No secret scanning (PHASE_02 unchecked). `.pem`, `.key`, `.env*` and `audit-sink*` are not excluded | Add `.gitignore` for `*.pem`, `*.key`, `.env*`, `*.token`, `audit-sink*`, `__pycache__`. Enable secret scanning and push protection. Install the pre-commit scan | A test push of a fake key pattern is blocked. `.gitignore` committed | 00 |
| B-05 | Backups have never been restored. S4 B4 R4 C2 | DISASTER_RECOVERY: first restore date "set in Week 4". CHARTER criterion 4. No restore record exists | Restore the repository and a copy of the audit log into a scratch folder. Record duration against RTO and loss against RPO | Restore record filed with date, RTO and RPO results | 00 |
| B-06 | No pipeline for the DevSecOps checks. S4 B4 R4 C2 | SECURITY_BASELINE "Pipeline checks" table. No `.github/`. CLAUDE.md checks are manual | Define the documentation pipeline: Markdown lint, link check, header check, secret scan. Build only after owner approval, since Phase 00 forbids infrastructure code | A PR with a broken link fails. A PR with a test secret pattern fails | 01 |
| B-07 | Enforcement by permission rules is incomplete. S4 B4 R4 C2 | `.claude/settings.json` deny list has no `WebFetch`, `WebSearch`, `gh api`, `git commit --no-verify`. ADR-0011 says "no web tools in the allow-list", which is not a deny | Add deny entries. Restrict subagent `tools` (architect and docs-maintainer have Bash). Record a denied-call test per entry | Each entry tested and recorded in ADR-0027 | 00 |
| B-08 | Audit log and agent keys have no backup or key-loss procedure. S4 B4 R4 C2 | BACKUP_STRATEGY lists no audit or key data set. Audit log path is under the owner profile. Keys are in `C:\ProgramData\9dot5dotA1\agent-keys` with no passphrase | Write ADR-0022 (platform, encryption, key custody). Add data sets. Write the key-loss procedure (rotation under AGENT_IDENTITIES rule 4) | BACKUP_STRATEGY updated. Test restore of keys into a scratch folder | 00 |
| B-09 | Agent runtime hardening is undecided. S4 B4 R4 C2 | ADR-0017 decision 5 says "fail closed". The post-hook cannot block. HTTPS is not enforced. See B-07, B-11, B-26 | Write ADR-0027 amending ADR-0017: post-hook as alert, HTTPS-only sink, deny-list additions, tool restrictions | ADR-0027 Accepted. Code changes tested | 00 |
| B-10 | Prompt-injection controls (T-03, High/High) are not tested. S4 B4 R3 C3 | THREAT_MODEL T-03 "Reduce". DoD for AI components requires injection tests and an evaluation set. None exist | Build an evaluation set: about 20 documents and tool outputs with injected instructions, plus denial-of-access cases. Score each subagent against it | Set in `governance/evals/` (new). Results recorded. Pass threshold agreed by the owner | 00 |
| B-11 | Audit sink accepts plain HTTP. S4 B3 R5 C1 | `agent_audit.py` `sink_settings()` does not check the URL scheme. `ship()` sends `Authorization: Bearer`/`ApiKey`/`Api-Token` | Refuse any URL that is not `https://`, except `localhost` in tests. Apply the same check in `start-agent.ps1` | Test with an `http://` URL is blocked (exit 2). Change recorded in ADR-0027 | 00 |
| B-12 | Disk encryption on hosts holding keys and logs is unverified. S4 B3 R5 C1 | Keys and audit log on local disk. No encryption statement in any document | Record BitLocker (or equivalent) status for each host in SERVICE_CATALOG hosts table | Status recorded for each host | 00 |
| B-13 | Threat model misses known threats. S4 B3 R5 C1 | THREAT_MODEL has 16 entries. Missing: owner-account takeover, supply chain (Claude Code, Python hook, PowerShell scripts), audit-sink outage, device loss, shell bypass of deny rules | Add TM-01 to TM-05 with treatments. Link to B-02, B-07, B-12, B-15 | Five entries added with likelihood, impact and control | 00 |
| B-14 | Privileged setup scripts have had no security review. S4 B3 R4 C2 | `setup-agent-runner.ps1` elevates, creates an account, grants traverse on the owner profile, writes deny ACLs, and prints a password | Owner-led review against SECURITY_BASELINE. Record findings and decisions in ADR-0025 | Review record filed. Findings fixed or accepted with expiry | 00 |
| B-15 | Runbook for audit shipping is missing. S4 B3 R4 C2 | MONITORING_STRATEGY rows point to "RB-agent-audit-ship (to be written)". ADR-0018: agents are blocked while the sink is down | Write RB-agent-audit-ship: outage, token rotation, chain verification, alert response. Then write the other missing runbooks (see TD-07) | Runbook tested once against the mock sink | 01 |
| B-16 | Shared agent account risk has no formal acceptance. S4 B3 R2 C4 | ADR-0017 negative consequence: all agent keys readable by one account. AGENT_IDENTITIES "Known limits" | Owner records the risk in RISK_REGISTER (R-11) with treatment and expiry. Plan per-agent accounts for Phase 08 | Owner decision recorded with expiry date | 08 |
| B-17 | Agent account password is written to a transcript. S4 B2 R5 C1 | `setup-agent-runner.ps1` line 587: `Start-Transcript` to `%TEMP%\agent-runner-setup.log`. Line 626: `Write-Host $plain` | Do now: check for `%TEMP%\agent-runner-setup.log` and delete it. Run `-ResetPassword`. Change the script so passwords are never written to output or transcripts | No file contains the password. New password in the owner's password manager | 00 |
| B-18 | Agents run under a Proposed ADR. S3 B5 R5 C1 | ADR-0011 is Proposed. ROI_MATRIX says "Adopted on Proposed ADR". DECISION_FRAMEWORK says Proposed is not binding | Owner accepts or revises ADR-0011 to ADR-0018. Agents stay blocked until then | Each ADR set to Accepted, Rejected or Returned by the owner | 00 |
| B-19 | No data classification standard. S3 B4 R5 C2 | Classes "Internal", "Secret", "Personal" and "Restricted" appear in THREAT_MODEL, ADR-0008, ADR-0011, ADR-0017 without a definition. "Restricted" has no folder | Write ADR-0019 and `security/DATA_CLASSIFICATION.md`: definitions, handling, labels, and retention per class (also resolves the 90-day vs 12-month conflict, TD-15) | ADR-0019 Accepted. Every class use matches the definition | 00 |
| B-20 | Governance changes are uncommitted. S3 B4 R4 C1 | `git status`: 10 modified tracked files, 13 untracked paths (`.claude/`, `CLAUDE.md`, ADR-0011 to ADR-0018, `operations/AGENT_IDENTITIES.md`, `operations/GITHUB_APPS.md`, `scripts/`) | Owner reviews the diff. Branch `docs/adr-0011-0018-agent-governance`, PR, owner merges. Agents do not commit unless asked (CLAUDE.md rule 3) | Commit merged after owner review | 00 |
| B-21 | No data-handling decision for hosted AI and SaaS. S3 B4 R4 C2 | ADR-0011 says repository content "may be processed by a hosted model". ADR-0007 rule 3 requires a recorded decision: none exists. No DPA check recorded for GitHub, Atlassian, Dynatrace or Anthropic | Write ADR-0021: data classes allowed per provider, DPA status, exit path (ADR-0006 item 2). Create `operations/THIRD_PARTY_REGISTER.md` | ADR-0021 Accepted. Register lists each provider | 00 |
| B-22 | Approval rules contradict each other. S3 B3 R5 C1 | ACCESS_CONTROL: "at least one approval". CONTRIBUTING and ADR-0010: 0 approvals in sole-owner mode. FIRST_4_WEEKS step 3: one approval | Align all four documents with ADR-0020 | No document disagrees on approval count (grep check) | 00 |
| B-23 | No `SECURITY.md`. S3 B3 R5 C1 | Repository root. CONTRIBUTING security section | Add `SECURITY.md` with a private reporting route and response times. Link from README and CONTRIBUTING | File present. Links resolve | 00 |
| B-24 | Sole-owner continuity is undefined. S3 B3 R4 C1 | ACCESS_CONTROL: "keep an offline recovery path". DISASTER_RECOVERY scenario 5 refers to a note that does not exist | Write a break-glass record: who can act if the owner is unavailable, where recovery material is held, and what they may do | Record filed; owner confirms it | 00 |
| B-25 | Incident contacts and the restricted record store are missing. S3 B3 R4 C1 | INCIDENT_RESPONSE: records "stored in the restricted section of the repository". The section does not exist | Create an incident record template and the restricted store (outside the public tree). Add a contact list with escalation order | Template and store exist. Contact list filed | 00 |
| B-26 | Post-hook failures do not stop anything. S3 B3 R4 C2 | `agent_audit.py post` returns exit 2 after the action has run. ADR-0017 says "fail closed" | Decide in ADR-0027: post failures raise an alert within the MONITORING_STRATEGY window. Add the alert rule | Alert rule exists and is tested with a sink outage | 00 |
| B-27 | No logging standard for the platform. S3 B3 R4 C2 | ADR-0009 rule 5 and SECURITY_BASELINE "Logging" are generic. ADR-0017 covers agents only | Write `security/LOGGING_STANDARD.md`: fields, UTC timestamps, redaction tests, retention per class | Standard Accepted. Redaction test defined | 02 |
| B-28 | No vulnerability or dependency management process. S3 B3 R4 C2 | SECURITY_BASELINE lists scans but no owner, cadence or SLA | Write `security/VULNERABILITY_MANAGEMENT.md`: scan sources, SLAs by severity, exception path | Document Accepted. First scan run | 02 |
| B-29 | Audit head hash is not exported on schedule. Dynatrace payload unchecked. S3 B3 R4 C2 | ADR-0017 follow-up; ADR-0018 "must be checked against the owner's tenant before go-live" | Add a scheduled head-hash export to the owner's archive. Check the Dynatrace payload against the tenant and amend ADR-0018 | Export job runs and is logged. Payload check recorded | 00 |
| B-30 | No GDPR record of processing or DPIA trigger. S3 B3 R3 C2 | "Personal" is a class, but there is no record of processing (ROPA) and no DPIA trigger in SECURITY_GOVERNANCE review triggers | Write ADR-0026: ROPA template, DPIA trigger, 72-hour notification route tied to INCIDENT_RESPONSE step 4 | ADR-0026 Accepted. ROPA contains the audit log and knowledge store | 00 |
| B-31 | No access model for the portal or knowledge store. S3 B3 R3 C3 | ACCESS_CONTROL roles are not mapped to services. ADR-0008 requires restricted documents to be excluded from agents | Write the access model: role to permission per service, classification to visibility, retrieval filter rule | Model Accepted before Phase 03 gate | 03 |
| B-32 | Host configuration method is not decided. S3 B3 R3 C3 | ADR-0001 rule 4 and DoD (Infrastructure) require declarative, pipeline-applied configuration. Setup scripts are imperative | Write ADR-0025: declarative target, or a recorded exception with expiry for the setup scripts | ADR-0025 Accepted. Exception has an expiry date | 00 |
| B-33 | Phase 00 gate: ADR-0001 to ADR-0010 not accepted. S2 B5 R5 C1 | Status Proposed for all ten. CHARTER criterion 1 targets end of week 2 | Owner accepts, revises or rejects each one (FIRST_4_WEEKS steps 5 and 6) | All ten have a recorded decision | 00 |
| B-34 | Repository name and owner are inconsistent. S2 B4 R5 C1 | GITHUB_APPS: repository `9dot5/9dot5dotA1`, but installs on the "9dot5dotA1" organisation, which does not exist yet. Memory note: org creation pending | Owner decides: organisation or personal account. Align README, CHARTER, GITHUB_APPS and CODEOWNERS | One name used everywhere. Grep check passes | 00 |
| B-35 | Capacity claims are estimates. S2 B4 R5 C2 | ROI rows for reverse proxy, secret manager, portal and identity are marked estimate. ADR-0014 and ADR-0015 sit at exactly 3.50 | Measure RAM, CPU, disk and power on the control-plane candidate host. Replace the estimates | Measurements recorded. ROI rows updated | 03 |
| B-36 | Confluence publication is undecided. S2 B4 R4 C2 | PHASE_01 deliverable: "to be written". FIRST_4_WEEKS step 13 | Write ADR-0023: method (manual copy, script, or connector), owner, frequency | ADR-0023 Accepted. One page published and linked | 01 |
| B-37 | Portal architecture and hosting are undecided. S2 B4 R3 C4 | PHASE_03 exit: ADR accepted naming the hosting location. ADR-0015 provisional on an unmeasured host | Write ADR-0024 after B-35 | ADR-0024 Accepted | 03 |
| B-38 | Document headers do not meet the CLAUDE.md check. S2 B3 R5 C1 | Text search: 17 non-ADR documents have no review date. 12 have no owner. Examples: MISSION, ROI_MATRIX, DECISION_FRAMEWORK, PRINCIPLES, standards | Add Owner, Status and Review by to each header, using the ADR template style | Governance-checker passes on all documents | 00 |
| B-39 | Templates are missing. S2 B3 R5 C1 | CONTRIBUTING refers to a PR template that does not exist. No change, risk or incident templates | Create `.github/pull_request_template.md` (Phase 01), `docs/templates/` for change, risk and incident records | Templates exist and are linked from CONTRIBUTING | 00 |
| B-40 | No interface contract standard. S2 B3 R4 C2 | ADR-0001 rule 2 requires inputs, outputs, errors and authentication for each interface. No template | Write `architecture/INTERFACE_CONTRACT_TEMPLATE.md` | Template Accepted and used by the first MCP server ADR | 02 |
| B-41 | Trust-boundary diagram is missing. S2 B3 R4 C2 | `diagrams/security/README.md`: "source files are added in Phase 02". No diagram exists | Draw the trust-boundary diagram in Mermaid, with threat IDs, legend and date | Diagram in `diagrams/security/`, matches CONTEXT.md boundaries 1 to 5 | 02 |
| B-42 | Asset and third-party inventory is empty. S2 B3 R4 C2 | SERVICE_CATALOG table has no rows. External services (GitHub, Atlassian, Dynatrace, Anthropic) are not listed | List all services and external providers, with class and exit path | Inventory covers every provider in B-21 | 01 |
| B-43 | Environments and promotion are undefined. S2 B3 R3 C3 | DEPLOYMENT_STRATEGY: staging "to be defined in Phase 05" | Write the environment ADR: staging, production, promotion rules | ADR Accepted before Phase 05 | 05 |
| B-44 | Python must be on the agent account's PATH. S2 B2 R4 C1 | `.claude/settings.json` calls `python`. The agent account has its own profile and may not have Python | Check that `python` resolves for `agent-runner`, or use the full path in the hook command | Hook runs for the agent account and the record appears | 00 |
| B-45 | No work-tracking model. S1 B3 R3 C2 | README: Jira is the execution source. No ADR on keys, statuses or linking | Write ADR-0028: Jira project keys, Epic/Story/Task rules, PR linking | ADR-0028 Accepted | 01 |
| B-46 | Terminology drift. S1 B2 R5 C1 | "Claude CLI" and "Claude Code" are used for the same tool (ADR-0011, AGENT_STRATEGY, CONTEXT). Devin is referenced in ADR-0010 and ADR-0011 but not used. Glossary has neither term | Pick one term, fix the references, add to the glossary | Grep finds one term for the tool | 00 |

## 4. Notes

- Items B-02, B-04, B-11, B-12 and B-17 are not ranked first for lack of effort. They are quick and carry a current risk, so the owner should do them before the rest of the list.
- B-06 creates delivery configuration. Phase 00 forbids infrastructure code, so it starts only after the owner approves it.
- No item here changes any ADR status. Acceptance is for the owner.
