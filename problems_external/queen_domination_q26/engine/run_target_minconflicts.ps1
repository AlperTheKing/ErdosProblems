param(
  [Parameter(Mandatory = $true)] [string] $RunDir,
  [int] $N = 26,
  [int] $K = 13,
  [ValidateRange(1, 64)] [int] $Threads = 64,
  [int] $Seconds = 3600,
  [UInt64] $Seed = 261000,
  [switch] $BalancedParity,
  [switch] $AuditDeltas
)

$ErrorActionPreference = 'Stop'
$engineDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$targetDir = [System.IO.Path]::GetFullPath($RunDir)
$exe = Join-Path $engineDir 'local_search_minconflicts.exe'
$verifyDir = Join-Path (Split-Path -Parent $engineDir) 'verify'
$scalar = Join-Path $verifyDir 'scalar_verify.py'
$bitset = Join-Path $verifyDir 'bitset_verify.py'

New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
$stdoutPath = Join-Path $targetDir 'stdout.jsonl'
$stderrPath = Join-Path $targetDir 'stderr.txt'
$candidatePath = Join-Path $targetDir 'candidate.json'
$summaryPath = Join-Path $targetDir 'summary.json'

$arguments = @(
  '--n', $N,
  '--k', $K,
  '--threads', $Threads,
  '--seconds', $Seconds,
  '--samples', 48,
  '--seed', $Seed,
  '--strategy', 'target-minconflicts'
)
if ($BalancedParity) { $arguments += '--balanced-parity' }
if ($AuditDeltas) { $arguments += '--audit-deltas' }

$started = Get-Date
$process = Start-Process -FilePath $exe -ArgumentList $arguments `
  -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath `
  -WindowStyle Hidden -PassThru -Wait
$finished = Get-Date

$resultLine = Get-Content -LiteralPath $stdoutPath -Tail 1
if ([string]::IsNullOrWhiteSpace($resultLine)) {
  throw "min-conflicts search emitted no result line; see $stderrPath"
}
$result = $resultLine | ConvertFrom-Json
if ($result.strategy -ne 'target-minconflicts') {
  throw "unexpected strategy in result: $($result.strategy)"
}
[System.IO.File]::WriteAllText($candidatePath, $resultLine + [Environment]::NewLine)

$scalarExit = $null
$bitsetExit = $null
$verified = $false
if ($result.status -eq 'SAT') {
  $scalarOutput = & python $scalar $candidatePath --expect $K 2>&1
  $scalarExit = $LASTEXITCODE
  $scalarOutput | Out-File -LiteralPath (Join-Path $targetDir 'scalar_verify.txt') -Encoding utf8

  $bitsetOutput = & python $bitset $candidatePath --expect $K 2>&1
  $bitsetExit = $LASTEXITCODE
  $bitsetOutput | Out-File -LiteralPath (Join-Path $targetDir 'bitset_verify.txt') -Encoding utf8
  $verified = ($scalarExit -eq 0 -and $bitsetExit -eq 0)
}

$summary = [ordered]@{
  schema = 'queen-domination-local-run-v2'
  started = $started.ToString('o')
  finished = $finished.ToString('o')
  run_dir = $targetDir
  parameters = [ordered]@{
    n = $N
    k = $K
    threads = $Threads
    seconds = $Seconds
    seed = $Seed
    balanced_parity = [bool]$BalancedParity
    strategy = 'target-minconflicts'
    audit_deltas = [bool]$AuditDeltas
  }
  search_exit_code = $process.ExitCode
  status = $result.status
  best_uncovered = $result.best_uncovered
  scalar_exit_code = $scalarExit
  bitset_exit_code = $bitsetExit
  independently_verified = $verified
  candidate_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $candidatePath).Hash
}
$summary | ConvertTo-Json -Depth 5 | Out-File -LiteralPath $summaryPath -Encoding utf8

if ($result.status -eq 'SAT' -and -not $verified) { exit 3 }
exit 0
