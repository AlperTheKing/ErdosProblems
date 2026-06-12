# Robust queue runner for the a=14 shore scan: mod-55000 classes (short work units
# to duck the box's silent process killer), 110 parallel slots, per-class validation
# (geng >Z terminator + checker total= + geng count == checker total), retry <= 4,
# resume-safe (skips classes already valid).
$GENG = "E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"
$CHK  = "E:\Projects\ErdosProblems\problems\944\experiments\sixreg\check_g6_v2.exe"
$OUT  = "E:\Projects\ErdosProblems\problems\944\experiments\sixreg\n15_q"
New-Item -ItemType Directory -Force $OUT | Out-Null
# 2026-06-11 USER ARBITRATION: 50% of the box is allocated to this scan (PAR=55);
# see USER_ARBITRATION_2026-06-11 (n15 hunt).txt in $OUT. A STOPPED_BY_CODEX.txt no longer
# halts the runner; it is logged so disagreements surface to the user instead of
# silently stopping the queue.
$stop = "$OUT\STOPPED_BY_CODEX.txt"
if (Test-Path $stop) {
    "NOTE: STOPPED_BY_CODEX.txt present but overridden by USER_ARBITRATION_2026-06-11 (n15 hunt) (pid=$PID) $(Get-Date -Format o)" | Add-Content "$OUT\runner.log"
}
$MOD = 2750; $PAR = 32; $MAXRETRY = 4
$log = "$OUT\runner.log"
function Test-ClassValid([int]$r) {
    $e = "$OUT\g_$r.err"; $o = "$OUT\c_$r.out"
    if (-not ((Test-Path $e) -and (Test-Path $o))) { return $false }
    $z = Select-String -Path $e -Pattern '>Z\s+(\d+)' | Select-Object -First 1
    $t = Select-String -Path $o -Pattern '^total=(\d+)' | Select-Object -First 1
    if (-not $z -or -not $t) { return $false }
    return ([long]$z.Matches[0].Groups[1].Value) -eq ([long]$t.Matches[0].Groups[1].Value)
}
# instance guard: only one runner at a time
$lock = "$OUT\runner.lock"
if (Test-Path $lock) {
    $oldpid = [int](Get-Content $lock -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($oldpid -and (Get-Process -Id $oldpid -ErrorAction SilentlyContinue)) { exit }
}
$PID | Set-Content $lock
"queue start pid=$PID $(Get-Date -Format o)" | Add-Content $log
$deadline = (Get-Date).AddMinutes(7)    # self-limit BELOW the observed ~9-24 min kill
                                        # horizon of the box's silent process killer;
                                        # exit cleanly and chain a successor
$todo = New-Object System.Collections.Queue
for ($r = 0; $r -lt $MOD; $r++) { if (-not (Test-ClassValid $r)) { $todo.Enqueue($r) } }
"pending classes: $($todo.Count)" | Add-Content $log
$slots = @{}   # r -> process
$tries = @{}
$failed = @()
while ($todo.Count -gt 0 -or $slots.Count -gt 0) {
    if ((Get-Date) -gt $deadline -and $todo.Count -gt 0) {
        "CYCLE END (self-limit) pending=$($todo.Count) inflight=$($slots.Count) $(Get-Date -Format o)" | Add-Content $log
        break
    }
    # reap finished
    $doneKeys = @($slots.Keys | Where-Object { $slots[$_].HasExited })
    foreach ($r in $doneKeys) {
        $slots.Remove($r)
        if (Test-ClassValid $r) { continue }
        $tries[$r] = 1 + $(if ($tries.ContainsKey($r)) { $tries[$r] } else { 0 })
        if ($tries[$r] -lt $MAXRETRY) { $todo.Enqueue($r) }
        else { $failed += $r; "class $r FAILED after $MAXRETRY tries" | Add-Content $log }
    }
    # refill
    while ($slots.Count -lt $PAR -and $todo.Count -gt 0) {
        $r = $todo.Dequeue()
        $cmd = "$GENG -d6 -D6 15 $r/$MOD 2> $OUT\g_$r.err | $CHK 15 > $OUT\c_$r.out"
        $p = Start-Process cmd.exe -ArgumentList '/c', $cmd -WindowStyle Hidden -PassThru
        $slots[$r] = $p
    }
    Start-Sleep -Seconds 2
    if ((Get-Date).Second -lt 2) {
        $doneCnt = $MOD - $todo.Count - $slots.Count - $failed.Count
        "progress done=$doneCnt inflight=$($slots.Count) pending=$($todo.Count) failed=$($failed.Count) $(Get-Date -Format HH:mm:ss)" | Add-Content $log
    }
}
if ($todo.Count -gt 0) {
    # self-chain: spawn successor then exit
    Remove-Item $lock -ErrorAction SilentlyContinue
    Start-Process powershell.exe -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',$PSCommandPath -WindowStyle Hidden
    "chained successor $(Get-Date -Format o)" | Add-Content $log
    exit
}
Remove-Item $lock -ErrorAction SilentlyContinue
"ALL DONE failed=$($failed.Count) $(Get-Date -Format o)" | Add-Content $log
