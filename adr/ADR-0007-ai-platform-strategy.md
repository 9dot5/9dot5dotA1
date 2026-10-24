# ADR-0007: AI platform strategy

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-01-24

## Context

Local AI models are attractive for privacy and control, but they need memory and compute
that the current hardware does not provide in every host. Hardware available in the
project today: a 7.9 GB laptop, a 15 GB shared university VM, a 15 GB lab machine that is
not ours to load, and a 16 GB desktop with an RTX 3060 Ti.

## Decision

1. AI components are added only after the ROI matrix approves them (phase 04 gate).
2. Model serving is capacity-tested on the host that will run it. The test result is recorded before the service is documented as available.
3. Hosted model APIs may be used for non-sensitive work under a recorded data-handling decision.
4. Agents act through MCP interfaces with scoped permissions. They do not hold administrative credentials.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Staged, measured local models plus hosted APIs by data class | Right-sized; private where needed | Ongoing tuning | — |
| B: Local models everywhere now | Full control | Exceeds current hardware | — |
| C: Hosted only | Simple | Data leaves the platform; cost | — |

## Consequences

- Positive: decisions follow measured capacity, not preference.
- Negative: the AI phase is gated on evidence and may start later than planned.

## Security and compliance notes

Prompt and model inputs are classified like any data (see THREAT_MODEL, AI-specific
threats: prompt injection, data exfiltration through tools, unsafe tool use).
