# Result protocol for the fixed `K_19-C_19` CaDiCaL run

Status: **FROZEN PRE-LAUNCH PROCEDURE**.  This procedure classifies only a
run of the exact DIMACS instance identified below.  It does not launch or
modify a solver run, decoder, verifier, or proof checker.

## 1. Frozen artifacts and acceptance threshold

All commands below are run from `E:\Projects\ErdosProblems` in PowerShell 7.
Set `$runDir` to the one canonical run directory produced by
`run_cycle19_cadical.ps1`; do not combine artifacts from different runs.

```powershell
$engine = (Resolve-Path -LiteralPath 'problems_external\ssnc_refutation\engine').Path
$wrapper = (Resolve-Path -LiteralPath "$engine\run_cycle19_cadical.ps1").Path
$cnf = (Resolve-Path -LiteralPath "$engine\instances\cycle19-fixed-v1\cycle19.cnf").Path
$manifest = (Resolve-Path -LiteralPath "$engine\instances\cycle19-fixed-v1\manifest.json").Path
$decoder = (Resolve-Path -LiteralPath "$engine\decode_cycle19_model.py").Path
$scalar = (Resolve-Path -LiteralPath "$engine\verify_scalar.py").Path
$bitset = (Resolve-Path -LiteralPath "$engine\verify_bitset.exe").Path
$checker = (Resolve-Path -LiteralPath 'third_party\cadical\build\drat-trim.exe').Path
$runDir = (Resolve-Path -LiteralPath '<canonical-run-dir>').Path

function Assert-Sha256([string]$Path, [string]$Expected) {
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
    if ($actual -ne $Expected) { throw "SHA-256 mismatch for ${Path}: $actual" }
}

Assert-Sha256 $wrapper 'DD753A4C38EC91E9C8C0A0804C955270C2044F19A77D02E838F423C229E8DBA2'
Assert-Sha256 $cnf 'A030330116CF8C7F1DA9A4A84C868D375A8177FDAA3E57B924936113E095EA38'
Assert-Sha256 $manifest '4CF5469273AD6F2DF524EC21B30379151D174B2533AF0BC463A33A6DDA4D687E'
Assert-Sha256 $decoder 'E0E43B151F32B4659D779FACCFCAA106ADC3B3CED6052BBB858AB8102C4E44F6'
Assert-Sha256 $scalar '71B9C070AEDAA563A16A4FD6B3BE5334C87B6AA3F876679DEB8C5D223A2EB443'
Assert-Sha256 $bitset 'E6683BEA5B835B5BFD78464DAB21BA2EBEF0436218C468AF1A5EE933BAB439EC'
Assert-Sha256 $checker '5D2FBA5B49CF82D04411CD1A42BAD481AF8777A4F97DD53B22968ABD9D5F52BC'
```

The raw run files are immutable evidence.  Before parsing anything, record
the byte size and SHA-256 of `summary.json`, `state.json`,
`solver.stdout.txt`, `solver.stderr.txt`, `solution.txt`, and `proof.drat`
whenever present.  The `summary.json` value `cnf_sha256` must equal the frozen
CNF hash.  A missing/malformed summary, a different CNF hash, a nonempty
solver stderr, or disagreement between `summary.json` and the actual files is
`FAILED`, not a mathematical result.

The patched wrapper checks `ExpectedCnfSha256` before computing or creating
`RunDir`.  A bad expected hash must terminate the wrapper with exit 1 and
leave the requested run directory nonexistent.  This was exercised against
the frozen CNF without starting CaDiCaL: `wrapper_exit=1` and
`run_dir_exists=false`.

The raw wrapper statuses are deliberately unverified.  Distinguish the
solver exit stored in `summary.json` from the wrapper process exit:

- solver exit 10 gives `SAT_UNVERIFIED`; wrapper exit 0;
- solver exit 20 gives `UNSAT_PROOF_UNCHECKED`; wrapper exit 0;
- deadline termination gives `TIMEOUT`; wrapper exit 124; and
- every other solver exit gives `FAILED`; wrapper exit 1.

Never change `summary.json` from `independently_verified=false`.  Record
independent replay in separate ledger/checker artifacts.

## 2. SAT branch

Enter this branch only when all of the following hold:

```text
summary.status             = SAT_UNVERIFIED
summary.solver_exit_code   = 10
summary.independently_verified = false
summary.cnf_sha256         = A0303301...095EA38
summary.stderr_bytes       = 0
solution.txt contains exactly one status line: s SATISFIABLE
```
Enforce these conditions rather than reading them visually:

```powershell
$summary = Get-Content -Raw -LiteralPath "$runDir\summary.json" | ConvertFrom-Json
if ($summary.status -ne 'SAT_UNVERIFIED' -or
    $summary.solver_exit_code -ne 10 -or
    $summary.independently_verified -ne $false -or
    $summary.cnf_sha256 -ne 'A030330116CF8C7F1DA9A4A84C868D375A8177FDAA3E57B924936113E095EA38' -or
    $summary.stderr_bytes -ne 0) {
    throw 'raw SAT summary contract failed'
}
$statusLines = @(Get-Content -LiteralPath "$runDir\solution.txt" |
    Where-Object { $_ -match '^s ' })
if ($statusLines.Count -ne 1 -or $statusLines[0] -ne 's SATISFIABLE') {
    throw 'raw SAT solution status contract failed'
}
```

### 2.1 Decode the raw model

The decoder accepts only CaDiCaL competition-format `s`/`v` lines, requires
all 152 orientation variables, reconstructs the fixed support, and checks
the symmetry, degree, source-unreachable, and target-unreachable ledgers.
Its success is still labelled `DECODED_UNVERIFIED`.

```powershell
python $decoder --solution "$runDir\solution.txt" --manifest $manifest `
    --output "$runDir\certificate.json" `
    1> "$runDir\decode.stdout.json" 2> "$runDir\decode.stderr.txt"
if ($LASTEXITCODE -ne 0) { throw 'SAT model decoding failed' }

$decode = Get-Content -Raw -LiteralPath "$runDir\decode.stdout.json" | ConvertFrom-Json
if ($decode.status -ne 'DECODED_UNVERIFIED' -or $decode.orientation_variables -ne 152) {
    throw 'unexpected decoder result'
}
if ((Get-Item -LiteralPath "$runDir\decode.stderr.txt").Length -ne 0) {
    throw 'decoder wrote stderr'
}

$solutionHash = (Get-FileHash -Algorithm SHA256 -LiteralPath "$runDir\solution.txt").Hash
$certificateFileHash = (Get-FileHash -Algorithm SHA256 -LiteralPath "$runDir\certificate.json").Hash
$certificateCanonicalHash = $decode.certificate_sha256
```

Preserve and report all three hashes.  `certificateFileHash` identifies the
exact pretty-printed file; `certificateCanonicalHash` identifies the
canonical adjacency object independently of whitespace.

### 2.2 Run both independent exhaustive verifiers

```powershell
python $scalar "$runDir\certificate.json" `
    1> "$runDir\scalar.ledger.json" 2> "$runDir\scalar.stderr.txt"
$scalarExit = $LASTEXITCODE

& $bitset "$runDir\certificate.json" `
    1> "$runDir\bitset.ledger.json" 2> "$runDir\bitset.stderr.txt"
$bitsetExit = $LASTEXITCODE

if ($scalarExit -ne 0 -or $bitsetExit -ne 0) { throw 'a verifier rejected the certificate' }
if ((Get-Item "$runDir\scalar.stderr.txt").Length -ne 0 -or
    (Get-Item "$runDir\bitset.stderr.txt").Length -ne 0) {
    throw 'a verifier wrote stderr'
}

$s = Get-Content -Raw "$runDir\scalar.ledger.json" | ConvertFrom-Json
$b = Get-Content -Raw "$runDir\bitset.ledger.json" | ConvertFrom-Json
if ($s.status -ne 'VERIFIED_COUNTEREXAMPLE' -or
    $b.status -ne 'VERIFIED_COUNTEREXAMPLE' -or
    $s.n -ne 19 -or $b.n -ne 19 -or
    $s.failing_vertices.Count -ne 0 -or $b.failing_vertices.Count -ne 0 -or
    $s.errors.Count -ne 0 -or $b.errors.Count -ne 0) {
    throw 'verifier status contract failed'
}

python -c "import json,sys; a=json.load(open(sys.argv[1],encoding='utf-8-sig')); b=json.load(open(sys.argv[2],encoding='utf-8-sig')); assert a==b; print('LEDGER_AGREEMENT')" `
    "$runDir\scalar.ledger.json" "$runDir\bitset.ledger.json"
if ($LASTEXITCODE -ne 0) { throw 'verifier ledgers disagree' }
```

Exit 0 and status `VERIFIED_COUNTEREXAMPLE` are both mandatory.  Exit 1 is a
valid oriented graph that is not a counterexample.  Exit 2 is an invalid
certificate.  Raw JSON byte equality is not required because the two
implementations order object keys differently; parsed JSON equality is
required.

### 2.3 Produce the complete presentation ledger

The verifier ledger contains exact `N+(v)` and new `N2+(v)`.  Derive the
unreachable set as their off-diagonal complement and check both axes:

```powershell
$agreed = Get-Content -Raw "$runDir\scalar.ledger.json" | ConvertFrom-Json
$targetCounts = [int[]]::new(19)
$rows = @()
foreach ($row in $agreed.per_vertex) {
    $unreachable = @(0..18 | Where-Object {
        $_ -ne [int]$row.vertex -and $_ -notin $row.n1 -and $_ -notin $row.n2_new
    })
    if ($row.d1 -ne 8 -or $row.d2 -ne 7 -or
        -not $row.strict_d2_lt_d1 -or $unreachable.Count -ne 3) {
        throw "bad neighborhood ledger at vertex $($row.vertex)"
    }
    foreach ($target in $unreachable) { $targetCounts[$target]++ }
    $rows += [ordered]@{
        vertex = [int]$row.vertex
        n1 = @($row.n1)
        d1 = [int]$row.d1
        n2_new = @($row.n2_new)
        d2 = [int]$row.d2
        unreachable = $unreachable
        unreachable_count = $unreachable.Count
        strict_d2_lt_d1 = [bool]$row.strict_d2_lt_d1
    }
}
if (@($targetCounts | Where-Object { $_ -ne 3 }).Count -ne 0) {
    throw "target-unreachable ledger is not all 3: $targetCounts"
}
[ordered]@{ n = 19; per_vertex = $rows; target_unreachable_counts = @($targetCounts) } |
    ConvertTo-Json -Depth 8 |
    Set-Content -LiteralPath "$runDir\complete.ledger.json" -Encoding utf8NoBOM
$completeLedgerHash = (Get-FileHash -Algorithm SHA256 -LiteralPath "$runDir\complete.ledger.json").Hash
```

SAT acceptance requires the canonical `certificate.json`, both verifier
ledger files, `complete.ledger.json`, their hashes, both verifier exits 0,
both exact statuses, parsed-ledger agreement, and all 19 rows equal to
`(d1,d2,unreachable_count)=(8,7,3)`.

On acceptance, stop every active search immediately.  Repeat the live
current-status and novelty search before any discovery statement.  A decoder
failure, verifier rejection, ledger disagreement, or missing artifact is
`SAT_REPLAY_FAILED`; it is not a counterexample and does not authorize an
automatic rerun.

## 3. UNSAT branch

Enter this branch only when all of the following hold:

```text
summary.status             = UNSAT_PROOF_UNCHECKED
summary.solver_exit_code   = 20
summary.independently_verified = false
summary.cnf_sha256         = A0303301...095EA38
summary.stderr_bytes       = 0
solution.txt contains exactly one status line: s UNSATISFIABLE
proof.drat exists and has positive byte length
```
Enforce the raw UNSAT preconditions:

```powershell
$summary = Get-Content -Raw -LiteralPath "$runDir\summary.json" | ConvertFrom-Json
if ($summary.status -ne 'UNSAT_PROOF_UNCHECKED' -or
    $summary.solver_exit_code -ne 20 -or
    $summary.independently_verified -ne $false -or
    $summary.cnf_sha256 -ne 'A030330116CF8C7F1DA9A4A84C868D375A8177FDAA3E57B924936113E095EA38' -or
    $summary.stderr_bytes -ne 0) {
    throw 'raw UNSAT summary contract failed'
}
$statusLines = @(Get-Content -LiteralPath "$runDir\solution.txt" |
    Where-Object { $_ -match '^s ' })
if ($statusLines.Count -ne 1 -or $statusLines[0] -ne 's UNSATISFIABLE') {
    throw 'raw UNSAT solution status contract failed'
}
```

Record the proof size and hash before checking, then invoke the independent
checker on the frozen DIMACS and that exact proof:

```powershell
$proof = (Resolve-Path -LiteralPath "$runDir\proof.drat").Path
$proofBytes = (Get-Item -LiteralPath $proof).Length
if ($proofBytes -le 0) { throw 'empty proof artifact' }
$proofHashBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $proof).Hash

& $checker $cnf $proof `
    1> "$runDir\drat-trim.stdout.txt" 2> "$runDir\drat-trim.stderr.txt"
$checkerExit = $LASTEXITCODE
$proofHashAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $proof).Hash

if ($checkerExit -ne 0) { throw "DRAT checker exit $checkerExit" }
if ($proofHashAfter -ne $proofHashBefore) { throw 'proof changed during checking' }
if (-not (Select-String -LiteralPath "$runDir\drat-trim.stdout.txt" `
        -Pattern '^s VERIFIED$' -Quiet)) {
    throw 'checker output lacks exact s VERIFIED line'
}
```

Both checker exit 0 and an exact `s VERIFIED` line are mandatory.  Solver
exit 20 alone, a nonempty proof file, CaDiCaL's internal status, or an
unchecked `s UNSATISFIABLE` line is not an UNSAT result.  Preserve and report
the CNF hash, proof byte size, proof hash, checker executable hash, checker
exit, and checker stdout/stderr hashes.

A checked proof closes only the exact orientation family encoded here:
outdegree-8 orientations of `K_19-C_19` with the sharp three-by-three
unreachable ledger (the single `0->2` symmetry unit is sound by the frozen
dihedral argument).  It does not prove SSNC, exclude other order-19
2-factors, exclude all `q=19` graphs, or authorize another order/degree lane.
Stop this connected-cycle lane after recording the checked finite result.

## 4. Timeout, failure, and hard stops

| Raw outcome | Mathematical classification | Required action |
|---|---|---|
| `SAT_UNVERIFIED` | no result until Section 2 passes completely | replay once; accept or record `SAT_REPLAY_FAILED`; stop |
| `UNSAT_PROOF_UNCHECKED` | no result until Section 3 passes completely | check the exact proof once; accept or record `UNSAT_PROOF_REJECTED`; stop |
| `TIMEOUT` (wrapper exit 124) | `NO_HIT` / mechanism `BLOCKED` | preserve every artifact and process-exit fact; do not decode partial output or treat a partial proof as evidence; stop |
| `FAILED` | infrastructure/solver failure, no mathematical result | preserve summary, stderr, exit, sizes, and hashes; report the anomaly; stop |
| missing or inconsistent summary | `FAILED`, no mathematical result | preserve files; do not infer SAT/UNSAT from fragments; stop |

No branch permits an automatic cascade to another 2-factor, value of `q`,
order, or degree.  A verified SAT certificate triggers a global search stop
and live novelty gate.  A checked UNSAT proof closes only this fixed family.
All other outcomes leave SSNC unresolved and terminate this registered lane.
