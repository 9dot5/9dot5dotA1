# Decision Framework

**Status:** Proposed

## Decision classes

| Class | Examples | Who decides | Record |
|---|---|---|---|
| **Reversible, low impact** | Naming, folder layout, local tooling | Author, with peer review | Commit message |
| **Reversible, medium impact** | A library, a CI step, a dashboard | Architecture reviewer | ADR (short form) |
| **Hard to reverse** | Data store, identity provider, licence, hosting model | Owner, after architecture and security review | ADR (full form) |
| **Risk-bearing** | Accepting a security exception, storing new personal data | Owner only | ADR + risk register entry |

Agents may prepare any decision and implement the reversible ones. They may not decide
the last two classes.

## Decision steps

1. State the problem in one sentence.
2. List at least two options, including "do nothing".
3. Score the options with [ROI_MATRIX.md](ROI_MATRIX.md) where a component is involved.
4. Check the principles in [PRINCIPLES.md](PRINCIPLES.md).
5. Record the decision and its expiry or review date.

## Revisiting decisions

An accepted ADR is changed only by a new ADR that **supersedes** it. The old ADR keeps
its text and gains a link to the new one. Nothing is silently edited.
