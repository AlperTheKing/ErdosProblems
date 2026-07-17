# rebuild_and_probe.ps1 — honest rebuild + axiom probe of
# Erdos23Delta0.Gamma.LiveMiddleSwapCrossOuter.live_middle_swap_has_cross_outer
#
# The module's transitive import chain (5 files, linear) is elaborated from
# source against a Lake workspace that has Mathlib oleans built, then a probe
# file runs `#print axioms` on the theorem against the freshly produced
# oleans. Acceptance: every axiom is in {propext, Classical.choice,
# Quot.sound}. Exit 0 only on PASS_AXIOM_PROBE; any compile failure or an
# out-of-set axiom exits 1.
#
# Usage (PowerShell 7+):
#   ./rebuild_and_probe.ps1 -LakeProject <dir with lakefile + built Mathlib> `
#                           -SourceRoot  <dir containing Erdos23Delta0/>     `
#                           [-OutDir <scratch dir>] [-Threads 8]
#
# Reference run (2026-07-17): Lean 4.27.0, mathlib rev a3a10db0e9d6,
# LakeProject = formal-conjectures checkout, SourceRoot = problems/23/lean.

param(
  [Parameter(Mandatory=$true)][string]$LakeProject,
  [Parameter(Mandatory=$true)][string]$SourceRoot,
  [string]$OutDir = (Join-Path ([System.IO.Path]::GetTempPath()) 'lmsco_axiom_probe'),
  [int]$Threads = 8
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$chain = @(
  'CertGraph',
  'Gamma\CheckedC5BaseTransfer',
  'Gamma\CheckedRowCompanionBaseTransfer',
  'Gamma\MinimumDemandRowSelection',
  'Gamma\LiveMiddleSwapCrossOuter'
)

# -- provenance: the compiled production source must be byte-identical to the
#    archived copy anc/lean/LiveMiddleSwapCrossOuter.lean (SHA 3dff7897...).
$prod = Join-Path $SourceRoot 'Erdos23Delta0\Gamma\LiveMiddleSwapCrossOuter.lean'
$arch = Join-Path $scriptDir '..\lean\LiveMiddleSwapCrossOuter.lean'
$hProd = (Get-FileHash $prod -Algorithm SHA256).Hash.ToLower()
Write-Output "SHA256(production LiveMiddleSwapCrossOuter.lean) = $hProd"
if (Test-Path $arch) {
  $hArch = (Get-FileHash $arch -Algorithm SHA256).Hash.ToLower()
  Write-Output "SHA256(archived   LiveMiddleSwapCrossOuter.lean) = $hArch"
  if ($hProd -ne $hArch) { Write-Output 'FAIL_SOURCE_MISMATCH'; exit 1 }
} else {
  Write-Output 'NOTE: archived copy not found next to this script; hash printed above only.'
}

New-Item -ItemType Directory -Force (Join-Path $OutDir 'Erdos23Delta0\Gamma') | Out-Null
$env:LEAN_PATH = $OutDir
Set-Location $LakeProject

foreach ($m in $chain) {
  $src  = Join-Path $SourceRoot "Erdos23Delta0\$m.lean"
  $ole  = Join-Path $OutDir    "Erdos23Delta0\$m.olean"
  $log  = Join-Path $OutDir    ("build_" + ($m -replace '\\','_') + '.log')
  $t    = Get-Date
  lake env lean --threads=$Threads --root=$SourceRoot -o $ole $src *> $log
  $code = $LASTEXITCODE
  $dt   = [math]::Round(((Get-Date) - $t).TotalSeconds, 1)
  Write-Output "module=$m exit=$code seconds=$dt"
  if ($code -ne 0) { Get-Content $log; Write-Output 'FAIL_BUILD'; exit 1 }
  if (Select-String -Path $log -Pattern 'error|sorry' -Quiet) {
    Get-Content $log; Write-Output 'FAIL_ERROR_TOKEN_IN_LOG'; exit 1
  }
}

$probe    = Join-Path $scriptDir 'probe_live_middle_swap.lean'
$probeLog = Join-Path $OutDir 'probe.log'
lake env lean --threads=$Threads $probe *> $probeLog
$code = $LASTEXITCODE
Get-Content $probeLog
Write-Output "probe exit=$code"
if ($code -ne 0) { Write-Output 'FAIL_PROBE'; exit 1 }

$line = Select-String -Path $probeLog -Pattern 'live_middle_swap_has_cross_outer' | Select-Object -First 1
if (-not $line -or $line.Line -notmatch 'depends on axioms:\s*\[([^\]]*)\]') {
  Write-Output 'FAIL_NO_AXIOM_LINE'; exit 1
}
$axioms  = $Matches[1] -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ }
$allowed = @('propext', 'Classical.choice', 'Quot.sound')
$bad     = $axioms | Where-Object { $allowed -notcontains $_ }
Write-Output ("axioms = [" + ($axioms -join ', ') + "]")
if ($bad) { Write-Output ("FAIL_AXIOM_OUT_OF_SET: " + ($bad -join ', ')); exit 1 }
Write-Output 'PASS_AXIOM_PROBE'
exit 0
