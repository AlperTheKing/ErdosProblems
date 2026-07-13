param([ValidateRange(1,9)][int]$ThrottleLimit = 9)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$runtime = Join-Path $root 'tmp\fanout\_runtime\codex.exe'

1..9 | ForEach-Object -Parallel {
    $lane = 'child_{0:D2}' -f $_
    $dir = Join-Path $using:root "tmp\fanout\r29_fullbank_referee\$lane"
    $prompt = Join-Path $dir 'prompt.md'
    $final = Join-Path $dir 'final.md'
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

