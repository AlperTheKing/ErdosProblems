$dir = "E:\Projects\ErdosProblems\tmp\agent_hunt\falsifier_t6"
$expected = @(
    "t6_sweep_l10_r11_2000","t6_sweep_l11_r10_2000","t6_sweep_l12_r9_2000","t6_sweep_l13_r8_2000",
    "t6_sweep_l12_r12_w2","t6_sweep_l14_r14_w2","t6_sweep_l15_r15_w2",
    "t6_cuttight_l12_r12",
    "t6_sharedstar_l12_r10","t6_sharedstar_ct_l13_r11",
    "t6_cuttight_l12_r9_harvest","t6_cuttight_l12_r9_deep",
    "cuttight_t5_retry","t5_cuttight_l11_r9_pinch"
)
$deadline = (Get-Date).AddMinutes(50)
while ((Get-Date) -lt $deadline) {
    $done = @(); $crashed = @()
    foreach ($b in $expected) {
        $j = Join-Path $dir "$b.json"
        $e = Join-Path $dir "$b.log.err"
        if ((Test-Path $j) -and (Get-Item $j).Length -gt 0) { $done += $b }
        elseif (Test-Path $e) {
            $bad = @(Get-Content $e | Where-Object { $_ -match "Error|Traceback|Exception" })
            if ($bad.Count -gt 0) { $crashed += $b }
        }
    }
    if ($done.Count -gt 0 -or $crashed.Count -gt 0) {
        Write-Output "DONE: $($done -join ',') CRASHED: $($crashed -join ',')"
        exit 0
    }
    Start-Sleep -Seconds 60
}
Write-Output "TIMEOUT_50MIN_NO_NEW_CELL"
