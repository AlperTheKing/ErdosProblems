$dir = "E:\Projects\ErdosProblems\tmp\agent_hunt\falsifier_t6"
Set-Location $dir
$deadline = (Get-Date).AddMinutes(75)
while ((Get-Date) -lt $deadline) {
    $sweeps = @(Get-ChildItem "t6_sweep_*.json" -ErrorAction SilentlyContinue)
    $parity = @(Get-ChildItem "t5_parity_*.json" -ErrorAction SilentlyContinue)
    if ($sweeps.Count -ge 8 -and $parity.Count -ge 1) { break }
    Start-Sleep -Seconds 30
}
$lines = @()
foreach ($f in (Get-ChildItem "t6_sweep_*.json", "t5_parity_*.json" -ErrorAction SilentlyContinue)) {
    $lines += (python summarize_result.py $f.Name 2>&1)
}
$lines | Set-Content wave1_summary.txt
$lines | Write-Output
