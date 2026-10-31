# ADR-0043: A work queue for the agent dev loop, with client projects as separate repositories

- **Status:** Proposed
- **Date:** 2026-10-31
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-30
- **Related:** ADR-0010, ADR-0011, ADR-0016, ADR-0034, ADR-0036, [BACKLOG.md](../BACKLOG.md) (B-34, B-45), [security/THREAT_MODEL.md](../security/THREAT_MODEL.md) (T-03), [operations/HOST_INVENTORY.md](../operations/HOST_INVENTORY.md)

## Context

On 2026-10-31 the owner asked for the homelab to work on the project around the clock. The work would come from a queue that holds the dev loop of our application and requests for new client projects. Each client project is developed on its own line until it is merged into the ecosystem, and the design stays modular. The owner's choices in the session were:

- the repository is `agent-sandbox`;
- the queue is GitHub Issues with labels;
- merges are automatic into a client's integration branch;
- each client gets its own repository, created from a template.

Facts:

- `agent-sandbox` already holds the worker. `agent.yml` runs on the `homelab-arch` runners (k3s on `host-ops-01`), uses OpenCode with the local Ollama models, and opens a pull request. `code-review.yml` then reviews it with a hosted model. The worker is started only by hand (`workflow_dispatch`).
- `host-ops-01` does not sleep on AC power. Its WSL VM (k3s) and Ollama start only at user logon, from the Startup folder. After the reboot of 2026-10-31 (04:32) the homelab stayed down until 05:21.
- On a personal GitHub account, self-hosted runners are registered per repository. The `homelab-arch` scale set serves only `agent-sandbox`.
- The VRAM of `host-ops-01` (8 GB, stated in agent-sandbox, not measured) fits one large model at a time.
- Jira as the work-tracking source is undecided (B-45, ADR-0028 not written).

## Decision

1. **Queue.** A GitHub issue labelled `queue:ready` is a unit of work. Its state is a label: `queue:ready` → `queue:running` → `queue:review`, or `queue:failed` / `queue:needs-info`. Options are labels too: `agent:plan`, `prio:high` and `base:<branch>`. Only the owner creates queue items, because the repositories are private and issues are not open to the public. The queue source sits behind one contract (pick, mark, dispatch), so a Jira adapter can replace it once B-45 is decided.
2. **Dispatcher.** A scheduled workflow (`queue.yml`, every 10 minutes and on label) dispatches the next item to the worker. The order is `prio:high` first, then the oldest. Capacity is `QUEUE_MAX_RUNNING`, default 1, because of the single model in VRAM. Items stuck for more than 90 minutes without an active run are marked failed.
3. **Worker.** `agent.yml` works on a branch `agent/GH-<n>-…`, opens one pull request per item with `Closes #n`, and reports the outcome back on the issue. The worker never pushes to `main`.
4. **Automatic merge, bounded.** A pull request is merged without a person only when all of the following hold:
   - its head is `agent/*`;
   - its base is in `AUTO_MERGE_BASES` (default `integration client/*`);
   - the base is **not** `main` and not the default branch;
   - the review ends in `VEREDICTO: APROVADO`;
   - every other check passed;
   - the head is the reviewed commit.

   Every merge into `main` or the default branch stays with the owner (ADR-0010).
5. **Client projects.** Each client gets its own private repository, created from `agent-sandbox/templates/client`:
   - `agent/*` → `integration` is merged automatically (decision 4);
   - `integration` → `main` is merged by the owner only.

   Reusable code is written as modules with their own interface, inside `modules/<name>/`. A module enters the ecosystem only through a pull request that the owner merges. Client data, names and secrets never enter this public repository.
6. **Prerequisites for the first client** (owner):
   - a GitHub organisation (B-34), so that one runner scale set serves every client repository;
   - access for client repositories to the `agent-sandbox` workflows;
   - branch protection on each client `main`.
7. **Always on.** On `host-ops-01`, the WSL VM (k3s) and the Ollama server start at boot, without a logon, as scheduled tasks under the `yau` account in S4U mode, so no password is stored. The owner applies them. The script was prepared on 2026-10-31.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: GitHub Issues queue, bounded automatic merge into integration branches, one repository per client (chosen) | Runs unattended; works now with no new tool; per-client isolation of access and secrets; `main` stays human | Code reviewed only by a model reaches integration branches; an organisation is needed before the first client | 3.57 (estimate) |
| B: Same queue, every merge by the owner | Strongest control (ADR-0010 as written) | The owner becomes the bottleneck of a 24/7 loop | Rejected by the owner |
| C: One repository, a branch per client | Simplest; one runner scale set | No isolation between clients' access and secrets | Rejected by the owner |
| D: Jira as the queue now | Matches the stated execution source | B-45 undecided; GitHub for Jira not installed | Deferred |

Score for A is an estimate. Values: value 5, frequency 4, cost 3, risk 2, reversibility 4, learning 4. Weighted sum, with the weights used in ADR-0040: 15 + 8 + 9 + 6 + 8 + 4 = 50, divided by 14 = 3.57. Risk is 2 because model-reviewed code is merged without a person.

## Consequences

- Positive: work continues while the owner is away. Each item leaves a trail: issue, run, pull request and review.
- Negative: model-reviewed code reaches integration branches without a person. Mitigation: `main` is never automatic; the gate has all checks green and a reviewed head; integration branches are reviewed by the owner before promotion.
- Negative: an issue body is model input (T-03). Mitigation: only the owner creates items in private repositories; the worker has repository-scoped tokens only; it holds no secrets beyond `GITHUB_TOKEN`.
- Negative: hosted review sends the diff to a model provider. ADR-0021 (hosted-AI data handling) is still missing, and for client code it has to be decided before the first client.
- Follow-up: write ADR-0028 (work tracking) before any Jira adapter.
- Follow-up: the owner applies decision 7 and verifies it after one reboot.

## Security and compliance notes

- Trust boundaries: GitHub (queue, workflows) to the `homelab-arch` runners on `host-ops-01` (TB-8 / node), unchanged from ADR-0034.
- Data classes: our code is Internal. Client code and data are Confidential and stay in the client repositories.
- Threats: T-03 (prompt injection through queue items). Unreviewed merge into a shared branch is bounded by decision 4.
- This ADR changes how merges happen. It does not change ADR-0010 for `main`.
