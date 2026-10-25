# ADR-0036: Agent authority on GitHub

- **Status:** Accepted
- **Superseded in part by:** [ADR-0038](ADR-0038-repository-administration-owner-only.md) (decisions 1 and 4, repository administration)
- **Date:** 2026-10-25
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-25
- **Related:** ADR-0010, ADR-0011, ADR-0017, ADR-0025, ADR-0034, [CLAUDE.md](../CLAUDE.md), [CONTRIBUTING.md](../CONTRIBUTING.md), [operations/AGENT_IDENTITIES.md](../operations/AGENT_IDENTITIES.md), [operations/GITHUB_APPS.md](../operations/GITHUB_APPS.md), [security/ACCESS_CONTROL.md](../security/ACCESS_CONTROL.md), [RISK_REGISTER.md](../RISK_REGISTER.md) (R-02, R-18, R-31)

## Context

The owner wants agents to be able to do everything on GitHub except delete repositories (owner statement, 2026-10-25).

Facts:

- ADR-0010 decision 2 requires a named human to approve every merge to `main`. CLAUDE.md rule 3, CONTRIBUTING sole-owner mode, AGENT_IDENTITIES rule 6 and ACCESS_CONTROL forbid agents to push or merge.
- Until the GitHub Apps of AGENT_IDENTITIES step 3 exist, agent sessions reach GitHub through the owner's `gh` login. GitHub then records agent actions as the owner's (R-01).
- The owner's current `gh` token has the scopes `repo`, `read:org`, `gist` and `admin:public_key`. It does not have `delete_repo`, so it cannot delete a repository.
- ADR-0025 makes `main` the configuration source for owner hosts, so a merge to `main` reaches PC Alentejo through `ansible-pull`.

## Decision

1. **Agents may perform every GitHub action except deleting a repository.** This includes pushing, opening, reviewing and merging pull requests, managing branches, issues, releases, labels, Actions workflows and repository settings, and changing repository visibility.
2. **Repository deletion is blocked on two layers.** No token or GitHub App given to an agent has the `delete_repo` scope or the Administration permission needed to delete. The Claude Code permissions deny `gh repo delete`.
3. **Merges to `main` still need passing checks.** Branch protection on `main` stays on, with required status checks. An agent may merge its own pull request once the checks pass. This revises ADR-0010 decision 2 for GitHub: the owner's prior approval is no longer required for each merge.
4. **Changes to branch protection, rulesets, Actions secrets, collaborators and repository visibility are recorded.** Each is an audited tool call (ADR-0017), and the owner is alerted on each one (MONITORING_STRATEGY).
5. **Unchanged:** agents do not accept risks and do not set an ADR status other than Proposed (CLAUDE.md rule 2, ADR-0010 decision 3). Those are decisions, not GitHub actions.
6. **Attribution moves to GitHub Apps when they exist.** Until then, agent actions on GitHub carry the owner's identity, and the audit log of the session is the only record of which agent acted.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Everything except repository deletion, with checks on `main` and alerts on settings changes (chosen) | Meets the owner's requirement; agents finish work end to end; deletion is blocked by token scope, not by convention | An agent can merge a defect or a wrong governance statement; a merge reaches the hosts through ansible-pull | 3.50 (estimate) |
| B: Owner-only merge (ADR-0010 as written) | Strongest control | Does not meet the owner's requirement | Rejected by the owner |
| C: Everything, including deletion | No exceptions | One injected or mistaken session can destroy the repository and its history | Rejected by the owner |

Score for A is an estimate. Values: value 5, frequency 5, cost 4, risk 2, reversibility 2, learning 2. Weighted sum: 15 + 10 + 12 + 6 + 4 + 2 = 49, divided by 14 = 3.50. Reversibility is 2 because a merge reaches the hosts through ansible-pull. The score sits exactly at the threshold; the owner should re-score after the first month.

## Consequences

- Positive: agents can open, check and merge their own work without waiting for the owner.
- Negative: prompt injection (T-03, R-06) or a wrong change can reach `main` and, through ansible-pull, every host. Mitigation: required checks on `main`; ansible-pull applies only after `ansible-lint` and `--check` pass; alerts on every merge; the owner can revert. Recorded as R-31.
- Negative: while agents use the owner's login, GitHub cannot tell owner and agent apart. Mitigation: GitHub Apps per agent (AGENT_IDENTITIES step 3) as the next step.
- Follow-up: update CLAUDE.md rule 3, CONTRIBUTING sole-owner mode, AGENT_IDENTITIES rule 6, ACCESS_CONTROL agent rows and `.claude/settings.json` to match (done with this ADR).
- Follow-up: GitHub App permissions in GITHUB_APPS.md: Contents, Pull requests, Issues, Actions, Workflows write; Administration read only. On GitHub, Administration write both changes settings and deletes the repository, and the two cannot be separated. Settings changes therefore go through the owner's `gh` login (no `delete_repo` scope), not through an App. Done with this ADR.

## Security and compliance notes

- Trust boundaries: TB-1 (agent to repository) widens from "propose" to "change and merge". TB-3 is reached indirectly, through ansible-pull.
- Controls: no `delete_repo` scope; deny rule for `gh repo delete`; required checks on `main`; alerts on merges and settings changes; audit records per tool call.
- Threats: T-03 (prompt injection), T-09 (tampering with `main`), T-12 (wrong governance statement merged). Residual risk is the owner's to accept when deciding this ADR.

## Change history

| Date | Change | By |
|---|---|---|
| 2026-10-25 | Accepted, with residual risks R-02, R-31 and the attribution gap (R-01) until GitHub Apps exist. ADR-0037 double check: automatic check passed, owner confirmed in the session ("sim aceito") | Owner decision, recorded by an unregistered Claude Code session (no `AGENT_ID`, see R-01) |
