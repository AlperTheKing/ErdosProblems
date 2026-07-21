[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$engineDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$launcher = Join-Path $engineDir 'run_unrestricted19_stochastic.ps1'
$realScalar = Join-Path $engineDir 'verify_scalar.py'
$realBitset = Join-Path $engineDir 'verify_bitset.exe'
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfff')
$auditBuild = Join-Path $PSScriptRoot "launcher-audit-build-$stamp-$PID"
New-Item -ItemType Directory -Path $auditBuild | Out-Null
$fakeSource = Join-Path $auditBuild 'launcher_fake_engine.cpp'
$fakeEngine = Join-Path $auditBuild 'launcher_fake_engine.exe'
$fakeScalar = Join-Path $auditBuild 'launcher_fake_scalar_accept.py'
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'launcher_fake_engine.cpp') -Destination $fakeSource
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'launcher_fake_scalar_accept.py') -Destination $fakeScalar

& 'C:\msys64\mingw64\bin\g++.exe' -std=c++20 -O2 -Wall -Wextra -pedantic $fakeSource -o $fakeEngine
if ($LASTEXITCODE -ne 0) { throw 'isolated fake engine compilation failed' }

function Hash([string]$Path) { (Get-FileHash -Algorithm SHA256 $Path).Hash.ToUpperInvariant() }
$sourceHash = Hash $fakeSource
$engineHash = Hash $fakeEngine
$realScalarHash = Hash $realScalar
$realBitsetHash = Hash $realBitset
$fakeScalarHash = Hash $fakeScalar
$logs = Join-Path $engineDir 'logs'
$script:passed = 0

function Assert([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

function Invoke-LauncherCase {
    param([string]$Name, [string]$Mode, [string]$ExpectedStatus,
          [int]$ExpectedExit, [switch]$AuditOnly, [switch]$FakeDisagreement,
          [switch]$BadHash)
    $run = Join-Path $logs "launcher-isolated-audit-$stamp-$PID-$Name"
    $env:SSNC_FAKE_MODE = $Mode
    $env:SSNC_FAKE_VERIFIER_EXIT = if ($FakeDisagreement) { '1' } else { '0' }
    $scalar = if ($FakeDisagreement) { $fakeScalar } else { $realScalar }
    $bitset = if ($FakeDisagreement) { $fakeEngine } else { $realBitset }
    $scalarHash = if ($FakeDisagreement) { $fakeScalarHash } else { $realScalarHash }
    $bitsetHash = if ($FakeDisagreement) { $engineHash } else { $realBitsetHash }
    $wantedEngineHash = if ($BadHash) { '0' * 64 } else { $engineHash }
    $arguments = @(
        '-NoProfile','-File',$launcher,
        '-Source',$fakeSource,'-Engine',$fakeEngine,'-RunDir',$run,
        '-ExpectedSourceSha256',$sourceHash,'-ExpectedEngineSha256',$wantedEngineHash,
        '-ScalarVerifier',$scalar,'-BitsetVerifier',$bitset,
        '-ExpectedScalarSha256',$scalarHash,'-ExpectedBitsetSha256',$bitsetHash,
        '-Threads','2','-CanarySeconds','1','-Seed','99173',
        '-TestMode','-TestProductionSeconds','60'
    )
    if ($AuditOnly) { $arguments += '-AuditOnly' }
    $output = & 'C:\Program Files\PowerShell\7\pwsh.exe' @arguments 2>&1
    $code = $LASTEXITCODE
    Assert ($code -eq $ExpectedExit) "$Name exit $code != $ExpectedExit; $output"
    if ($BadHash) {
        Assert (-not (Test-Path -LiteralPath $run)) "$Name created a run directory before hash acceptance"
    } else {
        $summaryPath = Join-Path $run 'summary.json'
        Assert (Test-Path -LiteralPath $summaryPath) "$Name omitted summary.json"
        $summary = Get-Content -Raw $summaryPath | ConvertFrom-Json
        Assert ($summary.status -eq $ExpectedStatus) "$Name status $($summary.status) != $ExpectedStatus"
        Assert ((Get-Content -Raw (Join-Path $run 'state.json') | ConvertFrom-Json).status -eq $ExpectedStatus) "$Name final state mismatch"
        Assert ((Get-ChildItem $run -Filter '*.tmp-*' -Recurse | Measure-Object).Count -eq 0) "$Name left atomic JSON temporaries"
        if ($ExpectedStatus -ne 'VERIFIED_COUNTEREXAMPLE') {
            Assert (-not $summary.independently_verified) "$Name set independently_verified"
        }
    }
    ++$script:passed
}

try {
    Invoke-LauncherCase -Name 'bad-hash' -Mode normal -ExpectedStatus '' -ExpectedExit 1 -BadHash
    Invoke-LauncherCase -Name 'selftest-nonzero' -Mode selftest_fail -ExpectedStatus SELF_TEST_FAILED -ExpectedExit 1
    Invoke-LauncherCase -Name 'canary-timeout' -Mode canary_timeout -ExpectedStatus CANARY_TIMEOUT -ExpectedExit 1
    Invoke-LauncherCase -Name 'partial-candidate' -Mode partial_candidate -ExpectedStatus INVALID_HIT_CANDIDATE -ExpectedExit 1
    Invoke-LauncherCase -Name 'verifier-disagreement' -Mode candidate -ExpectedStatus VERIFIER_DISAGREEMENT -ExpectedExit 1 -FakeDisagreement
    Invoke-LauncherCase -Name 'production-timeout' -Mode production_timeout -ExpectedStatus NO_HIT_HARD_DEADLINE -ExpectedExit 0
    Invoke-LauncherCase -Name 'audit-only-pass' -Mode normal -ExpectedStatus AUDIT_PASS_NO_PRODUCTION -ExpectedExit 0 -AuditOnly
} finally {
    Remove-Item Env:SSNC_FAKE_MODE -ErrorAction SilentlyContinue
    Remove-Item Env:SSNC_FAKE_VERIFIER_EXIT -ErrorAction SilentlyContinue
}

Write-Output ("PASS unrestricted19 isolated launcher adversarial cases={0} build_dir={1} source_sha256={2} exe_sha256={3}" -f $passed,$auditBuild,$sourceHash,$engineHash)
