$ErrorActionPreference = 'Stop'

$engineDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $engineDir
try {
    & g++ -std=c++20 -O3 -pthread -Wall -Wextra s_lane_search.cpp -o s_lane_search.exe
    if ($LASTEXITCODE -ne 0) {
        throw "g++ failed with exit code $LASTEXITCODE"
    }
} finally {
    Pop-Location
}
