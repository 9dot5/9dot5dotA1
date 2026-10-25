# RB-<service>-<topic>: Title

- **Owner:** [name or role]
- **Service:** [catalogue entry]
- **Last tested:** YYYY-MM-DD · **Result:** pass | fail | not tested
- **Severity this runbook addresses:** S1 | S2 | S3 | S4

## Purpose

One sentence: what situation this runbook resolves.

## Preconditions

- Access required (role from ACCESS_CONTROL.md):
- Tools and versions:
- Confirm this is the right host and environment before continuing.

## Steps

1. Step, with the exact command or action.
   - Expected result:
   - If not: go to Rollback.
2. ...

## Verification

How to confirm the service is healthy again, and what the monitoring should show.

## Rollback

Steps to return to the state before this runbook was used.

## Destructive steps

Mark each step that deletes or overwrites data with **[CONFIRM]**. An agent or operator must
get explicit human confirmation before running it (ADR-0010).

## Escalation

Who to contact, in what order, and within what time.

## Change history

| Date | Change | By |
|---|---|---|
