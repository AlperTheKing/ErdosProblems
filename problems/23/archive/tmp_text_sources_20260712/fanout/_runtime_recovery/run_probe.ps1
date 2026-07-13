param()

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$runtime = Join-Path $root 'tmp\fanout\_runtime\codex.exe'
$outDir = Join-Path $PSScriptRoot 'probe'
$final = Join-Path $outDir 'final.md'
$stdout = Join-Path $outDir 'stdout.log'
$stderr = Join-Path $outDir 'stderr.log'
$exitCode = Join-Path $outDir 'exit_code.txt'
$promptPath = Join-Path $outDir 'prompt.md'

New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$prompt = @"
This is a read-only runtime recovery probe. Use the command tool exactly once to run:
Get-Location; Test-Path 'tmp/fanout/_runtime/codex-code-mode-host.exe'; Get-FileHash 'tmp/fanout/_runtime/codex-code-mode-host.exe' -Algorithm SHA256
Do not edit any file. Return the working directory, Boolean, and full SHA256 only, prefixed by CHILD_HOST_PROBE.
"@

$prompt | Set-Content -Encoding utf8 $promptPath
$proc = Start-Process -FilePath $runtime -ArgumentList @(
    '-a', 'never', 'exec', '-C', $root, '-s', 'read-only',
    '--ephemeral', '--color', 'never', '-o', $final, '-'
) -RedirectStandardInput $promptPath -RedirectStandardOutput $stdout `
    -RedirectStandardError $stderr -WindowStyle Hidden -Wait -PassThru
$proc.ExitCode | Set-Content -Encoding ascii $exitCode
exit $proc.ExitCode
