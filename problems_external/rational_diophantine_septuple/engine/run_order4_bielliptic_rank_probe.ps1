param(
    [Parameter(Mandatory = $true)]
    [string]$ReportPath,
    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory
)

$ErrorActionPreference = "Stop"
$reportFull = (Resolve-Path -LiteralPath $ReportPath).Path
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$outputFull = (Resolve-Path -LiteralPath $OutputDirectory).Path

$root = "/mnt/e/Projects/ErdosProblems/problems_external/rational_diophantine_septuple/tools/eclib-ubuntu/root"
$libraryPath = "$root/usr/lib/x86_64-linux-gnu"
$binary = "$root/usr/bin/mwrank"

foreach ($label in @("E_plus", "E_minus")) {
    $curve = @'
import json,sys
report=json.load(open(sys.argv[1],encoding="utf-8"))
model=report["bielliptic_split"][sys.argv[2]]["compact_integral_probe"]["ainvariants"]
print("["+",".join(map(str,model))+"]")
'@ | python - $reportFull $label
    if ($LASTEXITCODE -ne 0) { throw "model extraction failed for $label" }

    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = "wsl.exe"
    $psi.ArgumentList.Add("-d")
    $psi.ArgumentList.Add("Ubuntu")
    $psi.ArgumentList.Add("--")
    $psi.ArgumentList.Add("env")
    $psi.ArgumentList.Add("LD_LIBRARY_PATH=$libraryPath")
    $psi.ArgumentList.Add($binary)
    foreach ($arg in @("-q", "-v", "1", "-p", "60", "-b", "2", "-x", "5", "-s", "-d", "-S", "2")) {
        $psi.ArgumentList.Add($arg)
    }
    $psi.UseShellExecute = $false
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $psi
    if (-not $process.Start()) { throw "could not launch mwrank for $label" }
    $process.StandardInput.WriteLine($curve)
    $process.StandardInput.Close()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    [System.IO.File]::WriteAllText((Join-Path $outputFull "$label.stdout.txt"), $stdout, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllText((Join-Path $outputFull "$label.stderr.txt"), $stderr, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllText((Join-Path $outputFull "$label.curve.txt"), "$curve`n", [System.Text.UTF8Encoding]::new($false))
    if ($process.ExitCode -ne 0) { throw "mwrank exit $($process.ExitCode) for $label" }
}
