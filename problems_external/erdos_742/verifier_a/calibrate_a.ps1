param(
    [string]$Verifier = (Join-Path $PSScriptRoot "verifier_a.exe")
)

$ErrorActionPreference = "Stop"
$fixtureDir = Join-Path $PSScriptRoot "fixtures"
$ledgerDir = Join-Path $PSScriptRoot "calibration_ledgers"
New-Item -ItemType Directory -Force $ledgerDir | Out-Null

function Invoke-Case {
    param(
        [string]$Name,
        [int]$ExpectedExit,
        [string[]]$Arguments,
        [string[]]$Needles
    )
    $text = (& $Verifier @Arguments 2>&1 | Out-String)
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne $ExpectedExit) {
        throw "$Name exit=$exitCode expected=$ExpectedExit`n$text"
    }
    foreach ($needle in $Needles) {
        if (-not $text.Contains($needle)) {
            throw "$Name missing='$needle'`n$text"
        }
    }
    [PSCustomObject]@{
        case = $Name
        exit = $exitCode
        checks = $Needles.Count
    }
}

$cases = @()
$cases += Invoke-Case "k12_13_structural" 0 @(
    (Join-Path $fixtureDir "k12_13.edge"),
    "--expect-n", "25", "--min-edges", "156",
    "--ledger", (Join-Path $ledgerDir "k12_13_structural.ledger")
) @("actual_edges=156", "diameter_exactly_2=true",
    "edge_critical=true", "target_accept=true")

$cases += Invoke-Case "k12_13_target_threshold" 1 @(
    (Join-Path $fixtureDir "k12_13.edge"),
    "--expect-n", "25", "--min-edges", "157",
    "--ledger", (Join-Path $ledgerDir "k12_13_target_threshold.ledger")
) @("edge_critical=true", "threshold_ok=false", "target_accept=false")

$cases += Invoke-Case "star_disconnecting_deletions" 0 @(
    (Join-Path $fixtureDir "star_k1_4.edge"),
    "--expect-n", "5", "--min-edges", "4",
    "--ledger", (Join-Path $ledgerDir "star_k1_4.ledger")
) @("connected=true", "original_diameter=2",
    "edge_critical=true", "target_accept=true")

$cases += Invoke-Case "c5_edge" 0 @(
    (Join-Path $fixtureDir "c5.edge"),
    "--expect-n", "5", "--min-edges", "5",
    "--ledger", (Join-Path $ledgerDir "c5_edge.ledger")
) @("format=edge", "original_diameter=2", "critical_edges=5/5",
    "target_accept=true")

$cases += Invoke-Case "c5_adjacency" 0 @(
    (Join-Path $fixtureDir "c5.adj"),
    "--expect-n", "5", "--min-edges", "5",
    "--ledger", (Join-Path $ledgerDir "c5_adjacency.ledger")
) @("format=adj", "original_diameter=2", "critical_edges=5/5",
    "target_accept=true")

$cases += Invoke-Case "dense_noncritical" 1 @(
    (Join-Path $fixtureDir "k25_minus_edge.edge"),
    "--expect-n", "25", "--min-edges", "157",
    "--ledger", (Join-Path $ledgerDir "dense_noncritical.ledger")
) @("actual_edges=299", "diameter_exactly_2=true",
    "edge_critical=false", "target_accept=false")

$cases += Invoke-Case "corrupted_positive_plus_edge" 1 @(
    (Join-Path $fixtureDir "k12_13_plus_edge.edge"),
    "--expect-n", "25", "--min-edges", "157",
    "--ledger", (Join-Path $ledgerDir "corrupted_positive_plus_edge.ledger")
) @("actual_edges=157", "diameter_exactly_2=true",
    "edge_critical=false", "target_accept=false")

$cases += Invoke-Case "corrupted_positive_missing_edge" 1 @(
    (Join-Path $fixtureDir "k12_13_missing_edge.edge"),
    "--expect-n", "25", "--min-edges", "0",
    "--ledger", (Join-Path $ledgerDir "corrupted_positive_missing_edge.ledger")
) @("actual_edges=155", "diameter_exactly_2=false", "target_accept=false")

$cases += Invoke-Case "disconnected_infinite_distance" 1 @(
    (Join-Path $fixtureDir "disconnected.edge"),
    "--expect-n", "4", "--min-edges", "0",
    "--ledger", (Join-Path $ledgerDir "disconnected.ledger")
) @("connected=false", "original_diameter=INF",
    "diameter_exactly_2=false", "target_accept=false")

$cases += Invoke-Case "parser_duplicate" 2 @(
    (Join-Path $fixtureDir "bad_duplicate.edge")
) @("VERIFIER_A_PARSE_ERROR", "duplicate edge")

$cases += Invoke-Case "parser_loop" 2 @(
    (Join-Path $fixtureDir "bad_loop.edge")
) @("VERIFIER_A_PARSE_ERROR", "loop is not allowed")

$cases += Invoke-Case "parser_reversed" 2 @(
    (Join-Path $fixtureDir "bad_reversed.edge")
) @("VERIFIER_A_PARSE_ERROR", "endpoints must satisfy U < V")

$cases += Invoke-Case "parser_count" 2 @(
    (Join-Path $fixtureDir "bad_count.edge")
) @("VERIFIER_A_PARSE_ERROR", "declared edge count")

$cases += Invoke-Case "parser_asymmetry" 2 @(
    (Join-Path $fixtureDir "bad_asymmetric.adj")
) @("VERIFIER_A_PARSE_ERROR", "asymmetric adjacency relation")

$kLedger = Get-Content (Join-Path $ledgerDir "k12_13_structural.ledger")
if (($kLedger | Where-Object { $_ -like "deleted *" }).Count -ne 156) {
    throw "K12,13 ledger does not contain exactly 156 deleted-edge rows"
}
if (($kLedger | Where-Object { $_ -like "w *" }).Count -ne 156) {
    throw "K12,13 ledger does not contain exactly 156 witness rows"
}
if (($kLedger | Where-Object {
        $_ -like "deleted *" -and $_ -notlike "*diameter 3 witness_count 1"
    }).Count -ne 0) {
    throw "K12,13 deleted-edge ledger is not uniformly one distance-3 witness"
}

$starLedger = Get-Content (Join-Path $ledgerDir "star_k1_4.ledger")
if (($starLedger | Where-Object { $_ -like "deleted *" }).Count -ne 4) {
    throw "star ledger does not contain exactly four deleted-edge rows"
}
if (($starLedger | Where-Object {
        $_ -like "deleted *" -and $_ -notlike "*connected 0 diameter INF*"
    }).Count -ne 0) {
    throw "star deletion did not produce the required infinite diameter"
}

$denseLedger = Get-Content (Join-Path $ledgerDir "dense_noncritical.ledger")
if (($denseLedger | Where-Object { $_ -like "deleted *" }).Count -ne 299) {
    throw "dense ledger does not contain exactly 299 deleted-edge rows"
}
if (($denseLedger | Where-Object {
        $_ -like "deleted *" -and $_ -notlike "*witness_count 0"
    }).Count -ne 0) {
    throw "dense noncritical ledger unexpectedly contains a critical edge"
}

$c5EdgeHash = (Get-FileHash -Algorithm SHA256 (
    Join-Path $ledgerDir "c5_edge.ledger")).Hash
$c5AdjHash = (Get-FileHash -Algorithm SHA256 (
    Join-Path $ledgerDir "c5_adjacency.ledger")).Hash
if ($c5EdgeHash -ne $c5AdjHash) {
    throw "edge and adjacency parsers disagree on the C5 ledger"
}

$disconnectedLedger = Get-Content (Join-Path $ledgerDir "disconnected.ledger")
if (($disconnectedLedger |
        Where-Object { $_ -like "w * distance INF" }).Count -eq 0) {
    throw "disconnected ledger contains no infinite-distance witness"
}

$cases | Format-Table -AutoSize
Write-Output "CALIBRATION_A_OK cases=$($cases.Count) ledger_checks=9"
