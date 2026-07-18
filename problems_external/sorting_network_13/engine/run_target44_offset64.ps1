[CmdletBinding()]
param(
    [switch]$ConfirmRun,
    [switch]$SelfTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$engineDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$exe = Join-Path $engineDir "SorterHunter\SorterHunter.exe"
$verifier = Join-Path $engineDir "verify_bitslice.exe"
$upstreamDir = Join-Path $engineDir "SorterHunter"
$entrySource = Join-Path $engineDir "sorterhunter_entry.cpp"
$hardDeadline = [DateTimeOffset]::Parse("2026-07-18T21:57:27+03:00")
$targetLength = 44
$pollMilliseconds = 1000
$expectedExeHash = "4d0dd968d4252039451fe84e6b2fcd2595ee406d203b13d7551486ace8b26789"
$expectedVerifierHash = "e67746909f6fad2dd3d33baa1259ed6988d894c22cbe1889db0a54bc48ced4b6"
$expectedEntryHash = "4565a76562ec87026651c175f85d4010c449cd63e9dc17adab43c0b738dabee4"
$expectedUpstreamCommit = "392762f916688756242d90febced98ad157bc6d2"

$families = @(
    [pscustomobject]@{ Name="dobbelaere"; Fixture=(Join-Path $engineDir "fixtures\n13_45_dobbelaere.net"); Sha256="4ca03000a09042e6c6be79a9dc667176dfcf0056e37e2a2c3e28f8916703fc30" },
    [pscustomobject]@{ Name="end13"; Fixture=(Join-Path $engineDir "fixtures\n13_45_end13.net"); Sha256="fb65e2171ed8d696a261a29824b019dc410f86b7527c48739dc6d3bdf7f03698" },
    [pscustomobject]@{ Name="senso13"; Fixture=(Join-Path $engineDir "fixtures\n13_45_senso13.net"); Sha256="7299a538f2a9ec4d7380f1d2afa6aeba25fc44fdb62036ec3c5f4fa49f54696d" },
    [pscustomobject]@{ Name="cal131016"; Fixture=(Join-Path $engineDir "results\n13_seed131016_45.net"); Sha256="2bf0aaba84a7488d7dcbe0c8883e8c0b7a817365b1631826adab063c81dfec72" }
)

$profiles = @(
    [pscustomobject]@{ Name="baseline"; Escape=1000; Force=1; Max=2; Remove=1; Swap=1; Replace=0; Cross=1; Intersect=2; Half=1; Restart=0 },
    [pscustomobject]@{ Name="gentle"; Escape=4000; Force=1; Max=1; Remove=2; Swap=2; Replace=0; Cross=1; Intersect=3; Half=1; Restart=250000000 },
    [pscustomobject]@{ Name="explore"; Escape=250; Force=0; Max=3; Remove=1; Swap=1; Replace=1; Cross=2; Intersect=1; Half=2; Restart=50000000 },
    [pscustomobject]@{ Name="topology"; Escape=750; Force=1; Max=2; Remove=2; Swap=1; Replace=1; Cross=3; Intersect=3; Half=2; Restart=100000000 }
)

$specifications = @(
    for ($fi=0; $fi -lt $families.Count; $fi++) {
        for ($pi=0; $pi -lt $profiles.Count; $pi++) {
            for ($rep=0; $rep -lt 4; $rep++) {
                [pscustomobject]@{
                    Family=$families[$fi]
                    Profile=$profiles[$pi]
                    Replicate=$rep
                    Seed=(44000001 + 1000*$fi + 100*$pi + $rep)
                }
            }
        }
    }
)

function Convert-NetworkToInitial {
    param([Parameter(Mandatory=$true)][string]$Path)
    $header = $false
    $pairs = [Collections.Generic.List[string]]::new()
    foreach ($raw in Get-Content -LiteralPath $Path) {
        $line = $raw.Trim()
        if ($line.Length -eq 0 -or $line.StartsWith("#")) { continue }
        if ($line -match '^n\s+13$') { $header=$true; continue }
        if ($line -notmatch '^([0-9]+)\s+([0-9]+)$') { throw "Malformed fixture line in ${Path}: $line" }
        $a=[int]$Matches[1]; $b=[int]$Matches[2]
        if ($a -lt 0 -or $a -ge $b -or $b -ge 13) { throw "Invalid comparator in ${Path}: $line" }
        $pairs.Add("($a,$b)") | Out-Null
    }
    if (-not $header -or $pairs.Count -ne 45) { throw "Expected N13L45 fixture in $Path" }
    return ($pairs -join ',')
}

function Read-NewLogText {
    param([Parameter(Mandatory=$true)]$Runner)
    if (-not (Test-Path -LiteralPath $Runner.Stdout -PathType Leaf)) {
        return [pscustomobject]@{ Text=""; Bytes=0 }
    }
    $stream = $null
    try {
        $share = [IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete
        $stream = [IO.FileStream]::new($Runner.Stdout,[IO.FileMode]::Open,[IO.FileAccess]::Read,$share)
        if ($Runner.ReadOffset -gt $stream.Length) {
            $Runner.ReadOffset = [int64]0
            $Runner.ReadRemainder = ""
        }
        [void]$stream.Seek($Runner.ReadOffset,[IO.SeekOrigin]::Begin)
        $available = $stream.Length - $Runner.ReadOffset
        if ($available -le 0) { return [pscustomobject]@{ Text=""; Bytes=0 } }
        if ($available -gt [int]::MaxValue) { throw "Unread log chunk exceeds 2 GiB: $($Runner.Stdout)" }
        $buffer = [byte[]]::new([int]$available)
        $total = 0
        while ($total -lt $buffer.Length) {
            $read = $stream.Read($buffer,$total,$buffer.Length-$total)
            if ($read -le 0) { break }
            $total += $read
        }
        $Runner.ReadOffset += $total
        $decoded = [Text.Encoding]::UTF8.GetString($buffer,0,$total)
        $combined = $Runner.ReadRemainder + $decoded
        $lastLf = $combined.LastIndexOf("`n")
        if ($lastLf -lt 0) {
            $Runner.ReadRemainder = $combined
            return [pscustomobject]@{ Text=""; Bytes=$total }
        }
        $complete = $combined.Substring(0,$lastLf+1)
        $Runner.ReadRemainder = $combined.Substring($lastLf+1)
        return [pscustomobject]@{ Text=$complete; Bytes=$total }
    }
    finally {
        if ($null -ne $stream) { $stream.Dispose() }
    }
}

function Test-CandidateLine {
    param(
        [Parameter(Mandatory=$true)][string]$Line,
        [Parameter(Mandatory=$true)]$Runner,
        [Parameter(Mandatory=$true)][string]$RunDir,
        [switch]$SyntheticVerifier
    )
    $pattern = "^\s*\{'N':13,'L':44,'D':(?<depth>[0-9]+),'sw':'(?<sw>[^']+)','ESC':(?<esc>[0-9]+),'Prefix':(?<prefix>[0-9]+),'Postfix':(?<postfix>[0-9]+),'nw':\[(?<pairs>.*)\]\}\s*$"
    $header = [regex]::Match($Line,$pattern)
    if (-not $header.Success) { return $null }
    $pairText = $header.Groups['pairs'].Value
    $pairMatches = [regex]::Matches($pairText,'\(([0-9]+),([0-9]+)\)')
    if ($pairMatches.Count -ne 44) { return $null }
    $canonical = [Collections.Generic.List[string]]::new()
    $netLines = [Collections.Generic.List[string]]::new()
    foreach ($pair in $pairMatches) {
        $a=[int]$pair.Groups[1].Value; $b=[int]$pair.Groups[2].Value
        if ($a -lt 0 -or $a -ge $b -or $b -ge 13) { return $null }
        $canonical.Add("($a,$b)") | Out-Null
        $netLines.Add("$a $b") | Out-Null
    }
    if (($canonical -join ',') -ne $pairText) { return $null }
    $candidatePath = Join-Path $RunDir ("candidate-{0}-{1}-seed{2}.net" -f $Runner.Family,$Runner.Profile,$Runner.Seed)
    $candidateText = "# Candidate captured from SorterHunter stdout`r`nn 13`r`n" + ($netLines -join "`r`n") + "`r`n"
    [IO.File]::WriteAllText($candidatePath,$candidateText,[Text.UTF8Encoding]::new($false))
    if ($SyntheticVerifier) {
        $verification = "synthetic-parser-pass"
    } else {
        $verificationLines = @(& $verifier $candidatePath 44)
        $verification = $verificationLines -join "`n"
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Rejected emitted L44 after exhaustive verification: $candidatePath :: $verification"
            return $null
        }
    }
    return [pscustomobject]@{
        Line=$Line
        CandidatePath=$candidatePath
        CandidateSha256=(Get-FileHash -LiteralPath $candidatePath -Algorithm SHA256).Hash.ToLowerInvariant()
        PairCount=44
        Verification=$verification
    }
}

function Stop-AllRunners {
    param(
        [Parameter(Mandatory=$true)]$Runners,
        [Parameter(Mandatory=$true)][string]$State
    )
    $active = @($Runners | Where-Object { $null -ne $_.Process -and -not $_.Process.HasExited })
    $ids = @($active | ForEach-Object { $_.Process.Id } | Sort-Object -Unique)
    if ($ids.Count -gt 0) { Stop-Process -Id $ids -Force -ErrorAction SilentlyContinue }
    $stoppedAt = [DateTimeOffset]::Now
    foreach ($runner in $Runners) {
        try { if ($null -ne $runner.Process) { $runner.Process.WaitForExit() } } catch {}
        if ($runner.State -eq "running") { $runner.State=$State }
        if ($null -eq $runner.StopTime) { $runner.StopTime=$stoppedAt }
    }
}

$allocation = @(
    foreach ($family in $families) {
        [pscustomobject]@{
            family=$family.Name
            workers=@($specifications | Where-Object { $_.Family.Name -eq $family.Name }).Count
            fixture=$family.Fixture
            sha256=$family.Sha256
        }
    }
)
$plan = [ordered]@{
    canonical_script=$MyInvocation.MyCommand.Path
    armed=[bool]$ConfirmRun
    self_test=[bool]$SelfTest
    cpu_only=$true
    target="N13L44"
    workers_total=$specifications.Count
    hard_deadline=$hardDeadline.ToString('o')
    families=$allocation
    profiles=@($profiles)
    seeds_unique=(@($specifications.Seed | Sort-Object -Unique).Count -eq 64)
    executable_sha256=$expectedExeHash
    verifier_sha256=$expectedVerifierHash
    upstream_commit=$expectedUpstreamCommit
    detection="append-only byte offsets + partial-line buffers; complete N13L44/44-pair parse; exhaustive C++ verification before stop-all"
}

if ($SelfTest) {
    if ($ConfirmRun) { throw "SelfTest and ConfirmRun are mutually exclusive." }
    $testDir = Join-Path $engineDir ("logs\selftest-offset-" + (Get-Date -Format "yyyyMMddTHHmmssfff"))
    New-Item -ItemType Directory -Force -Path $testDir | Out-Null
    $dummyRunners = [Collections.Generic.List[object]]::new()
    try {
        for ($i=0; $i -lt 3; $i++) {
            $path = Join-Path $testDir "dummy-$i.log"
            [IO.File]::WriteAllText($path,"",[Text.UTF8Encoding]::new($false))
            $process = Start-Process -FilePath (Get-Command pwsh).Source -ArgumentList @('-NoProfile','-Command','Start-Sleep -Seconds 120') -WindowStyle Hidden -PassThru
            $dummyRunners.Add([pscustomobject]@{ Family="self";Profile="offset";Seed=$i;Stdout=$path;Process=$process;State="running";StopTime=$null;ReadOffset=[int64]0;ReadRemainder="" })
        }
        $sourcePairs = [Collections.Generic.List[string]]::new()
        foreach ($raw in Get-Content -LiteralPath $families[0].Fixture) {
            if ($raw.Trim() -match '^([0-9]+)\s+([0-9]+)$' -and $sourcePairs.Count -lt 44) {
                $sourcePairs.Add("($($Matches[1]),$($Matches[2]))") | Out-Null
            }
        }
        $synthetic = " {'N':13,'L':44,'D':10,'sw':'SELFTEST','ESC':1,'Prefix':0,'Postfix':0,'nw':[$($sourcePairs -join ',')]}"
        $split = [Math]::Floor($synthetic.Length/2)
        [IO.File]::AppendAllText($dummyRunners[0].Stdout,$synthetic.Substring(0,$split),[Text.UTF8Encoding]::new($false))
        $firstRead = Read-NewLogText -Runner $dummyRunners[0]
        $decoys = (0..599 | ForEach-Object { "Iteration $_ t=0.0 s 1.0 it/s" }) -join "`n"
        [IO.File]::AppendAllText($dummyRunners[0].Stdout,$synthetic.Substring($split)+"`n"+$decoys+"`n",[Text.UTF8Encoding]::new($false))
        $secondRead = Read-NewLogText -Runner $dummyRunners[0]
        $detected = $null
        foreach ($line in ($secondRead.Text -split "\r?\n")) {
            if ($line -notmatch "'L':44") { continue }
            $detected = Test-CandidateLine -Line $line -Runner $dummyRunners[0] -RunDir $testDir -SyntheticVerifier
            if ($null -ne $detected) { break }
        }
        if ($null -eq $detected) { throw "Self-test failed to recover the split L44 line." }
        Stop-AllRunners -Runners $dummyRunners -State "selftest-target"
        $alive = @($dummyRunners | Where-Object { Get-Process -Id $_.Process.Id -ErrorAction SilentlyContinue }).Count
        $result = [ordered]@{
            self_test_pass=($firstRead.Text.Length -eq 0 -and $detected.PairCount -eq 44 -and $alive -eq 0)
            first_partial_read_complete_chars=$firstRead.Text.Length
            recovered_after_decoy_lines=600
            recovered_pair_count=$detected.PairCount
            byte_offset=$dummyRunners[0].ReadOffset
            stopped_processes=$dummyRunners.Count
            live_processes_after_stop=$alive
            test_dir=$testDir
        }
        $result | ConvertTo-Json -Compress
        if (-not $result.self_test_pass) { throw "Self-test assertions failed." }
    }
    finally {
        Stop-AllRunners -Runners $dummyRunners -State "selftest-cleanup"
    }
    return
}

if (-not $ConfirmRun) {
    $plan | ConvertTo-Json -Depth 7
    Write-Host "DRY PLAN ONLY: no SorterHunter process was started. Use -ConfirmRun to launch."
    return
}

if ($specifications.Count -ne 64 -or @($specifications.Seed | Sort-Object -Unique).Count -ne 64) { throw "Worker/seed safety guard failed." }
if ([DateTimeOffset]::Now -ge $hardDeadline) { throw "Hard deadline has passed." }
if (@(Get-Process -Name SorterHunter -ErrorAction SilentlyContinue).Count -ne 0) { throw "SorterHunter is already running." }
foreach ($pin in @(
    @($exe,$expectedExeHash), @($verifier,$expectedVerifierHash), @($entrySource,$expectedEntryHash)
)) {
    if (-not (Test-Path -LiteralPath $pin[0] -PathType Leaf)) { throw "Missing pinned file: $($pin[0])" }
    $actual=(Get-FileHash -LiteralPath $pin[0] -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $pin[1]) { throw "Pinned hash mismatch: $($pin[0]) :: $actual" }
}
$commit=(& git -C $upstreamDir rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $commit -ne $expectedUpstreamCommit) { throw "Upstream commit mismatch: $commit" }

$initialNetworks=@{}
foreach ($family in $families) {
    if ((Get-FileHash -LiteralPath $family.Fixture -Algorithm SHA256).Hash.ToLowerInvariant() -ne $family.Sha256) { throw "Fixture hash mismatch: $($family.Name)" }
    $fixtureVerification=@(& $verifier $family.Fixture 45)
    if ($LASTEXITCODE -ne 0) { throw "Fixture verification failed: $($family.Name) :: $($fixtureVerification -join ' ')" }
    $initialNetworks[$family.Name]=Convert-NetworkToInitial -Path $family.Fixture
}

$runId=Get-Date -Format "yyyyMMddTHHmmssfff"
$runDir=Join-Path $engineDir "logs\target44-offset-$runId"
$configDir=Join-Path $runDir "configs"
New-Item -ItemType Directory -Force -Path $configDir | Out-Null
$rendered=@(
    foreach ($spec in $specifications) {
        $f=$spec.Family; $p=$spec.Profile
        $stem="{0}-{1}-r{2}-seed{3}" -f $f.Name,$p.Name,$spec.Replicate,$spec.Seed
        $config=Join-Path $configDir "$stem.txt"
        $text=@"
Ninputs=13
Symmetric=0
RandomSeed=$($spec.Seed)
EscapeRate=$($p.Escape)
ForceValidUphillStep=$($p.Force)
MaxMutations=$($p.Max)
WeigthRemovePair=$($p.Remove)
WeigthSwapPairs=$($p.Swap)
WeigthReplacePair=$($p.Replace)
WeightCrossPairs=$($p.Cross)
WeightSwapIntersectingPairs=$($p.Intersect)
WeightReplaceHalfPair=$($p.Half)
PrefixType=0
InitialNetwork=$($initialNetworks[$f.Name])
RestartRate=$($p.Restart)
Verbosity=3
"@
        [IO.File]::WriteAllText($config,$text,[Text.UTF8Encoding]::new($false))
        [pscustomobject]@{ Family=$f.Name;Profile=$p.Name;Replicate=$spec.Replicate;Seed=$spec.Seed;Config=$config;Stdout=(Join-Path $runDir "$stem.out.log");Stderr=(Join-Path $runDir "$stem.err.log") }
    }
)

$runners=[Collections.Generic.List[object]]::new()
$hit=$null
$runStart=[DateTimeOffset]::Now
$lastHeartbeat=[DateTimeOffset]::MinValue
try {
    foreach ($spec in $rendered) {
        if ([DateTimeOffset]::Now -ge $hardDeadline) { throw "Deadline reached during worker launch." }
        $process=Start-Process -FilePath $exe -ArgumentList @($spec.Config) -WorkingDirectory (Split-Path -Parent $exe) -WindowStyle Hidden -PassThru -RedirectStandardOutput $spec.Stdout -RedirectStandardError $spec.Stderr
        $runners.Add([pscustomobject]@{ Family=$spec.Family;Profile=$spec.Profile;Replicate=$spec.Replicate;Seed=$spec.Seed;Config=$spec.Config;Stdout=$spec.Stdout;Stderr=$spec.Stderr;Process=$process;StartTime=[DateTimeOffset]::Now;StopTime=$null;State="running";Hit=$false;ReadOffset=[int64]0;ReadRemainder="" })
        if ($runners.Count -gt 64 -or @(Get-Process -Name SorterHunter -ErrorAction SilentlyContinue).Count -gt 64) { throw "64-worker safety ceiling exceeded." }
    }
    if ($runners.Count -ne 64) { throw "Expected 64 launched workers; got $($runners.Count)." }

    :monitor while ([DateTimeOffset]::Now -lt $hardDeadline) {
        foreach ($runner in $runners) {
            if ([DateTimeOffset]::Now -ge $hardDeadline) { break monitor }
            $chunk=Read-NewLogText -Runner $runner
            if ($chunk.Text.Length -gt 0) {
                foreach ($line in ($chunk.Text -split "\r?\n")) {
                    if ($line -notmatch "'L':44") { continue }
                    $candidate=Test-CandidateLine -Line $line -Runner $runner -RunDir $runDir
                    if ($null -ne $candidate) {
                        $runner.Hit=$true; $runner.State="target-hit"
                        $hit=[ordered]@{ family=$runner.Family;profile=$runner.Profile;replicate=$runner.Replicate;seed=$runner.Seed;stdout=$runner.Stdout;line=$candidate.Line;candidate=$candidate.CandidatePath;candidate_sha256=$candidate.CandidateSha256;pair_count=$candidate.PairCount;verification=$candidate.Verification;detected_at=[DateTimeOffset]::Now.ToString('o') }
                        break monitor
                    }
                }
            }
            if ($runner.State -eq "running" -and $runner.Process.HasExited) { $runner.State="exited"; $runner.StopTime=[DateTimeOffset]::Now }
        }
        if (@($runners | Where-Object State -eq "running").Count -eq 0) { break }
        $now=[DateTimeOffset]::Now
        if (($now-$lastHeartbeat).TotalSeconds -ge 60) {
            [ordered]@{event="heartbeat";at=$now.ToString('o');running=@($runners | Where-Object State -eq "running").Count;deadline=$hardDeadline.ToString('o')} | ConvertTo-Json -Compress | Write-Output
            $lastHeartbeat=$now
        }
        $remaining=[Math]::Floor(($hardDeadline-[DateTimeOffset]::Now).TotalMilliseconds)
        if ($remaining -gt 0) { Start-Sleep -Milliseconds ([int][Math]::Min($pollMilliseconds,$remaining)) }
    }
}
finally {
    $stopState=if($null -ne $hit){"global-target"}elseif([DateTimeOffset]::Now -ge $hardDeadline){"hard-deadline"}else{"no-workers"}
    Stop-AllRunners -Runners $runners -State $stopState
}

$runStop=[DateTimeOffset]::Now
$workerSummary=@(
    foreach($runner in $runners){
        [pscustomobject]@{family=$runner.Family;profile=$runner.Profile;replicate=$runner.Replicate;seed=$runner.Seed;hit=$runner.Hit;state=$runner.State;start_time=$runner.StartTime.ToString('o');stop_time=$runner.StopTime.ToString('o');wall_seconds=[Math]::Round(($runner.StopTime-$runner.StartTime).TotalSeconds,3);bytes_consumed=$runner.ReadOffset;config=$runner.Config;stdout=$runner.Stdout;stderr=$runner.Stderr}
    }
)
$summary=[ordered]@{run_id=$runId;target="N13L44";started_at=$runStart.ToString('o');stopped_at=$runStop.ToString('o');hard_deadline=$hardDeadline.ToString('o');workers_total=$runners.Count;target_found=($null -ne $hit);hit_evidence=$hit;binary_sha256=$expectedExeHash;verifier_sha256=$expectedVerifierHash;workers=$workerSummary}
$summaryPath=Join-Path $runDir "summary.json"
$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryPath -Encoding utf8
$workerSummary | Export-Csv -LiteralPath (Join-Path $runDir "workers.csv") -NoTypeInformation -Encoding utf8
[ordered]@{event="complete";run_id=$runId;target_found=($null -ne $hit);workers=$runners.Count;summary=$summaryPath} | ConvertTo-Json -Compress | Write-Output
if ($null -eq $hit) { exit 2 }
