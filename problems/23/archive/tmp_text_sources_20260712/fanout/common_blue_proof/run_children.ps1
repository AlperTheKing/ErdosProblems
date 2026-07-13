param([ValidateRange(1,9)][int]$ThrottleLimit = 9)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$runtime = Join-Path $root 'tmp\fanout\_runtime\codex.exe'
$lanes = @(
  'child_01_shore','child_02_maxcut','child_03_surplus',
  'child_04_finite_gate','child_05_dual','child_06_lean',
  'child_07_adapter','child_08_falsifier','child_09_referee'
)

$lanes | ForEach-Object -Parallel {
  $dir = Join-Path $using:PSScriptRoot $_
  $prompt = Join-Path $dir 'PROMPT.md'
  $final = Join-Path $dir 'FINAL.md'
  $stdout = Join-Path $dir 'stdout.log'
  $stderr = Join-Path $dir 'stderr.log'
  $exitCode = Join-Path $dir 'exit_code.txt'
  $proc = Start-Process -FilePath $using:runtime -ArgumentList @(
    '-a','never','exec','-C',$using:root,'-s','workspace-write',
    '--ephemeral','--color','never','-o',$final,'-'
  ) -RedirectStandardInput $prompt -RedirectStandardOutput $stdout `
    -RedirectStandardError $stderr -WindowStyle Hidden -Wait -PassThru
  $proc.ExitCode | Set-Content -Encoding ascii $exitCode
} -ThrottleLimit $ThrottleLimit
