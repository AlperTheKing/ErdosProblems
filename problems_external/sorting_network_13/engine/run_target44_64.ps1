[CmdletBinding()]
param(
    [switch]$ConfirmRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$engineDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$exe = Join-Path $engineDir "SorterHunter\SorterHunter.exe"
$verifier = Join-Path $engineDir "verify_bitslice.exe"
$hardDeadline = [DateTimeOffset]::Parse("2026-07-18T21:57:27+03:00")
$targetLength = 44
$replicatesPerCell = 4
$pollMilliseconds = 1000

$families = @(
    [pscustomobject]@{
        Name = "dobbelaere"
        Fixture = Join-Path $engineDir "fixtures\n13_45_dobbelaere.net"
        Sha256 = "4ca03000a09042e6c6be79a9dc667176dfcf0056e37e2a2c3e28f8916703fc30"
    },
    [pscustomobject]@{
        Name = "end13"
        Fixture = Join-Path $engineDir "fixtures\n13_45_end13.net"
        Sha256 = "fb65e2171ed8d696a261a29824b019dc410f86b7527c48739dc6d3bdf7f03698"
    },
    [pscustomobject]@{
        Name = "senso13"
        Fixture = Join-Path $engineDir "fixtures\n13_45_senso13.net"
        Sha256 = "7299a538f2a9ec4d7380f1d2afa6aeba25fc44fdb62036ec3c5f4fa49f54696d"
    },
    [pscustomobject]@{
        Name = "cal131016"
        Fixture = Join-Path $engineDir "results\n13_seed131016_45.net"
        Sha256 = "2bf0aaba84a7488d7dcbe0c8883e8c0b7a817365b1631826adab063c81dfec72"
    }
)

$profiles = @(
    [pscustomobject]@{
        Name = "baseline"
        EscapeRate = 1000
        ForceValid = 1
        MaxMutations = 2
        Remove = 1
        Swap = 1
        Replace = 0
        Cross = 1
        Intersect = 2
        Half = 1
        RestartRate = 0
    },
    [pscustomobject]@{
        Name = "gentle"
        EscapeRate = 4000
        ForceValid = 1
        MaxMutations = 1
        Remove = 2
        Swap = 2
        Replace = 0
        Cross = 1
        Intersect = 3
        Half = 1
        RestartRate = 250000000
    },
    [pscustomobject]@{
        Name = "explore"
        EscapeRate = 250
        ForceValid = 0
        MaxMutations = 3
        Remove = 1
        Swap = 1
        Replace = 1
        Cross = 2
        Intersect = 1
        Half = 2
        RestartRate = 50000000
    },
    [pscustomobject]@{
        Name = "topology"
        EscapeRate = 750
        ForceValid = 1
        MaxMutations = 2
        Remove = 2
        Swap = 1
        Replace = 1
        Cross = 3
        Intersect = 3
        Half = 2
        RestartRate = 100000000
    }
)

$specifications = @(
    for ($familyIndex = 0; $familyIndex -lt $families.Count; $familyIndex++) {
        for ($profileIndex = 0; $profileIndex -lt $profiles.Count; $profileIndex++) {
            for ($replicate = 0; $replicate -lt $replicatesPerCell; $replicate++) {
                $seed = 44000001 + 1000 * $familyIndex + 100 * $profileIndex + $replicate
                [pscustomobject]@{
                    Family = $families[$familyIndex]
                    Profile = $profiles[$profileIndex]
                    Replicate = $replicate
                    Seed = $seed
                }
            }
        }
    }
)

$allocation = @(
    foreach ($family in $families) {
        [pscustomobject]@{
            family = $family.Name
            fixture = $family.Fixture
            sha256 = $family.Sha256
            workers = @($specifications | Where-Object { $_.Family.Name -eq $family.Name }).Count
        }
    }
)

$plan = [ordered]@{
    armed = [bool]$ConfirmRun
    cpu_only = $true
    target = "N13L44"
    executable = $exe
    hard_deadline = $hardDeadline.ToString("o")
    workers_total = $specifications.Count
    families = $allocation
    profiles = @($profiles)
    replicates_per_family_profile = $replicatesPerCell
    seeds_unique = (@($specifications.Seed | Sort-Object -Unique).Count -eq $specifications.Count)
    stop_policy = "Stop all workers on the first emitted L44 line; otherwise stop all at the absolute deadline."
}

if (-not $ConfirmRun) {
    $plan | ConvertTo-Json -Depth 7
    Write-Host "DRY PLAN ONLY: no SorterHunter process was started. Use -ConfirmRun to launch."
    return
}

if ($specifications.Count -ne 64) {
    throw "Safety guard: expected exactly 64 workers, got $($specifications.Count)."
}
if (@($specifications.Seed | Sort-Object -Unique).Count -ne 64) {
    throw "Safety guard: worker seeds are not unique."
}
if ([DateTimeOffset]::Now -ge $hardDeadline) {
    throw "Hard deadline has already passed: $($hardDeadline.ToString('o'))"
}
if (@(Get-Process -Name SorterHunter -ErrorAction SilentlyContinue).Count -ne 0) {
    throw "Safety guard: a SorterHunter process is already running."
}
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
    throw "Missing executable: $exe"
}
if (-not (Test-Path -LiteralPath $verifier -PathType Leaf)) {
    throw "Missing verifier: $verifier"
}

function Convert-NetworkToInitial {
    param([Parameter(Mandatory = $true)][string]$Path)

    $sawHeader = $false
    $pairs = [Collections.Generic.List[string]]::new()
    foreach ($rawLine in Get-Content -LiteralPath $Path) {
        $line = $rawLine.Trim()
        if ($line.Length -eq 0 -or $line.StartsWith("#")) { continue }
        if ($line -match '^n\s+13$') {
            if ($sawHeader) { throw "Duplicate n header in $Path" }
            $sawHeader = $true
            continue
        }
        if ($line -notmatch '^([0-9]+)\s+([0-9]+)$') {
            throw "Malformed fixture line in ${Path}: $line"
        }
        $left = [int]$Matches[1]
        $right = [int]$Matches[2]
        if ($left -ge $right -or $left -lt 0 -or $right -ge 13) {
            throw "Invalid comparator in ${Path}: $line"
        }
        $pairs.Add("($left,$right)") | Out-Null
    }
    if (-not $sawHeader -or $pairs.Count -ne 45) {
        throw "Expected N13L45 fixture in $Path; pairs=$($pairs.Count), header=$sawHeader"
    }
    return ($pairs -join ',')
}

$initialNetworks = @{}
foreach ($family in $families) {
    if (-not (Test-Path -LiteralPath $family.Fixture -PathType Leaf)) {
        throw "Missing fixture: $($family.Fixture)"
    }
    $actualHash = (Get-FileHash -LiteralPath $family.Fixture -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $family.Sha256) {
        throw "Fixture hash mismatch for $($family.Name): $actualHash"
    }
    $verification = & $verifier $family.Fixture 45
    if ($LASTEXITCODE -ne 0) {
        throw "Fixture verifier failed for $($family.Name): $verification"
    }
    $initialNetworks[$family.Name] = Convert-NetworkToInitial -Path $family.Fixture
}

$runId = Get-Date -Format "yyyyMMddTHHmmssfff"
$runDir = Join-Path $engineDir "logs\target44-$runId"
$configDir = Join-Path $runDir "configs"
New-Item -ItemType Directory -Force -Path $configDir | Out-Null

$renderedSpecifications = foreach ($specification in $specifications) {
    $family = $specification.Family
    $profile = $specification.Profile
    $stem = '{0}-{1}-r{2}-seed{3}' -f $family.Name, $profile.Name, $specification.Replicate, $specification.Seed
    $configPath = Join-Path $configDir "$stem.txt"
    $configText = @"
Ninputs=13
Symmetric=0
RandomSeed=$($specification.Seed)
EscapeRate=$($profile.EscapeRate)
ForceValidUphillStep=$($profile.ForceValid)
MaxMutations=$($profile.MaxMutations)
WeigthRemovePair=$($profile.Remove)
WeigthSwapPairs=$($profile.Swap)
WeigthReplacePair=$($profile.Replace)
WeightCrossPairs=$($profile.Cross)
WeightSwapIntersectingPairs=$($profile.Intersect)
WeightReplaceHalfPair=$($profile.Half)
PrefixType=0
InitialNetwork=$($initialNetworks[$family.Name])
RestartRate=$($profile.RestartRate)
Verbosity=3
"@
    [IO.File]::WriteAllText($configPath, $configText, [Text.UTF8Encoding]::new($false))
    [pscustomobject]@{
        Family = $family.Name
        Profile = $profile.Name
        Replicate = $specification.Replicate
        Seed = $specification.Seed
        Config = $configPath
        Stdout = Join-Path $runDir "$stem.out.log"
        Stderr = Join-Path $runDir "$stem.err.log"
    }
}

$runners = [Collections.Generic.List[object]]::new()
$hitEvidence = $null
$runStart = [DateTimeOffset]::Now
$lastHeartbeat = [DateTimeOffset]::MinValue

function Stop-Runner {
    param(
        [Parameter(Mandatory = $true)]$Runner,
        [Parameter(Mandatory = $true)][string]$State
    )
    try {
        if (-not $Runner.Process.HasExited) {
            Stop-Process -Id $Runner.Process.Id -Force -ErrorAction SilentlyContinue
            $Runner.Process.WaitForExit()
        }
    }
    catch {
        # The process may have exited between HasExited and Stop-Process.
    }
    if ($Runner.State -eq "running") { $Runner.State = $State }
    if ($null -eq $Runner.StopTime) { $Runner.StopTime = [DateTimeOffset]::Now }
}

try {
    foreach ($specification in $renderedSpecifications) {
        $process = Start-Process -FilePath $exe `
            -ArgumentList @($specification.Config) `
            -WorkingDirectory (Split-Path -Parent $exe) `
            -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput $specification.Stdout `
            -RedirectStandardError $specification.Stderr
        $runners.Add([pscustomobject]@{
            Family = $specification.Family
            Profile = $specification.Profile
            Replicate = $specification.Replicate
            Seed = $specification.Seed
            Config = $specification.Config
            Stdout = $specification.Stdout
            Stderr = $specification.Stderr
            Process = $process
            StartTime = [DateTimeOffset]::Now
            StopTime = $null
            State = "running"
            Hit = $false
        })
    }

    if ($runners.Count -ne 64) {
        throw "Safety guard: expected 64 launched workers; got $($runners.Count)."
    }
    if (@(Get-Process -Name SorterHunter -ErrorAction SilentlyContinue).Count -gt 64) {
        throw "Safety guard: more than 64 SorterHunter processes detected."
    }

    while ([DateTimeOffset]::Now -lt $hardDeadline) {
        foreach ($runner in $runners) {
            if ($runner.State -ne "running") { continue }
            if (-not (Test-Path -LiteralPath $runner.Stdout -PathType Leaf)) { continue }
            $match = Get-Content -LiteralPath $runner.Stdout -Tail 256 |
                Select-String -Pattern "'L':44(?:,|})" | Select-Object -First 1
            if ($null -ne $match) {
                $runner.Hit = $true
                $runner.State = "target-hit"
                $hitEvidence = [ordered]@{
                    family = $runner.Family
                    profile = $runner.Profile
                    replicate = $runner.Replicate
                    seed = $runner.Seed
                    stdout = $runner.Stdout
                    network = $match.Line
                    detected_at = [DateTimeOffset]::Now.ToString('o')
                }
                break
            }
        }
        if ($null -ne $hitEvidence) { break }

        foreach ($runner in $runners) {
            if ($runner.State -eq "running" -and $runner.Process.HasExited) {
                $runner.State = "exited"
                $runner.StopTime = [DateTimeOffset]::Now
            }
        }
        if (@($runners | Where-Object State -eq "running").Count -eq 0) { break }

        $now = [DateTimeOffset]::Now
        if (($now - $lastHeartbeat).TotalSeconds -ge 60) {
            [ordered]@{
                event = "heartbeat"
                at = $now.ToString('o')
                running = @($runners | Where-Object State -eq "running").Count
                deadline = $hardDeadline.ToString('o')
            } | ConvertTo-Json -Compress | Write-Output
            $lastHeartbeat = $now
        }
        Start-Sleep -Milliseconds $pollMilliseconds
    }
}
finally {
    $finalState = if ($null -ne $hitEvidence) { "global-target" } else { "hard-deadline" }
    foreach ($runner in $runners) {
        if ($runner.State -eq "running") {
            Stop-Runner -Runner $runner -State $finalState
        }
        elseif ($runner.State -eq "target-hit") {
            Stop-Runner -Runner $runner -State "target-hit"
        }
    }
}

$runStop = [DateTimeOffset]::Now
$workerSummary = @(
    foreach ($runner in $runners) {
        $minimumLength = $null
        $lastIteration = $null
        $lastIps = $null
        if (Test-Path -LiteralPath $runner.Stdout -PathType Leaf) {
            foreach ($line in Get-Content -LiteralPath $runner.Stdout) {
                if ($line -match "'L':([0-9]+)") {
                    $length = [int]$Matches[1]
                    if ($null -eq $minimumLength -or $length -lt $minimumLength) { $minimumLength = $length }
                }
                if ($line -match 'Iteration ([0-9]+).*?([0-9]+(?:\.[0-9]+)?) it/s') {
                    $lastIteration = [uint64]$Matches[1]
                    $lastIps = [double]$Matches[2]
                }
            }
        }
        [pscustomobject]@{
            family = $runner.Family
            profile = $runner.Profile
            replicate = $runner.Replicate
            seed = $runner.Seed
            hit = $runner.Hit
            state = $runner.State
            start_time = $runner.StartTime.ToString('o')
            stop_time = $runner.StopTime.ToString('o')
            wall_seconds = [Math]::Round(($runner.StopTime - $runner.StartTime).TotalSeconds, 3)
            minimum_emitted_length = $minimumLength
            last_reported_iteration = $lastIteration
            last_reported_iterations_per_second = $lastIps
            config = $runner.Config
            stdout = $runner.Stdout
            stderr = $runner.Stderr
        }
    }
)

$summary = [ordered]@{
    run_id = $runId
    target = "N13L44"
    started_at = $runStart.ToString('o')
    stopped_at = $runStop.ToString('o')
    hard_deadline = $hardDeadline.ToString('o')
    workers_total = $runners.Count
    target_found = ($null -ne $hitEvidence)
    hit_evidence = $hitEvidence
    workers = $workerSummary
}
$summaryPath = Join-Path $runDir "summary.json"
$csvPath = Join-Path $runDir "workers.csv"
$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryPath -Encoding utf8
$workerSummary | Export-Csv -LiteralPath $csvPath -NoTypeInformation -Encoding utf8
if ($null -ne $hitEvidence) {
    $hitEvidence.network | Set-Content -LiteralPath (Join-Path $runDir "candidate_L44.raw.txt") -Encoding utf8
}
[ordered]@{
    event = "complete"
    run_id = $runId
    target_found = ($null -ne $hitEvidence)
    workers_total = $runners.Count
    summary = $summaryPath
} | ConvertTo-Json -Compress | Write-Output

if ($null -eq $hitEvidence) { exit 2 }
