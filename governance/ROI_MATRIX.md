# ROI Matrix

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

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
| Git hosting (GitHub) | 00 | 5 | 5 | 5 | 4 | 4 | 3 | 4.50 | Accepted by default | ADR-0006 |
| Knowledge base (Markdown in Git) | 01 | 5 | 5 | 5 | 5 | 5 | 3 | 4.86 | Accepted by default | ADR-0008 |
| Identity provider (SSO, MFA) | 04 | 4 | 4 | 3 | 3 | 3 | 4 | 3.43 (below threshold) | To evaluate | ADR-0012 (Proposed) |
| Local AI models | 05 | 3 | 3 | 1 | 3 | 4 | 5 | 2.86 (below threshold) | To evaluate; cost 1 needs a recorded mitigation | ADR-0007 |
| Vector store / RAG | 05 | 3 | 2 | 2 | 3 | 4 | 4 | 2.86 (below threshold) | To evaluate | ADR-0008 |
| Agents: Claude Code in-repo | 00 | 5 | 5 | 2 | 2 | 4 | 5 | 3.57 (estimate) | Adopted on Proposed ADR | ADR-0011 (Proposed) |
| Reverse proxy (candidate: Caddy) | 04 | 4 | 3 | 4 | 3 | 5 | 3 | 3.71 (estimate) | Candidate; confirm in Phase 04 | ADR-0013 (Proposed) |
| Secret manager (candidate: OpenBao) | 04 | 4 | 3 | 3 | 4 | 3 | 4 | 3.50 (estimate) | Candidate; confirm in Phase 04 | ADR-0014 (Proposed) |
| Portal hosting (control-plane candidate) | 03 | 4 | 4 | 3 | 3 | 4 | 3 | 3.50 (estimate) | Provisional until measured | ADR-0015 (Proposed) |
| Automation: scheduled scripts in Git | 06 | 3 | 4 | 5 | 4 | 5 | 2 | 4.00 (estimate) | Start here; re-score with Phase 06 inventory | ADR-0016 (Proposed) |

Scores are the weighted sum from the Scoring table, rounded to two decimals. Rows marked
"estimate" use values that are not measured; they are replaced by measurements in the phase
named in the decision column. Arithmetic check: Identity = (4×3 + 4×2 + 3×3 + 3×3 + 3×2 + 4×1) / 14 = 48 / 14 = 3.43.
