# Agent Strategy

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

**Status:** Proposed · **Related:** ADR-0010, ADR-0011, MCP_STRATEGY.md

The agent setup in this repository is defined in [ADR-0011](../adr/ADR-0011-agent-architecture.md),
with instructions in [CLAUDE.md](../CLAUDE.md), permissions in `.claude/settings.json`, and the
subagents in `.claude/agents/`. Devin is not used; Claude Code fills the executor role under the
same limits.

## Roles

| Agent | Role | Allowed | Not allowed |
|---|---|---|---|
| Claude Code, `architect` subagent | Architect, documenter | Read the repository; draft ADRs and documents as Proposed; run checks | Merge; change production; accept risk; set a status to Accepted |
| Claude Code, `governance-checker` and `security-reviewer` | Reviewer | Read the repository; report findings | Edit files; suppress or accept findings |
| Claude Code, `docs-maintainer` | Maintainer | Fix links, dates and terms | Change status of a decision |
| Claude Code, executor session | Executor | Create branches; implement reversible changes; run tests; open pull requests when asked | Merge; push to `main`; modify CODEOWNERS or LICENSE; change security controls without approval |
| Governance agent (phase 08) | Checker | Verify ADR metadata, links, status lifecycle; report | Edit decisions |
| Security agent (phase 08) | Scanner | Run scans; open findings | Accept risk; suppress findings |
| Documentation agent (phase 08) | Maintainer | Propose updates; fix broken links | Change status of a decision |

## Operating rules

1. Each agent has its own identity: a Git author, an SSH signing key and, for pull requests, its own
   GitHub account. Identities are registered in `.claude/agent-identities.json` (ADR-0017). An agent
   whose identity is not active does not start.
2. Every agent-authored commit is signed with the agent's key. Every tool call is recorded, before and
   after it runs, in the audit log that is exported to monitoring (ADR-0017). Records are not edited,
   and a broken chain is an alert. A linked Jira task is added when Jira is in use.
3. An agent reads the relevant ADRs and standards before acting, and cites them in its summary.
4. When uncertain about intent, the agent asks the human rather than choosing.
5. Agents must stop and report when a check fails; they do not weaken checks to pass them.

## Evaluation

Each agent's output is sampled monthly for accuracy, citations and policy compliance.
Results are recorded in operations/ and drive any change to its permissions.
