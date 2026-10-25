#Requires -Version 5.1
<#
.SYNOPSIS
Prepares the separate account that runs agent sessions, its file permissions, and one SSH signing key per agent (ADR-0017).

.DESCRIPTION
Creates the local standard account 'agent-runner' (if missing), prints its password once, and sets:
  - read and execute on C:\ProgramData\9dot5dotA1 (owner full control);
  - traverse on the owner's profile folder, and modify on the repository;
  - deny-write on .claude, scripts, .git\hooks, CLAUDE.md, CODEOWNERS, LICENSE and .git\config.
It generates one ed25519 signing key per registered agent in C:\ProgramData\9dot5dotA1\agent-keys,
writes the public keys to .claude\agent-identities.json and .claude\allowed_signers.

The password is printed while the transcript is paused, so it never reaches the transcript file.
The transcript file is deleted when the script ends, successfully or not.

The script elevates itself. Accept the single UAC prompt.

.PARAMETER ResetPassword
Set a new password for an existing agent-runner account and print it.

.EXAMPLE
scripts\setup-agent-runner.ps1
#>
[CmdletBinding()]
param(
    [string]$RepoPath = '',
    [string]$OwnerAccount = $env:USERNAME,
    [string]$RunnerName = 'agent-runner',
    [string]$DataRoot = (Join-Path $env:ProgramData '9dot5dotA1'),
    [switch]$ResetPassword
)

$ErrorActionPreference = 'Stop'
if (-not $RepoPath) { $RepoPath = Split-Path -Parent (Split-Path -Parent $PSCommandPath) }
$transcript = Join-Path $env:TEMP 'agent-runner-setup.log'

function Stop-SetupTranscript {
    try { Stop-Transcript | Out-Null } catch { }
    Remove-Item -LiteralPath $transcript -Force -ErrorAction SilentlyContinue
}

# Shows a secret once. The transcript is paused for the duration, so the value is not logged.
function Show-OnceSecret {
    param([string]$Value, [string]$Caption)
    try { Stop-Transcript | Out-Null } catch { }
    Write-Host ''
    Write-Host $Caption -ForegroundColor Yellow
    Write-Host $Value -ForegroundColor Yellow
    Read-Host 'Save it in your password manager, then press Enter' | Out-Null
    try { Start-Transcript -Path $transcript -Append -Force | Out-Null } catch { }
}

# On any error, keep the window open and show the message (the elevated window would otherwise close).
trap {
    Write-Host ''
    Write-Host "SETUP FAILED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "At: $($_.InvocationInfo.ScriptName):$($_.InvocationInfo.ScriptLineNumber)" -ForegroundColor Red
    Stop-SetupTranscript
    Read-Host 'Press Enter to close'
    break
}
try { Start-Transcript -Path $transcript -Force | Out-Null } catch { }

function Test-Administrator {
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    Stop-SetupTranscript
    $arguments = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"",
                   '-RepoPath', "`"$RepoPath`"", '-OwnerAccount', $OwnerAccount, '-RunnerName', $RunnerName)
    if ($ResetPassword) { $arguments += '-ResetPassword' }
    Start-Process -FilePath powershell.exe -ArgumentList $arguments -Verb RunAs -Wait
    exit
}

$RepoPath = (Resolve-Path -LiteralPath $RepoPath).Path
$registryPath = Join-Path $RepoPath '.claude\agent-identities.json'
$keyDir = Join-Path $DataRoot 'agent-keys'
$sessionDir = Join-Path $DataRoot 'sessions'
$sshKeygen = Join-Path $env:SystemRoot 'System32\OpenSSH\ssh-keygen.exe'

Write-Host "Repository:    $RepoPath"
Write-Host "Owner account: $OwnerAccount"
Write-Host "Agent account: $RunnerName"
Write-Host "Data root:     $DataRoot"

# 1. Agent account -------------------------------------------------------------
$runner = Get-LocalUser -Name $RunnerName -ErrorAction SilentlyContinue
if (-not $runner) {
    $bytes = New-Object byte[] 24
    [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $plain = [Convert]::ToBase64String($bytes)
    $secure = ConvertTo-SecureString $plain -AsPlainText -Force
    New-LocalUser -Name $RunnerName -Password $secure -PasswordNeverExpires -UserMayNotChangePassword `
        -Description 'Runs 9dot5dotA1 agent sessions (ADR-0017)' | Out-Null
    Add-LocalGroupMember -Group 'Users' -Member $RunnerName
    Show-OnceSecret -Value $plain -Caption "Account '$RunnerName' created. Password (shown once):"
} elseif ($ResetPassword) {
    $bytes = New-Object byte[] 24
    [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $plain = [Convert]::ToBase64String($bytes)
    Set-LocalUser -Name $RunnerName -Password (ConvertTo-SecureString $plain -AsPlainText -Force)
    Show-OnceSecret -Value $plain -Caption "New password for '$RunnerName' (shown once):"
} else {
    Write-Host "Account '$RunnerName' already exists; password unchanged."
}

# 2. Data folder: owner full control, agent read-only -------------------------
New-Item -ItemType Directory -Force -Path $keyDir, $sessionDir | Out-Null
& icacls $DataRoot /inheritance:r `
    /grant "${OwnerAccount}:(OI)(CI)F" "SYSTEM:(OI)(CI)F" "Administrators:(OI)(CI)F" "${RunnerName}:(OI)(CI)RX" | Out-Null
if ($LASTEXITCODE -ne 0) { throw "icacls failed on $DataRoot" }

# 3. Repository permissions ----------------------------------------------------
$profileDir = Join-Path $env:SystemDrive "Users\$OwnerAccount"
& icacls $profileDir /grant "${RunnerName}:(X)" | Out-Null          # traverse only, this folder
& icacls $RepoPath /grant "${RunnerName}:(OI)(CI)M" | Out-Null      # work in the repository
if ($LASTEXITCODE -ne 0) { throw "icacls failed on $RepoPath" }

$denyWrite = "${RunnerName}:(WD,AD,WEA,WA,DE)"
$denyWriteTree = "${RunnerName}:(OI)(CI)(WD,AD,WEA,WA,DE,DC)"
foreach ($folder in @('.claude', 'scripts', '.git\hooks')) {
    $path = Join-Path $RepoPath $folder
    if (Test-Path -LiteralPath $path) { & icacls $path /deny $denyWriteTree | Out-Null }
}
foreach ($file in @('CLAUDE.md', 'CODEOWNERS', 'LICENSE', '.git\config')) {
    $path = Join-Path $RepoPath $file
    if (Test-Path -LiteralPath $path) { & icacls $path /deny $denyWrite | Out-Null }
}
Write-Host 'Repository permissions set: agent may modify the repository, not .claude, scripts, .git\hooks, .git\config, CLAUDE.md, CODEOWNERS or LICENSE.'

# 4. Per-agent signing keys and registry ---------------------------------------
$registry = Get-Content -Raw -LiteralPath $registryPath | ConvertFrom-Json
$allowed = @()
foreach ($property in $registry.agents.PSObject.Properties) {
    $name = $property.Name
    $identity = $property.Value
    $keyPath = Join-Path $keyDir "${name}_ed25519"
    if (-not (Test-Path -LiteralPath $keyPath)) {
        & cmd.exe /c "`"$sshKeygen`" -q -t ed25519 -N `"`" -C `"$($identity.git_name)`" -f `"$keyPath`""
        if ($LASTEXITCODE -ne 0) { throw "ssh-keygen failed for $name" }
    }
    $publicKey = (Get-Content -LiteralPath "$keyPath.pub" -Raw).Trim()
    if (-not $identity.git_email) {
        # Reserved .invalid domain: a label for attribution, not a mailbox.
        $identity | Add-Member -NotePropertyName git_email -NotePropertyValue "$name@agents.9dot5dotA1.invalid" -Force
    }
    $identity | Add-Member -NotePropertyName signing_key -NotePropertyValue $keyPath -Force
    $identity | Add-Member -NotePropertyName public_key -NotePropertyValue $publicKey -Force
    $allowed += "$($identity.git_email) namespaces=`"git`" $publicKey"
}

$registry | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $registryPath -Encoding utf8
Set-Content -LiteralPath (Join-Path $RepoPath '.claude\allowed_signers') -Value $allowed -Encoding ascii
Write-Host "Keys: $keyDir (one per agent). Public keys written to .claude\agent-identities.json and .claude\allowed_signers."

# 5. Monitoring destination (no secret in this file) ----------------------------
$sinkConfig = Join-Path $DataRoot 'audit-sink.json'
if (-not (Test-Path -LiteralPath $sinkConfig)) {
    $template = [ordered]@{
        kind       = ''                                   # json | elastic | dynatrace
        url        = ''                                   # ingest endpoint of the chosen backend
        token_file = (Join-Path $DataRoot 'audit-sink.token')   # write-only ingest token, one line
        index      = 'agent-audit'                        # elastic only
    }
    $template | ConvertTo-Json | Set-Content -LiteralPath $sinkConfig -Encoding utf8
    Write-Host "Monitoring destination template written to $sinkConfig. Agents stay blocked until it is filled in."
}

Write-Host ''
Write-Host 'Done. Next steps are in operations/AGENT_IDENTITIES.md (Claude login for the agent account, GitHub Apps, monitoring sink).'
Stop-SetupTranscript
Read-Host 'Press Enter to close'
