# Agent Strategy

**Status:** Proposed · **Related:** ADR-0010, MCP_STRATEGY.md

## Roles

| Agent | Role | Allowed | Not allowed |
|---|---|---|---|
| Claude CLI | Architect, reviewer, documenter | Read the repository; draft ADRs and documents; comment on pull requests; run checks | Merge; change production; accept risk |
| Devin | Executor | Create branches; implement reversible changes; run tests; open pull requests | Merge; change production; modify CODEOWNERS or security controls without approval |
| Governance agent (phase 08) | Checker | Verify ADR metadata, links, status lifecycle; report | Edit decisions |
| Security agent (phase 08) | Scanner | Run scans; open findings | Accept risk; suppress findings |
| Documentation agent (phase 08) | Maintainer | Propose updates; fix broken links | Change status of a decision |

## Operating rules

1. Each agent has its own identity and token. Tokens are scoped to its role.
2. Every agent-authored change is labelled with the agent name and linked to a Jira task.
3. An agent reads the relevant ADRs and standards before acting, and cites them in its summary.
4. When uncertain about intent, the agent asks the human rather than choosing.
5. Agents must stop and report when a check fails; they do not weaken checks to pass them.

## Evaluation

Each agent's output is sampled monthly for accuracy, citations and policy compliance.
Results are recorded in operations/ and drive any change to its permissions.
