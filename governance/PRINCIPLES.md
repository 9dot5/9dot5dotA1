# Principles

**Status:** Proposed. Each principle is recorded in its own ADR where a decision depends on it.

| # | Principle | Meaning in practice | ADR |
|---|---|---|---|
| 1 | **ROI First** | Before adopting a component, state the value it produces and how that will be measured. | [ROI_MATRIX](ROI_MATRIX.md) |
| 2 | **Governance First** | Ownership, decision rights and review paths exist before the system they govern. | [ADR-0002](../adr/ADR-0002-governance-model.md) |
| 3 | **Security First** | Threats are modelled before design is final. Security is a design input, not a final gate. | [ADR-0003](../adr/ADR-0003-security-first.md) |
| 4 | **Architecture First** | Context, boundaries and interfaces are agreed before implementation. | [ADR-0001](../adr/ADR-0001-architecture-principles.md) |
| 5 | **Documentation First** | A change that alters behaviour starts with its document. | [ADR-0005](../adr/ADR-0005-documentation-first.md) |
| 6 | **Open Source First** | Prefer open-source components with an exit path. | [ADR-0006](../adr/ADR-0006-open-source-first.md) |
| 7 | **Cloud Agnostic** | No design depends on one provider's proprietary service without an exit plan. | [ADR-0001](../adr/ADR-0001-architecture-principles.md) |
| 8 | **Human in the Loop** | Agents propose and execute within policy. A named human approves consequential actions. | [ADR-0010](../adr/ADR-0010-human-in-the-loop.md) |
| 9 | **Zero Trust** | No implicit trust from network location. Every request is authenticated and authorised. | [ADR-0004](../adr/ADR-0004-zero-trust.md) |
| 10 | **DevSecOps** | Security checks run in the delivery pipeline, on every change. | [SECURITY_BASELINE](../security/SECURITY_BASELINE.md) |
| 11 | **OWASP by Design** | Application design follows OWASP ASVS and the Top 10 from the start. | [OWASP_ADOPTION](../security/OWASP_ADOPTION.md) |

## Conflicts between principles

When two principles conflict, the order above is the default priority, with two
exceptions that always win: **Security First** and **Human in the Loop**. Any other
resolution is recorded as an ADR that names both principles and the trade-off accepted.
