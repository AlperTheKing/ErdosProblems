# n=15 six-regular 4-VC hunt, mod-550 classes in waves of 110 parallel pairs.
# Class r: geng -q -d6 -D6 15 r/550 | check_g6_v2 15
# Guards: every class must end with geng's >Z line and the checker's total= line.
$GENG = "E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"
$CHK  = "E:\Projects\ErdosProblems\problems\944\experiments\sixreg\check_g6_v2.exe"
$OUT  = "E:\Projects\ErdosProblems\problems\944\experiments\sixreg\n15_waves"
New-Item -ItemType Directory -Force $OUT | Out-Null
$MOD = 550
$WAVE = 55
$log = Join-Path $OUT "runner.log"
"start $(Get-Date -Format o)" | Add-Content $log
for ($w = 0; $w -lt [int]($MOD / $WAVE); $w++) {
    $lo = $w * $WAVE
    $hi = $lo + $WAVE - 1
    for ($r = $lo; $r -le $hi; $r++) {
        $cmd = "$GENG -d6 -D6 15 $r/$MOD 2> $OUT\geng_$r.err | $CHK 15 > $OUT\cls_$r.out 2> $OUT\chk_$r.err"
        Start-Process cmd.exe -ArgumentList '/c', $cmd -WindowStyle Hidden
    }
    do { Start-Sleep -Seconds 15 } while ((Get-Process check_g6_v2 -ErrorAction SilentlyContinue).Count -gt 0)
    $bad = @()
    for ($r = $lo; $r -le $hi; $r++) {
        $z = Select-String -Path "$OUT\geng_$r.err" -Pattern '>Z' -Quiet
        $t = Select-String -Path "$OUT\cls_$r.out" -Pattern '^total=' -Quiet
        if (-not ($z -and $t)) { $bad += $r }
    }
    if ($bad.Count -gt 0) { "wave $w BAD CLASSES: $($bad -join ',')" | Add-Content $log }
    else { "wave $w ok $(Get-Date -Format o)" | Add-Content $log }
}
"done $(Get-Date -Format o)" | Add-Content $log
