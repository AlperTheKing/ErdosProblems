[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Source,
    [Parameter(Mandatory = $true)][string]$Engine,
    [Parameter(Mandatory = $true)][string]$RunDir,
    [Parameter(Mandatory = $true)][string]$ExpectedSourceSha256,
    [Parameter(Mandatory = $true)][string]$ExpectedEngineSha256,
    [string]$ScalarVerifier = (Join-Path $PSScriptRoot 'verify_scalar.py'),
    [string]$BitsetVerifier = (Join-Path $PSScriptRoot 'verify_bitset.exe'),
    [string]$ExpectedScalarSha256 = '71B9C070AEDAA563A16A4FD6B3BE5334C87B6AA3F876679DEB8C5D223A2EB443',
    [string]$ExpectedBitsetSha256 = 'E6683BEA5B835B5BFD78464DAB21BA2EBEF0436218C468AF1A5EE933BAB439EC',
    [ValidateRange(1, 64)][int]$Threads = 64,
    [UInt64]$Seed = 2026072101,
    [ValidateRange(1, 300)][int]$CanarySeconds = 5,
    [switch]$AuditOnly,
    [switch]$TestMode,
    [ValidateRange(1, 60)][int]$TestProductionSeconds = 2
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$schema = 'ssnc-unrestricted19-native-run-v1'
$productionSeconds = if ($TestMode) { $TestProductionSeconds } else { 8 * 60 * 60 }
$runPath = $null
$statePath = $null
$summaryPath = $null
$started = Get-Date
$phaseRecords = [System.Collections.Generic.List[object]]::new()

function Write-AtomicJson {
    param([Parameter(Mandatory = $true)][string]$Path,
          [Parameter(Mandatory = $true)][object]$Value)
    $temporary = "$Path.tmp-$PID-$([Guid]::NewGuid().ToString('N'))"
    $Value | ConvertTo-Json -Depth 16 | Set-Content -LiteralPath $temporary -Encoding utf8
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Resolve-CheckedFile {
    param([string]$Path, [string]$ExpectedHash, [string]$Label)
    if ($ExpectedHash -notmatch '^[0-9A-Fa-f]{64}$') {
        throw "$Label expected SHA-256 is not 64 hexadecimal characters"
    }
    $resolved = (Resolve-Path -LiteralPath $Path).Path
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolved).Hash.ToUpperInvariant()
    if ($actual -ne $ExpectedHash.ToUpperInvariant()) {
        throw "$Label SHA-256 mismatch: expected $($ExpectedHash.ToUpperInvariant()), found $actual"
    }
    [pscustomobject]@{ path = $resolved; sha256 = $actual }
}

function Quote-NativeArgument {
    param([string]$Value)
    if ($Value.Contains('"')) { throw 'native argument contains an unsupported quote' }
    if ($Value -match '[\s&|<>^()]') { return '"' + $Value + '"' }
    return $Value
}

function Get-FileBytes {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path) { return (Get-Item -LiteralPath $Path).Length }
    return 0
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
        seed = $Seed
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
        if ($HitPath -and (Test-Path -LiteralPath $HitPath)) {
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
        seed = $Seed
        test_mode = [bool]$TestMode
        audit_only = [bool]$AuditOnly
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
    $summary | ConvertTo-Json -Depth 16 -Compress
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

try {
    # All four immutable artifacts are authenticated before a run directory exists.
    $sourceInfo = Resolve-CheckedFile $Source $ExpectedSourceSha256 'source'
    $engineInfo = Resolve-CheckedFile $Engine $ExpectedEngineSha256 'engine'
    $scalarInfo = Resolve-CheckedFile $ScalarVerifier $ExpectedScalarSha256 'scalar verifier'
    $bitsetInfo = Resolve-CheckedFile $BitsetVerifier $ExpectedBitsetSha256 'bitset verifier'

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
        schema = $schema; status = 'CREATED'; phase = 'preflight'; wrapper_pid = $PID
        started_at = $started.ToString('o'); run_dir = $runPath
        source_sha256 = $sourceInfo.sha256; engine_sha256 = $engineInfo.sha256
        scalar_sha256 = $scalarInfo.sha256; bitset_sha256 = $bitsetInfo.sha256
        production_seconds = $productionSeconds; threads = $Threads; seed = $Seed
    }
    Write-AtomicJson -Path (Join-Path $staging 'state.json') -Value $initialState
    Move-Item -LiteralPath $staging -Destination $runPath
    $statePath = Join-Path $runPath 'state.json'
    $summaryPath = Join-Path $runPath 'summary.json'

    $selfOut = Join-Path $runPath 'self_test.stdout.jsonl'
    $selfErr = Join-Path $runPath 'self_test.stderr.txt'
    $selfRun = Invoke-HiddenNative -Executable $engineInfo.path `
        -Arguments @('--self-test', '--seed', [string]$Seed) `
        -StdoutPath $selfOut -StderrPath $selfErr -Deadline (Get-Date).AddMinutes(30) -Phase 'self-test'
    $phaseRecords.Add($selfRun)
    $selfJson = $null
    try { $selfJson = Read-LastJsonLine $selfOut } catch { }
    if ($selfRun.reason -ne 'EXITED' -or $selfRun.exit_code -ne 0 -or `
        $selfRun.stderr_bytes -ne 0 -or $null -eq $selfJson -or `
        $selfJson.status -ne 'SELF_TEST_PASS' -or $selfJson.failures -ne 0 -or `
        $selfJson.production_run -ne $false) {
        Complete-Run 'SELF_TEST_FAILED' $false 1 $null 'self-test gate rejected the engine'
    }

    $canaryDir = Join-Path $runPath 'canary'
    $canaryOut = Join-Path $runPath 'canary.stdout.jsonl'
    $canaryErr = Join-Path $runPath 'canary.stderr.txt'
    $canaryHit = Join-Path $canaryDir 'hit_candidate.json'
    $canaryDeadline = (Get-Date).AddSeconds($CanarySeconds + 60)
    $canaryRun = Invoke-HiddenNative -Executable $engineInfo.path `
        -Arguments @('--threads','1','--seconds',[string]$CanarySeconds,'--seed',[string]($Seed + 1), `
                     '--output-dir',$canaryDir) `
        -StdoutPath $canaryOut -StderrPath $canaryErr -Deadline $canaryDeadline `
        -HitPath $canaryHit -Phase 'one-thread-canary'
    $phaseRecords.Add($canaryRun)
    if ($canaryRun.reason -eq 'HIT_FILE' -or (Test-Path -LiteralPath $canaryHit)) {
        $verification = Replay-Hit $canaryHit 'canary-hit'
        if ($verification.independently_verified) { Complete-Run 'VERIFIED_COUNTEREXAMPLE' $true 0 $verification }
        Complete-Run $verification.status $false 1 $verification 'canary candidate failed independent replay'
    }
    if ($canaryRun.reason -eq 'DEADLINE') { Complete-Run 'CANARY_TIMEOUT' $false 1 $null 'one-thread canary exceeded its wall deadline' }
    if ($canaryRun.reason -ne 'EXITED' -or $canaryRun.exit_code -ne 0 -or $canaryRun.stderr_bytes -ne 0) {
        Complete-Run 'CANARY_FAILED' $false 1 $null 'one-thread canary failed or wrote stderr'
    }
    $canaryEngineSummary = Join-Path $canaryDir 'summary.json'
    try { $canaryJson = Get-Content -Raw -LiteralPath $canaryEngineSummary | ConvertFrom-Json } catch {
        Complete-Run 'CANARY_FAILED' $false 1 $null 'missing or malformed canary summary.json'
    }
    if ($canaryJson.status -ne 'NO_HIT' -or $canaryJson.threads -ne 1) {
        Complete-Run 'CANARY_FAILED' $false 1 $null 'canary summary contract mismatch'
    }
    if ($AuditOnly) { Complete-Run 'AUDIT_PASS_NO_PRODUCTION' $false 0 }

    $searchDir = Join-Path $runPath 'search'
    $searchOut = Join-Path $runPath 'search.stdout.jsonl'
    $searchErr = Join-Path $runPath 'search.stderr.txt'
    $hitPath = Join-Path $searchDir 'hit_candidate.json'
    $productionStarted = Get-Date
    $productionDeadline = $productionStarted.AddSeconds($productionSeconds)
    $searchRun = Invoke-HiddenNative -Executable $engineInfo.path `
        -Arguments @('--threads',[string]$Threads,'--seconds',[string]$productionSeconds, `
                     '--seed',[string]$Seed,'--output-dir',$searchDir) `
        -StdoutPath $searchOut -StderrPath $searchErr -Deadline $productionDeadline `
        -HitPath $hitPath -Phase 'production-search'
    $phaseRecords.Add($searchRun)
    if ($searchRun.reason -eq 'HIT_FILE' -or (Test-Path -LiteralPath $hitPath)) {
        $verification = Replay-Hit $hitPath 'production-hit'
        if ($verification.independently_verified) { Complete-Run 'VERIFIED_COUNTEREXAMPLE' $true 0 $verification }
        Complete-Run $verification.status $false 1 $verification 'raw hit failed independent replay'
    }
    if ($searchRun.reason -eq 'STDERR_NONEMPTY') {
        Complete-Run 'FAILED_STDERR' $false 1 $null 'production engine wrote stderr'
    }
    if ($searchRun.reason -eq 'DEADLINE') {
        Complete-Run 'NO_HIT_HARD_DEADLINE' $false 0 $null ''
    }
    if ($searchRun.reason -ne 'EXITED' -or $searchRun.exit_code -ne 0 -or $searchRun.stderr_bytes -ne 0) {
        Complete-Run 'ENGINE_FAILED' $false 1 $null 'production engine failed'
    }
    $elapsed = ((Get-Date) - $productionStarted).TotalSeconds
    if (-not $TestMode -and $elapsed -lt ($productionSeconds - 2)) {
        Complete-Run 'FAILED_EARLY_EXIT' $false 1 $null 'production engine exited before the eight-hour boundary'
    }
    $engineSummaryPath = Join-Path $searchDir 'summary.json'
    try { $engineSummary = Get-Content -Raw -LiteralPath $engineSummaryPath | ConvertFrom-Json } catch {
        Complete-Run 'ENGINE_FAILED' $false 1 $null 'missing or malformed production summary.json'
    }
    if ($engineSummary.status -ne 'NO_HIT' -or $engineSummary.threads -ne $Threads) {
        Complete-Run 'ENGINE_FAILED' $false 1 $null 'production summary contract mismatch'
    }
    Complete-Run 'NO_HIT' $false 0
} catch {
    if ($runPath -and $statePath -and $summaryPath -and (Test-Path -LiteralPath $runPath)) {
        Complete-Run 'HARNESS_FAILED' $false 1 $null $_.Exception.Message
    }
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
