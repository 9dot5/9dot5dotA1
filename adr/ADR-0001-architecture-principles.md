# ADR-0001: Architecture principles

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24

## Context

The platform will outlive its first technology choices. Without shared architectural
rules, each component adds its own identity system, storage format and deployment method.

## Decision

We will design against these rules:

1. **Boundaries first.** Every component has a stated purpose, owner and data it owns.
2. **Interfaces are contracts.** Each interface documents inputs, outputs, errors and authentication.
3. **Replaceable components.** No component is designed to depend on a single product's
   proprietary feature without an exit plan recorded in its ADR.
4. **Declarative where possible.** Desired state is stored in Git and reconciled, not
   configured by hand on a host.
5. **Failure is designed.** Each component states what happens when it is down and how
   it is restored.
6. **Single source per fact.** A fact has one authoritative location; others link to it.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Rules as above | Coherent over years; cheap to apply | Requires discipline in reviews | — |
| B: No rules, decide per component | Fast start | Accumulates unmanaged variety; the failure mode described in the Context | — |

## Consequences

- Positive: consistent review criteria for every later ADR.
- Negative: slower first decisions.
- Follow-up: write [architecture/TARGET_ARCHITECTURE.md](../architecture/TARGET_ARCHITECTURE.md) against these rules.

## Security and compliance notes

Rule 3 and 5 reduce the blast radius of a single component failure or compromise.
