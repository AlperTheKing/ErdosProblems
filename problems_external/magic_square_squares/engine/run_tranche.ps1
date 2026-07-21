[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [switch] $Launch,

    [Parameter(Mandatory = $false)]
    [string] $Python = "python"
)

$ErrorActionPreference = "Stop"
$engineDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$supervisor = Join-Path $engineDir "tranche_supervisor.py"
$logsDir = Join-Path $engineDir "logs"
$runDir = Join-Path $logsDir "tranche64-frozen-manifest-v1"

if (-not $Launch) {
    throw "Production launch requires the explicit -Launch switch."
}
if (Test-Path -LiteralPath $runDir) {
    throw "Canonical run directory already exists: $runDir"
}
if (-not (Test-Path -LiteralPath $supervisor -PathType Leaf)) {
    throw "Supervisor is missing: $supervisor"
}

$pythonCommand = Get-Command $Python -ErrorAction Stop
$null = & $pythonCommand.Source $supervisor --run-dir $runDir --preflight-only
if ($LASTEXITCODE -ne 0) {
    throw "Frozen tranche preflight failed."
}
$startInfo = [System.Diagnostics.ProcessStartInfo]::new()
$startInfo.FileName = $pythonCommand.Source
$startInfo.UseShellExecute = $false
$startInfo.CreateNoWindow = $true
$startInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
$startInfo.WorkingDirectory = $engineDir
$null = $startInfo.ArgumentList.Add($supervisor)
$null = $startInfo.ArgumentList.Add("--run-dir")
$null = $startInfo.ArgumentList.Add($runDir)

$process = [System.Diagnostics.Process]::Start($startInfo)
if ($null -eq $process) {
    throw "Failed to start tranche supervisor."
}

[pscustomobject]@{
    SupervisorPid = $process.Id
    RunDir = $runDir
    DurationSeconds = 28800
    WorkerCap = 64
}
