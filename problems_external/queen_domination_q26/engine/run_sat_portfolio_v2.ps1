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
if ([DateTimeOffset]::Now -ge $Deadline) {
  throw 'Refusing to launch a portfolio whose global deadline has expired.'
}

$engineDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$targetDir = [System.IO.Path]::GetFullPath($RunDir)
if ($targetDir -match '\s') {
  throw 'The canonical run path must not contain whitespace.'
}
$solverScript = Join-Path $engineDir 'pysat_search.py'
$verifyDir = Join-Path (Split-Path -Parent $engineDir) 'verify'
$scalar = Join-Path $verifyDir 'scalar_verify.py'
$bitset = Join-Path $verifyDir 'bitset_verify.py'
$python = (Get-Command python).Source
$lockPath = Join-Path $targetDir 'portfolio.lock'
$statePath = Join-Path $targetDir 'portfolio_state.json'
$summaryPath = Join-Path $targetDir 'portfolio_summary.json'
$candidatePath = Join-Path $targetDir 'verified_candidate.json'
$dimacsPath = Join-Path $targetDir 'q26_k13_atmost_hilbert_mtotalizer.cnf'
$proofPath = Join-Path $targetDir 'q26_k13_atmost_hilbert_mtotalizer.drup'

if (Test-Path -LiteralPath $targetDir) {
  if (@(Get-ChildItem -LiteralPath $targetDir -Force).Count -ne 0) {
    throw "refusing nonempty run directory: $targetDir"
  }
} else {
  New-Item -ItemType Directory -Path $targetDir | Out-Null
}

$lockStream = [System.IO.File]::Open(
  $lockPath,
  [System.IO.FileMode]::CreateNew,
  [System.IO.FileAccess]::Write,
  [System.IO.FileShare]::None
)
$lanes = [System.Collections.Generic.List[object]]::new()
$finalSummary = $null
$exitCode = 4
$caughtFailure = $null

function Write-JsonAtomic([string] $Path, [object] $Value) {
  $temporary = "$Path.tmp.$PID"
  $json = ($Value | ConvertTo-Json -Depth 8) + [Environment]::NewLine
  [System.IO.File]::WriteAllText(
    $temporary,
    $json,
    [System.Text.UTF8Encoding]::new($false)
  )
  for ($attempt = 0; $attempt -lt 5; ++$attempt) {
    try {
      [System.IO.File]::Move($temporary, $Path, $true)
      return
    } catch [System.IO.IOException] {
      if ($attempt -eq 4) { throw }
      Start-Sleep -Milliseconds 50
    }
  }
}

function Read-Json([string] $Path) {
  if (-not (Test-Path -LiteralPath $Path)) { return $null }
  try {
    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
  } catch {
    return $null
  }
}

function Stop-And-Wait-Lanes {
  foreach ($lane in $lanes) {
    if (-not $lane.Process.HasExited) {
      Stop-Process -Id $lane.Process.Id -Force -ErrorAction SilentlyContinue
    }
  }
  foreach ($lane in $lanes) {
    if (-not $lane.Process.HasExited) {
      $lane.Process.WaitForExit(5000) | Out-Null
    }
  }
  $survivors = @($lanes | Where-Object { -not $_.Process.HasExited })
  foreach ($lane in $survivors) {
    Stop-Process -Id $lane.Process.Id -Force -ErrorAction SilentlyContinue
  }
  foreach ($lane in $survivors) {
    if (-not $lane.Process.HasExited) {
      $lane.Process.WaitForExit(5000) | Out-Null
    }
  }
  return @($lanes | Where-Object { -not $_.Process.HasExited } | ForEach-Object { $_.Process.Id })
}

function Lane-Records {
  return @($lanes | ForEach-Object {
    [ordered]@{
      lane = $_.Lane
      solver = $_.Solver
      seed = $_.Seed
      pid = $_.Process.Id
      exited = $_.Process.HasExited
      exit_code = if ($_.Process.HasExited) { $_.Process.ExitCode } else { $null }
      model_json = $_.ModelJson
      stderr = $_.Stderr
    }
  })
}

function Write-State([string] $Status, [object] $Extra) {
  Write-JsonAtomic $statePath ([ordered]@{
    schema = 'q26-unrestricted-sat-portfolio-v2'
    status = $Status
    run_dir = $targetDir
    deadline = $Deadline.ToString('o')
    updated = [DateTimeOffset]::Now.ToString('o')
    formula = [ordered]@{
      n = 26
      relation = 'at-most-13'
      ordering = 'hilbert'
      encoding = 'mtotalizer'
      exact = $false
      balanced_parity = $false
      d4_lex = $false
    }
    lanes = @(Lane-Records)
    extra = $Extra
  })
}

function Get-LaneErrors {
  $errors = @()
  foreach ($lane in $lanes) {
    if (-not $lane.Process.HasExited) { continue }
    $result = Read-Json $lane.ModelJson
    if ($lane.Process.ExitCode -ne 0 -or $null -eq $result) {
      $stderrBytes = if (Test-Path -LiteralPath $lane.Stderr) {
        (Get-Item -LiteralPath $lane.Stderr).Length
      } else { $null }
      $errors += [ordered]@{
        lane = $lane.Lane
        solver = $lane.Solver
        exit_code = $lane.Process.ExitCode
        model_json_present = (Test-Path -LiteralPath $lane.ModelJson)
        stderr_bytes = $stderrBytes
      }
    }
  }
  return $errors
}

function Harvest-FinalArtifact {
  foreach ($lane in $lanes) {
    $result = Read-Json $lane.ModelJson
    if ($null -eq $result -or $result.status -ne 'SAT') { continue }
    if (-not $result.independent_model_check) {
      return [pscustomobject]@{
        Kind = 'SAT_VERIFIER_DISAGREEMENT'
        Data = @{ lane = $lane.Lane; stage = 'internal model check' }
      }
    }

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
    Write-JsonAtomic $candidatePath $candidate
    $scalarOutput = & $python $scalar $candidatePath --expect 13 2>&1
    $scalarExit = $LASTEXITCODE
    $scalarOutput | Out-File -LiteralPath (Join-Path $targetDir 'scalar_verify.txt') -Encoding utf8
    $bitsetOutput = & $python $bitset $candidatePath --expect 13 2>&1
    $bitsetExit = $LASTEXITCODE
    $bitsetOutput | Out-File -LiteralPath (Join-Path $targetDir 'bitset_verify.txt') -Encoding utf8
    if ($scalarExit -eq 0 -and $bitsetExit -eq 0) {
      return [pscustomobject]@{
        Kind = 'SAT_VERIFIED'
        Data = [ordered]@{
          lane = $lane.Lane
          solver = $lane.Solver
          seed = $lane.Seed
          candidate = $candidatePath
          scalar_exit_code = $scalarExit
          bitset_exit_code = $bitsetExit
        }
      }
    }
    return [pscustomobject]@{
      Kind = 'SAT_VERIFIER_DISAGREEMENT'
      Data = @{
        lane = $lane.Lane
        scalar_exit_code = $scalarExit
        bitset_exit_code = $bitsetExit
      }
    }
  }

  if ($lanes.Count -ge 1) {
    $proofResult = Read-Json $lanes[0].ModelJson
    if ($null -ne $proofResult -and $proofResult.status -eq 'UNSAT' -and
        (Test-Path -LiteralPath $dimacsPath) -and
        (Get-Item -LiteralPath $dimacsPath).Length -gt 0 -and
        (Test-Path -LiteralPath $proofPath) -and
        (Get-Item -LiteralPath $proofPath).Length -gt 0) {
      return [pscustomobject]@{
        Kind = 'UNSAT_PROOF_UNCHECKED'
        Data = [ordered]@{
          lane = 1
          solver = $lanes[0].Solver
          dimacs = $dimacsPath
          proof = $proofPath
          proof_bytes = (Get-Item -LiteralPath $proofPath).Length
          proof_check = 'NOT_RUN'
        }
      }
    }
  }
  return $null
}

try {
  for ($index = 1; $index -le 64; ++$index) {
    $solver = if ($index -le $CadicalLanes) { 'cadical195' } else { 'glucose42' }
    $seed = $BaseSeed + $index
    $tag = '{0:D2}-{1}-s{2}' -f $index, $solver, $seed
    $modelJson = Join-Path $targetDir "$tag.json"
    $stdout = Join-Path $targetDir "$tag.stdout.txt"
    $stderr = Join-Path $targetDir "$tag.stderr.txt"
    $arguments = @(
      $solverScript,
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
      -RedirectStandardOutput $stdout -RedirectStandardError $stderr `
      -WindowStyle Hidden -PassThru
    $lanes.Add([pscustomobject]@{
      Lane = $index
      Solver = $solver
      Seed = $seed
      Process = $process
      ModelJson = $modelJson
      Stdout = $stdout
      Stderr = $stderr
    })
    Write-State 'LAUNCHING' @{ launched = $lanes.Count }
  }

  Write-State 'RUNNING' @{ launched = 64 }
  while ([DateTimeOffset]::Now -lt $Deadline) {
    $artifact = Harvest-FinalArtifact
    if ($null -ne $artifact -and $artifact.Kind -eq 'SAT_VERIFIED') {
      $finalSummary = [ordered]@{
        schema = 'q26-unrestricted-sat-portfolio-summary-v2'
        status = 'SAT'
        independently_verified = $true
        artifact = $artifact.Data
        finished = [DateTimeOffset]::Now.ToString('o')
      }
      $exitCode = 0
      break
    }
    if ($null -ne $artifact -and $artifact.Kind -eq 'SAT_VERIFIER_DISAGREEMENT') {
      $finalSummary = [ordered]@{
        schema = 'q26-unrestricted-sat-portfolio-summary-v2'
        status = 'SAT_VERIFIER_DISAGREEMENT'
        independently_verified = $false
        artifact = $artifact.Data
        finished = [DateTimeOffset]::Now.ToString('o')
      }
      $exitCode = 3
      break
    }

    $active = @($lanes | Where-Object { -not $_.Process.HasExited }).Count
    $errors = @(Get-LaneErrors)
    if ($active -eq 0) {
      if ($null -ne $artifact -and $artifact.Kind -eq 'UNSAT_PROOF_UNCHECKED') {
        $status = 'UNSAT_PROOF_UNCHECKED'
        $artifactData = $artifact.Data
      } elseif ($errors.Count -gt 0) {
        $status = 'FAILED'
        $artifactData = @{ lane_errors = $errors }
      } else {
        $status = 'NO_HIT'
        $artifactData = @{ message = 'all proofless lanes ended without a checked certificate' }
      }
      $finalSummary = [ordered]@{
        schema = 'q26-unrestricted-sat-portfolio-summary-v2'
        status = $status
        independently_verified = $false
        artifact = $artifactData
        finished = [DateTimeOffset]::Now.ToString('o')
      }
      $exitCode = 2
      break
    }

    Write-State 'RUNNING' @{
      active_lanes = $active
      lane_errors = $errors
      proof_pending = ($null -ne $artifact -and $artifact.Kind -eq 'UNSAT_PROOF_UNCHECKED')
    }
    Start-Sleep -Seconds 5
  }

  if ($null -eq $finalSummary) {
    $beforeStop = Harvest-FinalArtifact
    if ($null -ne $beforeStop -and $beforeStop.Kind -eq 'SAT_VERIFIED') {
      $finalSummary = [ordered]@{
        schema = 'q26-unrestricted-sat-portfolio-summary-v2'
        status = 'SAT'
        independently_verified = $true
        artifact = $beforeStop.Data
        finished = [DateTimeOffset]::Now.ToString('o')
      }
      $exitCode = 0
    } elseif ($null -ne $beforeStop -and $beforeStop.Kind -eq 'SAT_VERIFIER_DISAGREEMENT') {
      $finalSummary = [ordered]@{
        schema = 'q26-unrestricted-sat-portfolio-summary-v2'
        status = 'SAT_VERIFIER_DISAGREEMENT'
        independently_verified = $false
        artifact = $beforeStop.Data
        finished = [DateTimeOffset]::Now.ToString('o')
      }
      $exitCode = 3
    } else {
      $activeAtDeadline = @(
        $lanes | Where-Object { -not $_.Process.HasExited } |
          ForEach-Object { $_.Lane }
      )
      $errorsBeforeStop = @(Get-LaneErrors)
      $survivorsAfterStop = @(Stop-And-Wait-Lanes)
      $afterStop = Harvest-FinalArtifact
      if ($null -ne $afterStop -and $afterStop.Kind -eq 'SAT_VERIFIED') {
        $status = 'SAT'
        $verified = $true
        $artifactData = $afterStop.Data
        $exitCode = 0
      } elseif ($null -ne $afterStop -and $afterStop.Kind -eq 'SAT_VERIFIER_DISAGREEMENT') {
        $status = 'SAT_VERIFIER_DISAGREEMENT'
        $verified = $false
        $artifactData = $afterStop.Data
        $exitCode = 3
      } elseif ($null -ne $afterStop -and $afterStop.Kind -eq 'UNSAT_PROOF_UNCHECKED') {
        $status = 'UNSAT_PROOF_UNCHECKED'
        $verified = $false
        $artifactData = $afterStop.Data
        $exitCode = 2
      } elseif ($survivorsAfterStop.Count -gt 0) {
        $status = 'FAILED'
        $verified = $false
        $artifactData = @{ surviving_solver_pids = $survivorsAfterStop }
        $exitCode = 4
      } else {
        # Forced deadline stops are expected exhaustion, not lane crashes.
        $status = 'NO_HIT'
        $verified = $false
        $artifactData = @{
          reason = 'global deadline reached without a verified final certificate'
          active_lanes_stopped_at_deadline = $activeAtDeadline
          lane_errors_before_stop = $errorsBeforeStop
        }
        $exitCode = 2
      }
      $finalSummary = [ordered]@{
        schema = 'q26-unrestricted-sat-portfolio-summary-v2'
        status = $status
        independently_verified = $verified
        artifact = $artifactData
        finished = [DateTimeOffset]::Now.ToString('o')
      }
    }
  }
} catch {
  $caughtFailure = $_
  $finalSummary = [ordered]@{
    schema = 'q26-unrestricted-sat-portfolio-summary-v2'
    status = 'FAILED'
    independently_verified = $false
    error = $_.Exception.Message
    finished = [DateTimeOffset]::Now.ToString('o')
  }
  $exitCode = 4
} finally {
  $cleanupSurvivors = @(Stop-And-Wait-Lanes)
  try {
    if ($cleanupSurvivors.Count -gt 0) {
      if ($null -ne $finalSummary -and $finalSummary.status -eq 'SAT') {
        $finalSummary['cleanup_surviving_solver_pids'] = $cleanupSurvivors
      } else {
        $finalSummary = [ordered]@{
          schema = 'q26-unrestricted-sat-portfolio-summary-v2'
          status = 'FAILED'
          independently_verified = $false
          artifact = @{ surviving_solver_pids = $cleanupSurvivors }
          finished = [DateTimeOffset]::Now.ToString('o')
        }
        $exitCode = 4
      }
    }
    if ($null -ne $finalSummary) {
      Write-JsonAtomic $summaryPath $finalSummary
      Write-State $finalSummary.status $finalSummary
    }
  } finally {
    $lockStream.Dispose()
  }
}

if ($null -ne $caughtFailure) {
  Write-Error $caughtFailure -ErrorAction Continue
}
exit $exitCode
