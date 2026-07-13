$dir = "E:\Projects\ErdosProblems\tmp\agent_hunt\falsifier_t6"
$expected = @(
    "t6_cuttight_l12_r9_deep","cuttight_t5_retry",
    "t6_sharedstar_l12_r10","t6_sharedstar_ct_l13_r11","t6_cuttight_l12_r12",
    "t6_sweep_l12_r12_w2","t6_sweep_l14_r14_w2","t6_sweep_l15_r15_w2",
    "t6_sweep_l10_r11_2000","t6_sweep_l11_r10_2000","t6_sweep_l12_r9_2000","t6_sweep_l13_r8_2000"
)
$deadline = (Get-Date).AddMinutes(22)
while ((Get-Date) -lt $deadline) {
    $done = @()
    foreach ($b in $expected) {
        $j = Join-Path $dir "$b.json"
        if ((Test-Path $j) -and (Get-Item $j).Length -gt 0) { $done += $b }
    }
    if ($done.Count -gt 0) { Write-Output "DONE: $($done -join ',')"; exit 0 }
    Start-Sleep -Seconds 45
}
Write-Output "TIMEOUT_22MIN"
