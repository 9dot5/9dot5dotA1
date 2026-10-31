# ADR-0042: Coexistence of agent tools, resource leases and the owner's work workstation

- **Status:** Proposed
- **Date:** 2026-10-31
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-30
- **Related:** ADR-0011, ADR-0017, ADR-0030, ADR-0033, ADR-0034, ADR-0037, ADR-0040, ADR-0041, [operations/AGENT_IDENTITIES.md](../operations/AGENT_IDENTITIES.md), [operations/HOST_INVENTORY.md](../operations/HOST_INVENTORY.md), [operations/BREAK_GLASS_REGISTER.md](../operations/BREAK_GLASS_REGISTER.md), [RISK_REGISTER.md](../RISK_REGISTER.md) (R-01, R-27, R-37, R-38)

## Context

On 2026-10-31 the owner asked for an orchestrator under which Claude Code, Devin and other agent systems can work side by side ("quero ter o orquestrador para tu e ele poderem coexistir, ou outros sistemas"). The owner also stated that one machine is the owner's employer-issued work computer, that the owner wants to keep using SSH from it, and that it must never be used as a lab resource.

Facts, from the sessions of 2026-10-30 and 2026-10-31:

- Three agent sessions acted on the same resources without knowing about each other: a Devin CLI session on Legion, a Claude Code session on Legion, and a Claude Code session on PC Alentejo. Two of them changed the k3s namespace `monitoring` on `host-ops-01` within the same hour. Two of them opened pull requests that edit HOST_INVENTORY and BREAK_GLASS_REGISTER (#9 and this one).
- Both sessions on Legion used the owner's keys (`rsilv@Legion-9dot5`, and the `homelab` key for `ext-sigma-01`). On the target hosts their actions cannot be told apart from each other or from the owner. None had an `AGENT_ID` (R-01).
- ADR-0011 records Devin as "not in use". ADR-0034 and AGENT_IDENTITIES define identities for Claude Code sessions only.
- The Devin session installed a Prometheus and a Grafana in user space on `ext-sigma-01` (loopback only, started by `crontab`), and a pod on `host-ops-01` that holds a private key for the owner's university account to forward metrics to it. ADR-0030 rule 3 says every write on Sigma is manual and done by the owner.
- The tunnel key was authorised on Sigma without options, so it gave a full shell. On 2026-10-31 it was restricted to one local forward (`restrict`, `permitopen`, `command`), and the forward was checked working.
- The owner's work workstation has one key authorised on `ext-sigma-01`. The repository holds nothing about it.

## Decision

### Part A. Identities are per tool

1. **An identity names a role and a tool.** A registry entry in `.claude/agent-identities.json` gains a `tool` field (`claude-code`, `devin`, or another value the owner adds). The same role run by two tools is two identities, for example `executor-claude` and `executor-devin`. Each has its own Git author, signing key, SSH key per source host, GitHub App and `AGENT_ID`, as in ADR-0034 decision 1.
2. **Only the owner registers a tool.** A tool is registered when the owner adds its first identity and records how its sessions are started and audited. A tool whose sessions cannot be recorded under ADR-0017 stays at `max_state: pending`.
3. **The orchestrator (ADR-0034) may assign work to an identity of any registered tool**, under the same limits as ADR-0034 decision 3. Work passes through GitHub issues and pull requests, never through a session opened by one tool into another.
4. **No agent uses the owner's personal keys** once its own identity is active. Until then, an agent session that connects to a node or to `ext-sigma-01` does so on the owner's explicit instruction and is entered in BREAK_GLASS_REGISTER, whichever tool runs it.

### Part B. Leases on shared resources

5. **Before changing a shared resource, an agent takes a lease.** A lease is an open GitHub issue in this repository with the label `lease` and the resource ID in the title, for example `lease: host-ops-01/k3s/monitoring`. The body names the holder (identity, or tool and session if no identity exists yet), the purpose and an expiry, by default four hours. Closing the issue releases the lease.
6. **One open lease per resource.** An agent that finds an open, unexpired lease held by someone else does not change the resource. It reads, waits, or asks the owner. A lease past its expiry may be closed by the orchestrator or the owner with a comment.
7. **Resources that need a lease:** each node, each k3s namespace, the monitoring receiver on `ext-sigma-01`, and any shared course machine reached on the owner's behalf. Reads do not need a lease.
8. **Lease issues carry tasks only.** The repository is public: no addresses, account names, passwords or keys go in a lease (CLAUDE.md rule 5).

### Part C. Sigma and the work workstation

9. **The metrics receiver on `ext-sigma-01` is recorded as an exception to ADR-0030 rule 3**, pending the owner's decision. The owner either accepts it under this ADR (receive-only, loopback-only, a forward-only key from `host-ops-01`, no audit data), or removes it, and the metrics stay on `host-ops-01`. Until that decision, no agent changes it further.
10. **A new host class, *external workstation*.** A machine the owner uses but does not own. The owner's work computer is `ext-work-01`. It is recorded in HOST_INVENTORY without its host name, hardware or addresses, because those belong to the employer.
11. **`ext-work-01` is never a lab resource.** It holds no agent identity, signing key, repository write credential or secret of the lab. It has no role, is never a node, is not admitted under ADR-0031, and no agent or orchestrator connects to it or assigns work to it. The owner may use it as an SSH client, with its own key, to reach `ext-sigma-01`. Other outbound paths from it are added to HOST_INVENTORY by the owner, one at a time.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Identities per tool, leases as GitHub issues, external workstation class (chosen) | Several tools can work without overwriting each other; every action traceable to a tool; uses the channel ADR-0034 already chose; no new service | One more field in the registry; leases rely on agents checking first; lease issues add noise to the repository | 3.71 (estimate) |
| B: One tool only (status quo of ADR-0011) | Simplest; one identity model | Not what the owner wants; Devin is used anyway, without records | Rejected by the owner |
| C: Lease files on each host | Works without GitHub | Not visible across hosts; one more write path on nodes; no history | Rejected |
| D: A lock service (for example etcd or a small API) | Strong mutual exclusion | A new service to run, secure and monitor; overkill for one owner | Deferred |

Score for A is an estimate. Values: value 4, frequency 4, cost 4, risk 3, reversibility 4, learning 4. Weighted sum: 12 + 8 + 12 + 9 + 8 + 3 = 52, divided by 14 = 3.71.

## Consequences

- Positive: Claude Code, Devin and later tools can each be given work by the orchestrator, and a change on a host can be traced to the tool that made it.
- Positive: concurrent changes to the same namespace or host become visible before they happen, not after.
- Negative: a lease is advisory. An agent that skips the check still changes the resource. Mitigation: the check is part of each tool's instructions (CLAUDE.md, Devin rules); the audit chain shows changes made without a lease; R-37.
- Negative: amends ADR-0011 (Devin "not in use") and extends ADR-0034. ADR-0034 is Accepted, so this ADR adds to it and does not edit it. If accepted, ADR-0011 is revised to point here.
- Follow-up (owner): add the `tool` field, and Devin identities if wanted, to `.claude/agent-identities.json`. The file did not parse as JSON in a check on 2026-10-31; fix that first. Agents may not edit `.claude/**`.
- Follow-up (owner): create the `lease` label (agents may manage labels, so an agent may also do it).
- Follow-up (owner): decide decision 9: keep or remove the Sigma receiver. If kept, give the tunnel its own key per ADR-0041 decision 4 and record it in HOST_INVENTORY (done for the current key on 2026-10-31).
- Follow-up: add the lease check to CLAUDE.md and to the Devin rules file, once this ADR is accepted.

## Security and compliance notes

- Trust boundaries: TB-1 (agent to repository) gains lease issues. TB-8 gains the external workstation class, which crosses into nothing. The tunnel from `host-ops-01` to `ext-sigma-01` is outbound from the node and forward-only; it opens no path from Sigma to the node (ADR-0030 rule 4).
- Data classes: lease issues are Public. The work workstation's details are the employer's and are not recorded.
- Threats: an injected agent (T-03) takes a lease to block others. Mitigation: expiry and owner override. A node compromise uses the tunnel key against the owner's university account (R-38). Mitigation: the key is restricted to one loopback forward and cannot run commands.

## Change history

| Date | Change | By |
|---|---|---|
| 2026-10-31 | Proposed | Claude Code session on Legion (no `AGENT_ID`, R-01), on owner instruction |
