# System Landscape

**Review by:** 2027-01-25

**Status:** Proposed · Describes the current state. Target state is in TARGET_ARCHITECTURE.md.

## Current state (as of 2026-10-24, from the owner's environment)

| Element | Location | Role | Status |
|---|---|---|---|
| Engineering repositories | GitHub (organisation to be created) | Source of engineering truth | Planned |
| Course repositories | GitHub | Coursework; outside this platform | Active, separate |
| Lab shared host | University shared server | Scripts, scheduled jobs | Active, shared, not owned |
| Desktop control plane | Windows desktop, remote-control enabled | Operator workstation | Active |
| Laptop | Windows, 8 GB RAM | Development | Active; capacity-limited |
| WSL distribution | Local laptop | Container experiments | Under migration to Podman on Windows |
| PC Alentejo (`DESKTOP-Q3GOUP4`, `host-ops-01`) | Owner's desktop, user `yau` (owned, ADR-0031) | Monitoring stack installed 2026-10-25 (ADR-0035), second agent host (ADR-0034); runs Ollama | Active; not admitted to Operations MCP yet |
| maindesktop (`DESKTOP-QFGSNE9`, `host-ws-01`) | Owner's laptop, user `9dot5` | Workstation; SSH with Legion (ADR-0040) | Active; Windows 10 1903, out of support (R-36) |

The full list, with hardware, classes and access paths, is [operations/HOST_INVENTORY.md](../operations/HOST_INVENTORY.md). Host IDs there follow the naming convention.

## Gaps against the target

- No single control plane for services yet.
- No documented inventory of running services outside the lab host.
- Backups are not defined per data set.
- Identity is local to each host.

These gaps are tracked in phases 01–03.

## Rule

If a host or service is not in this landscape, it is not governed. Add it here before
using it.
