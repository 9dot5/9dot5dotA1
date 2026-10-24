# Contributing

## Ground rules

1. **Documentation first.** A change that alters architecture, security or operations
   starts with a document (ADR, phase or runbook) and only then code or configuration.
2. **Human in the loop.** AI agents (Devin, Claude CLI, MCP clients) may draft, implement
   and open pull requests. A named human approves every merge to `main`.
3. **No secrets in Git.** See [security/SECRET_MANAGEMENT.md](security/SECRET_MANAGEMENT.md).
4. **Small, reviewable changes.** One concern per pull request.

## Workflow

1. Find or create the Jira Story that the change serves (Epic → Story → Task).
2. Branch from `main`: `<type>/<short-topic>`, for example `docs/adr-0004-zero-trust`.
3. Write or update the governing document first when the change is a decision.
4. Open a pull request using the template. Link the Jira key and any ADR.
5. Pass the checks: markdown lint, link check, secret scan, and the reviews required by
   [governance/ARCHITECTURE_GOVERNANCE.md](governance/ARCHITECTURE_GOVERNANCE.md) and
   [security/SECURITY_BASELINE.md](security/SECURITY_BASELINE.md).
5. Merge after approval. Use a merge commit so each change keeps its review history.

## Commit messages

Imperative mood, under 72 characters, with the Jira key when one exists:

```
docs(adr): accept ADR-0004 zero trust baseline [PLAT-12]
```

Types: `docs`, `feat`, `fix`, `sec`, `ops`, `chore`.

## Definition of Done

The full Definition of Done is in [docs/standards.md](docs/standards.md). A pull request
is not ready to merge until it meets the criteria for its change type.

## Security issues

Do not open a public issue for a vulnerability. Follow
[security/INCIDENT_RESPONSE.md](security/INCIDENT_RESPONSE.md).

## Sole-owner mode

While the owner is the only maintainer, GitHub does not let an author approve their own
pull request. In this mode:

- Branch protection requires pull requests and passing status checks, with **0** required approvals.
- The owner's explicit merge decision, after the checks pass and the review checklist is complete, is the human approval required by ADR-0010.
- Agent-authored pull requests are merged only by the owner, never by the agent.
- When a second maintainer joins, raise the required approvals to 1 and update CODEOWNERS in the same change.
