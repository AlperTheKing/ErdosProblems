param()

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$formal = Join-Path $root 'formal-conjectures'
$srcRoot = Join-Path $root 'problems\23\lean'
$cache = Join-Path $root 'tmp\claude_lean_o_base_v1'
$lake = 'C:\Users\a\.elan\toolchains\leanprover--lean4---v4.27.0\bin\lake.exe'
$src = Join-Path $srcRoot 'Erdos23Delta0\Gamma\CommonBlueExtendedMatching.lean'
$out = Join-Path $PSScriptRoot 'olean\Erdos23Delta0\Gamma\CommonBlueExtendedMatching.olean'
$log = Join-Path $PSScriptRoot 'logs\commonblue_rebuild.log'

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $out) | Out-Null
$env:LEAN_PATH = $cache
Push-Location $formal
& $lake env lean "--root=$srcRoot" "--o=$out" $src *> $log
$rc = $LASTEXITCODE
Pop-Location

$hasError = Select-String -LiteralPath $log -SimpleMatch 'error:' -Quiet
$hasForbidden = Select-String -LiteralPath $src -Pattern '\bsorry\b|\badmit\b|native_decide|sorryAx' -Quiet
Write-Output "commonblue_rc=$rc error=$hasError forbidden=$hasForbidden"
if ($rc -ne 0 -or $hasError -or $hasForbidden) { exit 1 }
