# ADR-0010: Human in the loop

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24

## Context

AI agents (Devin, Claude CLI, MCP clients) can implement, test and open pull requests
quickly. Without explicit limits they could merge their own work, change production
state or accept risks on the owner's behalf.

## Decision

1. Agents may draft documents, implement changes, run tests and open pull requests.
2. A named human approves every merge to `main`, and every change to production or to security controls.
3. Agents never approve their own pull requests and never accept risks.
4. Destructive actions (delete, force push, data restore over live data) require explicit human confirmation in the moment, even when a runbook exists.
5. Every agent action on shared systems is attributable: the agent identity, the instruction, and the result are logged.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Human approval on consequential actions | Accountable; limits blast radius | Waiting time | — |
| B: Autonomous agents | Fast | Unattributable changes; unsafe merges | — |

## Consequences

- Positive: clear accountability.
- Negative: throughput is limited by reviewer availability.

## Security and compliance notes

Relates to ACCESS_CONTROL (agent roles) and INCIDENT_RESPONSE (agent-caused incidents are reviewed like any other).
