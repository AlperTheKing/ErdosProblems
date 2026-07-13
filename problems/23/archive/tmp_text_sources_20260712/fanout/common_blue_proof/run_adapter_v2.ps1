$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$runtime = Join-Path $root 'tmp\fanout\_runtime\codex.exe'
$dir = Join-Path $PSScriptRoot 'child_07_adapter'
$proc = Start-Process -FilePath $runtime -ArgumentList @(
  '-a','never','exec','-C',$root,'-s','workspace-write','--ephemeral',
  '--color','never','-o',(Join-Path $dir 'FINAL_V2.md'),'-'
) -RedirectStandardInput (Join-Path $dir 'PROMPT_V2.md') `
  -RedirectStandardOutput (Join-Path $dir 'stdout_v2.log') `
  -RedirectStandardError (Join-Path $dir 'stderr_v2.log') `
  -WindowStyle Hidden -Wait -PassThru
$proc.ExitCode | Set-Content -Encoding ascii (Join-Path $dir 'exit_code_v2.txt')
exit $proc.ExitCode
