# Ansible

**Owner:** Rui Silva (`9dot5`) · **Status:** Proposed · **Review by:** 2027-01-25
**Decisions:** [ADR-0025](../adr/ADR-0025-host-configuration-ansible.md) (pull model), [ADR-0035](../adr/ADR-0035-alentejo-monitoring-stack.md) (monitoring stack)

Host configuration for owner-controlled hosts. Each host applies its own configuration: a runner container on the host clones this repository and runs `ansible-playbook` against the host's Podman. No host connects to another to configure it.

**Not applied yet.** Nothing here has run on PC Alentejo. ADR-0025 and ADR-0035 are accepted and the Phase 00 exception is recorded (2026-10-25). Before the first run, the memory use of the stack is measured (ADR-0035 decision 7).

## Layout

| Path | Purpose |
|---|---|
| `runner/Containerfile` | The control node: Python, `ansible-core` and `containers.podman`, pinned. It drives the host's Podman through the mounted socket |
| `bootstrap/run-ansible-pull.ps1` | Run on the host by the owner. Creates folders and passwords, builds the runner, applies `site.yml` |
| `inventory/hosts.yml` | Host names only, no addresses (the repository is public) |
| `site.yml` | Which roles run on which host |
| `roles/monitoring/` | Elasticsearch, Kibana, Prometheus and Grafana as Podman containers |
| `requirements.yml` | Pinned collections, the same versions as the runner |

## Run on PC Alentejo (owner)

1. Podman is installed and its machine is running (`podman machine start`). Give the machine enough memory for the stack; the defaults in `roles/monitoring/defaults/main.yml` need about 4 GB.
2. Optional, for Windows host metrics: install `windows_exporter` on Windows (port 9182). It is outside Podman, so Ansible does not install it yet.
3. From a clone of this repository, in PowerShell:

   ```powershell
   powershell -ExecutionPolicy Bypass -File ansible\bootstrap\run-ansible-pull.ps1
   ```

4. Record the session in the break-glass register (ADR-0033). Later runs are the same command; a schedule comes with the next change.

## What the monitoring role does

- Creates the `monitoring` network and volumes for the data.
- Loads the three passwords from `C:\ProgramData\9dot5dotA1\monitoring-secrets` into Podman secrets.
- Runs Elasticsearch with security on, then sets the `kibana_system` password, creates the `agent_audit_writer` role (create documents in `agent-audit*` only) and issues one ingest key for the agent audit hook, stored as `audit-sink.token` beside the passwords.
- Runs Kibana, Prometheus (scraping itself and `windows_exporter`) and Grafana (Prometheus only, no audit data, ADR-0035 decision 4).
- Publishes every port on `127.0.0.1` only.

## Known limits of this version

| Limit | Why | Next step |
|---|---|---|
| No TLS on Elasticsearch, Kibana or Grafana | Ports are loopback only; TLS comes with the reverse proxy | ADR-0013 reverse proxy |
| Grafana is not yet reachable from Sigma (flow F-10) | Needs the overlay listener and TLS | Same as above |
| Agents on Legion cannot ship audit records to this Elasticsearch yet | That needs flow F-11 over TLS; the ingest key must not travel in clear (R-07) | Same as above |
| `host.containers.internal` may resolve to the Podman machine, not Windows | Not verified on a WSL-based Podman machine | Check on first run; set `monitoring_prometheus_windows_exporter_target` |
| No audit retention policy (12 months, ADR-0017) | Needs an index lifecycle with rollover | Follow-up in the role |
| No scheduled runs | First run is manual | Windows Task Scheduler entry, in a later change |
| Memory limits are estimates | Not measured on PC Alentejo | Measure, then set the defaults |

## Checks

Every pull request runs `ansible-lint` and `ansible-playbook --syntax-check` in CI (`.github/workflows/checks.yml`).
