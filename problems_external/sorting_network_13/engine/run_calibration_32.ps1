[CmdletBinding()]
param(
    [switch]$ConfirmRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$engineDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$exe = Join-Path $engineDir "SorterHunter\SorterHunter.exe"
$workersPerCohort = 16
$minutes = 30
$pollMilliseconds = 500

$cohorts = @(
    [pscustomobject]@{
        Name = "n12"
        Channels = 12
        SeedBase = 121001
        TargetLength = 39
        Template = Join-Path $engineDir "configs\n12_40_to_39_seed1.txt"
    },
    [pscustomobject]@{
        Name = "n13"
        Channels = 13
        SeedBase = 131001
        TargetLength = 45
        Template = Join-Path $engineDir "configs\n13_46_to_45_seed1.txt"
    }
)

$plan = [ordered]@{
    armed = [bool]$ConfirmRun
    executable = $exe
    workers_per_cohort = $workersPerCohort
    workers_total = $workersPerCohort * $cohorts.Count
    maximum_minutes = $minutes
    poll_milliseconds = $pollMilliseconds
    cohorts = @(
        foreach ($cohort in $cohorts) {
            [ordered]@{
                name = $cohort.Name
                channels = $cohort.Channels
                target_length = $cohort.TargetLength
                seeds = "$($cohort.SeedBase)-$($cohort.SeedBase + $workersPerCohort - 1)"
                template = $cohort.Template
            }
        }
    )
    stop_policy = "On the first target hit, stop that entire cohort; stop all when both cohorts pass or the 30-minute deadline expires."
}

if (-not $ConfirmRun) {
    $plan | ConvertTo-Json -Depth 5
    Write-Host "DRY PLAN ONLY: no SorterHunter process was started. Use -ConfirmRun to launch."
    exit 0
}

if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
    throw "Missing executable: $exe"
}
foreach ($cohort in $cohorts) {
    if (-not (Test-Path -LiteralPath $cohort.Template -PathType Leaf)) {
        throw "Missing template: $($cohort.Template)"
    }
}

$runId = Get-Date -Format "yyyyMMddTHHmmssfff"
$runDir = Join-Path $engineDir "logs\calibration-$runId"
$configDir = Join-Path $runDir "configs"
New-Item -ItemType Directory -Force -Path $configDir | Out-Null

$specifications = foreach ($cohort in $cohorts) {
    $templateText = Get-Content -LiteralPath $cohort.Template -Raw
    $seedFields = [regex]::Matches($templateText, '(?m)^RandomSeed=[0-9]+[ \t]*$')
    if ($seedFields.Count -ne 1) {
        throw "Expected one RandomSeed field in $($cohort.Template); found $($seedFields.Count)"
    }
    for ($worker = 0; $worker -lt $workersPerCohort; $worker++) {
        $seed = $cohort.SeedBase + $worker
        $stem = '{0}-w{1:D2}-seed{2}' -f $cohort.Name, $worker, $seed
        $configPath = Join-Path $configDir "$stem.txt"
        $rendered = [regex]::Replace(
            $templateText,
            '(?m)^RandomSeed=[0-9]+[ \t]*$',
            "RandomSeed=$seed"
        )
        [IO.File]::WriteAllText(
            $configPath,
            $rendered,
            [Text.UTF8Encoding]::new($false)
        )
        [pscustomobject]@{
            Cohort = $cohort.Name
            Channels = $cohort.Channels
            Worker = $worker
            Seed = $seed
            TargetLength = $cohort.TargetLength
            Stem = $stem
            Config = $configPath
            Stdout = Join-Path $runDir "$stem.out.log"
            Stderr = Join-Path $runDir "$stem.err.log"
        }
    }
}

$runners = [Collections.Generic.List[object]]::new()
$cohortHit = @{ n12 = $false; n13 = $false }
$cohortHitEvidence = @{ n12 = $null; n13 = $null }

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
    if ($Runner.State -eq "running") {
        $Runner.State = $State
    }
    if ($null -eq $Runner.StopUtc) {
        $Runner.StopUtc = [datetime]::UtcNow
    }
}

$runStartUtc = [datetime]::UtcNow
try {
    foreach ($specification in $specifications) {
        $process = Start-Process -FilePath $exe `
            -ArgumentList @($specification.Config) `
            -WorkingDirectory (Split-Path -Parent $exe) `
            -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput $specification.Stdout `
            -RedirectStandardError $specification.Stderr
        $runners.Add([pscustomobject]@{
            Cohort = $specification.Cohort
            Channels = $specification.Channels
            Worker = $specification.Worker
            Seed = $specification.Seed
            TargetLength = $specification.TargetLength
            Config = $specification.Config
            Stdout = $specification.Stdout
            Stderr = $specification.Stderr
            Process = $process
            StartUtc = [datetime]::UtcNow
            StopUtc = $null
            State = "running"
            Hit = $false
            HitLine = $null
        })
    }

    if ($runners.Count -ne 32) {
        throw "Expected 32 workers; launched $($runners.Count)"
    }

    # Starting the common window after the last launch gives every worker at
    # least 30 minutes unless its cohort reaches the registered target first.
    $deadlineUtc = [datetime]::UtcNow.AddMinutes($minutes)

    while ([datetime]::UtcNow -lt $deadlineUtc) {
        foreach ($cohort in $cohorts) {
            if ($cohortHit[$cohort.Name]) { continue }

            $hitRunner = $null
            $hitMatch = $null
            foreach ($runner in $runners) {
                if ($runner.Cohort -ne $cohort.Name) { continue }
                if (-not (Test-Path -LiteralPath $runner.Stdout -PathType Leaf)) { continue }
                $match = Select-String -LiteralPath $runner.Stdout `
                    -Pattern ("'L':{0}(?:,|}})" -f $cohort.TargetLength) | Select-Object -First 1
                if ($null -ne $match) {
                    $hitRunner = $runner
                    $hitMatch = $match
                    break
                }
            }

            if ($null -ne $hitRunner) {
                $hitRunner.Hit = $true
                $hitRunner.HitLine = $hitMatch.Line
                $cohortHit[$cohort.Name] = $true
                $cohortHitEvidence[$cohort.Name] = [ordered]@{
                    worker = $hitRunner.Worker
                    seed = $hitRunner.Seed
                    stdout = $hitRunner.Stdout
                    line_number = $hitMatch.LineNumber
                    network = $hitMatch.Line
                }
                foreach ($runner in $runners) {
                    if ($runner.Cohort -eq $cohort.Name) {
                        Stop-Runner -Runner $runner -State "cohort-target"
                    }
                }
                $hitRunner.State = "target-hit"
            }
        }

        foreach ($runner in $runners) {
            if ($runner.State -eq "running" -and $runner.Process.HasExited) {
                $runner.State = "exited"
                $runner.StopUtc = [datetime]::UtcNow
            }
        }

        if ($cohortHit.n12 -and $cohortHit.n13) { break }
        if (($runners | Where-Object State -eq "running").Count -eq 0) { break }
        Start-Sleep -Milliseconds $pollMilliseconds
    }
}
finally {
    foreach ($runner in $runners) {
        if ($runner.State -eq "running") {
            Stop-Runner -Runner $runner -State "time-limit"
        }
    }
}

$runStopUtc = [datetime]::UtcNow
$workerSummary = foreach ($runner in $runners) {
    $minimumLength = $null
    $lastIteration = $null
    $lastIps = $null
    if (Test-Path -LiteralPath $runner.Stdout -PathType Leaf) {
        foreach ($line in Get-Content -LiteralPath $runner.Stdout) {
            if ($line -match "'L':([0-9]+)") {
                $length = [int]$Matches[1]
                if ($null -eq $minimumLength -or $length -lt $minimumLength) {
                    $minimumLength = $length
                }
            }
            if ($line -match 'Iteration ([0-9]+).*?([0-9]+(?:\.[0-9]+)?) it/s') {
                $lastIteration = [uint64]$Matches[1]
                $lastIps = [double]$Matches[2]
            }
        }
    }
    [ordered]@{
        cohort = $runner.Cohort
        channels = $runner.Channels
        worker = $runner.Worker
        seed = $runner.Seed
        target_length = $runner.TargetLength
        hit = $runner.Hit
        state = $runner.State
        start_utc = $runner.StartUtc.ToString('o')
        stop_utc = $runner.StopUtc.ToString('o')
        wall_seconds = [Math]::Round(($runner.StopUtc - $runner.StartUtc).TotalSeconds, 3)
        minimum_emitted_length = $minimumLength
        last_reported_iteration = $lastIteration
        last_reported_iterations_per_second = $lastIps
        config = $runner.Config
        stdout = $runner.Stdout
        stderr = $runner.Stderr
    }
}

$summary = [ordered]@{
    run_id = $runId
    started_utc = $runStartUtc.ToString('o')
    stopped_utc = $runStopUtc.ToString('o')
    maximum_minutes = $minutes
    workers_total = $runners.Count
    n12_pass = $cohortHit.n12
    n13_pass = $cohortHit.n13
    calibration_pass = ($cohortHit.n12 -and $cohortHit.n13)
    hit_evidence = $cohortHitEvidence
    workers = @($workerSummary)
}

$summaryJson = Join-Path $runDir "summary.json"
$summaryCsv = Join-Path $runDir "workers.csv"
$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryJson -Encoding utf8
$workerSummary | Export-Csv -LiteralPath $summaryCsv -NoTypeInformation -Encoding utf8
$summary | Select-Object run_id, maximum_minutes, workers_total, n12_pass, n13_pass, calibration_pass | ConvertTo-Json -Compress
Write-Host "Summary: $summaryJson"

if (-not $summary.calibration_pass) {
    exit 2
}
