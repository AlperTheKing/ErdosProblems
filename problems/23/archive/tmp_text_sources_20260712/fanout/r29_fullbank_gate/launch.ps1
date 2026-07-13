param(
    [ValidateRange(1, 9)]
    [int] $ThrottleLimit = 9
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$runtime = Join-Path $root 'tmp\fanout\_runtime\codex.exe'
$common = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'COMMON.md')
$lanes = @(
    'lane01_semantics',
    'lane02_transfer',
    'lane03_reconstruct',
    'lane04_doors',
    'lane05_vertexslack',
    'lane06_c5base',
    'lane07_prune',
    'lane08_fullbank_lp',
    'lane09_referee'
)

$lanes | ForEach-Object -Parallel {
    $lane = $_
    $dir = Join-Path $using:PSScriptRoot $lane
    $promptPath = Join-Path $dir 'prompt.md'
    $effectivePath = Join-Path $dir 'effective_prompt.md'
    $finalPath = Join-Path $dir 'final.md'
    $stdoutPath = Join-Path $dir 'stdout.log'
    $stderrPath = Join-Path $dir 'stderr.log'
    $exitPath = Join-Path $dir 'exit_code.txt'

    $prompt = @"
$($using:common)

ASSIGNED LANE DIRECTORY: tmp/fanout/r29_fullbank_gate/$lane/

$(Get-Content -Raw -LiteralPath $promptPath)
"@
    $prompt | Set-Content -Encoding utf8 -LiteralPath $effectivePath
    $proc = Start-Process -FilePath $using:runtime -ArgumentList @(
        '-a', 'never', 'exec', '-C', $using:root, '-s', 'workspace-write',
        '--ephemeral', '--color', 'never',
        '-c', 'model_reasoning_effort="xhigh"',
        '-o', $finalPath, '-'
    ) -RedirectStandardInput $effectivePath -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath -WindowStyle Hidden -Wait -PassThru
    $proc.ExitCode | Set-Content -Encoding ascii -LiteralPath $exitPath
} -ThrottleLimit $ThrottleLimit

