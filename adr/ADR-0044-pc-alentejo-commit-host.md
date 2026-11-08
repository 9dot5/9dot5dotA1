# ADR-0044: PC Alentejo commits to this repository on the same terms as Legion

- **Status:** Proposed
- **Date:** 2026-11-08
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-02-08
- **Related:** ADR-0010, ADR-0011, ADR-0017, ADR-0034, ADR-0036, ADR-0039, ADR-0042, ADR-0043, [CLAUDE.md](../CLAUDE.md), [RISK_REGISTER.md](../RISK_REGISTER.md) (R-01, R-27), [roadmap/PHASE_08_AGENTS.md](../roadmap/PHASE_08_AGENTS.md)

## Context

On 2026-11-08 the owner asked that agent sessions on PC Alentejo (`host-ops-01`) can commit to this repository ("faz então este PC também dar para fazer commits"). The owner chose the interim option, the same practice Legion uses today, over first completing the per-agent identity setup.

Facts, checked on 2026-11-08:
- Every identity in `.claude/agent-identities.json` is `pending`, and the audit destination of ADR-0017 is not configured. `scripts/start-agent.ps1` therefore starts no session on any host.
- Sessions on Legion still commit and open pull requests:
  - commits authored "Devin", such as `d8862a6`;
  - commits authored by the owner from Claude Code sessions, such as `ee31225`.

  None has an `AGENT_ID`. This is R-01, recorded and open.
- On PC Alentejo, the clone of this repository is at `C:\Users\yau\9dot5dotA1`. Git is configured with the owner's author, and `gh` is authenticated as `9dot5`.
- The agent account `agent-runner` does not exist on this host, and there are no agent keys under `C:\ProgramData\9dot5dotA1`.
- ADR-0039 granted a one-off exception for 2026-10-25. Since then, sessions on this host have been told that the clone here is not used for commits.
- ADR-0034 Part B (Accepted) already allows this host to run agent sessions, through its own `agent-runner` account and its own keys, set up by the owner. The registry holds one signing key per identity, generated for Legion. Per-host keys need a registry change, which only the owner may make (CLAUDE.md, ADR-0017 rule 7).

## Decision

1. **Sessions on PC Alentejo may commit to this repository**, under the same rules as sessions on Legion today:
   - commits go on branches only, never on `main`;
   - changes reach `main` only through a pull request whose checks pass (CLAUDE.md rule 3, ADR-0036);
   - documents are created `Proposed`, and status changes follow ADR-0037.
2. **Commits from this host are identifiable.** Each commit message ends with trailers naming the tool and the host:

   ```
   Agent-Tool: claude-code
   Agent-Host: host-ops-01
   ```

   A Devin session uses `Agent-Tool: devin`. Until identities are active, the trailers are the only record of which tool and host made a commit authored by the owner.
3. **One host per branch.** A branch is worked on from one host at a time. Before changing a shared document that another open pull request also edits, a session takes a lease (ADR-0042 Part B).
4. **This is an interim regime.** It ends for an identity when that identity is `active` with a key for this host and the audit destination is configured (ADR-0017, ADR-0034 Part B). From then on, sessions here start through `scripts/start-agent.ps1`, as on Legion.
5. **No other access changes.** This ADR covers commits and pull requests to GitHub repositories only. It grants no new path between hosts (ADR-0034 decision 8, ADR-0041) and no access to nodes (ADR-0029).

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Same terms as Legion now, with tool and host trailers (chosen) | Works immediately; no new credential; the host is visible in history; ends automatically when identities are active | Commits remain under the owner's author (R-01); trailers are written by the session, not enforced | 3.50 (estimate) |
| B: Per-agent identities on this host first | Signed, attributable commits; closes R-01 for this host | Owner steps: `setup-agent-runner.ps1` elevated, per-host keys in the registry, audit destination. Nothing can start until all are done | Deferred; this ADR leads to it |
| C: Status quo, no commits from this host | No change | Work done here has to be carried to Legion by hand, which is slower and error-prone; rejected by the owner | Rejected |

Score for A is an estimate. Values: value 4, frequency 4, cost 5, risk 2, reversibility 4, learning 2. Weighted sum: 12 + 8 + 15 + 6 + 8 + 2 = 51, divided by 14 = 3.64, rounded down to 3.50 for the unmeasured risk.

## Consequences

- Positive: work prepared on PC Alentejo reaches the repository directly as a pull request. An example is the aigw ADR draft in `ai-gateway/docs/adr-draft-aigw.md`.
- Positive: history shows which host and tool produced each commit, even before identities exist.
- Negative: R-01 now covers two hosts. Mitigations:
  - the trailers;
  - branch-only commits;
  - review of every pull request by the owner or its checks;
  - the end condition in decision 4.
- Negative: a session can omit the trailers. Mitigation: a check on pull requests that flags commits without `Agent-Host` (follow-up).
- Follow-up (owner): to end the interim regime on this host:
  1. run `scripts/setup-agent-runner.ps1` elevated on PC Alentejo;
  2. extend `.claude/agent-identities.json` to hold one key per host (agents may not edit `.claude/**`);
  3. configure the audit destination (ADR-0018).
- Follow-up: add the trailer convention to CLAUDE.md "Identity and audit" once this ADR is accepted.
- Follow-up: a pull-request check for the trailers.

## Security and compliance notes

- Trust boundaries:
  - TB-1 (agent to repository) gains a second host, using the same GitHub credential as the owner's sessions on Legion.
  - TB-4 (node to node) is unchanged.
- Data classes: commits and pull requests in this public repository stay Public. Trailers name the host ID only (`host-ops-01`), never a host name or address (CLAUDE.md rule 5).
- Threats:
  - T-03, a prompt injection that pushes a malicious change. Mitigations:
    - branch-only commits;
    - required checks and the owner's merge;
    - CODEOWNERS on protected paths.
  - R-27 (routine work through an unregistered path) does not apply: commits use GitHub, the channel ADR-0034 chose, not a session into another host.
