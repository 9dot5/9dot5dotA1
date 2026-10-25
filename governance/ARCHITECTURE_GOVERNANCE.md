# Architecture Governance

**Review by:** 2027-01-25

**Status:** Proposed · **Decision authority:** owner, delegable to an architecture lead

## Architecture Review Process

1. **Trigger.** A proposal that adds a component, changes an interface, changes a data
   store, or changes a trust boundary.
2. **Preparation.** The author opens an ADR with status **Proposed**, using
   [adr/ADR_TEMPLATE.md](../adr/ADR_TEMPLATE.md). It must include context, options
   considered, the ROI row, and affected documents in `architecture/`.
3. **Review.** A reviewer checks, in this order:
   - Does it fit the principles?
   - Does it define its boundary, data flows and failure behaviour?
   - Is there an exit path (cloud agnostic, open source first)?
   - Is the security review trigger satisfied?
4. **Decision.** Accepted, Rejected (with reasons), or Returned for changes. Decisions
   are recorded in the ADR, not in chat or meeting notes.
5. **Follow-up.** Affected diagrams and `architecture/` documents are updated in the same
   pull request as the ADR, or the ADR records a dated task to do so.

Target review time: 5 working days for a standard ADR; 10 for one that changes a trust
boundary.

## Standards for every architecture document

- Each document names its owner and review date.
- Each diagram has a legend and a date, and its source file is versioned under `diagrams/`.
- Interfaces are described by contract: inputs, outputs, errors, authentication.

## Architecture debt

Known deviations from the target architecture are listed in `architecture/TARGET_ARCHITECTURE.md`
with an owner and a removal condition. Debt without a removal condition is not allowed.
