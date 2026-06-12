# a=14 shore filter, mod-5500 classes in waves of 110 parallel pairs.
# Each class r: geng -q -c -D6 14 39:39 r/5500 | enum_shore 14
#   stdout -> w\g6sum_r.out (checker counts + SURVIVOR lines)
#   geng stderr -> w\geng_r.err (MUST end with >Z line; silent-truncation guard)
$GENG = "E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"
$CHK  = "E:\Projects\ErdosProblems\problems\944\experiments\sixreg\enum_shore.exe"
$OUT  = "E:\Projects\ErdosProblems\problems\944\experiments\sixreg\shore14_waves"
New-Item -ItemType Directory -Force $OUT | Out-Null
$MOD = 5500
$WAVE = 110
$log = Join-Path $OUT "runner.log"
"start $(Get-Date -Format o)" | Add-Content $log
for ($w = 0; $w -lt [int]($MOD / $WAVE); $w++) {
    $lo = $w * $WAVE
    $hi = $lo + $WAVE - 1
    for ($r = $lo; $r -le $hi; $r++) {
        $cmd = "$GENG -c -D6 14 39:39 $r/$MOD 2> $OUT\geng_$r.err | $CHK 14 > $OUT\cls_$r.out"
        Start-Process cmd.exe -ArgumentList '/c', $cmd -WindowStyle Hidden
    }
    # wait for this wave to drain
    do { Start-Sleep -Seconds 10 } while ((Get-Process enum_shore -ErrorAction SilentlyContinue).Count -gt 0)
    # guard: every class in the wave must have a >Z line and a total= line
    $bad = @()
    for ($r = $lo; $r -le $hi; $r++) {
        $z = Select-String -Path "$OUT\geng_$r.err" -Pattern '>Z' -Quiet
        $t = Select-String -Path "$OUT\cls_$r.out" -Pattern '^total=' -Quiet
        if (-not ($z -and $t)) { $bad += $r }
    }
    if ($bad.Count -gt 0) {
        "wave $w BAD CLASSES: $($bad -join ',')" | Add-Content $log
    } else {
        "wave $w ok $(Get-Date -Format o)" | Add-Content $log
    }
}
"done $(Get-Date -Format o)" | Add-Content $log
