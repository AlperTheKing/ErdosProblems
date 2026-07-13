$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
$mapPath = Join-Path $PSScriptRoot 'semantic_map.json'
$tablePath = Join-Path $PSScriptRoot 'dependency_table.tsv'
$auditPath = Join-Path $PSScriptRoot 'AUDIT.md'
$map = Get-Content -LiteralPath $mapPath -Raw | ConvertFrom-Json

if ($map.schema -ne 'erdos23-r29-semantic-map-v1') {
    throw "Unexpected schema: $($map.schema)"
}
if ($map.exact_arithmetic_only -ne $true) {
    throw 'Map is not marked exact-arithmetic-only'
}

$anchorCount = 0
foreach ($entity in $map.entities) {
    foreach ($anchor in $entity.anchors) {
        $path = Join-Path $root $anchor.file
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Missing anchor file: $($anchor.file)"
        }
        $lines = Get-Content -LiteralPath $path
        $index = [int]$anchor.line - 1
        if ($index -lt 0 -or $index -ge $lines.Count) {
            throw "Anchor line out of range: $($anchor.file):$($anchor.line)"
        }
        if ($lines[$index] -notlike "*$($anchor.contains)*") {
            throw "Anchor mismatch: $($anchor.file):$($anchor.line) expected '$($anchor.contains)'"
        }
        $anchorCount++
    }
}

$null = & git -C $root grep -n 'CheckedTransferMatching' -- 'problems/23/lean'
$checkedTransferLeanHits = if ($LASTEXITCODE -eq 1) { 0 } elseif ($LASTEXITCODE -eq 0) { 1 } else {
    throw "git grep failed with exit code $LASTEXITCODE"
}
if ($checkedTransferLeanHits -ne 0) {
    throw 'CheckedTransferMatching unexpectedly appears in tracked Lean source'
}

$globalPackage = Get-Content -LiteralPath (Join-Path $root 'problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean') -Raw
foreach ($kind in @('| door', '| vertexSlack', '| c5Base', '| prune')) {
    if (-not $globalPackage.Contains($kind)) {
        throw "Missing compiled CapKind constructor: $kind"
    }
}
if ($globalPackage.Contains('| eta')) {
    throw 'Unexpected eta CapKind constructor'
}

$activeScoped = Get-Content -LiteralPath (Join-Path $root 'problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean') -Raw
foreach ($required in @('ActiveCollisionHalf G c omega', 'ActiveHitNeed G c omega', 'structure Matching', 'Function.Injective assign')) {
    if (-not $activeScoped.Contains($required)) {
        throw "Missing ActiveScoped semantic fragment: $required"
    }
}

$table = Import-Csv -LiteralPath $tablePath -Delimiter "`t"
if ($table.Count -ne 18) {
    throw "Expected 18 dependency rows, found $($table.Count)"
}

$small = $map.r29_smallest_falsifier
if (($small.scoped_demand - $small.scoped_source_neighborhood) -ne $small.defect) {
    throw 'R29 defect arithmetic mismatch'
}
if ($small.defect -ne 28) {
    throw "Unexpected R29 defect: $($small.defect)"
}

$laneFiles = Get-ChildItem -LiteralPath $PSScriptRoot -File |
    Where-Object { $_.Extension -in @('.json', '.tsv', '.md') }
$forbidden = Select-String -Path $laneFiles.FullName -Pattern '\bsorry\b|\badmit\b|\bnative_decide\b' -CaseSensitive
if ($forbidden) {
    throw "Forbidden token found: $($forbidden.Path):$($forbidden.LineNumber)"
}

$hashes = foreach ($path in @($mapPath, $tablePath, $auditPath, $PSCommandPath)) {
    $h = Get-FileHash -LiteralPath $path -Algorithm SHA256
    [pscustomobject]@{ file = (Split-Path $path -Leaf); sha256 = $h.Hash.ToLowerInvariant() }
}

[pscustomobject]@{
    schema = $map.schema
    entities = $map.entities.Count
    anchors_checked = $anchorCount
    dependency_rows = $table.Count
    checked_transfer_matching_tracked_lean_hits = $checkedTransferLeanHits
    source_kinds = ($map.source_kinds.kind -join ',')
    r29_exact_equation = "$($small.scoped_demand)-$($small.scoped_source_neighborhood)=$($small.defect)"
    hashes = $hashes
} | ConvertTo-Json -Depth 4
