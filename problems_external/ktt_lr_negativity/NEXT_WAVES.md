# NEXT_WAVES.md — KTT stretched-LR negativity campaign, completeness critique

Written 2026-07-21 (RUN-TOKEN R2, post-reset audit pass).
Scope: waves 1–4 of `problems_external/ktt_lr_negativity/runs/`.
Result of waves 1–4: **0 hits.** A no-hit sweep is not evidence for the
King–Tollu–Toumazet conjecture and is not treated as such anywhere below.

Target restated: one triple (lam, mu, nu) with a strictly negative monomial
coefficient in P(n) = c(n·nu; n·lam, n·mu). Degree bound D = (r−1)(r−2)/2,
r = #parts(nu); D = dim of the Knutson–Tao hive polytope Q.

---

## 0. Audit method for this document

- All per-family counts below are read from `runs/<family>/manifest.json`.
- The cross-family histograms in §1 come from a fresh streaming scan, made in
  this pass, of every `*.jsonl` under `runs/` except the five files >90 MB
  (`wave2_c456-census-midshell-r5/results.jsonl` 878 MB and four
  `wave2_selfconj-nu-involution-r6/r2b/*` census/screen files), whose contents
  are taken from their manifests instead.
  Scanned: 1,234 files, **980,641 records carrying an explicit `nu`** (screen +
  LP-analyze + profile records combined).
- Exact interpolations (records carrying a `deg` field) in the scanned set:
  **353,350**. Adding the excluded mid-shell census gives ≈ **3.34 M** exactly
  interpolated stretched polynomials campaign-wide.
- Exact n=1 screens campaign-wide ≈ **3.93 × 10^8**, of which 3.35 × 10^8 come
  from one family (`wave3_maxr-minweight-corner`).

---

## 1. What was actually covered

### 1.1 By r (records with an explicit nu, 980,641 scanned)

| r | records | exact interpolations | max deg P observed | D = (r−1)(r−2)/2 |
|---|---|---|---|---|
| 4 | 179 | 64 | 3 | 3 |
| 5 | 505,261 | 326,818 | 6 | 6 |
| 6 | 445,908 | 25,713 | 10 (67 records) | 10 |
| 7 | 26,228 | 755 | 9 (2 records) | 15 |
| 8 | 2,854 | 0 with a deg field | — | 21 |
| 9 | 211 | 0 with a deg field | — | 28 |

Degree histogram, r=6: {0:13, 1:115, 2:6065, 3:4399, 4:3046, 5:4839, 6:4412,
7:1308, 8:568, 9:881, 10:67}.
Degree histogram, r=7: {0:1, 2:62, 3:80, 4:121, 5:164, 6:151, 7:140, 8:34, 9:2}.

### 1.2 By c (records with an explicit nu)

| r | c=3–12 | c=13–24 | c=25–100 | c>100 |
|---|---|---|---|---|
| 5 | 463,751 | 12,014 | 11,713 | 7,774 |
| 6 | 246,368 | 88,455 | 17,156 | 10,932 |
| 7 | 17,611 | 2,759 | 885 | 2,604 |
| 8 | 2,854 | 0 | 0 | 0 |
| 9 | 211 | 0 | 0 | 0 |

(c=1 and c=2 records — the theorem validators — are excluded: 536+338 at r=5,
1,825+1,492 at r=6, 125+90 at r=7.)

The c>24 mass at r=6/7 is almost entirely **LP-oracle screening**, not exact
profiles. Exact profiles above c=24 exist only in
`wave4_oddc-hstar2-parity-break-heavy-r5` (r=5, c up to 1521) and
`wave4_heavy-unbiased-statistic-control-w4` (c up to 40,952 measured, but only
1,225 profiles, all gated to certified dim ≤ 6).

### 1.3 By |nu| (decade buckets, records with an explicit nu)

- r=5: 10–49 → 464,806; 50–119 → 39,695; ≥120 → 760.
- r=6: 10–49 → 245,251; 50–119 → 199,427; ≥120 → 1,230.
- r=7: 10–49 → 13,621; 50–119 → 12,603; ≥120 → 4.
- r=8: 10–39 → 2,854 only. r=9: 20–49 → 211 only.
- Campaign-wide, records with |nu| ≥ 120: **2,026** (760 r=5, 1,230 r=6, 4 r=7,
  32 r=4).

### 1.4 Exhaustive (not sampled) censuses actually completed

| family | census | triples |
|---|---|---|
| `wave2_c456-census-midshell-r5` | r=5, depth ≥4 mid-shell, W=22..34, all admissible | 29,712,059 screened / 2,990,538 profiled |
| `wave3_lowc-highdim-exhaustive-smallnu` | r=6,7,8 × W=18..24, c ≤ 6, exhaustive per cell | 9,288,190 screened / 11,712 oracle analyses |
| `wave4_c-eq-dim-plus-1-heavy-r5` | entire generator pool, 10,153 lam/mu pairs | 14,938,799 |
| `wave1_c3-total-sweep-r5` | c=3, r=5, W=18..30, all splits | 780,000 screened / 21,382 profiled |
| `wave1_stair5-interleave-core` | staircase pool ±4 band, complete | 71,592 |
| `wave1_degenerate-multiplicity-bait-r5` | all 990 repeated-part pairs × 42,343 nu | 3,157 c-band profiles |
| `wave1_conjugation-symmetric-r5` | conj-pairs + full self-conjugate census | 4,146 |
| `wave2_selfconj-nu-involution-r6` | all 32 self-conjugate 6-part nu, complete stratum | 120,590 orbit classes / 7,213 profiled |
| `wave3_selfconj-involution-r6r7` | complete r=6 self-conj census | 6,295 |
| `wave4_s3-cyclic-symmetric-hive` | S_3-fixed locus, N ∈ [8,20], complete | 4,463 LP censused |

### 1.5 Structural facts established (all exact, all reproducible from artifacts)

- `deg P ≤ c − 1` held on every one of ≈3.34 M exact polynomials. **`c ≤ deg P`
  (⇔ h*_1 < 0, the non-lattice jackpot flag) was never once observed**
  (`c_le_dimlo_count=0`, `c_le_dimlo_certificates=0`, min gap c−dim_lo = +1).
- No h*_j < 0 was ever observed. Observed h* support is confined to j ≤ 3 in the
  wave-1 atlas (118,639 triples) and to j ≤ 5 anywhere.
- Route-A arithmetic thresholds (exact, from the h*→monomial transfer matrix):
  negative a_1 needs Σh* ≥ 37 at d=6; h*_2 ≥ 204 at d=9; h*_2 ≥ 264 at d=10.
  Best Σh* ever attained inside the mandated cells: 4 (`wave4_hstar1-le2`), 20
  (`wave3_maxr-minweight-corner`), 478 at c=24 (`wave3_stair6-dimgated`, but
  a_1 = 1501/420 > 0 and ~201 further units of h*_2 short).
- Lattice-simplex requirement for negativity (exact, `wave4_hive-simplex-determinant-mine`):
  h*_1 = 0 together with normalized volume V ≥ 13 (d=3), ≥19 (d=5), ≥25 (d=7),
  ≥27 (d=4), ≥37 (d=6). All 1,886 certified h*_1=0 hive simplices found were
  unimodular (V=1).
- Weight scaling is inert: at fixed absolute perturbation the stretched
  polynomial is bit-identical for every base weight t ≥ 2 (checked to t=32,
  205/213 ladders already identical at t=1 vs t=2).

---

## 2. What was NOT covered

### 2.1 r ranges

- **r = 3 (d=1) and r = 4 (d=3): no census at all.** 179 r=4 records exist
  campaign-wide, incidental drift from evolvers; 0 at r=3. d=3 is the dimension
  of the classical Reeve simplex, i.e. the smallest dimension in which a lattice
  polytope can have a negative Ehrhart coefficient, and the campaign's own exact
  threshold there is the cheapest in the whole table (V ≥ 13 with h*_1 = 0,
  i.e. c = d+1 = 4). The cell "r=4, c=4, dim Q = 3" was **never enumerated**.
  It was excluded by the wave-1 hunt bias ("thin but high-dimensional,
  r ∈ {5,6}"), which was a heuristic, not a theorem.
- **r = 7 above degree 9: zero coverage.** Max degree ever attained at r=7 is 9
  (2 records). D=15. Degrees 10–15 at r=7 are empty of exact data.
- **r = 8 and r = 9: 3,065 records total, all from one minimal-weight family**
  (`wave3_maxr-minweight-corner`, screen cap 12, c ∈ [3,12], |nu| ≤ ~35). Their
  "these polytopes are simplex-like" verdict is a statement about **minimal**
  weight only. r=8/9 at |nu| ∈ [40,80] or c > 12: zero records.
- **r ≥ 10: zero records.**

### 2.2 c ranges

- **r=6, dim ∈ {9,10}, c ∈ [25,80]: measurement-blind, not covered.**
  `wave4_maxden-highc-dim9-r6` certified 1,332 dim-9 and 1,371 dim-10 triples
  but completed only 8 full profiles; its own best record (dim 9, q=3, c=52) has
  h* settled only through j=8 because P(9) returned CAP_EXCEEDED at the raised
  cap 4e7 after 318 s. h*_9 is unknown for every triple in this stratum.
- **c ∈ [13,24] at r=7: 2,759 records but only 16 exact profiles**, all from the
  two unbiased control families and all of degree ≤ 6. c > 24 at r=7: 6 exact
  profiles. Of the 755 r=7 exact polynomials, 733 have c ≤ 12.
- **c > 24 at r=6: 69 exact profiles out of 28,088 records** (61 at c ∈ [25,100],
  max degree 7; 8 at c > 100, max degree 6). Every degree-10 r=6 polynomial in
  the campaign — all 67 of them — comes from one family
  (`wave3_stair6-interleave-dimgated-r6`) and sits at c ∈ {16: 25, 20: 5,
  24: 37}; no odd c and no c ∉ [16,24] has ever produced degree 10 at r=6.
  Route A's own arithmetic says c ≤ 12 cannot
  work at d ≥ 6, so the band the theory points at is the band with the least
  profile coverage: the r=6 exact-profile counts are c ≤ 12 → 15,105,
  c ∈ [13,24] → 526, c > 24 → 69.
- **Odd c at r=6, dim 10: claimed empty (0/6,776) but on a non-rigorous
  measurement** — see §3.2. `dim10_c_distribution` for that family is
  {16:99, 20:41, 24:30}, all even, all from the even-c control cohort.

### 2.3 Shape classes

Never covered, with the run dir that was allocated and produced **zero data**:

| region | allocated slot | artifacts present |
|---|---|---|
| strict all-odd-part lam, mu at r=6 (denominator-2 vertex bait, seed 4307) | `runs/wave2_allodd-parity-r6/` | `hunt.py` only |
| near-Horn-wall r=5 at heavy weight W ∈ [52,56], 8 anchors, hug ≥ 2 | `runs/wave2_nearwall-r5-heavy/` | `driver.py` only |
| hook × fat at r=6 (long-first-row nu) | `runs/wave2_hook-vs-fat-r6/` | 3 probe batch files |
| r=7 Track-B lift (c ≤ deg), seed 4314 | `runs/wave2_r7-trackb-lift/` | `hunt.py` only |
| raised-cap full-degree shelf at r=6 | `runs/wave2_raisedcap-fulldeg-shelf-r6/` | `preflight.batch` only |
| r=6 interior cap-filter Track B | `runs/wave2_r6-interior-capfilter-trackb/` | calibration probe only |
| r=6 beam evolver at low k | `runs/wave2_beam-evolver-r6-lowk/` | none |
| r=6 small-weight census | `runs/wave2_smallw-census-r6/` | none |

That is **8 of 22 wave-2 hunter slots with no data whatsoever.** Waves 1, 3, 4
have 14 populated slots each; wave 2 has 14 populated of 22.

Other shape gaps:
- **Skew / near-disconnected glue at dim > 7: unprofiled.**
  `wave4_near-disconnected-skew-degenerate-content` certified 267 non-lattice
  polytopes, 24 of them at dim 10, and explicitly reports that leg as NOT dead —
  it is simply unprofilable at cap 4e6.
- **|nu| ≥ 120: 2,026 records total across all r** (essentially evolver drift).
  No designed heavy-weight family above |nu| = 64 except the r=5 staircase.
- **Repeated-part nu at r=7: 239 exact polynomials** (`wave2_r7-degenerate-collapse-probe`).
  Repeated-part nu at r ≥ 8: none.
- **Rect × rect, single-row and single-column shapes were prefiltered out
  everywhere by design** (LR-trivial). Not a gap, recorded for completeness.

### 2.4 Box budgets (perturbation / orbit mining)

- Single-box nu-orbits: used in every family.
- 2-box and 3-box coupled moves: only `wave2_rho-max-evolver-multibox-r5` (r=5).
- 5/8/13-box walks: only `wave2_unimodular-spike-probe-r6` (r=6, c ∈ [9,12]).
- **≥4-box coordinated moves at r=7 or above: never run.**
- **Simultaneous 3-way (lam, mu, nu) moves preserving |nu| = |lam|+|mu| beyond
  the two evolvers' repertoires: never run.**
- Corner peels were capped at 6 boxes and 334/3,306 pairs (~10% of the pair
  space) in `wave1_corner-peel-offwall-r5` — that family's own manifest states
  it is NOT exhausted.

### 2.5 Cap / engine reach (the real boundary of the campaign)

The campaign's reach was set by the cost of counting hives by DFS, not by
mathematics:
- Wave-1/2 value cap 200,000; wave-3/4 cap 4 × 10^6 (a few families 10^15–10^18).
- Node cap `LR_HIVE_NODE_CAP` was the true binding limit; raised to 2 × 10^10 in
  wave 3, which retroactively **falsified wave-1's "deg 9–10 cells are
  unreachable"** claim (`wave3_stair6-interleave-dimgated-r6`).
- Arithmetic exclusions that no cap raise inside the current engine can fix:
  a dim-10 polytope forces P(D+2) = P(12) ≥ C(22,10) = 646,646 at r=6, and at
  r=7 forces P(17) ≥ C(27,10) = 8,436,285 > 4 × 10^6. Hence **every r=7 family
  mandated to certify held-out points at dim ≥ 10 was arithmetically incapable
  of finishing** (`wave3_r7-thin-highdim-probe`).
- No Barvinok / LattE style *direct* Ehrhart computation was ever used. The
  entire campaign inferred P by sampling + interpolation.

---

## 3. Anomalies that deserve a dedicated follow-up

### 3.1 Eight unresolved DEGREE_ANOMALY triples (highest priority)

`runs/wave4_heavy-unbiased-statistic-control-w4/ares*.jsonl` records 41
DEGREE_ANOMALY resolutions: 33 `ok`, **8 `CAP_EXCEEDED`**. For those 8 the true
degree of P is still unknown and the low-degree fit demonstrably missed the
held-out points. Engine B agreed with engine A on every sample it could
complete. The triples (idx; r; lam | mu | nu; c; oracle dim; ambient D):

| idx | r | lam | mu | nu | c | oracle d | D |
|---|---|---|---|---|---|---|---|
| 3962 | 7 | 8,8,4,3,3,2,1 | 11,11,6,5,3,3,1 | 17,16,11,8,8,7,2 | 9 | 4 | 15 |
| 1907 | 7 | 21,8,8,4,3,3,1 | 11,9,5,3,2,1 | 30,11,10,10,6,6,6 | 28 | 6 | 15 |
| 1919 | 7 | 8,8,5,2,2,2 | 7,7,3,2,2,1 | 12,9,8,8,6,3,3 | 14 | 6 | 15 |
| 1769 | 7 | 13,7,3,2,2,1,1 | 13,13,11,5,1,1,1 | 19,14,13,11,8,6,3 | 18 | 5 | 15 |
| 3997 | 7 | 7,7,3,3,3,1 | 8,4,3,2,2,1 | 14,9,7,6,4,2,2 | 11 | 6 | 15 |
| 4494 | 7 | 14,8,8,8,2,2 | 9,8,7,3,2,2,1 | 18,16,15,9,7,6,3 | 8 | 5 | 15 |
| 5167 | 7 | 22,11,6,6,3,3,2 | 13,5,2,1,1,1 | 27,18,12,7,4,4,4 | 53 | 6 | 15 |
| 142 | 6 | 19,16,6,3,3 | 18,8,4,4,2,1 | 30,19,18,7,5,5 | 56 | 6 | 10 |

Seven are r=7, where the campaign has 755 exact polynomials total and none of
degree ≥ 10. These are the only triples in the entire campaign whose exact P is
unknown after a mismatch was observed.

### 3.2 The dimension oracle is not a certificate — cross-cutting re-audit needed

`runs/wave4_rho-uncapped-margin-evolver/anomalies.json` (type
`ORACLE_FALSIFICATION`) and the wave-4 control's resolution summary both
establish: **`hive_poly.analyze`'s `dim_lo == dim_hi` agreement test is not a
rigorous dimension certificate.** Root cause recorded: HiGHS returns the same
optimal vertex for many random objectives, so the "tight at every sampled
vertex" set is too large and `dim_hi` collapses together with `dim_lo`.

Measured failure rates: 3 of the first 24 wave-4 triples (12.5%) and 41 of 1,225
unbiased profiles (3.3%), with dim under-estimated by 1 or 2 in every case.
Documented consequence: **24 apparent negative coefficients were produced as
under-degree fitting artifacts and vanished at the true degree** (e.g.
lam=(13,5,4,1,1), mu=(6,5,2,2,1), nu=(16,10,6,5,2,1): analyze dim 6, true dim 8;
the deg-6 interpolant has coefficients 1, −43/10, 4123/180, −161/12, 637/72,
−77/60, 89/360 and misses both held-out points; at dim 8 every coefficient is
positive and both held-out points match).

A validated remedy already exists and was used in exactly one family:
`runs/wave4_rho-uncapped-margin-evolver/dimoracle.py` (implicit-equality method:
constraint i is an implicit equality iff max_{x∈Q}(b_i − A_i x) = 0;
dim Q = d − rank of the implicit set, rank taken exactly).

Every closure that depends on an *upper* bound on dim is therefore unproven,
because `dim_lo` is only a lower bound and `dim_hi` is heuristic. Concretely at
risk: `wave3_oddc-fulldeg-parity-r6` ("0 of 6,776 odd-c triples attained dim 10"),
`wave4_hstar1-le2-dim9-10-prime-cell-r6` (699 dim ≥ 9, `dim_10_certified = 0`
over 8,536 analyses), `wave3_stair6-interleave-dimgated-r6` (10,782 analyze
calls), `wave4_maxden-highc-dim9-r6` (5,061 analyses), `wave3_dim10-lp-census-r6`,
`wave3_selfconj-involution-r6r7` (1,191 analyses).

### 3.3 Certified fractional vertices with q = 4 and q = 5 exist (r = 7)

Three families closed directions on a "vertex denominator ceiling q = 3"
(`wave3_fracvertex-denominator-ladder-r6`, `wave3_horn-facet-degenerate-r6`,
`wave4_maxden-ladder-fulldim-r5`). Those are r=5 / r=6 statements. At r=7,
`runs/wave4_nonsimple-vertex-excess-r6-r7lift/CERT_fractional_q4_q5_r7.json`
carries two independently verified vertices:

- lam=(13,8,7,5,2,1), mu=(7,6,4,3,2,1), nu=(15,13,11,7,5,5,3): c=790,
  certified dim 14, **q = 5**, tight rank 15, tight-basis |det| 5.
- lam=(10,8,6,2,1), mu=(11,6,4,3,1,1), nu=(18,11,9,5,5,3,2): c=644,
  certified dim 12, **q = 4**, tight rank 15, tight-basis |det| 4.

Both are non-lattice hive polytopes, i.e. precisely the class where Stanley's
h* ≥ 0 does not apply. Neither has ever been profiled (c=790 / c=644 at dim
14 / 12 is out of reach of the DFS engine at any cap). The `q ≤ 3` claims must
be restated as r-restricted, and the q ≥ 4 stratum is unexplored.

### 3.4 Resolved in this pass (closed, no follow-up needed)

- `runs/wave2_stair5-heavy-interleave-w2/anomalies/anom_00{0,1,2}.json` were
  logged as DEGREE_ANOMALY with `deg: null`. Re-run of `engine/interp.py` on
  their stored sample tables in this pass returns exit 0 for all three:
  deg 5 (coeffs 1, 41/15, 3, 41/24, 1/2, 7/120), deg 5 (1, 161/60, 65/24, 31/24,
  7/24, 1/40), deg 3 (1, 13/6, 3/2, 1/3); both held-out points match in each
  case; all coefficients positive. Same failure mode as
  `wave2_random-thin-control-w2/degree_anomaly_A1_resolution.json`: a transient
  non-zero exit of the `interp.py` subprocess, i.e. tooling, not mathematics.
  **3 of the campaign's logged anomalies were tooling artifacts.**

### 3.5 Open frontier numbers worth re-attacking rather than re-deriving

- `wave3_dim10-lowc-frontier-r6`: minimum c at certified dim 10 is 28 unbiased,
  **16 after beam steering**; the lattice lower bound is 11; gap 5, never closed.
- `wave2_c11-shell-mapper-r6`: **14,146 distinct c ∈ {11,12} primaries found,
  348 profiled (2.5%)**. That shell is explicitly NOT exhausted.
- `wave4_maxden-highc-dim9-r6`: dim 9, q=3, c=52, h* = (1,42,388,892,534,60,0,0,0)
  with h*_9 unknown — the largest late-j h* mass anywhere in the campaign.

---

## 4. The 14 families to run next

Ordered by expected information per CPU-hour. Every family inherits the wave-3
non-negotiables (exact arithmetic only; dual-engine sample recomputation on any
candidate; mandatory held-out check at n = D+1, D+2) **plus one new
non-negotiable: no dimension may be taken from `hive_poly.analyze` alone — it
must be certified by the implicit-equality oracle `dimoracle.py`, and no
negative coefficient may be reported unless the interpolation degree is at or
above a rigorously certified dim Q.**

**N1. `engineC-barvinok-ehrhart` (infrastructure; run first).**
Replace sample+interpolate with direct Ehrhart computation of Q(lam,mu,nu)
(Barvinok / LattE `count --ehrhart-polynomial`, or an exact rational-generating-
function evaluator on the rhombus system). Removes the value cap and the DFS
node cap simultaneously. Validate against `engine/lr_hive.exe` on the c=1 and
c=2 theorem families and on the campaign's 6 completed dim-10 profiles.
Win condition: one r=7, dim ≥ 10 exact P produced end to end. This single item
gates N6, N8, N9, N10.

**N2. `dimoracle-reaudit-w3w4`.** Re-certify with `dimoracle.py` every dim used
to close a direction in §3.2: the 6,776 odd-c r=6 triples, the 8,536 prime-cell
analyses, the 10,782 stair6-dimgated analyses, the 5,061 maxden-highc analyses,
the 1,191 selfconj analyses. Falsifiable win: any triple whose certified dim
exceeds `analyze`'s by ≥1 and reaches dim 10 at r=6 (which would reopen
`oddc-fulldeg-parity-r6` and `hstar1-le2-dim9-10-prime-cell-r6`). Cost is LP
only, no counting.

**N3. `cap8-anomaly-closure`.** Resolve the 8 triples of §3.1 individually, with
N1's engine or with `LR_HIVE_NODE_CAP` unbounded and no wall timeout. Deliver
the exact P for each. Win: a negative coefficient, or the first r=7 exact
polynomial of degree ≥ 10, or an exact statement of why each is uncomputable.

**N4. `r4-reeve-cell-exhaustive`.** r=4, d=3. Enumerate exhaustively all triples
with |nu| ≤ 40 and c = 4 (⇔ h*_1 = 0), certify dim Q = 3, and compute the
normalized volume V = 6·lead(P). Target: V ≥ 13 (the campaign's own exact d=3
threshold). This is the cheapest cell in the entire problem — P values are tiny,
D = 3, four sample points settle each triple — and it has never been run.
Secondary sweep: c = 5, 6 with V ≥ 27 / larger thresholds at d = 3 is impossible,
so keep the census strictly at c = 4 and record the attained V distribution.

**N5. `q4q5-nonlattice-r7-descent`.** Seed on the two certified q ∈ {4,5} r=7
vertices of §3.3. Orbit-mine single- and double-box moves on (lam, mu, nu)
minimizing c subject to keeping q ≥ 4 certified. Win: a q ≥ 4 triple with c
small enough to profile under N1, or any triple with c ≤ certified dim
(h*_1 < 0), which is a proof of non-integrality and the cheapest jackpot flag
in the campaign — still never observed.

**N6. `nonlattice-full-hstar-remine`.** For every already-banked non-lattice
(q ≥ 2) polytope — 11,861 analyses in `wave3_fracvertex-denominator-ladder-r6`,
267 certified in `wave4_near-disconnected-skew-degenerate-content` (24 at dim 10),
492 q=3 in `wave4_s3-cyclic-symmetric-hive`, 1,499 q=2 + 2 q=3 in
`wave3_oddc-fulldeg-parity-r6` — compute the **full** h*, not the j ≤ 4 prefix.
Stanley gives no protection here and the campaign only ever measured prefixes on
these. Win: any h*_j < 0.

**N7. `r6-c11c12-shell-exhaust`.** Finish `wave2_c11-shell-mapper-r6`: profile
the remaining ~13,800 unprofiled c ∈ {11,12} primaries, ordered by certified dim
descending, node cap 2e10, value cap 1e15. Win: a dim-10 c=11 triple (h*_1 = 0
at d = 10), which is the exact Reeve cell at r=6 and was never found.

**N8. `r6-dim10-highc-hstar-tail`.** r=6, certified dim 10, c ∈ [25,80] — the
measurement-blind stratum of §2.2. Take the 1,371 certified dim-10 triples
already banked in `wave4_maxden-highc-dim9-r6` plus new draws, and compute the
complete h* (j = 0..10) under N1. Win: h*_2 ≥ 264 (the exact d=10 negativity
threshold), or a negative a_k directly. Current best in-cell is h*_2 = 388 with
h*_9, h*_10 unknown — this stratum is the only place where the Route-A
threshold has ever been numerically exceeded.

**N9. `r7-fulldeg-D15-shelf`.** r=7, target degree 10–15, c unconstrained above.
Generate with the dimension oracle first (LP only), profile only certified
dim ≥ 10 triples under N1. Win: the first exact r=7 polynomial of degree ≥ 10.
No such object exists anywhere in waves 1–4; the region occupies 6 of the 16
possible degrees at r=7 and is entirely unmeasured.

**N10. `r7-trackb-lift-rerun`.** Execute the dead wave-2 slot
(`runs/wave2_r7-trackb-lift/hunt.py`, seed 4314) with N1's engine and N2's
dimension certification. r=7 gives the largest D/c ratio available, i.e. the
best chance of c ≤ deg P. `wave3_r7-thin-highdim-probe` found 34 dim ≥ 10 r=7
triples and could not verify them; N1 removes that obstruction.

**N11. `allodd-parity-r6-rerun`.** Execute the dead wave-2 slot
(`runs/wave2_allodd-parity-r6/hunt.py`, seed 4307): strict all-odd-part lam, mu
at r=6, parity-matched nu, denominator-2 vertex bait, D=10, c ∈ [3,12]. Never
screened once. Extend its c band to [3,24] (the c ≤ 12 bias is a wave-1
heuristic that Route A's own arithmetic rules out at d ≥ 6).

**N12. `nearwall-r5-heavy-rerun`.** Execute the dead wave-2 slot
(`runs/wave2_nearwall-r5-heavy/driver.py`): 8 anchors at W ∈ [52,56], r=5,
all singleton-Horn slacks ≥ 1, hug ≥ 2. Wave 1 covered the same family only at
W ∈ [40,44]; §1.5's weight-rigidity result predicts a null, and that prediction
should be tested rather than assumed, since the wave-4 rigidity measurement was
made at fixed *absolute* perturbation, not at fixed near-wall geometry.

**N13. `hook-vs-fat-r6-rerun`.** Execute the dead wave-2 slot: long-first-row /
hook nu against fat lam, mu at r=6. Wave 1's verdict ("the 8-thick dominance
band caps deg ≤ 5, so D=6 is never attained") is an r=5 statement with b ≤ 8 and
|mu| ≤ 26; at r=6 the ambient dimension is 10 and the analogous cap is untested.

**N14. `qge4-with-small-h1-joint-cell`.** The Route-N × Route-R intersection,
never jointly targeted. Search directly for triples that are simultaneously
non-lattice (certified q ≥ 4) and thin (h*_1 = c − dim − 1 ≤ 2). The unbiased
base rate measured in `wave4_heavy-unbiased-statistic-control-w4` is 0: the
smallest h*_1 attached to any q ≥ 3 draw in 4,800 draws was 3, and every one of
the 186 h*_1 = 0 profiles was the unimodular simplex. Steer on the joint
objective (maximize q, minimize h*_1) with ≥ 4-box coordinated moves at r = 6,7 —
a move budget never used above r = 6. Win: any member of the joint cell, whose
Ehrhart function is then unprotected by Stanley *and* has no volume to spare.

---

## 5. Standing caveats

- No result in waves 1–4, and no result of the 14 families above, can be
  evidence for the King–Tollu–Toumazet conjecture. Absence of a hit bounds only
  where the generators plus the caps looked.
- Every "family exhausted" verdict in `APPROACH_REGISTRY.md` is conditional on
  that family's own filters, and — where it rests on an upper bound for dim Q —
  is additionally conditional on §3.2, which is now known to be unsound.
- The three claimed q-ceiling closures (§3.3) are r ≤ 6 statements and must not
  be cited at r ≥ 7.
