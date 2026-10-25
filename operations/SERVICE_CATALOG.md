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
| Elasticsearch | Audit store of record and logs | PC Alentejo | Production (planned) | Rui Silva | Internal: loopback now; overlay with TLS for F-11 | Internal (audit records) | RB-agent-audit-ship (to write) | ADR-0035 | 2026-10-25 |
| Kibana | Owner interface for audit records and logs | PC Alentejo | Production (planned) | Rui Silva | Internal: loopback only, never Sigma | Internal | to write | ADR-0035 | 2026-10-25 |
| Prometheus | Metrics store (ADR-0009 signals) | PC Alentejo | Production (planned) | Rui Silva | Internal: loopback only | Internal (metrics) | RB-host-resources | ADR-0035 | 2026-10-25 |
| Grafana | Metrics dashboards; Sigma view (F-10) | PC Alentejo | Production (planned) | Rui Silva | Internal: loopback now; overlay with TLS for F-10 | Internal (metrics) | to write | ADR-0035 | 2026-10-25 |

Status of the entries above: defined in `ansible/roles/monitoring`, not installed. Installation waits for ADR-0035 acceptance and the capacity measurement.

## Hosts

| Host | Role | Hardware (measured or stated) | Shared? | Notes |
|---|---|---|---|---|
| Control plane (candidate) | Portal, identity, operator access | To measure: candidate desktop 8C/16T, 16 GB, discrete GPU | No | Decision in ADR to be written |
| PC Alentejo (`DESKTOP-Q3GOUP4`) | Monitoring stack (ADR-0035), second agent host (ADR-0034), Ollama | Stated: 8 GB VRAM GPU; memory to measure | No (owned, ADR-0031) | Assumed to be the control-plane candidate above; to confirm when measured |
| Laptop | Development only | 6C/12T, 8 GB | No | Not a production host |
| Shared lab server | Scheduled jobs, coursework | 8 vCPU, 15 GB | Yes | Not a production host; no personal data |
