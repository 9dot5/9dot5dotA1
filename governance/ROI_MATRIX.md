# ROI Matrix

**Status:** Proposed · **Used by:** every ADR that adds a component, and every roadmap phase gate

No component is adopted without a completed row. The score decides whether the work
enters the roadmap, not whether it is interesting.

## Scoring

Each criterion scores 1 (low) to 5 (high).

| Criterion | Question | Weight |
|---|---|---|
| Value | Which concrete problem does it solve, and for whom? | 3 |
| Frequency | How often is the problem felt? | 2 |
| Cost to run | Hardware, licence, time to operate per month (inverted: 5 = cheap) | 3 |
| Risk added | New attack surface, data stored, dependencies (inverted: 5 = low) | 3 |
| Reversibility | How cleanly can it be removed? (5 = fully reversible) | 2 |
| Learning | Does it build a capability needed by a later phase? | 1 |

**Weighted score** = sum(score × weight) / sum(weights). Threshold for adoption: **≥ 3.5**,
and no criterion below 2 without a recorded mitigation.

## Required evidence

- **Value and frequency:** a sentence describing the problem and the times it occurred.
- **Cost:** measured resource use where possible (RAM, CPU, disk, watts). Estimates are
  marked as estimates.
- **Risk:** a link to the threat-model entry for the component.

## Register

| Component | Phase | Value | Freq | Cost | Risk | Revers. | Learn | Score | Decision | ADR |
|---|---|---|---|---|---|---|---|---|---|---|
| Git hosting (GitHub) | 00 | 5 | 5 | 5 | 4 | 4 | 3 | — | Accepted by default | ADR-0006 |
| Knowledge base (Markdown in Git) | 01 | 5 | 5 | 5 | 5 | 5 | 3 | — | Accepted by default | ADR-0008 |
| Identity provider (SSO, MFA) | 04 | 4 | 4 | 3 | 3 | 3 | 4 | — | To evaluate | — |
| Local AI models | 05 | 3 | 3 | 1 | 3 | 4 | 5 | — | To evaluate | ADR-0007 |
| Vector store / RAG | 06 | 3 | 2 | 2 | 3 | 4 | 4 | — | To evaluate | ADR-0008 |

Scores for rows marked "—" are computed when the component's ADR is proposed.
