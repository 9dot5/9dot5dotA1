# ADR-0018: Monitoring backend for agent audit records

- **Status:** Proposed
- **Date:** 2026-10-24
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-04-24
- **Related:** ADR-0003, ADR-0006, ADR-0009, ADR-0017, [operations/MONITORING_STRATEGY.md](../operations/MONITORING_STRATEGY.md), [roadmap/FIRST_4_WEEKS.md](../roadmap/FIRST_4_WEEKS.md)

## Context

ADR-0017 requires that every agent action is recorded in the platform's monitoring, and that a
record is stored before the action runs. The owner named Kibana and Dynatrace as candidates.
ADR-0009 fixes the signals to monitor but does not name a backend.

Facts:

- The audit hook ships each record to one configured destination, and blocks the action if the
  destination does not accept it. Three destination formats are implemented and tested against a
  local mock: a generic JSON endpoint, an Elasticsearch/OpenSearch bulk endpoint, and the Dynatrace
  log ingestion API v2. The Dynatrace format is written from the public API description and must be
  checked against the owner's tenant before go-live.
- Kibana is the user interface of the Elastic stack. Its open-source counterpart is OpenSearch
  Dashboards, which uses the OpenSearch engine. Elastic has offered AGPLv3 as a licence option since
  2024, but the licence terms should be checked at installation time.
- Dynatrace is a proprietary SaaS. ADR-0006 item 2 requires an ADR for any proprietary component,
  stating the lock-in, the data it holds and how data is exported.
- FIRST_4_WEEKS says: "Not in the first four weeks: installing any service, host or container." A
  self-hosted Kibana or OpenSearch is a service installation, so it cannot happen before the Phase 03
  or Phase 04 gate without an exception.
- Hardware: the laptop has 8 GB and is not a production host; the control-plane candidate (16 GB) is
  not yet measured (SERVICE_CATALOG). Elasticsearch-class engines need several gigabytes of memory.

## Decision

1. **One contract, several backends.** Records keep the format in ADR-0017 and are shipped directly by
   the hook to the destination named in `audit-sink.json`: `json`, `elastic` (Elasticsearch or
   OpenSearch) or `dynatrace`.
2. **Dynatrace first, if the owner has a tenant.** It needs no installation on the platform's hosts, so
   it does not conflict with the Phase 00 rule. It is recorded as a proprietary exception under ADR-0006
   item 2, with its lock-in and export path below. This decision is conditional on the owner accepting
   that exception.
3. **Kibana (OpenSearch Dashboards) later, on the Phase 04 host.** It is adopted when the control-plane
   capacity measurement shows room for it (ADR-0015), and at that point it can receive the same records
   through the `elastic` destination. Records are not migrated; the hash chain stays intact at each cut-over.
4. **Write-only ingest credentials.** The token on the agent account can only send records: the
   Dynatrace token has the `logs.ingest` scope only, and the Elastic API key can only create documents
   in the `agent-audit` index. Neither can read, update or delete records. Retention and deletion are
   owner-only operations in the backend.
5. **Dashboards and alerts** are the three agent signals of MONITORING_STRATEGY: chain verification,
   identity use, and actions on protected paths. Each alert has a runbook (RB-agent-audit-ship, to be written).

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Dynatrace SaaS (ingest only) | No installation; managed retention; available now if a tenant exists | Proprietary (ADR-0006 exception); data held by a vendor; cost per ingested volume; lock-in | 3.21 (estimate; below threshold) |
| B: OpenSearch with OpenSearch Dashboards (Kibana-compatible) | Open source (Apache-2.0); owner keeps data; full query and dashboards | Needs a host with several GB of memory; installation conflicts with Phase 00 until Phase 04 | 3.79 (estimate) |
| C: Elastic stack with Kibana | Same as B, mature tooling | Licence needs checking (AGPLv3 option since 2024); same host cost | 3.79 (estimate; same as B) |
| D: Local JSON files only | No new service | No central view; no alerting; the owner must read the files; a local copy can be changed | Rejected for the audit record of record; kept as local buffer |

Scores are estimates. Dynatrace values: value 5, frequency 5, cost 2, risk 2, reversibility 2, learning 4.
Weighted sum: 15 + 10 + 6 + 6 + 4 + 4 = 45, divided by 14 = 3.21. OpenSearch values: value 5, frequency 5,
cost 2, risk 3, reversibility 4, learning 5. Weighted sum: 15 + 10 + 6 + 9 + 8 + 5 = 53, divided by 14 = 3.79.

Because Dynatrace is below the 3.5 threshold, its adoption is an explicit owner exception, recorded here.
The reason is speed to a working audit trail without a host install; the cost is lock-in, which the
exit path below limits.

## Consequences

- Positive: the audit trail exists before any service is installed, and it is stored outside the agent's host.
- Positive: moving to a self-hosted backend later needs no change to the agents, only to `audit-sink.json`.
- Negative: while the destination is down, agents are blocked. This is intended (fail closed), but it means
  monitoring availability limits agent availability. Mitigation: the destination's own availability is
  monitored; a runbook covers an outage.
- Negative: the agent account can read its own ingest token, so it could send false records. Mitigation:
  records carry a hash chain that the backend can check, and the backend is append-only for the agent token.
- Follow-up: check the Dynatrace log ingestion payload against the owner's tenant before first use; record
  the result in an ADR amendment.
- Follow-up: write RB-agent-audit-ship.md (shipping, outage, token rotation, chain verification).
- Follow-up: record the Dynatrace exit path: periodic export of the audit records to the local archive
  in JSON Lines, with the head hash.

## Security and compliance notes

- Data classes: agent actions and tool inputs with secrets redacted. Personal data may appear in tool
  inputs; the 12-month retention in ADR-0017 applies.
- Trust boundary: agent host to monitoring backend. The connection is outbound over TLS only.
- Exit path (ADR-0006 item 2): records in the chain format are exported in full, with the head hash, to
  owner-controlled storage. The export format is the stored JSON line itself, so no vendor tool is needed to read it.
