param(
  [Parameter(Mandatory = $true)] [string] $RunDir,
  [DateTimeOffset] $Deadline = [DateTimeOffset]::Parse('2026-07-19T22:20:00+03:00'),
  [ValidateRange(1, 64)] [int] $CadicalLanes = 48,
  [ValidateRange(0, 64)] [int] $GlucoseLanes = 16,
  [int] $BaseSeed = 261000
)

$ErrorActionPreference = 'Stop'
if ($CadicalLanes + $GlucoseLanes -ne 64) {
  throw 'The portfolio must contain exactly 64 single-threaded solver lanes.'
}

$engineDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$targetDir = [System.IO.Path]::GetFullPath($RunDir)
$script = Join-Path $engineDir 'pysat_search.py'
$verifyDir = Join-Path (Split-Path -Parent $engineDir) 'verify'
$scalar = Join-Path $verifyDir 'scalar_verify.py'
$bitset = Join-Path $verifyDir 'bitset_verify.py'
$python = (Get-Command python).Source
$statePath = Join-Path $targetDir 'portfolio_state.json'
$summaryPath = Join-Path $targetDir 'portfolio_summary.json'
$candidatePath = Join-Path $targetDir 'verified_candidate.json'
$dimacsPath = Join-Path $targetDir 'q26_k13_atmost_hilbert_mtotalizer.cnf'
$proofPath = Join-Path $targetDir 'q26_k13_atmost_hilbert_mtotalizer.drup'

New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
if (Test-Path -LiteralPath $statePath) {
  throw "portfolio already initialized: $statePath"
}

$lanes = [System.Collections.Generic.List[object]]::new()

function Write-State([string] $status, [object] $extra) {
  $state = [ordered]@{
    schema = 'q26-unrestricted-sat-portfolio-v1'
    status = $status
    run_dir = $targetDir
    deadline = $Deadline.ToString('o')
    updated = [DateTimeOffset]::Now.ToString('o')
    lanes = @($lanes | ForEach-Object {
      [ordered]@{
        lane = $_.Lane
        solver = $_.Solver
        seed = $_.Seed
        pid = $_.Process.Id
        exited = $_.Process.HasExited
        exit_code = if ($_.Process.HasExited) { $_.Process.ExitCode } else { $null }
        model_json = $_.ModelJson
      }
    })
    extra = $extra
  }
  $state | ConvertTo-Json -Depth 6 | Out-File -LiteralPath $statePath -Encoding utf8
}

function Stop-Lanes {
  foreach ($lane in $lanes) {
    if (-not $lane.Process.HasExited) {
      Stop-Process -Id $lane.Process.Id -Force -ErrorAction SilentlyContinue
    }
  }
}

try {
  for ($index = 1; $index -le 64; ++$index) {
    $solver = if ($index -le $CadicalLanes) { 'cadical195' } else { 'glucose42' }
    $seed = $BaseSeed + $index
    $tag = '{0:D2}-{1}-s{2}' -f $index, $solver, $seed
    $modelJson = Join-Path $targetDir "$tag.json"
    $arguments = @(
      $script,
      '--n', '26',
      '--k', '13',
      '--encoding', 'mtotalizer',
      '--ordering', 'hilbert',
      '--solver', $solver,
      '--seed', [string]$seed,
      '--_solve-direct',
      '--model-json', $modelJson
    )
    if ($index -eq 1) {
      $arguments += @('--dimacs', $dimacsPath, '--proof', $proofPath)
    }
    $process = Start-Process -FilePath $python -ArgumentList $arguments `
      -RedirectStandardOutput (Join-Path $targetDir "$tag.stdout.txt") `
      -RedirectStandardError (Join-Path $targetDir "$tag.stderr.txt") `
      -WindowStyle Hidden -PassThru
    $lanes.Add([pscustomobject]@{
      Lane = $index
      Solver = $solver
      Seed = $seed
      Process = $process
      ModelJson = $modelJson
    })
  }
} catch {
  Stop-Lanes
  throw
}

Write-State 'RUNNING' @{ message = '64 unrestricted at-most-13 lanes launched' }
$seen = [System.Collections.Generic.HashSet[string]]::new()

while ([DateTimeOffset]::Now -lt $Deadline) {
  foreach ($lane in $lanes) {
    if (-not (Test-Path -LiteralPath $lane.ModelJson)) { continue }
    if (-not $seen.Add($lane.ModelJson)) { continue }
    try {
      $result = Get-Content -LiteralPath $lane.ModelJson -Raw | ConvertFrom-Json
    } catch {
      $seen.Remove($lane.ModelJson) | Out-Null
      continue
    }

    if ($result.status -eq 'SAT' -and $result.independent_model_check) {
      $candidate = [ordered]@{
        schema = 'queen-domination-candidate-v1'
        n = 26
        k = 13
        status = 'SAT'
        coordinates = $result.queens
        source_lane = $lane.Lane
        source_solver = $lane.Solver
        source_seed = $lane.Seed
      }
      $candidate | ConvertTo-Json -Depth 5 | Out-File -LiteralPath $candidatePath -Encoding utf8

      $scalarOutput = & $python $scalar $candidatePath --expect 13 2>&1
      $scalarExit = $LASTEXITCODE
      $scalarOutput | Out-File -LiteralPath (Join-Path $targetDir 'scalar_verify.txt') -Encoding utf8
      $bitsetOutput = & $python $bitset $candidatePath --expect 13 2>&1
      $bitsetExit = $LASTEXITCODE
      $bitsetOutput | Out-File -LiteralPath (Join-Path $targetDir 'bitset_verify.txt') -Encoding utf8

      if ($scalarExit -eq 0 -and $bitsetExit -eq 0) {
        Stop-Lanes
        $summary = [ordered]@{
          schema = 'q26-unrestricted-sat-portfolio-summary-v1'
          status = 'SAT'
          independently_verified = $true
          winning_lane = $lane.Lane
          solver = $lane.Solver
          seed = $lane.Seed
          candidate = $candidatePath
          scalar_exit_code = $scalarExit
          bitset_exit_code = $bitsetExit
          finished = [DateTimeOffset]::Now.ToString('o')
        }
        $summary | ConvertTo-Json -Depth 5 | Out-File -LiteralPath $summaryPath -Encoding utf8
        Write-State 'SAT_VERIFIED' $summary
        exit 0
      }
      Stop-Lanes
      Write-State 'SAT_VERIFIER_DISAGREEMENT' @{
        lane = $lane.Lane
        scalar_exit_code = $scalarExit
        bitset_exit_code = $bitsetExit
      }
      exit 3
    }
  }

  if (@($lanes | Where-Object { -not $_.Process.HasExited }).Count -eq 0) {
    $laneOne = Get-Content -LiteralPath $lanes[0].ModelJson -Raw -ErrorAction SilentlyContinue |
      ConvertFrom-Json -ErrorAction SilentlyContinue
    $status = if ($laneOne.status -eq 'UNSAT' -and (Test-Path -LiteralPath $proofPath)) {
      'UNSAT_PROOF_UNCHECKED'
    } else {
      'NO_HIT'
    }
    $summary = [ordered]@{
      schema = 'q26-unrestricted-sat-portfolio-summary-v1'
      status = $status
      independently_verified = $false
      proof_check = 'NOT_RUN'
      finished = [DateTimeOffset]::Now.ToString('o')
    }
    $summary | ConvertTo-Json -Depth 5 | Out-File -LiteralPath $summaryPath -Encoding utf8
    Write-State $status $summary
    exit 2
  }

  Write-State 'RUNNING' @{ completed_lanes = $seen.Count }
  Start-Sleep -Seconds 5
}

Stop-Lanes
$deadlineSummary = [ordered]@{
  schema = 'q26-unrestricted-sat-portfolio-summary-v1'
  status = 'NO_HIT'
  reason = 'global deadline reached without a verified final certificate'
  independently_verified = $false
  proof_check = 'NOT_RUN'
  finished = [DateTimeOffset]::Now.ToString('o')
}
$deadlineSummary | ConvertTo-Json -Depth 5 | Out-File -LiteralPath $summaryPath -Encoding utf8
Write-State 'NO_HIT' $deadlineSummary
exit 2
