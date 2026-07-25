[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Source,
    [Parameter(Mandatory = $true)][string]$Engine,
    [Parameter(Mandatory = $true)][string]$RunDir,
    [Parameter(Mandatory = $true)][string]$ExpectedSourceSha256,
    [Parameter(Mandatory = $true)][string]$ExpectedEngineSha256,
    [Parameter(Mandatory = $true)][string]$SeedFile,
    [Parameter(Mandatory = $true)][UInt64]$Seed,
    [string]$ScalarVerifier = (Join-Path $PSScriptRoot 'verify_scalar.py'),
    [string]$BitsetVerifier = (Join-Path $PSScriptRoot 'verify_bitset.exe'),
    [string]$ExpectedScalarSha256 = '71B9C070AEDAA563A16A4FD6B3BE5334C87B6AA3F876679DEB8C5D223A2EB443',
    [string]$ExpectedBitsetSha256 = 'E6683BEA5B835B5BFD78464DAB21BA2EBEF0436218C468AF1A5EE933BAB439EC',
    [ValidateRange(1, 64)][int]$Threads = 64,
    [UInt64]$RestartSteps = 250000,
    [ValidateRange(100, 60000)][int]$CheckpointMs = 5000,
    [ValidateRange(1, 300)][int]$CanarySeconds = 5,
    [switch]$AuditOnly,
    [switch]$TestMode,
    [ValidateRange(1, 60)][int]$TestProductionSeconds = 2
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$schema = 'ssnc-unrestricted19-native-run-v2'
$selfTestSchema = 'ssnc-unrestricted19-self-test-v2'
$configSchema = 'ssnc-unrestricted19-search-config-v2'
$checkpointSchema = 'ssnc-unrestricted19-best-checkpoint-v2'
$summarySchema = 'ssnc-unrestricted19-search-summary-v2'
$integratedContractSha256 = 'BCFD8319E9569FDED0373415F02516A1F71DFDD63B83DC4A59D29556D486801D'
$registeredSeedSha256 = '32CAB5626FAC027D1BD379A3063D8ADB8C9D4B4B1CC5AB65540323F582B6B6DA'
$registeredSeedBytes = 471
$fixedQ = 5
$rankStride = 457
$rankMax = 26505
$baselineRank = 4131
$acceptanceRule = 'objective_delta_if_nonzero_else_smooth_delta'
$productionSeconds = if ($TestMode) { $TestProductionSeconds } else { 8 * 60 * 60 }
$runPath = $null
$statePath = $null
$summaryPath = $null
$started = Get-Date
$phaseRecords = [System.Collections.Generic.List[object]]::new()

if ($RestartSteps -eq 0) { throw 'RestartSteps must be positive' }
if ($AuditOnly -and $TestMode) { throw 'AuditOnly and TestMode are mutually exclusive' }
if (-not $AuditOnly -and -not $TestMode -and $Threads -ne 64) {
    throw 'registered production requires exactly 64 threads'
}

function Write-AtomicJson {
    param([Parameter(Mandatory = $true)][string]$Path,
          [Parameter(Mandatory = $true)][object]$Value)
    $temporary = "$Path.tmp-$PID-$([Guid]::NewGuid().ToString('N'))"
    $Value | ConvertTo-Json -Depth 32 | Set-Content -LiteralPath $temporary -Encoding utf8
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Resolve-CheckedFile {
    param([string]$Path, [string]$ExpectedHash, [string]$Label)
    if ($ExpectedHash -notmatch '^[0-9A-Fa-f]{64}$') {
        throw "$Label expected SHA-256 is not 64 hexadecimal characters"
    }
    $resolved = (Resolve-Path -LiteralPath $Path).Path
    if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
        throw "$Label is not a regular file: $resolved"
    }
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolved).Hash.ToUpperInvariant()
    if ($actual -ne $ExpectedHash.ToUpperInvariant()) {
        throw "$Label SHA-256 mismatch: expected $($ExpectedHash.ToUpperInvariant()), found $actual"
    }
    [pscustomobject]@{ path = $resolved; sha256 = $actual }
}

function Resolve-RegisteredSeed {
    param([string]$Path)
    $resolved = (Resolve-Path -LiteralPath $Path).Path
    if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
        throw "seed file is not a regular file: $resolved"
    }
    [byte[]]$buffer = [IO.File]::ReadAllBytes($resolved)
    if ($buffer.Length -ne $registeredSeedBytes) {
        throw "seed byte-count mismatch: expected $registeredSeedBytes, found $($buffer.Length)"
    }
    $hasher = [Security.Cryptography.SHA256]::Create()
    try {
        [byte[]]$digest = $hasher.ComputeHash($buffer)
    } finally {
        $hasher.Dispose()
    }
    $actual = -join ($digest | ForEach-Object { $_.ToString('X2') })
    if ($actual -ne $registeredSeedSha256) {
        throw "seed SHA-256 mismatch: expected $registeredSeedSha256, found $actual"
    }
    if ($buffer[$buffer.Length - 1] -ne 10) {
        throw 'registered seed lacks its canonical terminal LF'
    }
    [pscustomobject]@{
        path = $resolved
        sha256 = $actual
        byte_count = [int]$buffer.Length
    }
}

function Assert-RegisteredSeedStillMatches {
    $current = Resolve-RegisteredSeed -Path $seedInfo.path
    if ($current.sha256 -ne $seedInfo.sha256 -or
        $current.byte_count -ne $seedInfo.byte_count) {
        throw 'registered seed changed after the preartifact gate'
    }
}

function Quote-NativeArgument {
    param([string]$Value)
    if ($Value.Contains('"')) { throw 'native argument contains an unsupported quote' }
    if ($Value -match '[\s&|<>^()]') { return '"' + $Value + '"' }
    return $Value
}

function Get-FileBytes {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        return (Get-Item -LiteralPath $Path).Length
    }
    return 0
}

function Get-RequiredProperty {
    param([Parameter(Mandatory = $true)][object]$Value,
          [Parameter(Mandatory = $true)][string]$Name,
          [Parameter(Mandatory = $true)][string]$Context)
    $property = $Value.PSObject.Properties[$Name]
    if ($null -eq $property) { throw "$Context lacks required property '$Name'" }
    return $property.Value
}

function Assert-SeedGateLedger {
    param([Parameter(Mandatory = $true)][object]$Ledger,
          [Parameter(Mandatory = $true)][string]$Context)
    $expected = [ordered]@{
        n = 19
        q = 5
        arcs = 166
        min_outdegree = 8
        objective = 9
        smooth = 18
        failing_mask = 451154
    }
    foreach ($entry in $expected.GetEnumerator()) {
        $actual = Get-RequiredProperty -Value $Ledger -Name $entry.Key -Context "$Context seed_gate_ledger"
        if ([Int64]$actual -ne [Int64]$entry.Value) {
            throw "$Context seed_gate_ledger.$($entry.Key) mismatch: expected $($entry.Value), found $actual"
        }
    }
}

function Assert-SeededV2Metadata {
    param([Parameter(Mandatory = $true)][object]$Value,
          [Parameter(Mandatory = $true)][string]$ExpectedSchema,
          [Parameter(Mandatory = $true)][string]$Context,
          [Nullable[int]]$ExpectedThreads = $null)
    if ((Get-RequiredProperty $Value 'schema' $Context) -ne $ExpectedSchema) {
        throw "$Context schema mismatch"
    }
    if ((Get-RequiredProperty $Value 'seeded_mode' $Context) -ne $true) {
        throw "$Context is not registered seeded mode"
    }
    if ([Int64](Get-RequiredProperty $Value 'fixed_q' $Context) -ne $fixedQ) {
        throw "$Context fixed_q is not $fixedQ"
    }
    $seedHash = [string](Get-RequiredProperty $Value 'seed_file_sha256' $Context)
    if ($seedHash.ToUpperInvariant() -ne $registeredSeedSha256) {
        throw "$Context seed_file_sha256 mismatch"
    }
    if ([Int64](Get-RequiredProperty $Value 'seed_file_bytes' $Context) -ne $registeredSeedBytes) {
        throw "$Context seed_file_bytes mismatch"
    }
    if ([Int64](Get-RequiredProperty $Value 'effective_warmup_steps' $Context) -ne 0) {
        throw "$Context effective_warmup_steps is not zero"
    }
    if ((Get-RequiredProperty $Value 'best_order' $Context) -ne 'objective_then_smooth') {
        throw "$Context best_order mismatch"
    }
    if ([Int64](Get-RequiredProperty $Value 'rank_stride' $Context) -ne $rankStride) {
        throw "$Context rank_stride mismatch"
    }
    if ([Int64](Get-RequiredProperty $Value 'rank_max' $Context) -ne $rankMax) {
        throw "$Context rank_max mismatch"
    }
    if ((Get-RequiredProperty $Value 'acceptance_rule' $Context) -ne $acceptanceRule) {
        throw "$Context acceptance_rule mismatch"
    }
    if ((Get-RequiredProperty $Value 'seed_origin' $Context) -ne 'registered_seed') {
        throw "$Context seed_origin mismatch"
    }
    Assert-SeedGateLedger -Ledger (Get-RequiredProperty $Value 'seed_gate_ledger' $Context) -Context $Context
    if ($null -ne $ExpectedThreads -and
        [Int64](Get-RequiredProperty $Value 'threads' $Context) -ne [Int64]$ExpectedThreads.Value) {
        throw "$Context thread count mismatch"
    }
    $portfolioProperty = $Value.PSObject.Properties['q_portfolio']
    if ($null -ne $portfolioProperty -and $null -ne $portfolioProperty.Value -and
        @($portfolioProperty.Value).Count -ne 0) {
        throw "$Context unexpectedly advertises an unseeded q portfolio"
    }
}

function Assert-CheckpointRank {
    param([Parameter(Mandatory = $true)][object]$Value,
          [Parameter(Mandatory = $true)][string]$Context)
    $rank = [Int64](Get-RequiredProperty $Value 'rank' $Context)
    $objective = [Int64](Get-RequiredProperty $Value 'objective' $Context)
    $smooth = [Int64](Get-RequiredProperty $Value 'smooth_witness_energy' $Context)
    if ($objective -lt 0 -or $objective -gt 57 -or $smooth -lt 0 -or $smooth -gt 456) {
        throw "$Context contains an out-of-domain rank component"
    }
    if ($rank -ne $rankStride * $objective + $smooth -or $rank -lt 0 -or $rank -gt $rankMax) {
        throw "$Context rank equation mismatch"
    }
    if ($rank -gt $baselineRank) { throw "$Context is worse than the installed seed baseline" }
}

function Assert-SummaryRank {
    param([Parameter(Mandatory = $true)][object]$Value,
          [Parameter(Mandatory = $true)][string]$Context)
    if ((Get-RequiredProperty $Value 'best_present' $Context) -ne $true) {
        throw "$Context lacks the installed seed baseline"
    }
    $rank = [Int64](Get-RequiredProperty $Value 'best_rank' $Context)
    $objective = [Int64](Get-RequiredProperty $Value 'best_literal_objective' $Context)
    $smooth = [Int64](Get-RequiredProperty $Value 'best_smooth_witness_energy' $Context)
    if ($objective -lt 0 -or $objective -gt 57 -or $smooth -lt 0 -or $smooth -gt 456) {
        throw "$Context contains an out-of-domain best rank component"
    }
    if ($rank -ne $rankStride * $objective + $smooth -or $rank -lt 0 -or $rank -gt $baselineRank) {
        throw "$Context best rank equation mismatch"
    }
}

function Write-RunState {
    param([string]$Status, [string]$Phase, [Nullable[int]]$NativePid,
          [Nullable[datetime]]$Deadline)
    if (-not $statePath) { return }
    $state = [ordered]@{
        schema = $schema
        status = $Status
        phase = $Phase
        wrapper_pid = $PID
        native_pid = $NativePid
        started_at = $started.ToString('o')
        deadline = if ($null -ne $Deadline) { ([datetime]$Deadline).ToString('o') } else { $null }
        production_seconds = $productionSeconds
        canary_seconds = $CanarySeconds
        threads = $Threads
        rng_seed = $Seed
        restart_steps = $RestartSteps
        checkpoint_ms = $CheckpointMs
        seeded_mode = $true
        fixed_q = $fixedQ
        effective_warmup_steps = 0
        seed_origin = 'registered_seed'
        seed_file = $seedInfo
        best_order = 'objective_then_smooth'
        rank_stride = $rankStride
        rank_max = $rankMax
        acceptance_rule = $acceptanceRule
        integrated_contract_sha256 = $integratedContractSha256
        run_dir = $runPath
        source = $sourceInfo.path
        source_sha256 = $sourceInfo.sha256
        engine = $engineInfo.path
        engine_sha256 = $engineInfo.sha256
        scalar_verifier = $scalarInfo.path
        scalar_sha256 = $scalarInfo.sha256
        bitset_verifier = $bitsetInfo.path
        bitset_sha256 = $bitsetInfo.sha256
    }
    Write-AtomicJson -Path $statePath -Value $state
}

function Invoke-HiddenNative {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$StdoutPath,
        [Parameter(Mandatory = $true)][string]$StderrPath,
        [Parameter(Mandatory = $true)][datetime]$Deadline,
        [string]$HitPath = '',
        [string]$Phase = 'native'
    )
    $quoted = @($Arguments | ForEach-Object { Quote-NativeArgument $_ })
    $process = Start-Process -FilePath $Executable -ArgumentList $quoted `
        -RedirectStandardOutput $StdoutPath -RedirectStandardError $StderrPath `
        -WindowStyle Hidden -PassThru
    Write-RunState -Status 'RUNNING' -Phase $Phase -NativePid $process.Id -Deadline $Deadline
    $reason = 'EXITED'
    while (-not $process.HasExited) {
        if ($HitPath -and (Test-Path -LiteralPath $HitPath -PathType Leaf)) {
            $reason = 'HIT_FILE'
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            break
        }
        if ((Get-FileBytes $StderrPath) -gt 0) {
            $reason = 'STDERR_NONEMPTY'
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            break
        }
        if ((Get-Date) -ge $Deadline) {
            $reason = 'DEADLINE'
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            break
        }
        Start-Sleep -Milliseconds 100
        $process.Refresh()
    }
    $process.WaitForExit()
    $process.Refresh()
    [pscustomobject]@{
        phase = $Phase
        pid = $process.Id
        reason = $reason
        exit_code = if ($reason -eq 'EXITED') { $process.ExitCode } else { $null }
        stdout = $StdoutPath
        stdout_bytes = Get-FileBytes $StdoutPath
        stderr = $StderrPath
        stderr_bytes = Get-FileBytes $StderrPath
        finished_at = (Get-Date).ToString('o')
    }
}

function Read-LastJsonLine {
    param([string]$Path)
    $lines = @(Get-Content -LiteralPath $Path | Where-Object { $_.Trim().Length -gt 0 })
    if ($lines.Count -eq 0) { throw "no JSON line in $Path" }
    return ($lines[-1] | ConvertFrom-Json)
}

function Read-JsonFile {
    param([string]$Path, [string]$Context)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Context is missing: $Path"
    }
    try {
        return (Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json)
    } catch {
        throw "$Context is not valid JSON: $($_.Exception.Message)"
    }
}

function Complete-Run {
    param([string]$Status, [bool]$Verified, [int]$ExitCode,
          [object]$Verification = $null, [string]$ErrorText = '')
    $finished = Get-Date
    $summary = [ordered]@{
        schema = $schema
        status = $Status
        independently_verified = $Verified
        error = $ErrorText
        wrapper_pid = $PID
        started_at = $started.ToString('o')
        finished_at = $finished.ToString('o')
        elapsed_seconds = [Math]::Round(($finished - $started).TotalSeconds, 3)
        production_seconds = $productionSeconds
        canary_seconds = $CanarySeconds
        threads = $Threads
        rng_seed = $Seed
        restart_steps = $RestartSteps
        checkpoint_ms = $CheckpointMs
        test_mode = [bool]$TestMode
        audit_only = [bool]$AuditOnly
        seeded_mode = $true
        fixed_q = $fixedQ
        effective_warmup_steps = 0
        seed_origin = 'registered_seed'
        seed_file = $seedInfo
        best_order = 'objective_then_smooth'
        rank_stride = $rankStride
        rank_max = $rankMax
        acceptance_rule = $acceptanceRule
        integrated_contract_sha256 = $integratedContractSha256
        run_dir = $runPath
        source = $sourceInfo
        engine = $engineInfo
        scalar_verifier = $scalarInfo
        bitset_verifier = $bitsetInfo
        phases = @($phaseRecords)
        verification = $Verification
    }
    Write-AtomicJson -Path $summaryPath -Value $summary
    Write-AtomicJson -Path $statePath -Value $summary
    $summary | ConvertTo-Json -Depth 32 -Compress
    exit $ExitCode
}

function Replay-Hit {
    param([string]$CandidatePath, [string]$Prefix)
    if (-not (Test-Path -LiteralPath $CandidatePath -PathType Leaf)) {
        return [pscustomobject]@{ status = 'MISSING_HIT_CANDIDATE'; independently_verified = $false }
    }
    $beforeHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $CandidatePath).Hash.ToUpperInvariant()
    $beforeBytes = (Get-Item -LiteralPath $CandidatePath).Length
    $pythonPath = (Get-Command python -ErrorAction Stop).Source
    $scalarOut = Join-Path $runPath "$Prefix.scalar.stdout.json"
    $scalarErr = Join-Path $runPath "$Prefix.scalar.stderr.txt"
    $bitsetOut = Join-Path $runPath "$Prefix.bitset.stdout.json"
    $bitsetErr = Join-Path $runPath "$Prefix.bitset.stderr.txt"
    $scalarRun = Invoke-HiddenNative -Executable $pythonPath `
        -Arguments @($scalarInfo.path, $CandidatePath) -StdoutPath $scalarOut `
        -StderrPath $scalarErr -Deadline (Get-Date).AddSeconds(120) -Phase 'scalar-replay'
    $bitsetRun = Invoke-HiddenNative -Executable $bitsetInfo.path `
        -Arguments @($CandidatePath) -StdoutPath $bitsetOut -StderrPath $bitsetErr `
        -Deadline (Get-Date).AddSeconds(120) -Phase 'bitset-replay'
    $afterHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $CandidatePath).Hash.ToUpperInvariant()
    $scalarStatus = $null
    $bitsetStatus = $null
    try { $scalarStatus = (Read-LastJsonLine $scalarOut).status } catch { $scalarStatus = 'UNPARSEABLE' }
    try { $bitsetStatus = (Read-LastJsonLine $bitsetOut).status } catch { $bitsetStatus = 'UNPARSEABLE' }
    $scalarAccept = $scalarRun.reason -eq 'EXITED' -and $scalarRun.exit_code -eq 0 -and `
        $scalarRun.stderr_bytes -eq 0 -and $scalarStatus -eq 'VERIFIED_COUNTEREXAMPLE'
    $bitsetAccept = $bitsetRun.reason -eq 'EXITED' -and $bitsetRun.exit_code -eq 0 -and `
        $bitsetRun.stderr_bytes -eq 0 -and $bitsetStatus -eq 'VERIFIED_COUNTEREXAMPLE'
    if ($beforeHash -ne $afterHash) {
        $status = 'CANDIDATE_MUTATED_DURING_REPLAY'
    } elseif ($scalarAccept -and $bitsetAccept) {
        $status = 'VERIFIED_COUNTEREXAMPLE'
    } elseif ($scalarAccept -ne $bitsetAccept) {
        $status = 'VERIFIER_DISAGREEMENT'
    } elseif ($scalarRun.exit_code -eq 2 -and $bitsetRun.exit_code -eq 2) {
        $status = 'INVALID_HIT_CANDIDATE'
    } else {
        $status = 'REJECTED_HIT_NOT_COUNTEREXAMPLE'
    }
    [pscustomobject]@{
        status = $status
        independently_verified = ($status -eq 'VERIFIED_COUNTEREXAMPLE')
        candidate = $CandidatePath
        candidate_bytes = $beforeBytes
        candidate_sha256_before = $beforeHash
        candidate_sha256_after = $afterHash
        scalar_status = $scalarStatus
        scalar_run = $scalarRun
        bitset_status = $bitsetStatus
        bitset_run = $bitsetRun
    }
}

function Assert-EngineConfig {
    param([string]$Directory, [int]$ExpectedThreads, [string]$Context)
    $config = Read-JsonFile (Join-Path $Directory 'config.json') "$Context config"
    Assert-SeededV2Metadata $config $configSchema "$Context config" $ExpectedThreads
    return $config
}

function Assert-EngineCheckpointIfPresent {
    param([string]$Directory, [string]$Context, [switch]$Required)
    $path = Join-Path $Directory 'best_checkpoint.json'
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        if ($Required) { throw "$Context checkpoint is missing" }
        return $null
    }
    $checkpoint = Read-JsonFile $path "$Context checkpoint"
    Assert-SeededV2Metadata $checkpoint $checkpointSchema "$Context checkpoint"
    Assert-CheckpointRank $checkpoint "$Context checkpoint"
    return $checkpoint
}

function Assert-EngineSummary {
    param([string]$Directory, [int]$ExpectedThreads, [string]$Context)
    $summary = Read-JsonFile (Join-Path $Directory 'summary.json') "$Context summary"
    Assert-SeededV2Metadata $summary $summarySchema "$Context summary" $ExpectedThreads
    Assert-SummaryRank $summary "$Context summary"
    return $summary
}

try {
    # All immutable inputs, including the exact registered seed buffer, are
    # authenticated before any run directory or log artifact is created.
    $sourceInfo = Resolve-CheckedFile $Source $ExpectedSourceSha256 'v2 source'
    $engineInfo = Resolve-CheckedFile $Engine $ExpectedEngineSha256 'v2 engine'
    $scalarInfo = Resolve-CheckedFile $ScalarVerifier $ExpectedScalarSha256 'scalar verifier'
    $bitsetInfo = Resolve-CheckedFile $BitsetVerifier $ExpectedBitsetSha256 'bitset verifier'
    $seedInfo = Resolve-RegisteredSeed $SeedFile

    $logsRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'logs'))
    $runPath = [IO.Path]::GetFullPath($RunDir)
    $logsPrefix = $logsRoot.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    if (-not $runPath.StartsWith($logsPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "RunDir must be a child of $logsRoot"
    }
    if (Test-Path -LiteralPath $runPath) { throw "RunDir already exists: $runPath" }
    if (-not (Test-Path -LiteralPath $logsRoot)) { New-Item -ItemType Directory -Path $logsRoot | Out-Null }
    $staging = "$runPath.creating-$PID-$([Guid]::NewGuid().ToString('N'))"
    New-Item -ItemType Directory -Path $staging | Out-Null
    $initialState = [ordered]@{
        schema = $schema
        status = 'CREATED'
        phase = 'preflight'
        wrapper_pid = $PID
        started_at = $started.ToString('o')
        run_dir = $runPath
        source = $sourceInfo
        engine = $engineInfo
        scalar_verifier = $scalarInfo
        bitset_verifier = $bitsetInfo
        seed_file = $seedInfo
        production_seconds = $productionSeconds
        threads = $Threads
        rng_seed = $Seed
        restart_steps = $RestartSteps
        checkpoint_ms = $CheckpointMs
        seeded_mode = $true
        fixed_q = $fixedQ
        effective_warmup_steps = 0
        seed_origin = 'registered_seed'
        best_order = 'objective_then_smooth'
        rank_stride = $rankStride
        rank_max = $rankMax
        acceptance_rule = $acceptanceRule
        integrated_contract_sha256 = $integratedContractSha256
    }
    Write-AtomicJson -Path (Join-Path $staging 'state.json') -Value $initialState
    Move-Item -LiteralPath $staging -Destination $runPath
    $statePath = Join-Path $runPath 'state.json'
    $summaryPath = Join-Path $runPath 'summary.json'

    Assert-RegisteredSeedStillMatches
    $selfOut = Join-Path $runPath 'self_test.stdout.jsonl'
    $selfErr = Join-Path $runPath 'self_test.stderr.txt'
    $selfRun = Invoke-HiddenNative -Executable $engineInfo.path `
        -Arguments @('--self-test','--seed',[string]$Seed,'--seed-file',$seedInfo.path) `
        -StdoutPath $selfOut -StderrPath $selfErr -Deadline (Get-Date).AddMinutes(30) -Phase 'seeded-self-test'
    $phaseRecords.Add($selfRun)
    $selfJson = $null
    try { $selfJson = Read-LastJsonLine $selfOut } catch { }
    try {
        if ($null -ne $selfJson) {
            Assert-SeededV2Metadata $selfJson $selfTestSchema 'seeded self-test'
        }
    } catch {
        Complete-Run 'SELF_TEST_FAILED' $false 1 $null $_.Exception.Message
    }
    if ($selfRun.reason -ne 'EXITED' -or $selfRun.exit_code -ne 0 -or `
        $selfRun.stderr_bytes -ne 0 -or $null -eq $selfJson -or `
        $selfJson.status -ne 'SELF_TEST_PASS' -or $selfJson.failures -ne 0 -or `
        $selfJson.production_run -ne $false) {
        Complete-Run 'SELF_TEST_FAILED' $false 1 $null 'seeded v2 self-test gate rejected the engine'
    }

    Assert-RegisteredSeedStillMatches
    $canaryDir = Join-Path $runPath 'canary'
    $canaryOut = Join-Path $runPath 'canary.stdout.jsonl'
    $canaryErr = Join-Path $runPath 'canary.stderr.txt'
    $canaryHit = Join-Path $canaryDir 'hit_candidate.json'
    $canaryDeadline = (Get-Date).AddSeconds($CanarySeconds + 60)
    $canaryRun = Invoke-HiddenNative -Executable $engineInfo.path `
        -Arguments @('--search','--threads','1','--seconds',[string]$CanarySeconds, `
                     '--seed',[string]$Seed,'--seed-file',$seedInfo.path, `
                     '--warmup-steps','0','--restart-steps',[string]$RestartSteps, `
                     '--checkpoint-ms',[string]$CheckpointMs,'--output-dir',$canaryDir) `
        -StdoutPath $canaryOut -StderrPath $canaryErr -Deadline $canaryDeadline `
        -HitPath $canaryHit -Phase 'seeded-one-thread-canary'
    $phaseRecords.Add($canaryRun)
    try { $canaryConfig = Assert-EngineConfig $canaryDir 1 'canary' } catch {
        Complete-Run 'CANARY_FAILED' $false 1 $null $_.Exception.Message
    }
    if ($canaryRun.reason -eq 'HIT_FILE' -or (Test-Path -LiteralPath $canaryHit -PathType Leaf)) {
        try { $null = Assert-EngineCheckpointIfPresent $canaryDir 'canary' } catch {
            Complete-Run 'CANARY_FAILED' $false 1 $null $_.Exception.Message
        }
        $verification = Replay-Hit $canaryHit 'canary-hit'
        if ($verification.independently_verified) { Complete-Run 'VERIFIED_COUNTEREXAMPLE' $true 0 $verification }
        Complete-Run $verification.status $false 1 $verification 'canary candidate failed independent replay'
    }
    if ($canaryRun.reason -eq 'DEADLINE') {
        Complete-Run 'CANARY_TIMEOUT' $false 1 $null 'seeded one-thread canary exceeded its wall deadline'
    }
    if ($canaryRun.reason -ne 'EXITED' -or $canaryRun.exit_code -ne 0 -or $canaryRun.stderr_bytes -ne 0) {
        Complete-Run 'CANARY_FAILED' $false 1 $null 'seeded one-thread canary failed or wrote stderr'
    }
    try {
        $canarySummary = Assert-EngineSummary $canaryDir 1 'canary'
        $null = Assert-EngineCheckpointIfPresent $canaryDir 'canary' -Required
    } catch {
        Complete-Run 'CANARY_FAILED' $false 1 $null $_.Exception.Message
    }
    if ($canarySummary.status -ne 'NO_HIT') {
        Complete-Run 'CANARY_FAILED' $false 1 $null 'seeded canary did not return NO_HIT'
    }
    if ($AuditOnly) { Complete-Run 'AUDIT_PASS_NO_PRODUCTION' $false 0 }

    Assert-RegisteredSeedStillMatches
    $searchDir = Join-Path $runPath 'search'
    $searchOut = Join-Path $runPath 'search.stdout.jsonl'
    $searchErr = Join-Path $runPath 'search.stderr.txt'
    $hitPath = Join-Path $searchDir 'hit_candidate.json'
    $productionStarted = Get-Date
    $productionDeadline = $productionStarted.AddSeconds($productionSeconds)
    $searchRun = Invoke-HiddenNative -Executable $engineInfo.path `
        -Arguments @('--search','--threads',[string]$Threads,'--seconds',[string]$productionSeconds, `
                     '--seed',[string]$Seed,'--seed-file',$seedInfo.path, `
                     '--warmup-steps','0','--restart-steps',[string]$RestartSteps, `
                     '--checkpoint-ms',[string]$CheckpointMs,'--output-dir',$searchDir) `
        -StdoutPath $searchOut -StderrPath $searchErr -Deadline $productionDeadline `
        -HitPath $hitPath -Phase 'seeded-production-search'
    $phaseRecords.Add($searchRun)
    try { $productionConfig = Assert-EngineConfig $searchDir $Threads 'production' } catch {
        Complete-Run 'ENGINE_FAILED' $false 1 $null $_.Exception.Message
    }
    if ($searchRun.reason -eq 'HIT_FILE' -or (Test-Path -LiteralPath $hitPath -PathType Leaf)) {
        try { $null = Assert-EngineCheckpointIfPresent $searchDir 'production' } catch {
            Complete-Run 'ENGINE_FAILED' $false 1 $null $_.Exception.Message
        }
        $verification = Replay-Hit $hitPath 'production-hit'
        if ($verification.independently_verified) { Complete-Run 'VERIFIED_COUNTEREXAMPLE' $true 0 $verification }
        Complete-Run $verification.status $false 1 $verification 'raw hit failed independent replay'
    }
    if ($searchRun.reason -eq 'STDERR_NONEMPTY') {
        Complete-Run 'FAILED_STDERR' $false 1 $null 'production engine wrote stderr'
    }
    if ($searchRun.reason -eq 'DEADLINE') {
        try { $null = Assert-EngineCheckpointIfPresent $searchDir 'production' -Required } catch {
            Complete-Run 'ENGINE_FAILED' $false 1 $null $_.Exception.Message
        }
        Complete-Run 'NO_HIT_HARD_DEADLINE' $false 0 $null ''
    }
    if ($searchRun.reason -ne 'EXITED' -or $searchRun.exit_code -ne 0 -or $searchRun.stderr_bytes -ne 0) {
        Complete-Run 'ENGINE_FAILED' $false 1 $null 'production engine failed'
    }
    $elapsed = ((Get-Date) - $productionStarted).TotalSeconds
    if (-not $TestMode -and $elapsed -lt ($productionSeconds - 2)) {
        Complete-Run 'FAILED_EARLY_EXIT' $false 1 $null 'production engine exited before the eight-hour boundary'
    }
    try {
        $engineSummary = Assert-EngineSummary $searchDir $Threads 'production'
        $null = Assert-EngineCheckpointIfPresent $searchDir 'production' -Required
    } catch {
        Complete-Run 'ENGINE_FAILED' $false 1 $null $_.Exception.Message
    }
    if ($engineSummary.status -ne 'NO_HIT') {
        Complete-Run 'ENGINE_FAILED' $false 1 $null 'production summary did not return NO_HIT'
    }
    Complete-Run 'NO_HIT' $false 0
} catch {
    if ($runPath -and $statePath -and $summaryPath -and (Test-Path -LiteralPath $runPath)) {
        Complete-Run 'HARNESS_FAILED' $false 1 $null $_.Exception.Message
    }
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
