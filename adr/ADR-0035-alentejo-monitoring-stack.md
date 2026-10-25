# ADR-0035: Monitoring stack on PC Alentejo

- **Status:** Accepted
- **Date:** 2026-10-25
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-25
- **Related:** ADR-0006, ADR-0009, ADR-0017, ADR-0018, ADR-0025, ADR-0030, ADR-0031, ADR-0034, [operations/MONITORING_STRATEGY.md](../operations/MONITORING_STRATEGY.md), [operations/SERVICE_CATALOG.md](../operations/SERVICE_CATALOG.md), [roadmap/FIRST_4_WEEKS.md](../roadmap/FIRST_4_WEEKS.md)

## Context

The owner wants Dynatrace and Kibana to run as container images on PC Alentejo, with an interface that Sigma uses for monitoring, and Grafana added to the monitoring (2026-10-25).

Facts:

- **Dynatrace cannot run as a local image.** It is a SaaS platform. The parts that run on a customer host are collectors (OneAgent, ActiveGate); the user interface and the data store stay in Dynatrace's cloud. The on-premises product (Dynatrace Managed) is a licensed installation, not a free image.
- Kibana needs Elasticsearch as its data store. Both are offered under AGPLv3 among other licences since 2024. The licence of the chosen image is checked at installation (ADR-0018).
- Grafana is licensed AGPLv3. It shows metrics from a metrics store; Prometheus (Apache-2.0) is the usual one, with `windows_exporter` for Windows host metrics.
- The audit hook already supports an Elasticsearch destination (`elastic` in `audit-sink.json`, ADR-0018).
- PC Alentejo is owned (ADR-0031) and is the stated control-plane candidate in SERVICE_CATALOG: 8 cores, 16 GB, discrete GPU, not yet measured. It also runs Ollama (agent-sandbox).
- ADR-0030: Sigma holds health and metrics only, never audit records, credentials or configuration. TB-4 denies node-to-node traffic unless a flow is declared.
- FIRST_4_WEEKS: no service, host or container is installed before the Phase 03 gate.

## Decision

1. **The stack on PC Alentejo**, each component a Podman container configured by Ansible (ADR-0025):

   | Component | Purpose | Data held |
   |---|---|---|
   | Elasticsearch | Store of record for agent audit records (ADR-0017) and logs | Internal; audit records |
   | Kibana | Owner interface for audit records and logs | none of its own |
   | Prometheus with `windows_exporter` | Metrics: health, resources, backup status (ADR-0009) | Internal; metrics |
   | Grafana | Dashboards for the ADR-0009 signals and the agent signals | none of its own |

2. **Elasticsearch becomes the audit sink.** `audit-sink.json` uses `kind: elastic` with the Elasticsearch endpoint on PC Alentejo, and a write-only API key limited to creating documents in `agent-audit` (ADR-0018 decision 4). This revises ADR-0018 decision 2: Dynatrace is not adopted as the record of record.
3. **Dynatrace is not adopted.** It cannot run on PC Alentejo. If the owner later wants it, it is a SaaS tenant with an ActiveGate container on PC Alentejo, recorded as a proprietary exception (ADR-0006 rule 2) in a new ADR.
4. **The interface for Sigma is Grafana, read-only, metrics only.** Sigma reaches one Grafana organisation that holds only the ADR-0009 signals, with a Viewer account. Kibana and Elasticsearch are never reachable from Sigma, because they hold audit records (ADR-0030 rules 1 and 2).
5. **A declared flow, F-10: Sigma to Grafana on PC Alentejo**, HTTPS, over the private overlay only, read-only. It is the only exception to TB-4 for Sigma, and it gives Sigma no path to any other service or node. This adds to ADR-0030, which so far only allowed nodes to push to Sigma.
5a. **A declared flow, F-11: agent hosts to the audit sink.** Agent sessions on Legion and on PC Alentejo send audit records to Elasticsearch on PC Alentejo, HTTPS only, with the write-only ingest key. On PC Alentejo itself the hook may use the loopback address. Legion's agents ship over the overlay only once TLS is in place (R-07): until then they stay blocked by the fail-closed hook.
6. **Nothing is exposed on the public address of PC Alentejo.** All four components listen on the overlay or on localhost only. The first version (`ansible/roles/monitoring`) publishes on localhost only; the overlay listeners for F-10 and F-11 come with the reverse proxy and TLS (ADR-0013).
7. **Preconditions before installation.** The owner records an exception to the FIRST_4_WEEKS rule for this stack; the memory and disk use of the four containers is measured on PC Alentejo alongside Ollama (DEPLOYMENT_STRATEGY principle 3); and the services are added to SERVICE_CATALOG.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Elasticsearch, Kibana, Prometheus and Grafana on PC Alentejo; Grafana read-only for Sigma (chosen) | Open source; owner keeps the data; resolves the audit sink; one host | Memory on a 16 GB host shared with Ollama; one host is a single point of failure for agents (fail closed) | 3.71 (estimate) |
| B: Dynatrace SaaS as the audit sink (ADR-0018 decision 2) | No installation | Proprietary; vendor holds the data; not what the owner asked for | Superseded by this ADR |
| C: OpenSearch and OpenSearch Dashboards instead of Elastic and Kibana | Apache-2.0; same audit format | The owner asked for Kibana | 3.79 (estimate, ADR-0018); kept as fallback if the Elastic licence check fails |
| D: Expose Kibana to Sigma too | One interface for everything | Audit records visible on a shared host; breaks ADR-0030 | Rejected |

Score for A is an estimate. Values: value 5, frequency 4, cost 3, risk 3, reversibility 4, learning 3. Weighted sum: 15 + 8 + 9 + 9 + 8 + 3 = 52, divided by 14 = 3.71. The cost value assumes the four containers fit beside Ollama in 16 GB; this is not measured.

## Consequences

- Positive: the audit sink exists without a SaaS dependency, and agents can be started once it runs.
- Positive: Sigma gets a monitoring view without holding any data.
- Negative: if PC Alentejo is down, the audit sink is down and every agent stops (fail closed, R-12). Mitigation: Grafana alerting on sink availability; a runbook for an outage (RB-agent-audit-ship).
- Negative: Elasticsearch needs several gigabytes of memory. Mitigation: heap limit set in the role; measured before installation; OpenSearch with a smaller heap as fallback.
- Follow-up: Ansible role `monitoring` (ADR-0025) with pinned image digests.
- Follow-up: amend ADR-0030 with flow F-10, and M2M_ARCHITECTURE §8 with flows F-10 and F-11 (done 2026-10-25).
- Follow-up: Ansible role `monitoring` with pinned image digests (done 2026-10-25, `ansible/roles/monitoring`, not applied).
- Follow-up: add the four services to SERVICE_CATALOG and the backup of Elasticsearch to BACKUP_STRATEGY (R-09).

## Security and compliance notes

- Trust boundaries: TB-5 (nodes to telemetry), TB-7 (Sigma, shared and hostile by assumption), TB-4 (node to node, declared exceptions F-10 and F-11).
- Data classes: audit records and logs are Internal and stay on PC Alentejo. Sigma sees metrics only.
- Controls: write-only ingest key for the audit hook; Viewer-only Grafana account for Sigma; no public exposure; TLS on every interface.
- Threats: a Sigma user reads the infrastructure metrics (T-08), accepted within ADR-0030. A stolen Grafana Viewer credential exposes metrics only. Added as R-30.

## Change history

| Date | Change | By |
|---|---|---|
| 2026-10-25 | Accepted, with residual risks R-12 and R-30. ADR-0037 double check: automatic check passed; owner named and confirmed it in the session ("sim, aceito a ADR-0025, ADR-0034 e ADR-0035, e a exceção da Fase 00") | Owner decision, recorded by an unregistered Claude Code session (no `AGENT_ID`, see R-01) |
