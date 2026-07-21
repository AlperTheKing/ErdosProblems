param(
  [Parameter(Mandatory = $true)] [string] $RunDir,
  [int] $N = 26,
  [int] $K = 13,
  [ValidateRange(2, 64)] [int] $Threads = 64,
  [int] $Seconds = 3600,
  [int] $Samples = 48,
  [UInt64] $Seed = 260100,
  [switch] $BalancedParity
)

$ErrorActionPreference = 'Stop'
$engineDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$targetDir = [System.IO.Path]::GetFullPath($RunDir)
$exe = Join-Path $engineDir 'local_search.exe'
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
  '--samples', $Samples,
  '--seed', $Seed
)
if ($BalancedParity) { $arguments += '--balanced-parity' }

$started = Get-Date
$process = Start-Process -FilePath $exe -ArgumentList $arguments `
  -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath `
  -WindowStyle Hidden -PassThru -Wait
$finished = Get-Date

$resultLine = Get-Content -LiteralPath $stdoutPath -Tail 1
if ([string]::IsNullOrWhiteSpace($resultLine)) {
  throw "local search emitted no result line; see $stderrPath"
}
$result = $resultLine | ConvertFrom-Json
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
  schema = 'queen-domination-local-run-v1'
  started = $started.ToString('o')
  finished = $finished.ToString('o')
  run_dir = $targetDir
  parameters = [ordered]@{
    n = $N
    k = $K
    threads = $Threads
    seconds = $Seconds
    samples = $Samples
    seed = $Seed
    balanced_parity = [bool]$BalancedParity
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
