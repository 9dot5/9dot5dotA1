# ADR-0002: Governance model

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24

## Context

Decisions made in chat, in meetings or in an agent's session are not recoverable by
anyone else. The project needs a single place where decisions are proposed, reviewed and
recorded, and clear rights to decide.

## Decision

We will govern the platform through:

- the decision classes and steps in [governance/DECISION_FRAMEWORK.md](../governance/DECISION_FRAMEWORK.md);
- Architecture and Security review processes in [governance/ARCHITECTURE_GOVERNANCE.md](../governance/ARCHITECTURE_GOVERNANCE.md) and [governance/SECURITY_GOVERNANCE.md](../governance/SECURITY_GOVERNANCE.md);
- one owner who holds final decision rights and can delegate review rights in writing.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Written model with one owner | Clear accountability; auditable | Owner is a single point of judgement | — |
| B: Consensus among contributors | Shared ownership | Slow; unclear in a one-person project | — |
| C: No model | None | Decisions lost; the pattern in the Vision document | — |

## Consequences

- Positive: every accepted change has a recorded reason and an owner.
- Negative: contributors must write before they build.

## Security and compliance notes

Risk acceptance is an owner-only decision (see SECURITY_GOVERNANCE). Agents cannot
approve their own changes.
