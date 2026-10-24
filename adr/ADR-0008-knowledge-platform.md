# ADR-0008: Knowledge platform

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24

## Context

The project needs decisions, runbooks and standards that people and agents can search and
cite. A retrieval system (RAG) is useful only when the underlying documents are well
structured and versioned.

## Decision

1. **Canonical store:** Markdown in Git. Engineering truth lives in GitHub; organisational
   truth is published to Confluence from the same files.
2. **Search and retrieval** is added in phase 05 and indexes the canonical store. It never
   becomes the source of truth.
3. **Document metadata** (owner, status, review date) is mandatory in each document, so
   retrieval can filter by status.
4. Superseded and deprecated documents are excluded from retrieval by default.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Git Markdown canonical, retrieval on top | Versioned; portable; agent-friendly | Discipline in metadata | — |
| B: Wiki as canonical | Easy editing | Weak history; lock-in | — |
| C: Vector store as canonical | Searchable | Opaque; no review | — |

## Consequences

- Positive: any tool can be replaced without losing knowledge.
- Negative: contributors must edit Markdown rather than a rich editor.

## Security and compliance notes

Retrieval respects the access classification of each document. Documents marked
restricted are not indexed for general-purpose agents.
