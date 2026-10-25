# Operations MCP: Threat Model Addendum

**Owner:** Rui Silva (`9dot5`) · **Status:** Proposed, for security review · **Review by:** 2027-01-25
**Related:** [THREAT_MODEL.md](THREAT_MODEL.md), [ADR-0029](../adr/ADR-0029-operations-mcp.md), [M2M_ARCHITECTURE.md](../architecture/M2M_ARCHITECTURE.md)

This addendum extends THREAT_MODEL for the Operations MCP. It is drafted for review, as CLAUDE.md rule 4 requires. Accepting any residual risk is the owner's decision. The `security-reviewer` role is read-only and cannot accept risk.

Method: STRIDE per component, with the OWASP LLM Top 10 for the agent-facing surface.

## Assets

| Asset | Class | Why it matters |
|---|---|---|
| Node access (what the gateway can do) | Secret | Control of every node |
| Approval decisions | Internal | Proof that a human allowed a change |
| Audit log | Internal, personal data possible | Evidence of every action |
| Token signing key | Secret | Forging any principal |
| Node registry | Internal | Which nodes are in scope |

## Threats

| ID | Threat (STRIDE) | Component | L | I | Treatment | Control in 0.1 | Gap |
|---|---|---|---|---|---|---|---|
| T-OPS-01 | An agent calls a write capability without approval (Elevation) | Gateway | 2 | 5 | Reduce | Write tier requires approval; adapter not reached | None in code path. Tested |
| T-OPS-02 | A forged or altered token gives a principal more roles (Spoofing) | Identity | 2 | 5 | Reduce | HMAC signature checked with constant-time compare; expiry checked | Shared key; move to Authentik (R-26) |
| T-OPS-03 | Prompt injection in tool output makes an agent request a write (Tampering) | Agents, all tools | 4 | 4 | Reduce | Output is data; approval needed for writes; no shell | No injection test set yet (BACKLOG B-10) |
| T-OPS-04 | An agent approves its own request (Elevation, Repudiation) | Approval | 2 | 5 | Reduce | Approver must be human, hold may_approve, differ from requester | Relies on identities being distinct (sole owner) |
| T-OPS-05 | An approval is reused for a different request (Tampering) | Approval | 2 | 4 | Reduce | Bound to request hash; one use; 15-minute expiry | None. Tested |
| T-OPS-06 | Audit records are altered or deleted (Repudiation) | Audit | 2 | 4 | Reduce | Hash chain; verify command; fsync | Head hash not exported (TD-06, B-29) |
| T-OPS-07 | Flood of approval requests fills memory (DoS) | Approval | 3 | 2 | Reduce | None | Rate limit per principal. To add |
| T-OPS-08 | Detail in refusal messages leaks node topology (Information disclosure) | Gateway | 2 | 2 | Accept (low) | Messages name the rule, not the host address | Review messages before activation |
| T-OPS-09 | Approval recorded before its audit write; a failed write leaves an approval with no record (Repudiation) | Approval | 2 | 4 | Reduce | Audit record written before each state change; a failed write changes nothing (ADR-0032) | Fixed in code, 2026-10-25 (R-22). Pending security review |
| T-OPS-10 | Logs or results carry personal data or secrets (Information disclosure) | Audit, results | 3 | 3 | Reduce | Arguments logged as given; results not redacted | Add redaction before return and before audit (ADR-0009 rule 5) |
| T-OPS-11 | A compromised Sigma reaches the gateway or the audit store (Elevation, Spoofing) | TB-5, TB-7 | 3 | 4 | Reduce | Sigma holds no credential and no audit record (ADR-0030); pushes data only | Push-only network rule needs the zones ADR (ADR-0034, to be written) |
| T-OPS-12 | A lab PC reached through a Sigma hop is untrusted (Lateral movement) | TB-4, C-6 | 3 | 4 | Avoid | Gate closed; no node admitted; hop needs ADR-0031 Part C | Decision pending (owner) |
| T-OPS-13 | Disabled node re-enabled without its access being recorded (Elevation) | Node registry | 2 | 4 | Reduce | Registry in Git; enabled flag reviewed | Protect `config/nodes.json` with CODEOWNERS and review |
| T-OPS-14 | A workflow identity is reused by a human or another workflow (Spoofing) | Identity | 2 | 4 | Reduce | Workflow token bound to commit SHA (M2M §4.1) | Not implemented in 0.1 |
| T-OPS-15 | Tool schema drift lets a new argument pass unchecked (Tampering) | API | 2 | 3 | Reduce | Unknown fields refused; contract test | None. Tested |
| T-OPS-16 | Node contacted before its governance conditions hold; a gate is bypassed or a flag is flipped (Elevation) | Gateway, node registry | 2 | 5 | Reduce | Security gate in code (ADR-0031 Part B): ADR status read from files, owner review records in `config/gate.json`. Gated calls refused and audited, with no approval created | Owner must review `config/gate.json` changes. Tested |
| T-OPS-17 | Routine work done through an unregistered out-of-band path, bypassing approval and audit (Repudiation, Elevation) | Nodes, operator | 4 | 4 | Reduce | Break-glass policy (ADR-0033): registered paths, per-session record, reconciliation within two working days | Current practice (plain SSH from a personal session, R-01) is not compliant until the register exists |
| T-OPS-18 | Shared-host administrator reads metrics about the owner's nodes at Sigma (Information disclosure) | Sigma | 3 | 3 | Reduce | Health and metrics only, no audit, no credential, no personal data (ADR-0030) | Residual risk accepted by the owner, not yet recorded (R-24) |
| T-OPS-19 | Approval state lost or replayed after a restart (Tampering, Repudiation) | Approval store | 3 | 4 | Reduce | Journal, replayed at start; used flag persisted; journal write failure refuses change (ADR-0032) | Fixed in code, 2026-10-25 (R-23). Pending security review |

## Residual risks requiring owner decision

- T-OPS-02 (shared key) until Authentik is live.
- T-OPS-07 (approval flood) until rate limits exist.
- T-OPS-12 (lab hop) until ADR-0031 Part C is decided for each host.
- T-OPS-17 (break-glass misuse) after ADR-0033 is accepted. The owner accepts this residual.
- T-OPS-18 (metrics visible on Sigma), recorded as R-24.

## Security gate (added 2026-10-25)

Operations MCP cannot contact a node until all of these hold (ADR-0031 Part B):

1. ADR-0029 to ADR-0033 are Accepted.
2. This threat model has been reviewed, recorded in `config/gate.json`.
3. The permission matrix (M2M_ARCHITECTURE §6) has been approved, recorded in `config/gate.json`.

Status when this section was written: **closed**. The shipped configuration fails all three.

## Changes on 2026-10-25

- R-22 fixed in code: audit precedes every state change (T-OPS-09).
- R-23 fixed in code: approval journal with replay (T-OPS-19).
- Threats T-OPS-16 to T-OPS-19 added.
- Requires security review of the changed code, and an update to the threat model's residual decisions by the owner.

## Controls mapping

ISO/IEC 27001:2022 controls referenced: A.5.15 (access control), A.5.17 (authentication information), A.5.18 (access rights), A.8.2 (privileged access rights), A.8.5 (secure authentication), A.8.15 (logging), A.8.16 (monitoring activities), A.8.24 (cryptography, for the token signature).

OWASP: LLM Top 10 LLM01 (prompt injection, T-OPS-03), LLM06 (excessive agency, mitigated by tiers and approval), LLM05 (improper output handling, output treated as data). API Security Top 10: API1 (object-level authorisation, per node), API5 (function-level authorisation, per role), API9 (improper inventory management, mitigated by the single capability registry).

## Test evidence

`ops-mcp/tests/test_ops_mcp.py`, 60 tests, passing on 2026-10-25. The tests cover T-OPS-01, 02, 04, 05, 06, 09, 15, 16 and 19. T-OPS-17 and T-OPS-18 are procedural and have no test.
