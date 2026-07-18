param(
    [Parameter(Mandatory = $true)][string]$Config,
    [int]$Seconds = 10,
    [string]$Tag = "single"
)

$ErrorActionPreference = "Stop"
$engineDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$exe = Join-Path $engineDir "SorterHunter\SorterHunter.exe"
$configPath = Join-Path $engineDir $Config
$logDir = Join-Path $engineDir "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$stamp = Get-Date -Format "yyyyMMddTHHmmssfff"
$stdoutPath = Join-Path $logDir "$Tag-$stamp.out.log"
$stderrPath = Join-Path $logDir "$Tag-$stamp.err.log"

$watch = [Diagnostics.Stopwatch]::StartNew()
$process = Start-Process -FilePath $exe -ArgumentList $configPath `
    -WorkingDirectory (Split-Path -Parent $exe) -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
$finished = $process.WaitForExit($Seconds * 1000)
if (-not $finished) {
    Stop-Process -Id $process.Id -Force
    $process.WaitForExit()
}
$watch.Stop()

$lines = if (Test-Path $stdoutPath) { Get-Content $stdoutPath } else { @() }
$reports = $lines | Select-String -Pattern 'Iteration ([0-9]+).*?([0-9]+(?:\.[0-9]+)?) it/s'
$lastReport = $reports | Select-Object -Last 1
$iteration = $null
$ips = $null
if ($lastReport -and $lastReport.Matches.Count -gt 0) {
    $iteration = [UInt64]$lastReport.Matches[0].Groups[1].Value
    $ips = [double]$lastReport.Matches[0].Groups[2].Value
}
$lengths = foreach ($line in $lines) {
    if ($line -match "'L':([0-9]+)") { [int]$Matches[1] }
}
$minimumLength = if ($lengths) { ($lengths | Measure-Object -Minimum).Minimum } else { $null }

[ordered]@{
    tag = $Tag
    config = $configPath
    requested_seconds = $Seconds
    wall_seconds = [Math]::Round($watch.Elapsed.TotalSeconds, 3)
    stopped_at_limit = -not $finished
    exit_code = if ($finished) { $process.ExitCode } else { $null }
    last_reported_iteration = $iteration
    last_reported_iterations_per_second = $ips
    minimum_emitted_length = $minimumLength
    stdout = $stdoutPath
    stderr = $stderrPath
} | ConvertTo-Json -Compress
