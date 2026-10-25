<#
.SYNOPSIS
Starts a Claude Code session for one registered agent, under the separate agent account (ADR-0011, ADR-0017).

.DESCRIPTION
Refuses to start unless the identity in .claude/agent-identities.json is 'active', its signing key
exists, and the monitoring destination in C:\ProgramData\9dot5dotA1\audit-sink.json is configured.
Then opens a console as the agent account (asks for its password) with:
  - AGENT_ID, so every tool call is recorded under this agent;
  - the agent's Git author and SSH signing key, so every commit is signed by this agent;
  - the monitoring destination, so each record is shipped before the action runs.
The owner's profile is not used for the session.

.PARAMETER Agent
One of the registered agents.

.EXAMPLE
scripts\start-agent.ps1 -Agent architect
#>
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('architect', 'governance-checker', 'security-reviewer', 'docs-maintainer', 'executor')]
    [string]$Agent,
    [string]$RunnerName = 'agent-runner',
    [string]$RunnerClaude = 'C:\Users\agent-runner\.local\bin\claude.exe',
    [string]$DataRoot = (Join-Path $env:ProgramData '9dot5dotA1')
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$registry = Get-Content -Raw -LiteralPath (Join-Path $root '.claude\agent-identities.json') | ConvertFrom-Json
$identity = $registry.agents.$Agent

if (-not $identity) { throw "Agent '$Agent' is not registered." }
if ($identity.status -ne 'active') {
    throw "Agent '$Agent' is '$($identity.status)'. See operations/AGENT_IDENTITIES.md to activate it."
}
if (-not $identity.git_email) { throw "Agent '$Agent' has no git_email." }
if (-not (Test-Path -LiteralPath $identity.signing_key)) { throw "Signing key for '$Agent' not found: $($identity.signing_key)" }
if (-not (Test-Path -LiteralPath $RunnerClaude)) { throw "Claude Code is not installed for '$RunnerName' at $RunnerClaude." }

$sinkPath = Join-Path $DataRoot 'audit-sink.json'
if (-not (Test-Path -LiteralPath $sinkPath)) { throw "Monitoring destination not configured: $sinkPath" }
$sink = Get-Content -Raw -LiteralPath $sinkPath | ConvertFrom-Json
if (-not $sink.kind -or -not $sink.url -or -not $sink.token_file) {
    throw "Monitoring destination incomplete in $sinkPath (kind, url and token_file are required)."
}
if (-not (Test-Path -LiteralPath $sink.token_file)) { throw "Monitoring token file not found: $($sink.token_file)" }

$credential = Get-Credential -UserName "$env:COMPUTERNAME\$RunnerName" -Message "Password for the agent account '$RunnerName'"

# The session file holds configuration only. Tokens are read from their own file by the audit hook.
$sessionDir = Join-Path $DataRoot 'sessions'
New-Item -ItemType Directory -Force -Path $sessionDir | Out-Null
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$sessionFile = Join-Path $sessionDir "$Agent-$stamp.cmd"
$runnerAuditDir = "C:\Users\$RunnerName\.9dot5dotA1\audit"
$lines = @(
    '@echo off',
    "set `"AGENT_ID=$Agent`"",
    "set `"AGENT_AUDIT_DIR=$runnerAuditDir`"",
    "set `"AUDIT_SINK_KIND=$($sink.kind)`"",
    "set `"AUDIT_SINK_URL=$($sink.url)`"",
    "set `"AUDIT_SINK_TOKEN_FILE=$($sink.token_file)`"",
    "set `"AUDIT_SINK_INDEX=$(if ($sink.index) { $sink.index } else { 'agent-audit' })`"",
    'set "GIT_CONFIG_COUNT=7"',
    "set `"GIT_CONFIG_KEY_0=user.name`" && set `"GIT_CONFIG_VALUE_0=$($identity.git_name)`"",
    "set `"GIT_CONFIG_KEY_1=user.email`" && set `"GIT_CONFIG_VALUE_1=$($identity.git_email)`"",
    "set `"GIT_CONFIG_KEY_2=user.signingkey`" && set `"GIT_CONFIG_VALUE_2=$($identity.signing_key)`"",
    'set "GIT_CONFIG_KEY_3=gpg.format" && set "GIT_CONFIG_VALUE_3=ssh"',
    'set "GIT_CONFIG_KEY_4=commit.gpgsign" && set "GIT_CONFIG_VALUE_4=true"',
    "set `"GIT_CONFIG_KEY_5=gpg.ssh.allowedSignersFile`" && set `"GIT_CONFIG_VALUE_5=$root\.claude\allowed_signers`"",
    "set `"GIT_CONFIG_KEY_6=safe.directory`" && set `"GIT_CONFIG_VALUE_6=$root`"",
    "cd /d `"$root`"",
    "`"$RunnerClaude`""
)
Set-Content -LiteralPath $sessionFile -Value $lines -Encoding ascii

Write-Host "Starting agent '$Agent' ($($identity.git_name) <$($identity.git_email)>) as '$RunnerName'. Session file: $sessionFile"
Start-Process -FilePath cmd.exe -ArgumentList @('/k', "`"$sessionFile`"") -Credential $credential `
    -WorkingDirectory $root -LoadUserProfile
