# Phase 08 — Agents

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

**Status:** Proposed · **Duration:** to be sized · **Related:** AGENT_STRATEGY.md, MCP_STRATEGY.md, ADR-0010

## Objective

Deploy governed agents for checking, scanning and documenting, using the MCP servers
defined in MCP_STRATEGY.md.

## Deliverables

- [ ] Governance agent: checks ADR metadata, links and status lifecycle
- [ ] Security agent: runs scans and opens findings; cannot suppress findings
- [ ] Documentation agent: proposes fixes for broken links and stale metadata
- [ ] MCP servers (Knowledge, Governance, Security, Architecture) with scoped tokens
- [ ] Monthly evaluation process from AGENT_STRATEGY.md running
- [ ] Orchestrator identity and a second agent host on PC Alentejo (ADR-0034, Proposed)
- [ ] Audit sink on PC Alentejo (Elasticsearch, ADR-0035, Proposed), so that agent sessions can start

## Exit criteria

- Each agent passes its evaluation on a fixed test set.
- Each agent's permissions are documented and match the role in ACCESS_CONTROL.md.

## Dependencies

Phase 02 (security controls), Phase 05 (retrieval), Phase 06 (automation engine).
