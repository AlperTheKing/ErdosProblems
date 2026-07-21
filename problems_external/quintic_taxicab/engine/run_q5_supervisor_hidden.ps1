param(
    [Parameter(Mandatory = $true)][string]$Python,
    [Parameter(Mandatory = $true)][string]$Manifest,
    [Parameter(Mandatory = $true)][string]$Authorization,
    [Parameter(Mandatory = $true)][ValidatePattern('^[0-9a-f]{64}$')][string]$ExpectedDigest,
    [Parameter(Mandatory = $true)][ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$')][string]$CampaignId,
    [Parameter(Mandatory = $true)][ValidateSet('CALIBRATION_ONLY', 'SELECTED_MAIN')][string]$Mode,
    [Parameter(Mandatory = $true)][ValidateSet('canonical_positive_u_positive_y', 'audit_signed_u_both_y')][string]$SearchMode,
    [ValidateRange(20, 5000)][int]$PollMs = 200,
    [switch]$Launch
)

$ErrorActionPreference = 'Stop'
if (-not $Launch) {
    throw 'Refusing to start: pass -Launch with the exact hash-pinned campaign parameters.'
}

$pythonPath = (Resolve-Path -LiteralPath $Python).Path
$authorizationPath = (Resolve-Path -LiteralPath $Authorization).Path
$manifestPath = (Resolve-Path -LiteralPath $Manifest).Path
$supervisorPath = Join-Path -Path $PSScriptRoot -ChildPath 'q5_supervisor.py'
$supervisorPath = (Resolve-Path -LiteralPath $supervisorPath).Path

try {
    $manifestEnvelope = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
} catch {
    throw "Cannot parse the hash-pinned manifest before launch: $($_.Exception.Message)"
}
if ([string]$manifestEnvelope.payload_sha256 -cne $ExpectedDigest) {
    throw 'Manifest envelope digest does not match -ExpectedDigest.'
}
try {
    $authorization = Get-Content -Raw -LiteralPath $authorizationPath | ConvertFrom-Json
} catch {
    throw "Cannot parse the launch authorization before launch: $($_.Exception.Message)"
}
$phase = [string]$authorization.phase
if ($phase -notin @('A', 'B', 'C', 'D', 'MAIN')) {
    throw 'Launch authorization phase is invalid.'
}
$fixedAuthorization = Join-Path $PSScriptRoot "logs\q5-eight-hour-tranche-v1\authorizations\$phase.json"
$fixedAuthorization = (Resolve-Path -LiteralPath $fixedAuthorization).Path
if (-not [System.StringComparer]::OrdinalIgnoreCase.Equals($authorizationPath, $fixedAuthorization)) {
    throw 'Launch authorization path is not the fixed phase path.'
}
if (-not [System.StringComparer]::OrdinalIgnoreCase.Equals(
    (Resolve-Path -LiteralPath ([string]$authorization.manifest_path)).Path, $manifestPath
)) {
    throw 'Launch authorization manifest path does not match -Manifest.'
}
$manifestFileDigest = (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ([string]$authorization.manifest_file_sha256 -cne $manifestFileDigest -or
    [string]$authorization.manifest_payload_sha256 -cne $ExpectedDigest) {
    throw 'Launch authorization manifest hash binding mismatch.'
}

if ([string]$manifestEnvelope.payload.campaign_id -cne $CampaignId) {
    throw 'Manifest campaign id does not match -CampaignId.'
}
if ([string]$manifestEnvelope.payload.mode -cne $Mode) {
    throw 'Manifest mode does not match -Mode.'
}
if ([string]$manifestEnvelope.payload.search_mode -cne $SearchMode) {
    throw 'Manifest search mode does not match -SearchMode.'
}

function Assert-PinnedRuntimeFile {
    param([string]$Role, [string]$ActualPath, [object]$Record)
    $recordedPath = (Resolve-Path -LiteralPath ([string]$Record.path)).Path
    if (-not [System.StringComparer]::OrdinalIgnoreCase.Equals($ActualPath, $recordedPath)) {
        throw "Runtime $Role path does not match the manifest artifact."
    }
    $item = Get-Item -LiteralPath $ActualPath
    $digest = (Get-FileHash -LiteralPath $ActualPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ([int64]$Record.size -ne $item.Length -or [string]$Record.sha256 -cne $digest) {
        throw "Runtime $Role hash does not match the manifest artifact."
    }
}

Assert-PinnedRuntimeFile -Role 'python_interpreter' -ActualPath $pythonPath -Record $manifestEnvelope.payload.artifacts.python_interpreter
Assert-PinnedRuntimeFile -Role 'supervisor' -ActualPath $supervisorPath -Record $manifestEnvelope.payload.artifacts.supervisor

$startInfo = [System.Diagnostics.ProcessStartInfo]::new()
$startInfo.FileName = $pythonPath
$startInfo.UseShellExecute = $false
$startInfo.CreateNoWindow = $true
$startInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
$arguments = @(
    $supervisorPath,
    '--manifest', $manifestPath,
    '--expected-digest', $ExpectedDigest,
    '--expected-campaign-id', $CampaignId,
    '--expected-mode', $Mode,
    '--expected-search-mode', $SearchMode,
    '--authorization', $authorizationPath,
    '--poll-ms', [string]$PollMs,
    '--launch'
)
foreach ($argument in $arguments) {
    [void]$startInfo.ArgumentList.Add($argument)
}

$process = [System.Diagnostics.Process]::Start($startInfo)
if ($null -eq $process) {
    throw 'Failed to start the hidden Q5 supervisor.'
}
[pscustomobject]@{
    supervisor_pid = $process.Id
    manifest = $manifestPath
    authorization = $authorizationPath
    expected_digest = $ExpectedDigest
    campaign_id = $CampaignId
}
