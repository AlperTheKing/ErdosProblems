param(
    [Parameter(Mandatory = $true)][string]$RunDir,
    [Parameter(Mandatory = $true)][string]$CnfPath,
    [Parameter(Mandatory = $true)][string]$SolverPath
)

$ErrorActionPreference = 'Stop'
$run = [System.IO.Path]::GetFullPath($RunDir)
$cnf = [System.IO.Path]::GetFullPath($CnfPath)
$solver = [System.IO.Path]::GetFullPath($SolverPath)

New-Item -ItemType Directory -Force -Path $run | Out-Null
$started = [DateTimeOffset]::Now
$state = [ordered]@{
    status = 'RUNNING'
    started_at = $started.ToString('o')
    wrapper_pid = $PID
    cnf = $cnf
    solver = $solver
    command = @('--no-colors', '--binary=false', '--check=1', '-w', (Join-Path $run 'solution.txt'), $cnf, (Join-Path $run 'proof.drat'))
}
$state | ConvertTo-Json -Depth 4 | Set-Content -Encoding ascii -LiteralPath (Join-Path $run 'state.json')

& $solver --no-colors --binary=false --check=1 -w (Join-Path $run 'solution.txt') $cnf (Join-Path $run 'proof.drat') 1> (Join-Path $run 'stdout.txt') 2> (Join-Path $run 'stderr.txt')
$exit = $LASTEXITCODE
$finished = [DateTimeOffset]::Now
$status = if ($exit -eq 10) { 'SAT_UNVERIFIED' } elseif ($exit -eq 20) { 'UNSAT_PROOF_UNCHECKED' } else { 'FAILED_OR_INTERRUPTED' }
$summary = [ordered]@{
    status = $status
    exit_code = $exit
    started_at = $started.ToString('o')
    finished_at = $finished.ToString('o')
    elapsed_seconds = [math]::Round(($finished - $started).TotalSeconds, 3)
    solution = (Join-Path $run 'solution.txt')
    proof = (Join-Path $run 'proof.drat')
    stdout = (Join-Path $run 'stdout.txt')
    stderr = (Join-Path $run 'stderr.txt')
}
$summary | ConvertTo-Json -Depth 4 | Set-Content -Encoding ascii -LiteralPath (Join-Path $run 'summary.json')
$state.status = $status
$state.finished_at = $finished.ToString('o')
$state.exit_code = $exit
$state | ConvertTo-Json -Depth 4 | Set-Content -Encoding ascii -LiteralPath (Join-Path $run 'state.json')
