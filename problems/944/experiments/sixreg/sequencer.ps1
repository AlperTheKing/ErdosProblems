# Waits for the a=14 shore wave run to finish, then launches the n=15 hunt.
$shoreLog = "E:\Projects\ErdosProblems\problems\944\experiments\sixreg\shore14_waves\runner.log"
$seqLog = "E:\Projects\ErdosProblems\problems\944\experiments\sixreg\sequencer.log"
"sequencer start $(Get-Date -Format o)" | Add-Content $seqLog
while ($true) {
    Start-Sleep -Seconds 120
    if ((Test-Path $shoreLog) -and (Select-String -Path $shoreLog -Pattern '^done' -Quiet)) { break }
}
"shore14 waves done; launching n15 $(Get-Date -Format o)" | Add-Content $seqLog
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File "E:\Projects\ErdosProblems\problems\944\experiments\sixreg\run_n15_waves.ps1"
"n15 finished $(Get-Date -Format o)" | Add-Content $seqLog
