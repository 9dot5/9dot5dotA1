# ADR-0038: Repository administration stays with the owner

- **Status:** Proposed
- **Date:** 2026-10-25
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-25
- **Related:** ADR-0010, ADR-0036, ADR-0037, [CLAUDE.md](../CLAUDE.md), [operations/GITHUB_APPS.md](../operations/GITHUB_APPS.md), [operations/AGENT_IDENTITIES.md](../operations/AGENT_IDENTITIES.md), [security/ACCESS_CONTROL.md](../security/ACCESS_CONTROL.md), [RISK_REGISTER.md](../RISK_REGISTER.md) (R-33)

## Context

ADR-0036 (Accepted) lets agents do everything on GitHub except delete a repository, including changing repository settings. The owner narrowed this on 2026-10-25: agents may merge, commit and manage the repository, but administration is the owner's.

Facts:

- On 2026-10-25, under ADR-0036, an agent session turned on branch protection for `main` (pull request required, 0 approvals, no force push, no deletion, enforced for administrators). That was an administration action.
- Agent sessions still reach GitHub through the owner's `gh` login. Its `repo` scope allows administration calls through `gh api`, so a permission rule in Claude Code can block the common commands but not every API call.
- GitHub Apps can be created without Administration write (GITHUB_APPS.md rule 1). An App token cannot change settings at all.

## Decision

1. **Agents manage the repository's content and work.** They may commit, push branches, open, review, merge and close pull requests, delete branches other than `main`, manage issues, labels, milestones and releases, edit workflow files under `.github/workflows/`, and run or re-run Actions workflows.
1a. **Agents may also archive, unarchive, rename and transfer a repository** (owner decision, 2026-10-25). A transfer goes only to the owner's own account or to an organisation the owner owns; a transfer anywhere else is not permitted, because it removes the owner's control and cannot be undone without the receiver.
2. **Other administration is owner-only.** Agents do not change: repository settings, visibility or description; branch protection and rulesets; collaborators, teams and permissions; Actions secrets and variables; webhooks, deploy keys and environments; GitHub App installations. Deletion stays forbidden (ADR-0036 decision 2).
3. **When an agent needs an administration change, it asks the owner** and gives the exact change and the command or setting. It does not make the change itself.
4. **Enforcement.** Claude Code denies `gh repo edit`, `gh repo delete`, `gh secret` and `gh variable`. Archive, rename and transfer are allowed by decision 1a; each is an audited tool call and the owner is alerted. GitHub Apps for agents have no Administration write. Until the Apps exist, sessions use the owner's login, so administration through `gh api` is blocked by rule only. Recorded as R-33.
5. **The branch protection set on 2026-10-25 stays as the owner's setting.** The owner may keep or change it.
6. **This supersedes ADR-0036 decisions 1 and 4 for administration.** The rest of ADR-0036 stands: agents push and merge after the required checks, and repository deletion is blocked.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Agents manage content and work; administration owner-only (chosen) | Agents finish work end to end; controls on the repository stay with the owner | Owner handles each settings change; rule-only enforcement until GitHub Apps exist | 3.86 (estimate) |
| B: ADR-0036 unchanged, agents administer too | No owner step for settings | An agent can remove branch protection or change visibility; not what the owner wants | Rejected by the owner |
| C: Agents propose only, owner merges | Strongest control | Undoes the owner's ADR-0036 decision | Rejected |

Score for A is an estimate. Values: value 4, frequency 4, cost 4, risk 4, reversibility 4, learning 2. Weighted sum: 12 + 8 + 12 + 12 + 8 + 2 = 54, divided by 14 = 3.86. Learning is low because the change narrows an existing permission.

## Consequences

- Positive: the controls that protect `main` cannot be changed by an agent through the normal commands.
- Negative: while agents use the owner's login, an agent can still reach administration endpoints through `gh api`. Mitigation: deny rules, audit records of every tool call, and GitHub Apps without Administration write as the next step.
- Follow-up: CLAUDE.md rule 3, GITHUB_APPS rule 1, AGENT_IDENTITIES rule 6 and ACCESS_CONTROL updated with this ADR. `.claude/settings.json` denies the administration commands.
- Follow-up: after acceptance, a link to this ADR is added to ADR-0036, as the status lifecycle allows for a superseded part.

## Security and compliance notes

- Trust boundaries: TB-1 (agent to repository). Narrows ADR-0036: agents change content, not the controls around it.
- Controls: deny rules; Apps without Administration write; owner review of every administration change.
- Threats: T-09 (tampering with `main` protection). Residual: R-33 until GitHub Apps replace the owner's login for agents, and R-34 for archive, rename and transfer.
