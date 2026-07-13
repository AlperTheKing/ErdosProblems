param(
    [ValidateRange(1, 64)]
    [int]$Threads = 32
)

$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Source = Join-Path $Here "solve_bnb.cpp"
$Exe = Join-Path $Here "solve_bnb.exe"
$Log = Join-Path $Here "oeis_endpoint_certificates.jsonl"

g++ -std=c++20 -O3 -DNDEBUG -pthread -Wall -Wextra -Wpedantic $Source -o $Exe
if ($LASTEXITCODE -ne 0) {
    throw "C++ build failed"
}

Remove-Item -LiteralPath $Log -ErrorAction SilentlyContinue
foreach ($N in 70, 80, 81, 85, 86, 100) {
    $Result = & $Exe --n $N --threads $Threads --timeout 0 |
        Where-Object { $_ -match '"type":"result"' }
    if ($LASTEXITCODE -ne 0 -or $Result -notmatch '"status":"proof-complete"') {
        throw "endpoint N=$N was not proof-complete"
    }
    Add-Content -LiteralPath $Log -Value $Result -Encoding ascii
}

Write-Output "wrote $Log"
