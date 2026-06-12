# Re-verify a=13 chunk counts: for each r in 0..109 run geng -u (count only) and
# require a >Z line; compare the count against the checker total in shore13_chunks/c<r>.out.
$GENG = "E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"
$DIR  = "E:\Projects\ErdosProblems\problems\944\experiments\sixreg"
$OUT  = "$DIR\verify13"
New-Item -ItemType Directory -Force $OUT | Out-Null
$pend = @{}
for ($r = 0; $r -lt 110; $r++) {
    if (Test-Path "$OUT\g_$r.err") { if (Select-String -Path "$OUT\g_$r.err" -Pattern '>Z' -Quiet) { continue } }
    $p = Start-Process $GENG -ArgumentList '-u','-c','-D6','13','36:36',"$r/110" -RedirectStandardError "$OUT\g_$r.err" -WindowStyle Hidden -PassThru
    $pend[$r] = $p
}
do { Start-Sleep -Seconds 5 } while ((Get-Process geng -ErrorAction SilentlyContinue).Count -gt 0)
# retry missing >Z up to 3 times
for ($try = 0; $try -lt 3; $try++) {
    $bad = @()
    for ($r = 0; $r -lt 110; $r++) { if (-not (Select-String -Path "$OUT\g_$r.err" -Pattern '>Z' -Quiet)) { $bad += $r } }
    if ($bad.Count -eq 0) { break }
    foreach ($r in $bad) { Start-Process $GENG -ArgumentList '-u','-c','-D6','13','36:36',"$r/110" -RedirectStandardError "$OUT\g_$r.err" -WindowStyle Hidden | Out-Null }
    do { Start-Sleep -Seconds 5 } while ((Get-Process geng -ErrorAction SilentlyContinue).Count -gt 0)
}
# compare
$mismatch = 0; $okc = 0; $sumg = [long]0
for ($r = 0; $r -lt 110; $r++) {
    $zline = (Select-String -Path "$OUT\g_$r.err" -Pattern '>Z\s+(\d+)' | Select-Object -First 1)
    $chk = (Select-String -Path "$DIR\shore13_chunks\c$r.out" -Pattern '^total=(\d+)' | Select-Object -First 1)
    if (-not $zline -or -not $chk) { "r=$r MISSING" | Add-Content "$OUT\result.txt"; $mismatch++; continue }
    $g = [long]$zline.Matches[0].Groups[1].Value
    $c = [long]$chk.Matches[0].Groups[1].Value
    $sumg += $g
    if ($g -ne $c) { "r=$r geng=$g checker=$c MISMATCH" | Add-Content "$OUT\result.txt"; $mismatch++ } else { $okc++ }
}
"chunks ok=$okc mismatch=$mismatch sum_geng=$sumg" | Add-Content "$OUT\result.txt"
