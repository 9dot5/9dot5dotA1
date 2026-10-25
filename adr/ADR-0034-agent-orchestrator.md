# ADR-0034: Orchestrator agent and a second agent host on PC Alentejo

- **Status:** Proposed
- **Date:** 2026-10-25
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-25
- **Related:** ADR-0004, ADR-0010, ADR-0011, ADR-0017, ADR-0018, ADR-0029, ADR-0031, ADR-0033, [operations/AGENT_IDENTITIES.md](../operations/AGENT_IDENTITIES.md), [roadmap/PHASE_08_AGENTS.md](../roadmap/PHASE_08_AGENTS.md), [RISK_REGISTER.md](../RISK_REGISTER.md) (R-11, R-28)

## Context

The owner wants agents that start, run and manage other agents, and wants one agent to run on PC Alentejo. Owner statement, 2026-10-25: "an agent can activate another agent as orchestrator."

Facts:

- ADR-0017 rule 7 and AGENT_IDENTITIES rule 7 deny agents any write to `.claude/**` and `scripts/**`. Activation (AGENT_IDENTITIES step 5) is an owner step: the owner sets `status` to `active` in `.claude/agent-identities.json`.
- All agent sessions share the operating-system account `agent-runner` (R-11). Anything one agent session can write, every other agent session can write too.
- No agent session can start today: every identity is `pending`, the audit sink is not configured, and the agent account has no Claude Code login.
- ADR-0029 forbids agents from opening SSH, API or console sessions to a node. ADR-0033 rule 6 forbids agents from using break-glass paths. TB-4 denies node-to-node traffic by default.
- PC Alentejo (`DESKTOP-Q3GOUP4`) is a candidate node under ADR-0031. Its ownership class is not recorded: the user account `yau` is not the owner's.
- The repository `9dot5/9dot5dotA1` exists on GitHub and is public.

Assumption: GitHub (issues, branches, pull requests) is reachable by outbound HTTPS from both hosts. Not verified on PC Alentejo.

## Decision

### Part A. The orchestrator identity

1. **A sixth registered identity, `orchestrator`.** It has its own Git author, signing key and GitHub App, like the other five, and its own audit records under `AGENT_ID=orchestrator`.
2. **The orchestrator is activated by the owner only.** No agent can activate the orchestrator, including itself. This is the single owner step that remains in the activation chain.
3. **The orchestrator may activate, suspend and start the other registered identities.** It changes their state from `pending` or `suspended` to `active`, or back, and starts their sessions with `scripts/start-agent.ps1`. It may not:
   - create a new identity, change an identity's role, key, Git author or GitHub App;
   - activate an identity that the owner has set to `revoked`;
   - grant merge rights, accept a risk, or change an ADR status (ADR-0010, CLAUDE.md rule 2);
   - edit `.claude/**`, `scripts/**`, the audit directory or its own permissions.
4. **Activation state lives outside the repository, in a file only the orchestrator can write.** `C:\ProgramData\9dot5dotA1\activations.json` holds one entry per identity: state, by whom, when, reason. The owner-controlled registry (`.claude/agent-identities.json`) keeps the identity definitions and a ceiling per identity (`max_state`: `active` or `pending`). `start-agent.ps1` starts a session only when both the registry ceiling and the activation file allow it.
5. **The orchestrator runs under its own operating-system account, `agent-orchestrator`.** Only that account and the owner can write `activations.json`. The `agent-runner` account can read it. Without this separation, any agent could activate any other (R-11), so this part is a precondition, not an option.
6. **Every activation, suspension and session start is an audited tool call** with the target identity and the reason. The owner is alerted on each activation (MONITORING_STRATEGY).

### Part B. An agent host on PC Alentejo

7. **PC Alentejo may run agent sessions as a second agent host.** It gets its own `agent-runner` account, its own signing keys (one per identity used there, not copies of the Legion keys), and its own Claude Code login, set up by the owner.
8. **No connection between hosts.** The orchestrator on Legion does not open SSH, remote desktop or any session to PC Alentejo (ADR-0029, ADR-0033 rule 6, TB-4). Work reaches PC Alentejo through GitHub only: the orchestrator opens an issue or a branch, the agent on PC Alentejo picks it up by outbound HTTPS and answers with a pull request.
9. **Audit records from PC Alentejo go to the same sink** (ADR-0018), with the host name in each record. A host whose records stop arriving is treated as down.
10. **Preconditions for Part B.** PC Alentejo is admitted under ADR-0031 Part A with its ownership class recorded by the owner. Its setup is done by the owner, and the setup session is recorded as break-glass under ADR-0033.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Owner activates the orchestrator; the orchestrator activates the others, under a separate account, with work passed to PC Alentejo through GitHub (chosen) | Meets the owner's requirement; one owner step; no node-to-node path; every activation audited | A second OS account; activation state outside the repository; slower hand-off to PC Alentejo | 3.57 (estimate) |
| B: Any agent may activate any other | Simplest | One compromised or injected session (T-03) activates every identity; no separation (R-11) | Rejected |
| C: Owner activates every identity (status quo) | Strongest control | Does not meet the owner's requirement | Rejected by the owner |
| D: Orchestrator on Legion drives PC Alentejo over SSH | Direct control of the remote agent | Violates ADR-0029, ADR-0033 and TB-4; keys for a node on an agent host | Rejected |

Score for A is an estimate. Values: value 4, frequency 4, cost 3, risk 3, reversibility 4, learning 4. Weighted sum: 12 + 8 + 9 + 9 + 8 + 4 = 50, divided by 14 = 3.57.

## Consequences

- Positive: agents can be started and managed without the owner editing the registry each time.
- Positive: PC Alentejo runs agents without any inbound connection or stored node credential.
- Negative: an orchestrator compromised by prompt injection (T-03) can activate the other registered identities. Mitigation: it cannot create identities or raise a ceiling; the owner is alerted on every activation; the owner can revoke the orchestrator in one step.
- Negative: the activation state is outside Git. Mitigation: every change is in the audit chain, which is the record of record (ADR-0017).
- Negative: amends ADR-0017 rule 7 and AGENT_IDENTITIES step 5 for the orchestrator only. Both are Proposed, so they are revised with this ADR rather than superseded.
- Follow-up: owner adds the `orchestrator` identity and the `max_state` ceilings to `.claude/agent-identities.json`.
- Follow-up: owner extends `scripts/setup-agent-runner.ps1` (account `agent-orchestrator`, permissions on `activations.json`) and `scripts/start-agent.ps1` (read the activation file). Agents may not edit `scripts/**`.
- Follow-up: owner records the ownership class of PC Alentejo (ADR-0031 Part A) before Part B starts.
- Follow-up: an activation alert in MONITORING_STRATEGY and a runbook RB-agent-activation.

## Security and compliance notes

- Trust boundaries: TB-1 (agent to repository), TB-4 (node to node, still denied), TB-8 (developer hosts). GitHub becomes the only channel between agent hosts.
- Data classes: the public repository holds no node address, account password or key (CLAUDE.md rule 5, ADR-0031 data class). Issues and pull requests used for hand-off to PC Alentejo are public too, so they carry tasks only, never Internal data.
- Controls: separate OS account for the orchestrator; registry ceiling owned by the owner; audited and alerted activations; no inbound path to either host.
- Threats: T-03 (prompt injection) leading to mass activation, added as R-28. Residual risk: the owner accepts or rejects it when deciding this ADR.
