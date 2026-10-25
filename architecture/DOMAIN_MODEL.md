# Domain Model

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

**Status:** Proposed

## Core concepts

| Concept | Definition | Owned by | Authoritative store |
|---|---|---|---|
| **Vision / Principle** | Long-lived statement of intent | Governance | Git (`governance/`) |
| **Decision (ADR)** | Recorded choice with context and consequences | Architecture | Git (`adr/`) |
| **Document** | Any canonical knowledge item, with owner and status | Knowledge | Git |
| **Component** | A deployable or consumable part of the platform | Architecture | Git (`operations/SERVICE_CATALOG.md`) |
| **Service** | A running instance of a component on a host | Operations | Service catalogue |
| **Host** | A machine or VM that runs services | Operations | Service catalogue |
| **Identity** | A human, agent or service principal | Security | Identity provider |
| **Role** | A named set of permissions | Security | Identity provider, documented in ACCESS_CONTROL |
| **Risk** | A recorded threat with likelihood, impact, treatment | Security | Risk register (Git) |
| **Control** | A measure that treats a risk | Security | SECURITY_BASELINE |
| **Backup** | A recoverable copy of a data set, with a restore test record | Operations | BACKUP_STRATEGY |
| **Change** | A proposed modification, traceable to an ADR and a Jira key | Operations | Pull request + Jira |
| **Incident** | An event that breaches or threatens a control | Security | Incident record |

## Relationships

- A **Decision** may **supersede** another Decision.
- A **Component** is governed by one or more **Decisions**.
- A **Service** is an instance of one **Component** on one **Host**.
- A **Risk** is treated by one or more **Controls**; a **Control** may treat many **Risks**.
- A **Change** implements one **Decision** and updates the affected **Documents**.

## Naming

Names follow [docs/naming-conventions.md](../docs/naming-conventions.md). A term defined here
is used with the same meaning in every other document; see [docs/glossary.md](../docs/glossary.md).
