param(
    [ValidateRange(1, 10)]
    [int] $ThrottleLimit = 10
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$runtime = Join-Path $root 'tmp\fanout\_runtime\codex.exe'
$sourceRoot = Join-Path $root 'tmp\fanout\referee_alt'
$destRoot = Join-Path $PSScriptRoot 'referee_alt'

1..10 | ForEach-Object -Parallel {
    $lane = 'child_{0:D2}' -f $_
    $sourcePrompt = Join-Path $using:sourceRoot "$lane\prompt.txt"
    $outDir = Join-Path $using:destRoot $lane
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null

    $override = @"
RECOVERY RELAUNCH OVERRIDE (newer and controlling): The original lane failed before any command ran. You may read the workspace and execute computations, but MUST NOT edit production proof files, PROGRESS_CODEX.md, coordination mailboxes, or any path outside tmp/fanout/_runtime_recovery/referee_alt/$lane/. Replace every original output-path instruction with this recovery path. Do not spawn descendants. Your final response is captured as final.md by the launcher. Do not invent results.

"@
    $prompt = $override + (Get-Content $sourcePrompt -Raw)
    $promptPath = Join-Path $outDir 'effective_prompt.md'
    $final = Join-Path $outDir 'final.md'
    $stdout = Join-Path $outDir 'stdout.log'
    $stderr = Join-Path $outDir 'stderr.log'
    $exitCode = Join-Path $outDir 'exit_code.txt'

    $prompt | Set-Content -Encoding utf8 $promptPath
    $proc = Start-Process -FilePath $using:runtime -ArgumentList @(
        '-a', 'never', 'exec', '-C', $using:root, '-s', 'workspace-write',
        '--ephemeral', '--color', 'never', '-o', $final, '-'
    ) -RedirectStandardInput $promptPath -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr -WindowStyle Hidden -Wait -PassThru
    $proc.ExitCode | Set-Content -Encoding ascii $exitCode
} -ThrottleLimit $ThrottleLimit
