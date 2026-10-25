# Phase 05 — Retrieval (RAG)

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

**Status:** Proposed · **Duration:** to be sized · **Related:** ADR-0008

## Objective

Index the canonical knowledge store so that people and agents can search it, and cite the
source document, without the index becoming a source of truth.

## Deliverables

- [ ] Document metadata validated (status, owner, review date); superseded documents excluded
- [ ] Ingestion from Git only; no ingestion from unmanaged sources without an ADR
- [ ] Access classification applied: restricted documents not indexed for general agents
- [ ] Citation format: every answer cites document path and revision
- [ ] Retrieval evaluation: a fixed set of questions with expected sources, scored each release

## Exit criteria

- Evaluation set passes the agreed threshold.
- Prompt-injection tests against retrieved content pass (OWASP LLM Top 10).

## Dependencies

Phase 04 (AI platform decision), Phase 01 (metadata standard).
