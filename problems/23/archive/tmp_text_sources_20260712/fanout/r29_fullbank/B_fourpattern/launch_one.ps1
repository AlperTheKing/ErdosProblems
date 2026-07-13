param([Parameter(Mandatory=$true)][int]$Worker)
$ErrorActionPreference = "Continue"
$root = "E:\Projects\ErdosProblems"
$dir = Join-Path $root "tmp\fanout\r29_fullbank\B_fourpattern\worker_$Worker"
$prompt = Join-Path $dir "PROMPT.txt"
$stdout = Join-Path $dir "events.jsonl"
$stderr = Join-Path $dir "stderr.txt"
$last = Join-Path $dir "LAST_MESSAGE.md"
Get-Content -Raw $prompt |
  & codex exec --ephemeral --json --dangerously-bypass-approvals-and-sandbox -C $root -o $last - 1> $stdout 2> $stderr
exit $LASTEXITCODE
