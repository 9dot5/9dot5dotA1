#Requires -Version 5.1
<#
.SYNOPSIS
Applies this repository's Ansible configuration to the local host with ansible-pull (ADR-0025).

.DESCRIPTION
Run on the host itself (PC Alentejo), from a clone of this repository. It:
  - creates C:\ProgramData\9dot5dotA1\monitoring and \monitoring-secrets (secrets: owner, SYSTEM and Administrators only);
  - creates any missing password file with a random value; values are never printed;
  - builds the Ansible runner image from ansible\runner;
  - in that image, clones the branch and runs ansible-playbook against the host's Podman. This is the
    pull model of ADR-0025, the same as ansible-pull, written out so each step is visible.

The first run is a break-glass session under ADR-0033: record it in the access register.

.PARAMETER Branch
Branch to apply. Default: main.

.PARAMETER Rebuild
Rebuild the runner image even if it exists.
#>
[CmdletBinding()]
param(
    [string]$RepoUrl = 'https://github.com/9dot5/9dot5dotA1.git',
    [string]$Branch = 'main',
    [switch]$Rebuild
)

$ErrorActionPreference = 'Stop'
$runnerImage = 'localhost/9dot5-ansible-runner:2.21.5'
$dataRoot = Join-Path $env:ProgramData '9dot5dotA1'
$configDir = Join-Path $dataRoot 'monitoring'
$secretsDir = Join-Path $dataRoot 'monitoring-secrets'
# The same folders as the Podman machine sees them.
$configDirVm = '/mnt/c/ProgramData/9dot5dotA1/monitoring'
$secretsDirVm = '/mnt/c/ProgramData/9dot5dotA1/monitoring-secrets'

if (-not (Get-Command podman -ErrorAction SilentlyContinue)) { throw 'podman is not installed.' }
& podman info --format '{{.Host.Arch}}' | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'The Podman machine is not running. Start it with: podman machine start' }

# 1. Folders ---------------------------------------------------------------------
New-Item -ItemType Directory -Force -Path $configDir, $secretsDir | Out-Null
& icacls $secretsDir /inheritance:r /grant "${env:USERNAME}:(OI)(CI)F" 'SYSTEM:(OI)(CI)F' 'Administrators:(OI)(CI)F' | Out-Null
if ($LASTEXITCODE -ne 0) { throw "icacls failed on $secretsDir" }

# 2. Passwords (created once, never printed) -------------------------------------
foreach ($name in 'elastic_password', 'kibana_system_password', 'grafana_admin_password') {
    $path = Join-Path $secretsDir $name
    if (-not (Test-Path -LiteralPath $path)) {
        $bytes = New-Object byte[] 24
        [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
        $value = [Convert]::ToBase64String($bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
        [IO.File]::WriteAllText($path, $value)
        Write-Host "Created $name in $secretsDir."
    }
}

# 3. Network the runner joins to reach Elasticsearch -----------------------------
& podman network exists monitoring
if ($LASTEXITCODE -ne 0) {
    & podman network create monitoring | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'podman network create failed' }
}

# 4. Runner image ----------------------------------------------------------------
& podman image exists $runnerImage
if ($Rebuild -or $LASTEXITCODE -ne 0) {
    & podman build -t $runnerImage (Join-Path $PSScriptRoot '..\runner')
    if ($LASTEXITCODE -ne 0) { throw 'podman build of the runner failed' }
}

# 5. ansible-pull ----------------------------------------------------------------
# podman info returns a URL (unix:///run/podman/podman.sock); a bind mount needs the bare path.
$socket = (& podman info --format '{{.Host.RemoteSocket.Path}}').Trim() -replace '^unix://', ''
if (-not $socket) { throw 'Could not find the Podman socket path.' }

& podman run --rm --network monitoring `
    -v "${socket}:/run/podman/podman.sock" `
    -v "${configDirVm}:${configDirVm}" `
    -v "${secretsDirVm}:${secretsDirVm}" `
    -e ANSIBLE_CONFIG=/work/repo/ansible/ansible.cfg `
    -e "REPO_URL=$RepoUrl" -e "REPO_BRANCH=$Branch" `
    $runnerImage `
    sh -c 'git clone --quiet --depth 1 --branch "$REPO_BRANCH" "$REPO_URL" /work/repo && cd /work/repo/ansible && ansible-playbook --limit alentejo site.yml'
if ($LASTEXITCODE -ne 0) { throw "The Ansible run failed with exit code $LASTEXITCODE" }

Write-Host ''
Write-Host 'Done. Kibana http://127.0.0.1:5601 (user elastic), Grafana http://127.0.0.1:3000 (user admin).'
Write-Host "Passwords are the files in $secretsDir. The audit ingest key is $secretsDir\audit-sink.token."
