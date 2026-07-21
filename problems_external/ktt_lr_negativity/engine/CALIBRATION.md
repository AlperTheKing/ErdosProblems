# CALIBRATION.md — cross-engine calibration gate (A vs B) + interp.py

- Date: 2026-07-21T01:40 (driver run) / 01:44 (end-to-end rehearsal)
- Operator: Fable-5 subagent (workflow ktt-lr-negativity-hunt, calibration gate)
- Driver: `calibrate.py` (this directory; deterministic seeds inside, artifacts under `calib/`)
- Engine A: `lr_hive.exe` (C++ Knutson–Tao hive model), sha256 `95d1fea3716756ffc48e662cfca117f04cc354ed598a638134163e50585b8cfc`
- Engine B: `engineB_lrrule.py` (Python classical LR lattice-word rule), sha256 `c7677d041ed184910a4290116b320000e529d70192c7f0cc91ccbfcc924b706c`
- All comparisons are raw-output-line string equality (exact big-integer counts or
  `CAP_EXCEEDED`); no floating point anywhere in any decision.

## VERDICT: **CALIBRATION PASS** (0 disagreements anywhere; interp.py 25/25 unit checks)

| Gate | Spec | Result |
|---|---|---|
| 1. Cross-compare | 300 random triples, r(ν)≤5, \|ν\|≤16, exact match every line | **PASS 300/300** (output files byte-identical) |
| 2. c=1 stretched | 20 random c=1 triples, c(nλ,nμ;nν)=1 for n=1..6, both engines | **PASS 240/240 checks** |
| 3. c=2 stretched | 20 random c=2 triples, count = n+1 for n=1..6, both engines | **PASS 240/240 checks** |
| 4. interp.py | exact Fraction Newton interpolation + held-out verify + unit tests | **PASS 25/25 checks** |

Reproduce: `python calibrate.py` (exit 0) and `python interp.py --selftest` (exit 0).

## Gate 1 — 300-triple cross-comparison

Batch `calib/triples300.batch` (sha256 `c5aad67a…`), one run per engine via
`--batch`; outputs `calib/phase1_A.out` / `calib/phase1_B.out`.

- Composition: 280 seeded random weight-matched triples (seed **20260721001**;
  ν uniform over partitions of N∈[2,16] with ≤5 parts, |λ|+|μ|=|ν|, λ,μ uniform
  over partitions with ≤5 parts; deduplicated) + 20 deterministic edge lines:
  8 weight-mismatch (→0), 6 parts(λ/μ)>parts(ν) (→0, incl. 8-part λ),
  3 empty-partition forms (`0;3,3,1;3,3,1`, `3,2;0;3,2`, `0;0;0` → 1),
  3 cap-semantics lines on the c=2 triple (2,1)² → (3,2,1): cap 1 → `CAP_EXCEEDED`,
  cap 2 → `2`, cap 10¹² → `2`.
- Result: **0 mismatches in 300**; `phase1_A.out` and `phase1_B.out` have the
  **same sha256** `44508388cb8feea0…` (byte-identical).
- Value distribution (from engine A line): `0`×226, `1`×69, `2`×3, `3`×1,
  `CAP_EXCEEDED`×1 (the deliberate cap-1 edge line). Max multiplicity in this
  window is 3 — expected for r≤5, |ν|≤16; higher-c coverage (to c=4) exists in
  the independent BUILD_A/BUILD_B ground-truth validations, and Gates 2–3 below
  exercise stretched values up to 7.
- Runtime: A 0.03 s, B 0.11 s.

## Gate 2 — 20 random c=1 triples: stretched counts all 1 (Knutson–Tao–Woodward)

- Pool: fresh seeded random triples (seed **20260721002**, |ν|≤12, r≤5) filtered
  to c=1 **by both engines in agreement** (every pool candidate batch, 400
  triples/round, was itself cross-compared with abort-on-disagreement: 0
  disagreements in ≥400 candidates). Pool found: 99; 20 drawn at random.
- Check: c(n·ν; n·λ, n·μ) for n=1..6 on **both** engines — 20×6×2 = **240
  values, all exactly 1**. Outputs byte-identical (sha256 `d564845fc403a0fd…`).
- Drawn triples (λ;μ;ν): `4,1,1;3,3;6,4,2` · `3;5,1,1;6,2,1,1` · `2;3;3,2` ·
  `3,2,1,1;1,1;3,3,1,1,1` · `4,1,1;1;4,1,1,1` · `1;1,1;1,1,1` ·
  `1,1;2,1,1;3,1,1,1` · `4,3,1,1;1,1;5,4,1,1` · `2,1,1;1,1,1;3,2,2` ·
  `4,3,1,1;1;5,3,1,1` · `3;2;3,2` · `2,1,1;1;3,1,1` · `1,1,1;1;2,1,1` ·
  `3;1;4` · `1,1,1,1;1;2,1,1,1` · `2,2;1,1;3,2,1` · `2,1;3,1;4,1,1,1` ·
  `1,1,1;1,1;2,1,1,1` · `2,1;1,1;3,2` · `2,1;1;3,1`
- Artifacts: `calib/stretch_c1.batch` + `_A.out`/`_B.out`. Runtime: A 0.03 s, B 0.10 s.

## Gate 3 — 20 random c=2 triples: stretched counts n+1 (Ikenmeyer/Sherman)

- Pool: seed **20260721003**, same procedure (candidates cross-compared,
  0 disagreements); pool found: 25; 20 drawn.
- Check: 20×6×2 = **240 values, all exactly n+1** (n=1..6; stretched |ν| up to
  72). Outputs byte-identical (sha256 `11887d2d109bb89f…`).
- Drawn triples (λ;μ;ν): `2,1;3,2;4,3,1` · `4,1,1,1;4,1;7,2,1,1,1` ·
  `3,2,1,1;2,1;3,3,2,1,1` · `2,1,1;3,1;4,2,1,1` · `4,2;2,1;5,3,1` ·
  `2,2,1;6,1;7,2,2,1` · `4,1,1,1;3,2;6,3,1,1,1` · `3,1;4,2,1,1;4,4,2,1,1` ·
  `3,2,1,1;2,1,1;3,3,2,2,1` · `3,2,2;2,2,1;4,4,3,1` · `2,1,1;2,2,1;3,3,2,1` ·
  `2,2,1,1;3,2,1;4,3,3,1,1` · `2,1;4,3,2;5,3,3,1` · `3,1,1;3,3,1;4,4,3,1` ·
  `2,1;3,2,1;4,2,2,1` · `3,2,1;2,2,1,1;4,4,2,1,1` · `3,2;3,2,2;4,3,2,2,1` ·
  `3,1;4,1;5,3,1` · `4,1;5,1,1;6,4,1,1` · `2,1,1;2,1,1;3,2,2,1`
- Artifacts: `calib/stretch_c2.batch` + `_A.out`/`_B.out`. Runtime: A 0.03 s, B 0.11 s.

## Gate 4 — interp.py (exact interpolation + held-out verification)

`interp.py` (sha256 prefix `8115e0cb0b9de58b`). Contract:

- `python interp.py <samples.txt>`; lines `n value` (value = integer or exact
  `p/q`; `#`-comments/blank lines ignored). **Last two lines are held-out
  verification points**; all earlier lines (the caller passes exactly D+1 of
  them) are interpolation nodes. Newton divided differences over
  `fractions.Fraction` — exact, no floats.
- Prints: `POINTS:<m>`, `DEGREE:<d>` (trailing zero coefficients stripped),
  `COEFFS_LOW_TO_HIGH:c0 c1 … cd` (exact Fractions, e.g. `1 3/2 1/2`),
  `NEGATIVE_COEFF:<k>` for every strictly negative coefficient (ascending k),
  two `HELDOUT n=… file=… poly=… match=…` lines, `EXTRA_POINT_MATCH:yes|no`
  (yes iff **both** held-out points match exactly).
- Exit codes: `0` ran + both held-out matched; `3` ran + mismatch (caller must
  treat as **DEGREE_ANOMALY**, never a hit); `2` malformed input (incl.
  duplicate nodes, non-numeric values such as a stray `CAP_EXCEEDED`).

Unit tests (`python interp.py --selftest`, **25/25 PASS**, exit 0):
T1 P≡1 (KTW shape) → `COEFFS 1`; T2 P=n+1 (c=2 shape) → `1 1`;
T3 P=(n+1)(n+2)/2 → fractional `1 3/2 1/2`; **T4 P=2n³−5n²+3n+7 →
`7 3 -5 2` with exactly `NEGATIVE_COEFF:2`** (the mandated
negative-coefficient case); T5 corrupted held-out on P=n² →
`EXTRA_POINT_MATCH:no` + exit 3; T6 degree-6 (r=5 hunt shape D=6) with 10³⁰-
scale coefficients → exact recovery, `NEGATIVE_COEFF:0` and `:5`; T7
fraction-valued samples P=n/2; T8 duplicate-n rejected; CLI subprocess checks
of exact output lines and exit codes 0/3.

### End-to-end rehearsal on real engine output (hunt-loop shape)

Triple `4,1,1,1;4,1;7,2,1,1,1` (r=5 ⇒ D=6) stretched n=0..8 on **both** engines
(byte-identical: `1 2 3 4 5 6 7 8 9`, stretched |ν| up to 96); `calib/e2e_samples.txt`
(9 lines = 7 nodes + 2 held-out) fed to interp.py →
`DEGREE:1`, `COEFFS_LOW_TO_HIGH:1 1`, both `HELDOUT … match=yes`,
`EXTRA_POINT_MATCH:yes`, exit 0. Matches Ikenmeyer/Sherman exactly.

## Cross-agreement tally

300 (gate 1) + 120+120 (stretched, both engines vs theorem AND each other)
+ ≥800 pool candidates (abort-on-disagreement) + 9 (end-to-end) =
**≥1349 triples cross-checked, 0 disagreements**; every A-vs-B output file
pair byte-identical.

## Artifact index (sha256 prefixes; full hashes in `calib/summary.json`)

| file | sha256 (16) |
|---|---|
| `calibrate.py` (driver, seeds 20260721001/2/3) | `63fa72b2124041d5` |
| `calib/triples300.batch` | `c5aad67a462a92c5` |
| `calib/phase1_A.out` = `phase1_B.out` | `44508388cb8feea0` |
| `calib/stretch_c1.batch` / A=B out | `c7a930a586268ccd` / `d564845fc403a0fd` |
| `calib/stretch_c2.batch` / A=B out | `7c84f678bc5713c0` / `11887d2d109bb89f` |
| `calib/e2e_c2_r5.batch`, `calib/e2e_samples.txt` | see `calib/`, `47d0ecb9c5b5cd52` |
| `interp.py` | `8115e0cb0b9de58b` |
| `calib/summary.json` | machine-readable summary of all three engine gates |

## Consequences for the hunt

- Engines A and B may be used as mutually confirming oracles; any future
  disagreement on a hunt triple is a hard stop (engine bug, not math).
- Candidate-negativity pipeline is armed: sample n=0..D (D=(r−1)(r−2)/2),
  interpolate through n=0..D, verify P(D+1), P(D+2) held-out via
  `interp.py` (`EXTRA_POINT_MATCH:no` ⇒ DEGREE_ANOMALY report, never a hit);
  `NEGATIVE_COEFF:k` on a verified polynomial = candidate hit → re-verify on
  the second engine before any claim.
