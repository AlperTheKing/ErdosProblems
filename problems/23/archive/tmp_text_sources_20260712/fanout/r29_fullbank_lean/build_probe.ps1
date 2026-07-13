param()

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$formal = Join-Path $root 'formal-conjectures'
$srcRoot = Join-Path $root 'problems\23\lean'
$cache = Join-Path $root 'tmp\claude_lean_o_base_v1'
$lake = 'C:\Users\a\.elan\toolchains\leanprover--lean4---v4.27.0\bin\lake.exe'
$outRoot = Join-Path $PSScriptRoot 'olean'
$logRoot = Join-Path $PSScriptRoot 'logs'

New-Item -ItemType Directory -Force -Path (Join-Path $outRoot 'Erdos23Delta0') | Out-Null
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null
$env:LEAN_PATH = $cache
Push-Location $formal

$probe = Join-Path $PSScriptRoot 'ProviderSeamProbe.lean'
$probeOut = Join-Path $outRoot 'ProviderSeamProbe.olean'
$probeLog = Join-Path $logRoot 'probe_build.log'
& $lake env lean "--root=$root" "--o=$probeOut" $probe *> $probeLog
$probeRc = $LASTEXITCODE

Write-Output "probe_rc=$probeRc"
Pop-Location
if ($probeRc -ne 0) { exit 1 }
