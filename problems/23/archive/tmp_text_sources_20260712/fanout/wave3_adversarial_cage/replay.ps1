$ErrorActionPreference = 'Stop'

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $Here '..\..\..')).Path
$Cadical = Join-Path $Root 'tmp\fanout\r51_independent_t5_verifier\cadical.exe'

Push-Location $Root
try {
    python -B (Join-Path $Here 'extract_first_supports.py')
    if ($LASTEXITCODE -ne 0) { throw 'support extraction failed' }
    python -B (Join-Path $Here 'build_triangle_obstruction.py')
    if ($LASTEXITCODE -ne 0) { throw 'exhaustive obstruction failed' }
    python -B (Join-Path $Here 'build_omission_budget_certificate.py')
    if ($LASTEXITCODE -ne 0) { throw 'small certificate failed' }
    python -B (Join-Path $Here 'build_small_obstruction_cnf.py')
    if ($LASTEXITCODE -ne 0) { throw 'small CNF generation failed' }

    foreach ($Stem in @('l9_r8', 'l10_r7', 'l11_r6')) {
        $Cnf = Join-Path $Here "small_obstruction_$Stem.cnf"
        $Lrat = Join-Path $Here "small_obstruction_$Stem.lrat"
        & $Cadical --lrat --no-binary $Cnf $Lrat
        if ($LASTEXITCODE -ne 20) { throw "CaDiCaL failed on $Stem" }
    }

    python -B (Join-Path $Here 'verify_obstruction.py')
    if ($LASTEXITCODE -ne 0) { throw 'independent verification failed' }
}
finally {
    Pop-Location
}

