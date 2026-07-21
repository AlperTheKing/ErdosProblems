[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Cnf,

    [Parameter(Mandatory = $true)]
    [string]$RunDir,

    [Parameter(Mandatory = $true)]
    [ValidateRange(1, 86400)]
    [int]$Seconds,

    [string]$Cadical = (Join-Path $PSScriptRoot '..\..\..\third_party\cadical\build\cadical.exe'),

    [string]$ExpectedCnfSha256 = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-AtomicJson {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object]$Value
    )
    $temporary = "$Path.tmp-$PID"
    $Value | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $temporary -Encoding utf8
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

$cnfPath = (Resolve-Path -LiteralPath $Cnf).Path
$cadicalPath = (Resolve-Path -LiteralPath $Cadical).Path
$actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $cnfPath).Hash.ToUpperInvariant()
if ($ExpectedCnfSha256 -and $actualHash -ne $ExpectedCnfSha256.ToUpperInvariant()) {
    throw "CNF SHA-256 mismatch: expected $ExpectedCnfSha256, found $actualHash"
}

$logsRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'logs'))
$runPath = [IO.Path]::GetFullPath($RunDir)
$logsPrefix = $logsRoot.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
if (-not $runPath.StartsWith($logsPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw "RunDir must be a child of $logsRoot"
}
if (Test-Path -LiteralPath $runPath) {
    if ((Get-ChildItem -LiteralPath $runPath -Force | Measure-Object).Count -ne 0) {
        throw "RunDir already exists and is not empty: $runPath"
    }
} else {
    New-Item -ItemType Directory -Path $runPath | Out-Null
}

$stdoutPath = Join-Path $runPath 'solver.stdout.txt'
$stderrPath = Join-Path $runPath 'solver.stderr.txt'
$solutionPath = Join-Path $runPath 'solution.txt'
$proofPath = Join-Path $runPath 'proof.drat'
$statePath = Join-Path $runPath 'state.json'
$summaryPath = Join-Path $runPath 'summary.json'
$started = Get-Date
$deadline = $started.AddSeconds($Seconds)

$arguments = @(
    '-w', ('"{0}"' -f $solutionPath),
    ('"{0}"' -f $cnfPath),
    ('"{0}"' -f $proofPath)
)
$process = Start-Process -FilePath $cadicalPath -ArgumentList $arguments `
    -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath `
    -NoNewWindow -PassThru

Write-AtomicJson -Path $statePath -Value ([ordered]@{
    schema = 'ssnc-cycle19-cadical-run-v1'
    status = 'RUNNING'
    wrapper_pid = $PID
    solver_pid = $process.Id
    started_at = $started.ToString('o')
    deadline = $deadline.ToString('o')
    seconds = $Seconds
    cnf = $cnfPath
    cnf_sha256 = $actualHash
    cadical = $cadicalPath
    stdout = $stdoutPath
    stderr = $stderrPath
    solution = $solutionPath
    proof = $proofPath
})

$timedOut = $false
while (-not $process.HasExited) {
    if ((Get-Date) -ge $deadline) {
        Stop-Process -Id $process.Id -Force
        $timedOut = $true
        break
    }
    Start-Sleep -Seconds 1
    $process.Refresh()
}
$process.WaitForExit()
$finished = Get-Date
$exitCode = $process.ExitCode

if ($timedOut) {
    $status = 'TIMEOUT'
} elseif ($exitCode -eq 10) {
    $status = 'SAT_UNVERIFIED'
} elseif ($exitCode -eq 20) {
    $status = 'UNSAT_PROOF_UNCHECKED'
} else {
    $status = 'FAILED'
}

$summary = [ordered]@{
    schema = 'ssnc-cycle19-cadical-run-v1'
    status = $status
    independently_verified = $false
    solver_exit_code = $exitCode
    wrapper_pid = $PID
    solver_pid = $process.Id
    started_at = $started.ToString('o')
    finished_at = $finished.ToString('o')
    elapsed_seconds = [Math]::Round(($finished - $started).TotalSeconds, 3)
    deadline = $deadline.ToString('o')
    cnf = $cnfPath
    cnf_sha256 = $actualHash
    stdout = $stdoutPath
    stdout_bytes = if (Test-Path -LiteralPath $stdoutPath) { (Get-Item -LiteralPath $stdoutPath).Length } else { 0 }
    stderr = $stderrPath
    stderr_bytes = if (Test-Path -LiteralPath $stderrPath) { (Get-Item -LiteralPath $stderrPath).Length } else { 0 }
    solution = $solutionPath
    solution_bytes = if (Test-Path -LiteralPath $solutionPath) { (Get-Item -LiteralPath $solutionPath).Length } else { 0 }
    proof = $proofPath
    proof_bytes = if (Test-Path -LiteralPath $proofPath) { (Get-Item -LiteralPath $proofPath).Length } else { 0 }
}
Write-AtomicJson -Path $summaryPath -Value $summary
Write-AtomicJson -Path $statePath -Value $summary
$summary | ConvertTo-Json -Depth 8 -Compress

if ($status -eq 'FAILED') {
    exit 1
}
if ($status -eq 'TIMEOUT') {
    exit 124
}
exit 0
