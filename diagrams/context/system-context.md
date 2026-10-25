# System context diagram

**Owner:** Rui Silva (`9dot5`)

**Status:** Proposed · **Review by:** 2027-01-25

Source for [architecture/CONTEXT.md](../../architecture/CONTEXT.md). Mermaid; render in GitHub or Confluence.

```mermaid
flowchart LR
  owner([Owner])
  collab([Collaborators])
  claude[Claude Code<br/>architect, reviewer, executor]
  mcp[MCP clients]

  subgraph platform[9dot5dotA1 platform]
    portal[Portal]
    knowledge[Knowledge store<br/>Git canonical]
    services[Services]
    data[(Data and backups)]
  end

  git[(GitHub)]
  confl[(Confluence)]
  jira[(Jira)]

  owner --> portal
  collab --> portal
  claude --> mcp
  claude --> git
  mcp --> portal
  portal --> knowledge
  portal --> services
  services --> data
  knowledge --> git
  git --> confl
  owner --> jira
```

Legend: solid arrows are requests. Trust boundaries are described in CONTEXT.md.
Date: 2026-10-24.
