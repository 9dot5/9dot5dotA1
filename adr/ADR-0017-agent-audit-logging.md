# ADR-0017: Agent identity, attribution and audit logging

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24
- **Related:** ADR-0003, ADR-0004, ADR-0009, ADR-0010, ADR-0011, [security/THREAT_MODEL.md](../security/THREAT_MODEL.md) (T-02, T-11, T-12), [operations/AGENT_IDENTITIES.md](../operations/AGENT_IDENTITIES.md)

## Context

The owner requires that agents have their own identity, that their actions cannot be denied
afterwards (non-repudiation), and that every action is recorded in the platform's monitoring.
ADR-0011 first accepted running agents under the owner's session. That does not meet the
requirement, so this ADR replaces that part of ADR-0011.

Facts:

- The Claude Code hook system can run a command before and after each tool call, with the
  tool name, its input, the session id and the working directory (verified on Claude Code 2.1.310
  with a live session, see Verification below).
- A hook runs with the same operating-system user as the session it observes. Anything the agent
  can write, it can change, unless the operating system separates the two.
- Git can sign commits with an SSH key (`gpg.format=ssh`, Git 2.35 on this machine).
- No monitoring backend is chosen. ADR-0009 fixes the signals (health, resources, backups) and
  requires open telemetry standards, but names no product.
- Hooks that fail to write a record must not allow the action.

## Decision

1. **Each agent has its own identity, on three layers.** An agent is one of five registered identities
   in `.claude/agent-identities.json`: `architect`, `governance-checker`, `security-reviewer`,
   `docs-maintainer`, `executor`. Each has:
   - a Git author name and a non-routable e-mail label, and its own SSH signing key;
   - its own GitHub App, with permissions for its role only ([operations/GITHUB_APPS.md](../operations/GITHUB_APPS.md));
   - an operating-system session that runs as the separate account `agent-runner`, never as the owner.
   A session without a registered, active identity does not start (`scripts/start-agent.ps1`).
2. **Commits are signed by the agent.** The session sets the agent's signing key for that session only.
   The public key is listed in `.claude/allowed_signers`, so `git log --show-signature` shows which agent
   signed each commit. GitHub Apps cannot own a signing key, so the commit proof is local and the API
   proof is the GitHub App's audit log. The owner's keys are never used by an agent.
2a. **Separate operating-system account.** All agent sessions run as `agent-runner`, a standard account.
   The owner's profile is not readable by it, the repository is writable only where agents need it, and
   the hook, the registry and the governance paths are write-denied to it (`scripts/setup-agent-runner.ps1`).
   This is the owner's decision (open question 2 answered 2026-10-24); it replaces option D's
   "Phase 08" timing for the account, while per-agent accounts or containers remain a Phase 08 item.
3. **Every tool call is recorded before and after it runs.** `.claude/hooks/agent_audit.py` writes
   one record per event: UTC time, agent identity, session id, tool name and tool-use id, the input
   (secrets redacted, file content replaced by its length), whether the result was an error, the
   operating-system user and the host.
4. **The log is tamper-evident.** Each record holds the hash of the previous record, so editing,
   inserting or removing a record breaks the chain. `agent_audit.py verify` checks it.
5. **Fail closed.** Without a registered `AGENT_ID`, or when a record cannot be written, the tool call
   is blocked (exit code 2). The agent cannot act without leaving a record.
6. **Records go to the monitoring backend before the action runs.** The hook appends each record to a
   local buffer outside the repository, then ships it to the destination in `audit-sink.json` (ADR-0018).
   If the destination does not accept the record, the action is blocked. The backend is append-only for
   the agent's token, so records shipped before a later local change cannot be altered there. The head
   hash is exported so the backend can detect truncation. Alerts follow MONITORING_STRATEGY.md: a broken
   chain, a missing identity, a failed shipment, or a blocked tool call.
7. **The agent cannot change its own controls.** Deny rules block edits to `.claude/**`, `scripts/**`
   and the audit directory, and to CODEOWNERS and LICENSE.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Per-agent Git identity and SSH signing, hook log with hash chain, export to monitoring (chosen) | Attributable commits; log with tamper evidence; no new service needed to start | Hook runs as the same OS user; the log is local until the shipper exists; a hook can be bypassed by a shell command the deny list does not cover | 3.93 (estimate) |
| B: Owner's identity for all agents (ADR-0011 first version) | Nothing to set up | Fails the owner's requirement; actions are not attributable | Rejected |
| C: Separate GitHub accounts and a monitoring agent only | Strong identity on GitHub | Without the local hook, tool calls are not logged | Partly; included in A |
| D: Separate OS account for all agent sessions (`agent-runner`) (chosen, owner decision) | Agent cannot read the owner's profile or write the governance paths; hook and config are write-denied to it | One shared account: keys of all agents are readable by any session; the owner logs in once to set it up | Adopted; scored with A |
| E: One account or container per agent | Keys and tokens isolated per agent | More setup; containers need capacity on the host | Not scored; Phase 08 |

Score for A is an estimate. Values: value 5, frequency 5, cost 3 (monitoring backend not yet chosen;
local storage), risk 3 (local hook and log under the same OS user; mitigated by export), reversibility 4,
learning 4. Weighted sum: 15 + 10 + 9 + 9 + 8 + 4 = 55, divided by 14 = 3.93.

## Consequences

- Positive: every agent action is attributable to an agent identity, and the commits are signed.
- Positive: the log can be checked for edits and gaps by anyone with the head hash.
- Positive: records reach the monitoring destination before the action runs. A destination outage blocks
  agents, which is the intended fail-closed behaviour.
- Negative: until the identities are active, the destination is configured, and Claude Code is installed
  for the agent account, no agent can start. This is intended.
- Negative: sessions share one operating-system account (`agent-runner`). Keys of different agents are
  readable from that account, so the attribution between agents on the same host rests on the monitoring
  record, not on key isolation. Mitigation: option E in Phase 08.
- Negative: the agent account can read its own monitoring token. It can add records but cannot read or
  delete them (ADR-0018).
- Negative: a subagent may not report its own name to the hook. `agent_type_reported` is stored as
  reported and is not used for attribution; attribution is the session's `AGENT_ID`.
- Follow-up: owner to choose the backend and accept the Dynatrace exception, or choose a self-hosted one (ADR-0018).
- Follow-up: write RB-agent-audit-ship.md (shipping, outage, token rotation, chain verification).
- Follow-up: export the head hash to the owner's archive on each review, so truncation is detectable.

## Verification

Tested on 2026-10-24 with Python 3.11 and Claude Code 2.1.310:

- Blocked: a `pre` call without `AGENT_ID`, and with an unregistered one (exit 2, tool not run).
- Recorded: a live session with `AGENT_ID=architect` produced one `tool_call_attempt` and one
  `tool_call_result`, and `verify` reported OK.
- Redacted: GitHub token, `--password=`, URL credentials and `Authorization` header were replaced by
  `<REDACTED>` in the stored input.
- Tamper detected: changing one field and deleting one record each made `verify` fail (exit 1).
- Concurrency: 15 parallel appends produced 15 records with a valid chain.
- Denied calls: a live session asked to run `git push origin main`, which the deny list blocks. The
  attempt was recorded as `tool_call_attempt` before the denial, and no result record was written because
  the tool never ran.
- Shipping: records reached a local mock destination in the three formats (generic JSON with bearer token,
  Elasticsearch/OpenSearch bulk with API key, Dynatrace ingest with Api-Token). A destination that is down,
  or not configured, blocked the action (exit 2). The Dynatrace and Elastic payloads are not yet checked
  against a real tenant or cluster.
- Workspace trust: Claude Code ignored the six `allow` entries of the project settings because the workspace
  was not yet trusted. The owner must accept the trust dialog once in an interactive session. The `deny`
  entries were not separately verified in untrusted mode; the owner should re-run the denied-call test after
  accepting trust.

## Security and compliance notes

- Data classes: the log holds agent actions on Internal material and may hold personal data in
  tool input. Retention: 12 months, which is stricter than the 90-day baseline because it is evidence
  of agent action. Access: owner only (ACCESS_CONTROL).
- Trust boundary: agent to platform (CONTEXT.md, boundary 4). The log is the record for T-02 and
  T-11.
- Redaction is pattern-based. It is not a guarantee. Secrets must not reach an agent in the first
  place (SECRET_MANAGEMENT rule 5).
- Logs are kept free of secrets and unredacted personal data (SECURITY_BASELINE, Logging).
