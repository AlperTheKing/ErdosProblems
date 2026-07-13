param()

$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$formal = Join-Path $root 'formal-conjectures'
$cache = Join-Path $root 'tmp\claude_lean_o_base_v1'
$lake = 'C:\Users\a\.elan\toolchains\leanprover--lean4---v4.27.0\bin\lake.exe'
$src = Join-Path $PSScriptRoot 'MissingProviderSymbolsProbe.lean'
$out = Join-Path $PSScriptRoot 'olean\MissingProviderSymbolsProbe.olean'
$log = Join-Path $PSScriptRoot 'logs\missing_provider_symbols.log'

$env:LEAN_PATH = $cache
Push-Location $formal
& $lake env lean "--root=$root" "--o=$out" $src *> $log
$rc = $LASTEXITCODE
Pop-Location

$errorCount = @(Select-String -LiteralPath $log -SimpleMatch 'error:').Count
Write-Output "missing_symbols_rc=$rc error_count=$errorCount"
if ($rc -eq 0 -or $errorCount -ne 5) { exit 1 }
exit 0
