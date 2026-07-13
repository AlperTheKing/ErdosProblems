$ErrorActionPreference = "Continue"
$dir = "E:\Projects\ErdosProblems\tmp\agent_hunt\falsifier_t6"
Set-Location $dir
# Wave 3: CUT-TIGHT DOUBLE-STAR circuit search (outward >= 2t = 12).
# Feasible support cells per cuttight_star_feasibility.json.
$splits = @(
    @(11,10), @(12,9), @(12,12), @(13,13)
)
$procs = @()
foreach ($s in $splits) {
    $l = $s[0]; $r = $s[1]
    $out = "t6_cuttight_l${l}_r${r}.json"
    $log = "t6_cuttight_l${l}_r${r}.log"
    $p = Start-Process -FilePath "python" -ArgumentList @(
        "sweep_t6_cuttight_star.py", "--t", "6",
        "--left", "$l", "--right", "$r",
        "--max-supports", "120",
        "--support-time", "60", "--circuit-time", "240",
        "--max-hits", "3",
        "--output", $out
    ) -RedirectStandardOutput $log -RedirectStandardError "$log.err" -PassThru -WindowStyle Hidden
    $procs += "$($p.Id) cuttight_l${l}_r${r}"
}
$procs | Set-Content wave3_pids.txt
Write-Output "launched: $($procs -join '; ')"
