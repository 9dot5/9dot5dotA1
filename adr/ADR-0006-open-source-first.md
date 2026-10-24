# ADR-0006: Open source first

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24

## Context

Proprietary platforms change price, terms and availability. The platform must remain
operable and portable for its owner over many years.

## Decision

1. Prefer components under OSI-approved licences, with an active upstream and a documented exit path.
2. A proprietary component requires its own ADR stating the lock-in, the data it holds, and how data is exported.
3. Use managed or SaaS services only where the ROI matrix shows a clear advantage and the data is not sensitive.
4. The platform code is released under the MIT License ([LICENSE](../LICENSE)). Decided 2026-10-24 by the sole owner.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Open source first | Portability; auditability | Operating cost on the owner | — |
| B: Proprietary by default | Less operation | Lock-in; cost changes | — |

## Consequences

- Positive: components can be replaced when the upstream changes.
- Negative: some proprietary tools (for example the Atlassian suite) are used as external services and are recorded as exceptions.

## Security and compliance notes

Open source does not imply secure. Dependencies are scanned and pinned (see SECURITY_BASELINE).
