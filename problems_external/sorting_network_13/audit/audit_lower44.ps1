$ErrorActionPreference = 'Stop'

function Get-CeilLog2([System.Numerics.BigInteger] $x) {
    if ($x -le 1) { return 0 }
    [System.Numerics.BigInteger] $power = 1
    $exponent = 0
    while ($power -lt $x) {
        $power *= 2
        $exponent++
    }
    return $exponent
}

$maxN = 17
$m = @{}
for ($depth = 0; $depth -le $maxN; $depth++) {
    $m["1,$depth"] = [System.Numerics.BigInteger]::Zero
}

for ($size = 2; $size -le $maxN; $size++) {
    for ($depth = 0; $depth -lt $size; $depth++) {
        $best = $null
        $rightDepth = $depth - 1
        for ($leftSize = 1; $leftSize -lt ($size - $rightDepth); $leftSize++) {
            $rightSize = $size - $leftSize
            for ($leftDepth = 0; $leftDepth -lt [Math]::Min($depth, $leftSize); $leftDepth++) {
                $leftKey = "$leftSize,$leftDepth"
                $rightKey = "$rightSize,$rightDepth"
                if (-not $m.ContainsKey($leftKey) -or -not $m.ContainsKey($rightKey)) { continue }
                $cross = [System.Numerics.BigInteger]::Pow(2, $leftDepth + $rightDepth)
                $candidate = 2 * ($m[$leftKey] + $m[$rightKey] + $cross)
                if ($null -eq $best -or $candidate -lt $best) { $best = $candidate }
            }
        }
        if ($null -ne $best) { $m["$size,$depth"] = $best }
    }
}

$rows = foreach ($n in 3..$maxN) {
    $fn = $null
    foreach ($depth in 0..($n - 1)) {
        $key = "$n,$depth"
        if ($m.ContainsKey($key) -and ($null -eq $fn -or $m[$key] -lt $fn)) { $fn = $m[$key] }
    }
    [pscustomobject]@{ n = $n; F = $fn.ToString(); ceilLog2 = Get-CeilLog2 $fn }
}

$row13 = $rows | Where-Object n -eq 13
if ($row13.F -ne '392') { throw "Expected F(13)=392, obtained $($row13.F)" }
if ($row13.ceilLog2 -ne 9) { throw "Expected ceil(log2(F(13)))=9, obtained $($row13.ceilLog2)" }
if (35 + $row13.ceilLog2 -ne 44) { throw 'Expected lower bound 44' }

$rows | Format-Table -AutoSize
Write-Output 'AUDIT PASS: F(13)=392; ceil(log2(F(13)))=9; 35+9=44.'
