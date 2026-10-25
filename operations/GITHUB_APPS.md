# GitHub Apps for agents

**Status:** Proposed · **Owner:** Rui Silva (`9dot5`) · **Review by:** 2027-01-24 · **Related:** ADR-0011, ADR-0017, [AGENT_IDENTITIES.md](AGENT_IDENTITIES.md)

Each agent acts on GitHub through its own GitHub App. A GitHub App has its own identity, its own
permissions, short-lived installation tokens, and its own entries in the GitHub audit log. Permissions
are set per app, so each agent gets only the rights of its role.

Commits are signed locally with the agent's SSH key (see AGENT_IDENTITIES.md). A GitHub App cannot own a
signing key, so the local signature is the commit-level proof, checked against `.claude/allowed_signers`.
The GitHub App proves the API actions: pull requests, comments, checks.

## Apps

| App name | Agent | Repository permissions | Account permissions | Install on |
|---|---|---|---|---|
| `9dot5-architect` | `architect` | Contents: read and write; Pull requests: read and write; Metadata: read | none | `9dot5dotA1` only |
| `9dot5-governance-checker` | `governance-checker` | Contents: read; Pull requests: read; Checks: read and write; Metadata: read | none | `9dot5dotA1` only |
| `9dot5-security-reviewer` | `security-reviewer` | Contents: read; Pull requests: read and write (comments only); Security events: read; Metadata: read | none | `9dot5dotA1` only |
| `9dot5-docs-maintainer` | `docs-maintainer` | Contents: read and write; Pull requests: read and write; Metadata: read | none | `9dot5dotA1` only |
| `9dot5-executor` | `executor` | Contents: read and write; Pull requests: read and write; Checks: read; Metadata: read | none | `9dot5dotA1` only |

## Rules that apply to every app

1. No app has **Administration**, **Workflows**, **Secrets**, **Environments** or **Members** permission.
   Merges are done by the owner (ADR-0010), so no app can merge: "Contents: write" allows pushes to
   branches, and branch protection on `main` is set so that apps cannot push to it.
2. No app is installed on any repository other than `9dot5dotA1`.
3. Private keys are generated in GitHub, downloaded once, and stored under `C:\ProgramData\9dot5dotA1\github-apps\`
   with read access for the agent account only. They are never committed or pasted into chat.
4. Installation tokens are created per session by the launcher and expire after one hour.
5. Each app is listed in ACCESS_CONTROL.md with its role, its permissions and its review date.

## Steps for the owner (per app, about five minutes each)

These steps need the owner's GitHub login, so they are not automated.

1. Open <https://github.com/settings/apps/new> and set the name from the table.
2. Homepage URL: `https://github.com/9dot5/9dot5dotA1`. Webhook: uncheck "Active". Callback URL: leave empty.
3. Set the repository permissions from the table. Leave all account permissions at "No access".
4. "Where can this GitHub App be installed?": "Only on this account".
5. Create the app, then "Generate a private key" and save the `.pem` file to
   `C:\ProgramData\9dot5dotA1\github-apps\<agent>.pem`.
6. Note the App ID and the Installation ID after installing the app on `9dot5dotA1`.
7. Record the App ID and Installation ID in `.claude/agent-identities.json` under `github_app_id`
   and `github_installation_id`. Neither is secret.

## Open items

- Repository `9dot5/9dot5dotA1` does not exist on GitHub yet. Apps can be created before it,
  but they can be installed only after it exists (FIRST_4_WEEKS, step 3).
- Branch protection on `main` (FIRST_4_WEEKS, step 3) must be enabled before any app is installed.
