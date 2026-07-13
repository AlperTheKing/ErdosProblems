param()

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$formal = Join-Path $root 'formal-conjectures'
$srcRoot = Join-Path $root 'problems\23\lean'
$cache = Join-Path $root 'tmp\claude_lean_o_base_v1'
$lake = 'C:\Users\a\.elan\toolchains\leanprover--lean4---v4.27.0\bin\lake.exe'
$outRoot = Join-Path $PSScriptRoot 'chain_olean'
$logRoot = Join-Path $PSScriptRoot 'logs\chain'

$modules = @(
  'Gamma\TypedFullBankSources',
  'Gamma\CheckedRowCompanionBaseTransfer',
  'CollisionTokenAssignment',
  'Ell5ActiveComponentBankHall',
  'Gamma\FullBankToLengthSurplusCharge',
  'Gamma\FullBankPortSinks',
  'Gamma\FullBankChargeCertProvider',
  'BranchB\PureUPOK0',
  'PackageProviderSkeleton'
)

New-Item -ItemType Directory -Force -Path $logRoot | Out-Null
$env:LEAN_PATH = $cache
Push-Location $formal
$failed = 0
foreach ($module in $modules) {
  $src = Join-Path $srcRoot ('Erdos23Delta0\' + $module + '.lean')
  $out = Join-Path $outRoot ('Erdos23Delta0\' + $module + '.olean')
  $log = Join-Path $logRoot (($module -replace '\\','__') + '.log')
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $out) | Out-Null
  $sw = [Diagnostics.Stopwatch]::StartNew()
  & $lake env lean "--root=$srcRoot" "--o=$out" $src *> $log
  $rc = $LASTEXITCODE
  $sw.Stop()
  $hasError = Select-String -LiteralPath $log -SimpleMatch 'error:' -Quiet
  $hasForbidden = Select-String -LiteralPath $src -Pattern '\bsorry\b|\badmit\b|native_decide|sorryAx' -Quiet
  Write-Output ("module={0} rc={1} error={2} forbidden={3} ms={4}" -f
    $module,$rc,$hasError,$hasForbidden,$sw.ElapsedMilliseconds)
  if ($rc -ne 0 -or $hasError -or $hasForbidden) { $failed++ }
}
Pop-Location
if ($failed -ne 0) { exit 1 }
