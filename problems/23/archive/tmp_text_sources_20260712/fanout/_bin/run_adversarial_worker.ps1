param(
    [Parameter(Mandatory = $true)]
    [string] $Lane
)

$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$dir = Join-Path $root "tmp\fanout\adversarial_search_$Lane"
$exe = Join-Path $root 'tmp\fanout\_bin\codex.exe'
$prompt = Get-Content (Join-Path $dir 'PROMPT.md') -Raw

& $exe -a never exec -C $root -s workspace-write --ephemeral --color never -o (Join-Path $dir 'FINAL.md') $prompt 1> (Join-Path $dir 'stdout.log') 2> (Join-Path $dir 'stderr.log')
$LASTEXITCODE | Set-Content (Join-Path $dir 'exit_code.txt')
