param([ValidateRange(1, 9)][int] $ThrottleLimit = 9)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$runtime = Join-Path $root 'tmp\fanout\_runtime\codex.exe'
if (-not (Test-Path -LiteralPath $runtime)) { throw "Missing runtime: $runtime" }

$lanes = @(
  'lane01_n6_n10', 'lane02_n11', 'lane03_n12', 'lane04_fixtures_small',
  'lane05_fixtures_mid', 'lane06_fixtures_large', 'lane07_base_obstructions',
  'lane08_adversarial_cage', 'lane09_referee'
)

$lanes | ForEach-Object -Parallel {
  $lane = $_
  $laneDir = Join-Path $using:PSScriptRoot $lane
  $prompt = Join-Path $laneDir 'prompt.md'
  $final = Join-Path $laneDir 'final.md'
  $stdout = Join-Path $laneDir 'stdout.log'
  $stderr = Join-Path $laneDir 'stderr.log'
  $exitCode = Join-Path $laneDir 'exit_code.txt'
  $effective = Join-Path $laneDir 'effective_prompt.md'
  $common = Get-Content (Join-Path $using:PSScriptRoot 'COMMON.md') -Raw
  $task = Get-Content $prompt -Raw
  ($common + "`r`n`r`nASSIGNED TASK:`r`n" + $task) | Set-Content -Encoding utf8 $effective
  $proc = Start-Process -FilePath $using:runtime -ArgumentList @(
    '-a', 'never', 'exec', '-C', $using:root, '-s', 'workspace-write',
    '--ephemeral', '--color', 'never', '-o', $final, '-'
  ) -RedirectStandardInput $effective -RedirectStandardOutput $stdout `
    -RedirectStandardError $stderr -WindowStyle Hidden -Wait -PassThru
  $proc.ExitCode | Set-Content -Encoding ascii $exitCode
} -ThrottleLimit $ThrottleLimit
