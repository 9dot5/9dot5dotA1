# ADR-0005: Documentation first

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24

## Context

Platforms are rebuilt because nobody can say why they were built the way they were.
Documentation written after the fact records what exists, not what was decided.

## Decision

1. A change that alters behaviour, architecture, security or operations starts with its
   document: an ADR, a phase document or a runbook.
2. Documents are reviewed like code, in pull requests.
3. Implementation follows the document; if they diverge, the document is updated first.
4. Agents must read the relevant ADR and standards before implementing a change.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Documentation first | Decisions survive; agents have context | Upfront time | — |
| B: Documentation after | Faster start | Undocumented decisions, drift | — |

## Consequences

- Positive: agents and humans share one context.
- Negative: small changes need a paragraph of justification; mitigated by the short ADR form.

## Security and compliance notes

Documents must not contain secrets, real credentials or personal data beyond what the
document requires. See SECRET_MANAGEMENT.md.
