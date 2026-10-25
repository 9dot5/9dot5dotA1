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

## Gaps against the target

- No single control plane for services yet.
- No documented inventory of running services outside the lab host.
- Backups are not defined per data set.
- Identity is local to each host.

These gaps are tracked in phases 01–03.

## Rule

If a host or service is not in this landscape, it is not governed. Add it here before
using it.
