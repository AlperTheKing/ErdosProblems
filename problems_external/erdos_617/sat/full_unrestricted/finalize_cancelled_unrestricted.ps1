param(
    [Parameter(Mandatory = $true)][string]$RunDir
)

$ErrorActionPreference = 'Stop'
$run = [System.IO.Path]::GetFullPath($RunDir)
$summaryPath = Join-Path $run 'summary.json'
$statePath = Join-Path $run 'state.json'
$proofPath = Join-Path $run 'proof.drat'
$cnfPath = Join-Path (Split-Path (Split-Path $run -Parent) -Parent) 'unrestricted_k26.cnf'

$wrapperSummary = Get-Content -Raw -LiteralPath $summaryPath | ConvertFrom-Json
$state = Get-Content -Raw -LiteralPath $statePath | ConvertFrom-Json
Copy-Item -LiteralPath $summaryPath -Destination (Join-Path $run 'wrapper_summary.json') -Force

$cancelled = [ordered]@{
    status = 'CANCELLED_INCONCLUSIVE'
    reason = 'solver lane reallocated by explicit task instruction'
    mathematical_result = 'none'
    sat_found = $false
    unsat_proved = $false
    wrapper_exit_code = $wrapperSummary.exit_code
    started_at = $wrapperSummary.started_at
    finished_at = $wrapperSummary.finished_at
    elapsed_seconds = $wrapperSummary.elapsed_seconds
    wrapper_pid = $wrapperSummary.wrapper_pid
    solver_pid = $wrapperSummary.solver_pid
    cnf = $cnfPath
    cnf_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $cnfPath).Hash
    proof = $proofPath
    proof_bytes = (Get-Item -LiteralPath $proofPath).Length
    proof_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $proofPath).Hash
    proof_status = 'PARTIAL_UNCHECKED'
    stdout = $wrapperSummary.stdout
    stderr = $wrapperSummary.stderr
}
$cancelled | ConvertTo-Json -Depth 4 | Set-Content -Encoding ascii -LiteralPath $summaryPath
$state.status = 'CANCELLED_INCONCLUSIVE'
$state | ConvertTo-Json -Depth 4 | Set-Content -Encoding ascii -LiteralPath $statePath
