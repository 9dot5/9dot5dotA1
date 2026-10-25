# Deployment Strategy

**Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-25

**Status:** Proposed · **Related:** ADR-0001 (declarative, cloud agnostic), ADR-0007 (capacity)

## Principles

1. **Declarative.** Desired state lives in Git. Hosts are configured from it, not edited by hand.
2. **Portable.** Workloads run in containers or on well-defined host services, so they can move between a home host, a VM and a cloud provider.
3. **Capacity-tested.** A service is deployed on a host only after its resource use has been measured there.
4. **Reversible.** Each deployment has a documented rollback.
5. **Separated environments.** Test and production are distinct; a lab host is never production.

## Environments

| Environment | Purpose | Hosts | Data |
|---|---|---|---|
| Development | Build and test | Developer workstations | Synthetic only |
| Staging | Pre-production verification | To be defined in Phase 05 | Synthetic or anonymised |
| Production | Owner's platform | Control plane host (decision in ADR-0001 follow-up) | Real |

## Release process

1. Change merged to `main` after review.
2. Automated checks run (build, tests, scans).
3. Deployment to staging; smoke test.
4. Human approval to promote to production.
5. Post-deployment check; rollback if it fails.

## Rollback

Every production change lists its rollback step in the pull request. Rollback is tested at least once per component before it is considered operational.
