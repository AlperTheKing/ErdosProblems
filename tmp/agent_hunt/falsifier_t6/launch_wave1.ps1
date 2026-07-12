$ErrorActionPreference = "Continue"
$dir = "E:\Projects\ErdosProblems\tmp\agent_hunt\falsifier_t6"
Set-Location $dir
$splits = @(
    @(10,10), @(11,9), @(12,8), @(13,7),
    @(10,11), @(11,10), @(12,9), @(13,8)
)
$procs = @()
foreach ($s in $splits) {
    $l = $s[0]; $r = $s[1]
    $out = "t6_sweep_l${l}_r${r}_2000.json"
    $log = "t6_sweep_l${l}_r${r}_2000.log"
    $p = Start-Process -FilePath "python" -ArgumentList @(
        "rooted_tN_support_cp_sat.py", "--t", "6",
        "--left", "$l", "--right", "$r",
        "--max-supports", "2000",
        "--support-time", "30", "--circuit-time", "120",
        "--local-classifier", "v", "--require-active-scope",
        "--max-hits", "3",
        "--output", $out
    ) -RedirectStandardOutput $log -RedirectStandardError "$log.err" -PassThru -WindowStyle Hidden
    $procs += "$($p.Id) l${l}_r${r}"
}
$procs | Set-Content wave1_pids.txt
Write-Output "launched: $($procs -join '; ')"
