# Service Catalogue

**Owner:** Rui Silva (`9dot5`)

**Review by:** 2027-01-25

**Status:** Proposed · **Rule:** a service not listed here is not governed and must not be used.

## Fields

Each entry records: name, component, host, environment, owner, purpose, data classification,
exposure (internal, VPN, public), authentication method, backup entry, monitoring entry,
runbook link, ADR link, last review date.

## Entries

| Service | Component | Host | Env | Owner | Exposure | Data class | Runbook | ADR | Last review |
|---|---|---|---|---|---|---|---|---|---|
| *(none yet — first entries come with Phase 01)* | | | | | | | | | |

## Hosts

| Host | Role | Hardware (measured or stated) | Shared? | Notes |
|---|---|---|---|---|
| Control plane (candidate) | Portal, identity, operator access | To measure: candidate desktop 8C/16T, 16 GB, discrete GPU | No | Decision in ADR to be written |
| Laptop | Development only | 6C/12T, 8 GB | No | Not a production host |
| Shared lab server | Scheduled jobs, coursework | 8 vCPU, 15 GB | Yes | Not a production host; no personal data |
