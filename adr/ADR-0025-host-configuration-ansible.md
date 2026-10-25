# ADR-0025: Host configuration with Ansible, pull model

- **Status:** Proposed
- **Date:** 2026-10-25
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-25
- **Related:** ADR-0001, ADR-0006, ADR-0029, ADR-0031, ADR-0033, ADR-0034, ADR-0035, ADR-0036, ADR-0038, [architecture/DEPLOYMENT_STRATEGY.md](../architecture/DEPLOYMENT_STRATEGY.md), [BACKLOG.md](../BACKLOG.md) (B-32)

## Context

ADR-0001 rule 4 and DEPLOYMENT_STRATEGY principle 1 require hosts to be configured declaratively from Git. Today the only host configuration is `scripts/setup-agent-runner.ps1`, which is imperative and has no recorded exception (B-32). The owner proposes Ansible for configuration (2026-10-25).

Facts:

- Ansible is licensed GPL-3.0, an OSI-approved licence (ADR-0006 rule 1).
- An Ansible control node runs on Linux or macOS, not natively on Windows. Windows hosts are managed over WinRM or SSH.
- ADR-0029 forbids agents, humans and workflows from opening SSH sessions to nodes for routine work. A push model, where one machine connects to each node to apply configuration, opens exactly such sessions.
- PC Alentejo is Windows and owned (ADR-0031, ownership class `owned`, 2026-10-25). Its workloads will run as Podman containers (ADR-0035).
- The repository `9dot5/9dot5dotA1` is public (R-29).

## Decision

1. **Ansible is the configuration tool** for owner-controlled hosts.
2. **Pull model only.** Each host applies its own configuration with `ansible-pull` from this repository, on a schedule and on demand. No host, agent or person pushes configuration to another host over SSH or WinRM.
3. **The control node runs in a container on the host it configures.** On a Windows host, `ansible-pull` runs inside a Podman container and manages the host's containers through the `containers.podman` collection and the Podman socket. Windows settings outside Podman are out of scope for the first version.
4. **Playbooks live in `ansible/`**, one role per service, with pinned collection versions in `ansible/requirements.yml`.
5. **No Internal data and no secrets in the repository.** The repository is public. Inventory files hold host names only, never addresses. Secrets come from a file outside the repository on the host, and later from the secret broker (ADR-0014). Ansible Vault files are not committed either: an encrypted secret in a public repository is still exposed to offline attack.
6. **Every change is checked before it is applied.** A pull request runs `ansible-lint` and `ansible-playbook --syntax-check`, and `--check --diff` against a test container where possible.
7. **Rollback is a revert.** Reverting the commit and running `ansible-pull` again restores the previous state. Roles are idempotent; a role that cannot be reverted says so in its README.
8. **Bootstrap is break-glass.** The first `ansible-pull` on a host is started by the owner on that host and recorded under ADR-0033. Later runs are scheduled.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Ansible, pull model, control node in a container on each host (chosen) | Declarative; no connection between hosts; fits ADR-0029; open source | Container on each host; Windows-level settings deferred | 3.71 (estimate) |
| B: Ansible, push model from Legion | Familiar; one control node | Opens SSH or WinRM to every node, violates ADR-0029; node credentials on a developer laptop | Rejected |
| C: PowerShell DSC | Native to Windows | Windows only; Linux hosts (Sigma user space, future nodes) need a second tool | Not scored |
| D: Imperative scripts (status quo) | Already written | Not declarative (ADR-0001 rule 4); drift is invisible | Rejected |

Score for A is an estimate. Values: value 4, frequency 4, cost 4, risk 3, reversibility 4, learning 3. Weighted sum: 12 + 8 + 12 + 9 + 8 + 3 = 52, divided by 14 = 3.71. The cost value assumes a small container per host; it is not measured.

## Consequences

- Positive: host state is reviewable in Git and reproducible.
- Positive: no host needs to accept inbound configuration connections.
- Negative: a failed `ansible-pull` on a host is seen only by that host's monitoring. Mitigation: each run reports its result as a health signal (ADR-0035).
- Negative: anyone who can merge to `main` changes every host, and agents may merge after the required checks (ADR-0036). Mitigation: the CI checks (`ansible-lint`, syntax check) run on every pull request; the owner makes them required on `main` (ADR-0038); each merge alerts the owner; the pull reads `main` only. Recorded as R-31.
- Follow-up: write the first role, for the monitoring stack (ADR-0035), and a test container for `--check` runs. The role is written (`ansible/roles/monitoring`, 2026-10-25); the test container is open.
- Follow-up: move `scripts/setup-agent-runner.ps1` into a role once Windows-level settings are in scope (B-32).

## Security and compliance notes

- Trust boundaries: TB-1 (repository to host). The repository becomes a configuration source for hosts, so a malicious merge reaches every host. Branch protection with required checks is a precondition (ADR-0036, ADR-0038).
- Data classes: Public in the repository. Internal and Secret data stay on the host.
- Threats: tampering with `main` (T-09). Supply chain of Ansible collections: versions are pinned and reviewed.
