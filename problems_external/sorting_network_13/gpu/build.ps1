$ErrorActionPreference = "Stop"

if (-not (Get-Command cl.exe -ErrorAction SilentlyContinue)) {
    $vsDevCmd = "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat"
    if (-not (Test-Path -LiteralPath $vsDevCmd)) {
        throw "VS2022 developer command file not found: $vsDevCmd"
    }
    $environment = & $env:ComSpec /s /c "`"$vsDevCmd`" -no_logo -arch=x64 -host_arch=x64 && set"
    $vsPath = $environment | Where-Object { $_ -cmatch '^PATH=' } | Select-Object -First 1
    foreach ($line in $environment) {
        if ($line -match '^([^=]+)=(.*)$') {
            if ($Matches[1] -ieq 'Path') { continue }
            Set-Item -Path ("Env:" + $Matches[1]) -Value $Matches[2]
        }
    }
    if (-not $vsPath) { throw "VS2022 environment did not supply PATH" }
    $env:Path = $vsPath.Substring(5)
}

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$nvcc = (Get-Command nvcc -ErrorAction Stop).Source
$source = Join-Path $here "sn_gpu.cu"
$output = Join-Path $here "sn_gpu.exe"

& $nvcc `
    -O3 `
    -std=c++17 `
    -arch=sm_120 `
    -Xcompiler=/O2 `
    -Xcompiler=/EHsc `
    $source -o $output
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
