param(
    [ValidateRange(1, 9)]
    [int] $ThrottleLimit = 9
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$runtime = Join-Path $root 'tmp\fanout\_runtime\codex.exe'
$common = Get-Content (Join-Path $PSScriptRoot 'COMMON.md') -Raw
$promptRoot = Join-Path $PSScriptRoot 'prompts'

1..9 | ForEach-Object -Parallel {
    $lane = 'child_{0:D2}' -f $_
    $outDir = Join-Path $using:PSScriptRoot $lane
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    $specific = Get-Content (Join-Path $using:promptRoot "$lane.md") -Raw
    $prompt = $using:common + "`r`n`r`nASSIGNED QUESTION:`r`n" + $specific +
        "`r`n`r`nYour only writable directory is tmp/fanout/r29_fullbank_repair/$lane/."
    $promptPath = Join-Path $outDir 'effective_prompt.md'
    $final = Join-Path $outDir 'final.md'
    $stdout = Join-Path $outDir 'stdout.log'
    $stderr = Join-Path $outDir 'stderr.log'
    $exitCode = Join-Path $outDir 'exit_code.txt'
    $prompt | Set-Content -Encoding utf8 $promptPath
    $proc = Start-Process -FilePath $using:runtime -ArgumentList @(
        '-a', 'never', 'exec', '-C', $using:root, '-s', 'workspace-write',
        '-m', 'gpt-5.6-sol', '-c', 'model_reasoning_effort="xhigh"',
        '--ephemeral', '--color', 'never', '-o', $final, '-'
    ) -RedirectStandardInput $promptPath -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr -WindowStyle Hidden -Wait -PassThru
    $proc.ExitCode | Set-Content -Encoding ascii $exitCode
} -ThrottleLimit $ThrottleLimit
