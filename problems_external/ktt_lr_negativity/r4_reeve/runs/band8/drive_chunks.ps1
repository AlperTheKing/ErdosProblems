# drive_chunks.ps1 -- exhaustive band-8 gap-class census, run as Cw slices.
# The union of the slices Cw = 0..90 IS the whole band region (every gap class
# realised by a triple with |nu| in [61,90] has Cw <= 90), so the slices are a
# partition of the exhaustive scan, not a sample.
Set-Location "E:\Projects\ErdosProblems\problems_external\ktt_lr_negativity\r4_reeve\runs\band8"
$bounds = @(0,45,50,55,60,63,66,69,72,75,78,81,84,86,88,89,90)
$lo = 0
foreach ($hi in $bounds) {
    if ($hi -lt $lo) { continue }
    $name = "chunk_Cw{0:d2}_{1:d2}" -f $lo, $hi
    if (Test-Path "$name.done") { $lo = $hi + 1; continue }
    $t = Get-Date
    & .\band8_gapscan3.exe --chunk $lo $hi 2> "$name.prog" | Out-File -Encoding ascii "$name.log"
    $sec = [math]::Round(((Get-Date) - $t).TotalSeconds, 1)
    "$name done in $sec s" | Out-File -Append -Encoding ascii drive_chunks.log
    New-Item -ItemType File "$name.done" -Force | Out-Null
    $lo = $hi + 1
}
"ALL CHUNKS DONE" | Out-File -Append -Encoding ascii drive_chunks.log
