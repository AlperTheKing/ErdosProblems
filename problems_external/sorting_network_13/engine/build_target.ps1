$ErrorActionPreference = "Stop"
$engineDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceDir = Join-Path $engineDir "SorterHunter"

Push-Location $sourceDir
try {
    & g++ -O3 -DNDEBUG -std=c++17 -Wall -Wextra -o SorterHunter.exe `
        prefix_processor.cpp hutils.cpp ConfigParser.cpp `
        (Join-Path $engineDir "sorterhunter_entry.cpp")
    if ($LASTEXITCODE -ne 0) { throw "SorterHunter build failed ($LASTEXITCODE)" }
}
finally {
    Pop-Location
}

& g++ -O3 -DNDEBUG -std=c++17 -Wall -Wextra -o `
    (Join-Path $engineDir "verify_bitslice.exe") `
    (Join-Path $engineDir "verify_bitslice.cpp")
if ($LASTEXITCODE -ne 0) { throw "verifier build failed ($LASTEXITCODE)" }
