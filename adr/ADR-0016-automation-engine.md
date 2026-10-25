# ADR-0016: Automation engine

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24
- **Related:** ADR-0006, ADR-0010, [roadmap/PHASE_06_AUTOMATION.md](../roadmap/PHASE_06_AUTOMATION.md), [architecture/TARGET_ARCHITECTURE.md](../architecture/TARGET_ARCHITECTURE.md)

## Context

TARGET_ARCHITECTURE.md lists an automation engine for scheduled and event workflows. Phase 06
requires the engine to be decided under the ROI matrix, and each automation to be owned, logged
and reversible. No recurring-task inventory exists yet, so the workload is not known.

Facts: no automation runs today. Assumption: the first automations are small scheduled jobs
(backup verification, documentation checks, reports).

## Decision

We will start with scheduled scripts kept in Git and run by the host's scheduler, each with a
log, an owner and a runbook. We will not adopt a workflow engine until the Phase 06 inventory
shows a need that scripts cannot meet. That need is recorded in a new ADR.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Scheduled scripts in Git, host scheduler (chosen) | Minimal dependencies; reviewable; easy to remove | Limited visibility; no UI; logic per script | 4.00 (estimate) |
| B: Node-RED | Open source (Apache-2.0); visual flows | Flows are hard to review in Git; another runtime to patch | Not scored; to evaluate |
| C: n8n | Large connector set | Sustainable Use licence, not OSI-approved; needs an ADR-0006 exception | Not scored; not adopted |
| D: Workflow platform (for example Temporal) | Durable, retried workflows | Heavy for a single owner; large operating cost | Not scored; rejected for now |

Score for A is an estimate. Values: value 3, frequency 4, cost 5, risk 4, reversibility 5,
learning 2.

## Consequences

- Positive: each automation is a file in Git, reviewed like any other change.
- Positive: no new service enters the service catalogue until one is needed.
- Negative: no central view of runs. Mitigation: each script writes to a log that the portal reads
  (Phase 03 and 07).
- Negative: retries and scheduling are basic. Mitigation: the Phase 06 inventory records which
  automations need more, and that need triggers a new ADR.
- Follow-up: inventory of recurring tasks with owner and frequency (Phase 06).
- Follow-up: classify each automation as read-only, reversible write, or consequential (ADR-0010).

## Security and compliance notes

- Trust boundary: platform services to data stores (CONTEXT.md, boundary 3). Scripts use service
  identities with least privilege (ACCESS_CONTROL).
- Consequential automations require recorded human approval before they run (ADR-0010 rule 2).
- Logs must not contain secrets or unredacted personal data (SECURITY_BASELINE).
