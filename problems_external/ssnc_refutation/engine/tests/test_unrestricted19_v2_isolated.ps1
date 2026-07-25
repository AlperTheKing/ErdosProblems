[CmdletBinding()]
param(
    [string]$Source,
    [string]$SeedFile,
    [string]$Compiler = 'C:\msys64\mingw64\bin\g++.exe'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (Test-Path variable:PSNativeCommandUseErrorActionPreference) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$engineDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$projectDir = (Resolve-Path (Join-Path $engineDir '..')).Path
if ([string]::IsNullOrWhiteSpace($Source)) {
    $Source = Join-Path $engineDir 'unrestricted19_stochastic_v2.cpp'
}
if ([string]::IsNullOrWhiteSpace($SeedFile)) {
    $SeedFile = Join-Path $projectDir 'theory_inputs\unrestricted19-q5-twin-fill-objective9.json'
}
$contract = Join-Path $projectDir 'UNRESTRICTED19_LEX_V2_INTEGRATED_CONTRACT.md'

$expectedContractSha = 'BCFD8319E9569FDED0373415F02516A1F71DFDD63B83DC4A59D29556D486801D'
$expectedSeedSha = '32CAB5626FAC027D1BD379A3063D8ADB8C9D4B4B1CC5AB65540323F582B6B6DA'
$expectedSeedBytes = 471
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfff')
$auditRoot = Join-Path $PSScriptRoot "unrestricted19-v2-isolated-$stamp-$PID"
$engine = Join-Path $auditRoot 'unrestricted19_stochastic_v2_audit.exe'
$script:passed = 0

function Assert([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

function Hash([string]$Path) {
    (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Invoke-Engine([string[]]$Arguments) {
    $lines = @(& $engine @Arguments 2>&1 | ForEach-Object { $_.ToString() })
    [pscustomobject]@{
        ExitCode = $LASTEXITCODE
        Lines = $lines
        Text = ($lines -join "`n")
    }
}

function Read-SingleJson([object]$Invocation, [string]$CaseName) {
    $jsonLines = @($Invocation.Lines | Where-Object { $_.TrimStart().StartsWith('{') })
    Assert ($jsonLines.Count -eq 1) "$CaseName emitted $($jsonLines.Count) JSON lines: $($Invocation.Text)"
    try {
        return $jsonLines[0] | ConvertFrom-Json
    } catch {
        throw "$CaseName emitted invalid JSON: $($Invocation.Text)"
    }
}

function Require-Field([object]$Object, [string]$Name, [string]$CaseName) {
    Assert ($Object.PSObject.Properties.Name -contains $Name) "$CaseName omitted field $Name"
    return $Object.$Name
}

function Invoke-NegativePreartifact {
    param(
        [string]$Name,
        [string[]]$Arguments,
        [string]$ExpectedToken,
        [string[]]$ForbiddenDirectories
    )
    foreach ($directory in $ForbiddenDirectories) {
        Assert (-not (Test-Path -LiteralPath $directory)) "$Name precondition failed: $directory already exists"
    }
    $result = Invoke-Engine $Arguments
    Assert ($result.ExitCode -ne 0) "$Name unexpectedly returned success: $($result.Text)"
    Assert ($result.Text.Contains($ExpectedToken)) "$Name omitted $ExpectedToken: $($result.Text)"
    foreach ($directory in $ForbiddenDirectories) {
        Assert (-not (Test-Path -LiteralPath $directory)) "$Name created pre-artifact directory $directory"
    }
    ++$script:passed
}

function Write-Utf8Mutant([string]$Name, [string]$Text) {
    $path = Join-Path $auditRoot "$Name.json"
    $utf8 = [System.Text.UTF8Encoding]::new($false, $true)
    [System.IO.File]::WriteAllBytes($path, $utf8.GetBytes($Text))
    return $path
}

function Write-ByteMutant([string]$Name, [byte[]]$Bytes) {
    $path = Join-Path $auditRoot "$Name.json"
    [System.IO.File]::WriteAllBytes($path, $Bytes)
    return $path
}

Assert (Test-Path -LiteralPath $Source -PathType Leaf) "missing v2 source: $Source"
Assert (Test-Path -LiteralPath $SeedFile -PathType Leaf) "missing registered seed: $SeedFile"
Assert (Test-Path -LiteralPath $Compiler -PathType Leaf) "missing compiler: $Compiler"
Assert (Test-Path -LiteralPath $contract -PathType Leaf) "missing integrated contract: $contract"
Assert ((Hash $contract) -eq $expectedContractSha) 'integrated contract SHA-256 drifted'
Assert ((Hash $SeedFile) -eq $expectedSeedSha) 'registered seed SHA-256 drifted'
Assert ((Get-Item -LiteralPath $SeedFile).Length -eq $expectedSeedBytes) 'registered seed byte count drifted'

New-Item -ItemType Directory -Path $auditRoot | Out-Null
& $Compiler -std=c++20 -O2 -Wall -Wextra -pedantic $Source -o $engine
Assert ($LASTEXITCODE -eq 0) 'isolated v2 compilation failed'

# This is the only successful engine invocation.  Self-test mode must perform
# no production search and must directly exercise internal parser/rank/race
# oracles which cannot be reached past the frozen production seed hash.
$positive = Invoke-Engine @('--self-test', '--seed', '2026072201', '--seed-file', $SeedFile)
Assert ($positive.ExitCode -eq 0) "registered-seed self-test failed: $($positive.Text)"
$report = Read-SingleJson $positive 'registered-seed self-test'
Assert ((Require-Field $report 'schema' 'registered-seed self-test') -eq 'ssnc-unrestricted19-self-test-v2') 'wrong v2 self-test schema'
Assert ((Require-Field $report 'status' 'registered-seed self-test') -eq 'SELF_TEST_PASS') 'v2 self-test did not pass'
Assert (-not [bool](Require-Field $report 'production_run' 'registered-seed self-test')) 'self-test claimed a production run'
Assert ([bool](Require-Field $report 'seeded_mode' 'registered-seed self-test')) 'self-test did not enter seeded mode'
Assert ((Require-Field $report 'fixed_q' 'registered-seed self-test') -eq 5) 'self-test fixed_q mismatch'
Assert ((Require-Field $report 'seed_file_sha256' 'registered-seed self-test').ToUpperInvariant() -eq $expectedSeedSha) 'self-test seed SHA mismatch'
Assert ((Require-Field $report 'seed_file_bytes' 'registered-seed self-test') -eq 471) 'self-test seed bytes mismatch'
Assert ((Require-Field $report 'effective_warmup_steps' 'registered-seed self-test') -eq 0) 'seeded self-test warmup was not zero'
Assert ((Require-Field $report 'best_order' 'registered-seed self-test') -eq 'objective_then_smooth') 'best ordering metadata mismatch'
Assert ((Require-Field $report 'rank_stride' 'registered-seed self-test') -eq 457) 'rank stride mismatch'
Assert ((Require-Field $report 'rank_max' 'registered-seed self-test') -eq 26505) 'rank maximum mismatch'
Assert ((Require-Field $report 'acceptance_rule' 'registered-seed self-test') -eq 'objective_delta_if_nonzero_else_smooth_delta') 'acceptance metadata mismatch'
Assert ((Require-Field $report 'seed_origin' 'registered-seed self-test') -eq 'registered_seed') 'seed origin mismatch'

$ledger = Require-Field $report 'seed_gate_ledger' 'registered-seed self-test'
$ledgerN = if ($ledger.PSObject.Properties.Name -contains 'n') { $ledger.n } else { $ledger.n19 }
$ledgerQ = if ($ledger.PSObject.Properties.Name -contains 'q') { $ledger.q } else { $ledger.q5 }
Assert (($ledgerN -eq 19) -or ($ledgerN -eq $true)) 'seed gate n19 mismatch'
Assert (($ledgerQ -eq 5) -or ($ledgerQ -eq $true)) 'seed gate q5 mismatch'
Assert ($ledger.arcs -eq 166) 'seed gate arc count mismatch'
Assert ($ledger.min_outdegree -eq 8) 'seed gate minimum outdegree mismatch'
Assert ($ledger.objective -eq 9) 'seed gate objective mismatch'
Assert ($ledger.smooth -eq 18) 'seed gate smooth mismatch'
Assert ($ledger.failing_mask -eq 451154) 'seed gate failing mask mismatch'

$requiredAudits = @(
    'sha256_kat_empty',
    'sha256_kat_abc',
    'sha256_kat_multiblock',
    'seed_positive_gate',
    'parser_whitespace_rejected',
    'parser_bom_rejected',
    'parser_crlf_rejected',
    'parser_trailing_bytes_rejected',
    'parser_key_order_rejected',
    'parser_leading_zero_rejected',
    'parser_duplicate_neighbor_rejected',
    'parser_unsorted_neighbor_rejected',
    'parser_unknown_schema_rejected',
    'rank_examples',
    'rank_smooth_457_rejected',
    'seeded_warmup_omitted_zero',
    'seeded_warmup_explicit_zero',
    'seeded_warmup_positive_preartifact',
    'unseeded_warmup_zero_rejected',
    'best_contention_minimum',
    'counter_partition_seeded',
    'counter_partition_unseeded',
    'raw_hit_exact_schema',
    'conditional_provenance'
)
$audited = @(Require-Field $report 'audited' 'registered-seed self-test')
foreach ($marker in $requiredAudits) {
    Assert ($audited -contains $marker) "self-test omitted audit marker $marker"
}
++ $script:passed

$seedBytes = [System.IO.File]::ReadAllBytes($SeedFile)
$utf8Strict = [System.Text.UTF8Encoding]::new($false, $true)
$canonical = $utf8Strict.GetString($seedBytes)
Assert ($canonical.EndsWith("`n")) 'registered seed omitted terminal LF'
Assert (-not $canonical.Contains("`r")) 'registered seed unexpectedly contains CR'
$prefix = '{"n":19,"out_neighbors":'
Assert ($canonical.StartsWith($prefix)) 'registered seed canonical prefix drifted'
$rowsJson = $canonical.Substring($prefix.Length, $canonical.Length - $prefix.Length - 2)
Assert ($rowsJson.StartsWith('[') -and $rowsJson.EndsWith(']')) 'cannot isolate registered adjacency rows'

$mutants = [ordered]@{}
$mutants.whitespace = Write-ByteMutant 'whitespace' ([byte[]](@([byte][char]' ') + $seedBytes))
$mutants.bom = Write-ByteMutant 'bom' ([byte[]](@(0xEF, 0xBB, 0xBF) + $seedBytes))
$mutants.crlf = Write-ByteMutant 'crlf' ([byte[]]($seedBytes[0..($seedBytes.Length - 2)] + @(0x0D, 0x0A)))
$mutants.trailing = Write-ByteMutant 'trailing' ([byte[]]($seedBytes + @([byte][char]' ')))
$mutants.key_order = Write-Utf8Mutant 'key-order' ('{"out_neighbors":' + $rowsJson + ',"n":19}' + "`n")
$mutants.leading_zero = Write-Utf8Mutant 'leading-zero' ($canonical.Replace('{"n":19,', '{"n":019,'))
$mutants.duplicate_neighbor = Write-Utf8Mutant 'duplicate-neighbor' ($canonical.Replace('[[3,5,6,', '[[3,3,5,6,'))
$mutants.unsorted_neighbor = Write-Utf8Mutant 'unsorted-neighbor' ($canonical.Replace('[[3,5,6,', '[[5,3,6,'))
$mutants.schema = Write-Utf8Mutant 'schema' ($canonical.Substring(0, $canonical.Length - 2) + ',"extra":0}' + "`n")

foreach ($entry in $mutants.GetEnumerator()) {
    Assert ((Hash $entry.Value) -ne $expectedSeedSha) "$($entry.Key) mutant retained the registered SHA"
    $forbidden = Join-Path $auditRoot "forbidden-mutant-$($entry.Key)"
    Invoke-NegativePreartifact -Name "mutant-$($entry.Key)" `
        -Arguments @('--search', '--threads', '1', '--seconds', '1', '--seed', '7',
                     '--seed-file', $entry.Value, '--output-dir', $forbidden) `
        -ExpectedToken 'SEED_HASH_MISMATCH' -ForbiddenDirectories @($forbidden)
}

# Every invocation below is invalid by construction and must exit before
# creating its requested output directory.  No valid search invocation occurs.
$warmupPositiveDir = Join-Path $auditRoot 'forbidden-seeded-positive-warmup'
Invoke-NegativePreartifact -Name 'seeded-positive-warmup' `
    -Arguments @('--search', '--threads', '1', '--seconds', '1', '--seed', '11',
                 '--seed-file', $SeedFile, '--warmup-steps', '1',
                 '--output-dir', $warmupPositiveDir) `
    -ExpectedToken 'SEEDED_WARMUP_NONZERO' -ForbiddenDirectories @($warmupPositiveDir)

$unseededZeroDir = Join-Path $auditRoot 'forbidden-unseeded-zero-warmup'
Invoke-NegativePreartifact -Name 'unseeded-zero-warmup' `
    -Arguments @('--search', '--threads', '1', '--seconds', '1', '--seed', '13',
                 '--warmup-steps', '0', '--output-dir', $unseededZeroDir) `
    -ExpectedToken 'warmup' -ForbiddenDirectories @($unseededZeroDir)

$duplicateCases = @(
    @{ Name = 'seed-file'; Extra = @('--seed-file', $SeedFile) },
    @{ Name = 'warmup-steps'; Extra = @('--warmup-steps', '0', '--warmup-steps', '0') },
    @{ Name = 'threads'; Extra = @('--threads', '1') },
    @{ Name = 'seconds'; Extra = @('--seconds', '1') },
    @{ Name = 'seed'; Extra = @('--seed', '17') },
    @{ Name = 'restart-steps'; Extra = @('--restart-steps', '100') },
    @{ Name = 'checkpoint-ms'; Extra = @('--checkpoint-ms', '100') }
)
foreach ($case in $duplicateCases) {
    $forbidden = Join-Path $auditRoot "forbidden-duplicate-$($case.Name)"
    $base = @('--search', '--threads', '1', '--seconds', '1', '--seed', '17',
              '--seed-file', $SeedFile, '--restart-steps', '100',
              '--checkpoint-ms', '100', '--output-dir', $forbidden)
    if ($case.Name -eq 'warmup-steps') {
        $arguments = $base + $case.Extra
    } else {
        $arguments = $base + $case.Extra
    }
    Invoke-NegativePreartifact -Name "duplicate-$($case.Name)" -Arguments $arguments `
        -ExpectedToken 'DUPLICATE_OPTION' -ForbiddenDirectories @($forbidden)
}

$duplicateOutputA = Join-Path $auditRoot 'forbidden-duplicate-output-a'
$duplicateOutputB = Join-Path $auditRoot 'forbidden-duplicate-output-b'
Invoke-NegativePreartifact -Name 'duplicate-output-dir' `
    -Arguments @('--search', '--threads', '1', '--seconds', '1', '--seed', '19',
                 '--seed-file', $SeedFile, '--output-dir', $duplicateOutputA,
                 '--output-dir', $duplicateOutputB) `
    -ExpectedToken 'DUPLICATE_OPTION' `
    -ForbiddenDirectories @($duplicateOutputA, $duplicateOutputB)

Write-Output ("PASS unrestricted19 v2 isolated audit cases={0} contract_sha256={1} seed_sha256={2} source_sha256={3} exe_sha256={4} build_dir={5}" -f `
    $passed, $expectedContractSha, $expectedSeedSha, (Hash $Source), (Hash $engine), $auditRoot)
