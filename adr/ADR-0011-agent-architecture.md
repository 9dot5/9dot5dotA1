# ADR-0011: Agent architecture with Claude Code

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24
- **Related:** ADR-0002, ADR-0005, ADR-0007, ADR-0010, [architecture/AGENT_STRATEGY.md](../architecture/AGENT_STRATEGY.md), [security/ACCESS_CONTROL.md](../security/ACCESS_CONTROL.md), Phase 00, Phase 08

## Context

AGENT_STRATEGY.md assigns two AI roles for Phase 00 to 07: Claude CLI as architect, reviewer and
documenter, and Devin as executor. The owner now wants Claude to carry out the work of this
repository, so Devin is not in use. The repository needs an agent setup that:

- keeps the human approval of ADR-0010 for every merge and every consequential action;
- uses the role limits in AGENT_STRATEGY.md and ACCESS_CONTROL.md;
- can be run before the Phase 08 services (MCP servers, scheduled agents) exist.

Facts: the owner's GitHub CLI session is the account `9dot5`, and Claude Code runs under the
owner's local user. Assumption: the owner's Claude plan covers the expected usage (not measured).

Revision of 2026-10-24, on the owner's requirement: every agent has its own identity, its actions
cannot be denied afterwards, and all actions are recorded in monitoring. The first version of this
ADR let agents run under the owner's session; that is withdrawn. The identity and logging design is
in [ADR-0017](ADR-0017-agent-audit-logging.md).

## Decision

We will run agents as Claude Code sessions in this repository, with four layers:

1. **Instructions.** A root `CLAUDE.md` states the ground rules that every session reads
   (documentation first, human approval, no secrets, status lifecycle, language).
2. **Permissions.** A project `.claude/settings.json` allows read-only git and denies pushes,
   merges, history rewrites, edits to CODEOWNERS and LICENSE, and reads of `.env` files.
3. **Roles.** Four subagents in `.claude/agents/`, each with a fixed role and an explicit list
   of things it must not do:
   - `architect`: drafts ADRs, architecture documents and ROI rows. Creates Proposed decisions only.
   - `governance-checker`: read-only. Checks ADR metadata, status lifecycle, links and naming.
   - `security-reviewer`: read-only. Checks threat-model entries, secret patterns and baseline
     controls. Reports findings; never accepts risk or suppresses a finding.
   - `docs-maintainer`: fixes broken links, stale review dates and glossary terms. Does not change
     any decision status.
4. **Human gate.** The owner accepts ADRs, approves merges (ADR-0010, CONTRIBUTING.md sole-owner
   mode) and signs phase gates. Agents do not commit unless the owner asks.
5. **Identity and audit.** Each subagent role is a registered agent identity with its own Git
   author and SSH signing key (`.claude/agent-identities.json`). Sessions start through
   `scripts/start-agent.ps1`, which refuses an unregistered or pending identity. Every tool call is
   recorded in a hash-chained log that is exported to monitoring (ADR-0017).

Model choice: all subagents run on the Haiku model, the cheapest option, as the owner's default
for agents. A stronger model is used only when the owner asks for it in a given session.

Phase 08 will move the governance, security and documentation roles into scheduled or MCP-backed
agents with their own identities. Until then, these subagents are the agent roles.

### Roles after this ADR

| Role | Implemented by | Changes AGENT_STRATEGY.md |
|---|---|---|
| Architect, reviewer, documenter | Claude Code, `architect` and checker subagents | Claude CLI row kept |
| Executor | Claude Code session, under CLAUDE.md rules | Devin row replaced |

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Claude Code in-repo, four subagents, permission file (chosen) | No new service; roles visible in Git; reversible | Runs under the owner's credentials until Phase 08; cost of usage | 3.57 (see ROI_MATRIX) |
| B: Devin as executor, as first written | Dedicated identity; PR-based workflow | Another paid external service; not available in this session | Not scored; not in use |
| C: MCP servers from Phase 08 now | Scoped tokens from day one | Requires services and identities that Phase 00 forbids | Not scored; deferred |
| D: No agents, owner does everything | No new risk | Slower; the owner is the only reviewer | Not scored |

## Consequences

- Positive: agent roles and limits are visible in Git and reviewable like any other document.
- Positive: the deny rules block the actions ADR-0010 forbids, even when a prompt asks for them.
- Positive: each action is attributable to a registered agent identity and recorded (ADR-0017).
- Negative: no agent can start until the owner creates its identities and keys. This is intended
  by the owner's requirement. Steps are in operations/AGENT_IDENTITIES.md.
- Negative: the identity is enforced by the owner's OS user. A process of that user can change the
  hook or the log. Mitigation: deny rules, export of the head hash, and a separate OS user for agents
  in Phase 08 (ADR-0017, option D).
- Negative: prompt injection can reach the agent through documents or web content (T-03).
  Mitigation: read-only subagents for review, no web tools in the settings allow-list, and human
  approval for every write outside the working tree.
- Negative: permission rules are advisory for shell commands with arbitrary arguments. Mitigation:
  the deny list covers the commands that matter; the owner reviews every diff before merge.
- Follow-up: revise AGENT_STRATEGY.md and CONTEXT.md to match this decision (done with this ADR).
- Follow-up: create the GitHub accounts and signing keys (operations/AGENT_IDENTITIES.md), then set
  each identity to `active`.
- Follow-up: Phase 08 moves agents to a separate OS user and to scoped tokens (ADR-0017 option D).

## Security and compliance notes

- Data classes: repository content is Internal. No secrets and no personal data are stored in the
  repository, so the content may be processed by a hosted model under ADR-0007 rule 3. Restricted
  material must not be pasted into a session.
- Trust boundary: agent to repository (CONTEXT.md, boundary 4). Agents hold no administrative
  credential. The `gh` CLI session is the owner's and is not used for merges by the agents.
- Controls: deny rules in `.claude/settings.json`; CODEOWNERS on the governance paths; owner
  approval for every merge (ADR-0010 rule 2).
