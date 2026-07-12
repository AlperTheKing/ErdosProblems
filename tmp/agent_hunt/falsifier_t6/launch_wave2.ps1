$ErrorActionPreference = "Continue"
$dir = "E:\Projects\ErdosProblems\tmp\agent_hunt\falsifier_t6"
Set-Location $dir
# Wave 2: high-order SPREAD regime (R51 s10: CheapGeometry plausible-false on
# spread high-order circuits).  Balanced shores maximize d4-pair supply.
$splits = @(
    @(12,12), @(13,13), @(14,14), @(15,15)
)
$procs = @()
foreach ($s in $splits) {
    $l = $s[0]; $r = $s[1]
    $out = "t6_sweep_l${l}_r${r}_w2.json"
    $log = "t6_sweep_l${l}_r${r}_w2.log"
    $p = Start-Process -FilePath "python" -ArgumentList @(
        "rooted_tN_support_cp_sat.py", "--t", "6",
        "--left", "$l", "--right", "$r",
        "--max-supports", "150",
        "--support-time", "60", "--circuit-time", "240",
        "--local-classifier", "v", "--require-active-scope",
        "--max-hits", "3",
        "--output", $out
    ) -RedirectStandardOutput $log -RedirectStandardError "$log.err" -PassThru -WindowStyle Hidden
    $procs += "$($p.Id) l${l}_r${r}_w2"
}
$procs | Set-Content wave2_pids.txt
Write-Output "launched: $($procs -join '; ')"
