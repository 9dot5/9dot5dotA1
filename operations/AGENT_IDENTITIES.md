# Agent Identities

**Status:** Proposed · **Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-24 · **Related:** ADR-0011, ADR-0017, ADR-0018, [GITHUB_APPS.md](GITHUB_APPS.md), [security/ACCESS_CONTROL.md](../security/ACCESS_CONTROL.md)

Each agent acts under its own identity, and every action is recorded. Three things identify an agent:

| Layer | What identifies the agent | Where it is enforced |
|---|---|---|
| Operating system | Sessions run as the local account `agent-runner`, not as the owner | Windows, `scripts/setup-agent-runner.ps1`, `scripts/start-agent.ps1` |
| Git | Commits are signed with the agent's own SSH key; the author is the agent's name | `.claude/allowed_signers`, checked by `git log --show-signature` |
| GitHub | Pull requests and comments are made by the agent's GitHub App | GitHub audit log, [GITHUB_APPS.md](GITHUB_APPS.md) |

Every tool call is also recorded, with the agent's `AGENT_ID`, in the monitoring destination (ADR-0017, ADR-0018).

## Register

| Agent (`AGENT_ID`) | Role | Git author | Signing key | GitHub App | Status |
|---|---|---|---|---|---|
| `architect` | Drafts ADRs and documents | agent-architect | generated locally | `9dot5-architect` | pending |
| `governance-checker` | Read-only governance checks | agent-governance-checker | generated locally | `9dot5-governance-checker` | pending |
| `security-reviewer` | Read-only security review | agent-security-reviewer | generated locally | `9dot5-security-reviewer` | pending |
| `docs-maintainer` | Links, dates, terms | agent-docs-maintainer | generated locally | `9dot5-docs-maintainer` | pending |
| `executor` | Reversible changes on branches | agent-executor | generated locally | `9dot5-executor` | pending |

An identity is `pending` until every step below is done. `start-agent.ps1` refuses any identity that is not `active`.

## Rules

1. One identity per agent. Identities are not shared between agents or with the owner.
2. Private keys are in `C:\ProgramData\9dot5dotA1\agent-keys\` (owner full control, agent account read-only).
   They are never committed, pasted into chat, or written into a document (SECRET_MANAGEMENT rule 1).
   Only public keys are recorded, in `.claude/agent-identities.json` and `.claude/allowed_signers`.
3. Each identity has an owner (the sole owner, until delegated in writing) and a review date.
4. Rotation: signing keys every 12 months, and at once on suspected exposure. GitHub App private keys
   yearly. Installation tokens expire within one hour (SECRET_MANAGEMENT rotation table).
5. Revocation: set the identity's status to `revoked`, remove the public key from `allowed_signers`, delete
   the App's installation, and record the date and reason in the access register.
6. Agent identities may merge pull requests once the required checks pass, and manage the repository's content and work (ADR-0036). They may archive, rename and transfer a repository (transfer only to the owner's account or an organisation the owner owns); other repository administration is the owner's (ADR-0038). No agent token or App has the `delete_repo` scope or Administration write.
7. The agent account can modify the repository but not `.claude/`, `scripts/`, `.git/hooks`, `.git/config`,
   `CLAUDE.md`, `CODEOWNERS` or `LICENSE`. Changes to those are made by the owner.

## Known limits (accepted with ADR-0017)

- All agent sessions share the `agent-runner` account. The keys are in a folder that the account can read,
  so a session could in principle use another agent's key. The mitigation is the monitoring record: a commit
  or call under the wrong identity leaves a trace. Full separation needs one account or container per agent,
  planned for Phase 08 (ADR-0017, option D).
- The monitoring write token is readable by the agent account. It can add records but not read or delete
  them (ADR-0018).
- Local signing keys have no passphrase, because a passphrase would have to be typed on every commit and
  agents run unattended. The protection is the file permission.

## Activation steps

### Step 1: account and keys (done by `scripts/setup-agent-runner.ps1`)

Run it from the repository, accept the UAC prompt, and save the account password that it shows once.
It creates the `agent-runner` account, the folders, the permissions and the five signing keys, and writes
the public keys into the registry and `allowed_signers`.

Re-run with `-ResetPassword` to change the account password.

### Step 2: Claude Code for the agent account (owner, interactive)

The agent account needs its own copy of Claude Code and its own login. Do this once:

1. Sign in to Windows as `agent-runner` in a separate session, or open a console with
   `runas /user:%COMPUTERNAME%\agent-runner cmd`.
2. Install Claude Code for that account, to `C:\Users\agent-runner\.local\bin\claude.exe`.
3. Run `claude`, log in with the owner's Claude account, and accept the workspace trust dialog for
   `C:\Users\rsilv\9dot5dotA1`.

Do not copy the owner's `.claude` folder into the agent account. Each account has its own login.

### Step 3: GitHub Apps (owner, in the browser)

Follow [GITHUB_APPS.md](GITHUB_APPS.md) for each of the five apps. Record the App ID and the Installation ID
in the registry as `github_app_id` and `github_installation_id`. The repository `9dot5/9dot5dotA1` must exist
on GitHub first, and branch protection must be on before an app is installed.

### Step 4: monitoring destination (owner)

Fill in `C:\ProgramData\9dot5dotA1\audit-sink.json` (`kind`, `url`) and put the write-only token in
`C:\ProgramData\9dot5dotA1\audit-sink.token` (one line, no quotes). Use the destination chosen in ADR-0018.
Dynatrace needs a token with the `logs.ingest` scope only. Check the payload against the tenant before the
first real use.

### Step 5: activate and verify (owner)

1. Set the agent's `status` to `active` in `.claude/agent-identities.json`. Commit this change yourself.
2. Start the agent: `scripts\start-agent.ps1 -Agent architect`. Enter the agent account's password.
3. In the agent's console, check that the session is recorded: the first tool call appears in the
   monitoring destination within a few seconds.
4. Make a test commit on a throwaway branch, then run `git log --show-signature`. The signature must show
   the agent's key as good. Delete the branch.
5. Record the activation date in the table above and in the access register.

## Open questions

None. The decisions are recorded: GitHub Apps (ADR-0017), a separate operating-system account for the agent
sessions (ADR-0017), and the monitoring destination (ADR-0018, pending the owner's acceptance of the Dynatrace
exception or a choice of self-hosted backend).
