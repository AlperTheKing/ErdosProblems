# r = 4 (Reeve dimension) census report

Target: a counterexample to the King-Tollu-Toumazet positivity conjecture (2004) — a triple of
partitions `(lam, mu, nu)` with `|lam| + |mu| = |nu|` whose stretched Littlewood-Richardson
polynomial `P(n) = c(n*nu; n*lam, n*mu)` has a strictly negative monomial coefficient.
Also a FrontierMath open problem.

Result of the whole r=4 run: **no negative coefficient was found anywhere.**
This closes the enumerated windows and nothing else. It is not evidence for KTT. See §8.

Date: 2026-07-21. Cell: `r = 4`, hive polytope `Q(lam,mu,nu)` in ambient dimension
`(r-1)(r-2)/2 = 3` (the Reeve dimension). All arithmetic exact (C++ integer / `__int128`,
Python `int` / `fractions.Fraction`); no floating point decides anything anywhere in the run.

---

## 1. Why r = 4

By Knutson-Tao, `c(nu; lam, mu) = #(Q(lam,mu,nu) ∩ Z^D)` where `Q` is the hive polytope cut out
of `R^D`, `D = (r-1)(r-2)/2`, by the three families of rhombus inequalities with boundary fixed
by the partial sums of `lam`, `mu`, `nu`. Stretching dilates `Q`, so `P` is the Ehrhart polynomial
of `Q` and `deg P = dim Q`.

- `r = 3` gives `D = 1`: `P` is linear with `P(0) = 1`, positivity is trivial.
- `r = 4` gives `D = 3` exactly. Dimension 3 is the smallest dimension in which an Ehrhart
  polynomial can have a negative coefficient; the classical witness is the Reeve tetrahedron
  `T_q = conv{(0,0,0),(1,0,0),(0,1,0),(1,1,q)}`, `h* = (1,0,q-1,0)`, normalized volume `q`,
  `a_1 = 2 - q/6 < 0` for `q >= 13`.
- The earlier four-wave, ~398,000,000-triple swarm hunted `r = 5,6,7,8,9` and never enumerated
  `r = 4`; its hunt bias excluded it.

So `r = 4` is the minimal live case and was untouched before this run.

## 2. The negativity criterion at d = 3, exactly

For a 3-dimensional lattice polytope write `P(n) = 1 + a_1 n + a_2 n^2 + a_3 n^3`,
`h* = (1, h*_1, h*_2, h*_3)`, `c = L(1) = 4 + h*_1` lattice points, `i = h*_3` interior points,
`V = 1 + h*_1 + h*_2 + h*_3` normalized volume (`= 3! * vol`).

- `a_0 = 1 > 0`.
- `a_3 = V/6 > 0`.
- `a_2 = 1/2 * (lattice-normalized surface area) > 0`.
- **Only `a_1` can be negative**, and

```
6*a_1 = 11 + 2*h*_1 - h*_2 + 2*h*_3 = 3*(c + i) - V = -11 + 18*L(1) - 9*L(2) + 2*L(3)
```

Hence the exact criterion:

```
a_1 < 0   <==>   V > 3*(c + i)   <==>   h*_2 > 11 + 2*h*_1 + 2*h*_3
```

Specialization to the Reeve mechanism: `c = 4` (i.e. `h*_1 = 0`, an empty lattice 3-simplex,
so `i = 0`) forces the requirement `V >= 13`.

Scale-free form: `a_1 < 0` requires `V/(c + i) > 3`. Note `V/c` alone is **not** a discriminant:
along an integer ray `g -> t*g` in gap space `V/c -> 6` while `a_1(t*g) = t*a_1(g)` keeps its sign,
so large `V/c` is harmless by itself.

Pipeline positive control (proves the detector fires): `hive4.py --selftest` reproduces
`T_q` for `q = 1..20` and reports `a_1 < 0` exactly for `q >= 13`; `q = 12` gives `a_1 = 0`,
`q = 13` gives `a_1 = -1/6`, `h* = (1,0,12,0)`. Re-run for this report: `SELFTEST: PASS`.

## 3. Engines and cross-calibration

| role | artifact |
|---|---|
| exact polytope / Ehrhart engine | `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/r4_reeve/hive4.py` (Fraction/int) |
| LR counter A (independent) | `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/engine/lr_hive.exe` |
| LR counter B (independent) | `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/engine/engineB_lrrule.py` |
| fast band scanners | `bandscan.cpp`, `bandscan9*.cpp`, `band10.cpp`, `band10w2.cpp`, `band11_vcscan.cpp`, `band12_scan.cpp`, `gapscan.cpp`, `vcheck.cpp` (all exact integer, rows in `{0,±1}`, no division) |

Calibration already in place before the run: both LR engines agree with brute-force Schur
products for all `|nu| <= 8`, and reproduce the theorems `c = 1 => P == 1` and `c = 2 => P = n+1`.

Cross-checks performed inside this run (selection, all with 0 mismatches unless stated):

- band1: 190 dim-3 checks (`n = 1..5`, `n = 4,5` held out) + 9,000 random-sample checks.
- band2: exhaustive cross-engine verification of the entire dim-3 stratum, 7,848 comparisons,
  0 disagreements; plus 135 random checks.
- band6: every one of the 115,839,959 triples with `c != 0` had `L(4)` and `L(5)` counted
  directly and compared against the `P` interpolated from `L(0..3)` — 0 failures.
- band12: gates 1-4 (independent enumerator recount; 8,500 broad triples; 5,000 dim-3/dim-2
  triples; 200 band-12 triples stretched to `n = 1..4` against both LR engines) — 0 mismatches.
- band10 wave 2: 224 homogeneity pairs, 250 scanner-vs-`hive4.py` triples, 120 `hive4.py`-vs-A-and-B
  stretched counts, 60/60 slab overflow cross-checks at weights up to 128,046 — verdict PASS.
- band11: 1,070 + 120 gap-vector lift-invariance and scanner agreement checks — 0 failures.

Independent re-verification done while writing this report (both LR engines, fresh calls):

- `lam = (4,2,1), mu = (4,2,1), nu = (6,4,3,1)`: `L = 5, 14, 30, 55` for `n = 1..4`, A = B,
  interpolant `P = 1 + 13n/6 + 3n^2/2 + n^3/3`, `P(4) = 55` matches the directly counted `L(4)`.
  This is the band1 max-volume record (`V = 2`, `c = 5`, `h* = (1,1,0,0)`).
- `lam = (4,2,1), mu = (4,2,1), nu = (7,4,2,1)` and `lam = (9,7,6), mu = (9,2,1), nu = (10,9,8,7)`:
  both give `L = 4, 10, 20, 35`, i.e. `P = C(n+3,3) = 1 + 11n/6 + n^2 + n^3/6`, `V = 1`,
  `h* = (1,0,0,0)`. These are the `a_1`-minimiser class of §5.

One recorded engine anomaly, not tuned away: `runs/band11/anchor_records.txt` line 32 is
`ANCHOR: FAIL` for `lam = (579,283,69), mu = (519,299,26), nu = (584,515,420,256)` at `n = 2`,
where engine A and the polytope engine both give 10 and engine B returns `CAP_EXCEEDED`.
Cause: engine-B state budget cap. It is reported as a FAIL with its cause, not suppressed.

## 4. Band inventory: exhaustive versus sampled, with exact counts

Two provably lossless reductions are used by several bands and must be stated:

- **(S1) symmetry.** `c(nu; lam, mu) = c(nu; mu, lam)`, so an unordered `{lam, mu}` may be visited once.
- **(S2) containment.** `c(nu; lam, mu) != 0` forces `lam ⊆ nu` and `mu ⊆ nu`; and `n*lam ⊆ n*nu`
  iff `lam ⊆ nu`, so non-contained triples have `P == 0` identically at every `n`.
  (S2) was falsification-tested in band6: `--nofilter` runs at `W = 20, 24, 28` enumerated
  6,322,520 unordered triples with no containment filter, found `noncontained_nonzero = 0`, and
  reproduced every filtered summary statistic exactly.

A third reduction is used by bands 8-11:

- **(M) moduli.** `Q` depends on `(lam,mu,nu)` only through the 9 consecutive-part gaps
  `a = (l1-l2, l2-l3, l3-l4)`, `b`, `c`, up to an integer translation of `R^3`. Hence `L(n)`, `V`,
  `h*`, `P` are functions of the gap vector alone, and **one gap class is an infinite family of
  triples of unbounded weight**. Verified: 386/386 random pairs (band10) and 1,070 + 120 random
  gap vectors each lifted to two different partition triples (band11) agree on
  `dim, c, L(0..5), h*, V, P` — 0 failures. Realisability: a gap class occurs at weight `W` iff
  `Cw <= W`, `4 | (W - Cw)`, `Aw + Bw <= W`, `4 | (W - Aw - Bw)`, where `Aw = a1 + 2a2 + 3a3` etc.

### 4a. Bounded-weight bands

| band | window | status | size enumerated (unit as stated) | min `a_1` on dim 3 | max `V` | max `V` at `h*_1 = 0` | negatives |
|---|---|---|---|---|---|---|---|
| 1 | `W ∈ [4,14]` | EXHAUSTIVE, no sampling | 150,547 ordered triples | 11/6 | 2 | 1 | 0 |
| 2 | `W ∈ [15,20]` | EXHAUSTIVE | 1,013,506 unordered (2,022,056 ordered) | 11/6 | 7 | 1 | 0 |
| 3 | `W ∈ [21,26]` | EXHAUSTIVE | 5,181,862 triples | 11/6 | 22 | 1 | 0 |
| 4 | `W ∈ [27,32]` | EXHAUSTIVE, no symmetry reduction | 89,948,655 ordered triples | 11/6 | 43 | 1 | 0 |
| 5 | `W ∈ [33,38]` | EXHAUSTIVE mod (S1) | 194,911,126 reduced (389,822,002 expanded) | 11/6 | 77 | 1 | 0 |
| 6 | `W ∈ [39,45]` | EXHAUSTIVE mod (S1)+(S2) | 1,837,187,424 ordered (278,174,626 lattice-counted) | 11/6 | 125 | 1 | 0 |
| 7 | `W ∈ [46,60]`, structured `nu` | **NOT exhaustive over all `nu`** | 533,158,073 unordered, 707 `nu` shapes | 11/6 | 312 | 1 | 0 |
| 12 | `W <= 60`, full census (band-12 = degenerate flag) | EXHAUSTIVE mod (S1)+(S2) | 5,386,289,297 triples total; 3,782,115,638 flagged band-12 | 11/6 | 312 | 1 | 0 |
| 8 | `W ∈ [61,90]` | EXHAUSTIVE (gap-class region gate matched exactly) | 176,528,678,464 gap classes = 1,877,911,502,602 ordered triples | 11/6 | 1,063 | 1 | 0 |
| 9 | `W ∈ [91,140]` | **NOT exhaustive** | 78,935,116,996 gap classes tested | 11/6 | 2,850 (climb) | 1 | 0 |

Notes on the two non-exhaustive weight bands:

- **band7** admits `nu` only if near-staircase (`max(c) - min(c) <= 2` for the `nu`-gaps) or
  near-rectangular (`nu1` minus the smallest positive part `<= 2`): 707 shapes across `W = 46..60`.
  All splits `(lam, mu)` for those `nu` are covered. It is not a census over all `nu` of those weights.
- **band12** did run the full exhaustive `r = 4` census for `W <= 60` (band-12 membership is only a
  flag), so the weight window `[46,60]` **is** closed by band12 even though band7 alone does not close it.
- **band9** exhaustive subregions are: `wcone S=64`, `wcone S=72`, `wbox 44/44/44`, `wbox 140/8/8`,
  `wbox 8/8/140`, `wbox 8/140/8`, `wbox 20/20/140`, `wbox 32/32/140`, `wbox 20/20/60`.
  Union = 56,043,104,209 gap classes = 8,846,458,835,872 band triples =
  **0.7166 % of the band's 7,820,553,811,824 gap classes and 5.1584 % of its 171,496,406,264,085 triples**.
  The rest of band9 is climbs and uniform random sampling: `climb` runs of 540,129,489 /
  147,752,132 / 77,267,272 gap classes, an `a1`-steered descent of 101,406,487, and 60,000,000
  uniform random band triples. The band as a whole is NOT exhausted.

### 4b. Unbounded-weight (gap-space) bands

By (M) these are censuses at every weight simultaneously, restricted to a region of the 9-dimensional
gap lattice.

| band | region | status | size | max `V` | max `V` at `h*_1 = 0` | negatives |
|---|---|---|---|---|---|---|
| 10 | cube `[0,12]^9` Ehrhart census | EXHAUSTIVE | 10,604,499,373 vectors, 1,654,867,200 realisable nonempty | 3,888 | 1 | 0 |
| 10 | structural census `[0,12]^9` | EXHAUSTIVE | 2,651,125,393 realisable classes | `V_simplex <= 216` | 1 | 0 |
| 10 | `c = 4` stratum, `[0,8]^9` | EXHAUSTIVE | 96,855,305 classes, 1,394,088 with `c = 4` exactly | — | 1 (`V >= 2` count: 0) | 0 |
| 10 w2 | cube `[0,10]^9` reproduced with a different binary | EXHAUSTIVE | 2,357,947,691 vectors, 365,961,425 realisable | 2,250 | 1 | 0 |
| 10 w2 | ladders `fib<=34`, `pow2<=128`, `geo<=316`; slabs `MAXUV = 4,8,10,12` up to `1e9` | EXHAUSTIVE on each ladder/slab | 387,420,489 / 387,420,489 / 40,353,607 vectors; slabs 1,003,976,272 max | 95,999,997,120 (slab `uv4`, ladder to 1e9) | 1 | 0 |
| 10 | random unbounded weight, `K` up to `1e9` / `1e11` | sampled | 4.0e8 + 2.0e8 + 4.0e7·3 gap vectors | 4-vertex lattice simplices up to `V = 103,813,825,188,771,821,384,673,875` | 1 (`c = 4` with `V >= 2`: 0) | 0 |
| 11 | `[0,12]^9 ∪ {g1+...+g9 <= 52}` | EXHAUSTIVE | 23,198,373,727 distinct vectors (13^9 = 10,604,499,373 cube; C(61,9) = 17,341,763,505 ball; intersection 4,747,889,151); 1,654,867,200 + 801,481,767 realisable nonempty | — | 1 | 0 |
| 11 | subregions `[0,6]^9`, `[0,8]^9`, `Σg <= 40` | EXHAUSTIVE | — | — | 1 | 0 |
| 11 | random `[0,100]^9` (1e7), `[0,300]^9` (1e6); hill-climbs on `V/(c+h*_3)` at `K = 64, 200, 600` | sampled | 686,037 valid dim-3 polytopes from the climbs | 195,928,992 | 1 | 0 |

Aborted and contributing nothing (explicitly excluded from every conclusion): band11 session 2
launched `Σg <= 64` (C(73,9) = 97,082,021,465) and `[0,16]^9` (17^9 = 118,587,876,497) and killed
both as infeasible under 12-hunter machine contention; band10 wave 2 left the box `[0,14]^9`
(38,443,359,375 vectors) in flight and unused.

### 4c. Campaign total

Summing the headline count of each of the 12 bands as reported (mixed units — ordered triples,
unordered pairs, and gap classes — so this is a tally, not a single well-defined cardinality):

```
1,991,720,856,481
```

of which 2,661,551,193 come from the bounded-weight bands 1-7 and 1,877,911,502,602 from band8.

## 5. Global extremes

**Minimum coefficient anywhere.** No coefficient of any `P` in the entire run is negative.

- Over the dim-3 stratum — the only stratum in which an Ehrhart coefficient can be negative —
  `min a_1 = 11/6` in **every single band**, bounded weight and unbounded weight alike.
  `11/6` is exactly the value forced by `h* = (1,0,0,0)`, i.e. the unimodular tetrahedron
  `P(n) = C(n+3,3) = 1 + 11n/6 + n^2 + n^3/6`. It is attained and never beaten, at every weight
  scanned, up to `|nu| = 1775` and beyond (band10 records a `c = 4, V = 1` triple at weight 8,058
  and another with parts above `1.0e7`).
- The smallest nonzero coefficient of any `P` anywhere is `1/6`, the leading coefficient `V/6`
  of a unimodular hive tetrahedron; first attained at `lam = (4,2,1), mu = (4,2,1), nu = (7,4,2,1)`.
- The literal minimum over all coefficients of all `P` is `0`, attained structurally and only in
  degenerate strata: `dim Q = 0` gives `c = 1` and `P == 1` (so `a_1 = a_2 = a_3 = 0`), and empty
  `Q` gives `P == 0`. These are not near-misses; they carry no linear term to be negative.
- `min a_2` over `dim >= 2` is `1/2` (band5).

**Maximum normalized volume.**

- Bounded weight, exhaustive: `V = 1,063` at `lam = (24,14,6), mu = (24,15,7), nu = (36,26,18,10)`,
  `W ∈ [61,90]` (band8), with `h*_2 = 685`.
- Bounded weight, non-exhaustive (band9 climbs, `W ∈ [91,140]`): `V = 2,850`, `h*_2 = 1,865`.
- Unbounded weight, exhaustive gap cube `[0,12]^9`: `V = 3,888` at
  `gaps = (12,...,12)`, `lam = mu = (36,24,12), nu = (54,42,30,18)`, `c = 832`,
  `h* = (1,828,2553,506)`, `P = [1, 21, 162, 648]`.
- Unbounded weight, targeted climb (band11): `V = 195,928,992` at
  `a = (383,600,362), b = (377,599,442), c = (491,518,533)`, `c = 32,890,946` lattice points,
  `6a_1 = 4,461 > 0`.
- Structural random probes on 4-vertex lattice simplices (band10, `K` up to `1e11`) reach
  `V = 103,813,825,188,771,821,384,673,875`; these are volume records only, all with
  `n_c4_candidates_V_ge_2 = 0`.

**Maximum normalized volume subject to `h*_1 = 0`:**

```
1
```

in every band, every subregion, every random probe, every climb, at every weight. Zero exceptions.

## 6. Does "h*_1 = 0 implies the unimodular simplex" hold at r = 4?

**It holds at r = 4. It does not break.** Every hive polytope in the run with `dim Q = 3` and
exactly 4 lattice points is a unimodular tetrahedron, `V = 1`, `h* = (1,0,0,0)`, `P = C(n+3,3)`.
Counts of verified instances (not exhaustive list): band4 200,675; band5 533,432; band7 3,093,971;
band10 `c = 4` stratum over `[0,8]^9` 1,394,088; and `hstar1_zero_dim3_with_V_gt_1 = 0` in every
band that tracked it. No Reeve simplex `T(p,q)` with `q >= 2` occurred anywhere.

Two supporting structural results, with their proof status stated exactly:

**(a) PROVEN — the empty-simplex volume bound.** In coordinates `h = (h(1,1), h(1,2), h(2,1))`
the 18 rhombus rows have exactly 15 distinct primitive directions, all entries in `{0,±1}`, and the
matrix `A` is **independent of `(lam,mu,nu)`** — only the right-hand side `b` moves, linearly
(`r4_reeve/cone_atlas.py`). `A` is not totally unimodular: over all `C(15,3) = 455` triples
`|det| = 0` (146), `1` (272), `2` (36), `4` (1); the single `|det| = 4` triple is exactly the three
odd rows `(1,-1,-1), (-1,1,-1), (-1,-1,1)` coming from rhombi `A(1,1), B(1,1), C(1,1)`. The 12
alcoved `A_3` directions alone would be TU. Lattice multiplicities of the simplicial cones
`C_S = {x : n_i·x <= 0, i ∈ S}` are `m ∈ {1 (272 cones), 2 (25), 4 (12)}`, so `m_max = 4`.

> **Theorem.** If an `r = 4` hive polytope `Q` is lattice-equivalent to an empty lattice 3-simplex —
> in particular to a Reeve simplex `T(p,q)` — then `V(Q) <= 4`, hence `q <= 4`.
> *Proof.* `Q = {h : A h <= b}`. A simplex is simple, so exactly 3 facets meet at each vertex `v`;
> every facet normal is a primitive row of `A`, so the tangent cone at `v` is `v + C_S`. Emptiness
> forces every edge to have lattice length 1, so the three edge vectors at `v` are the primitive ray
> generators of `C_S`. Therefore `V(Q) = |det(g_1,g_2,g_3)| = m(C_S) <= 4`. ∎

Consequence: `a_1 = 2 - q/6 >= 4/3 > 0` for every empty-simplex `r = 4` hive polytope. The classical
Reeve mechanism is unavailable in the `r = 4` cell by a factor of more than 3 below the `q >= 13`
threshold. **Multiplicity, not volume, is the binding constraint**, and the rhombus inequalities cap
it at 4.

**(b) NOT PROVEN — the sharpening to `V = 1`.** The normal-fan atlas (rederived independently in
band10 wave 2) finds 36 positively-spanning simple 4-subsets of the 15 fixed directions, with index
profiles `(1,1,1,1)` ×18, `(1,1,2,2)` ×6, `(1,1,1,4)` ×12. For an empty simplex all four vertex-cone
indices must equal `V`, and the only *constant* profile is `(1,1,1,1)`, so `V = 1` — **conditional on
the hypothesis that hive vertices are integral**. That hypothesis is verified, not proved:
`vcheck.cpp` scanned the complete moduli box with gaps `<= 10` (589,487,256 hive polytopes,
854,321,098 simple vertices) and found max vertex denominator 1 and every simple vertex cone
unimodular; band10 adds 1.65e9 exhaustive gap classes plus 6.4e8 random classes with gaps up to
`1e9`, all with max denominator 1. But integrality is not an identity in `b`: 49 of the 517
nonsingular row triples (48 with `|det| = 2`, one with `|det| = 4`) admit non-integral Cramer
solutions, and 147,614 non-integral Cramer points were seen — all of them infeasible, with no
uniformly violated row. Each of the 49 bad triples contains at least one odd row (the stronger claim
"`|det| > 1` implies at least two odd rows" was **refuted**: 18 triples have exactly one). Upgrading
`V = 1` to a theorem is a finite exact-LP job: for each of the 37 non-unimodular triples, decide
feasibility of the corresponding non-integral Cramer point against the full rhombus system.

**(c) PROVEN — the width lemma (band12).** With `A` fixed, both `+d` and `-d` occur among the rows
for each of the six directions `d ∈ {e1, e2, e3, e2-e1, e3-e1, e3-e2}`, and the slab widths are exactly

```
width(e1)    = min(lam1-lam2, nu1-nu2)      width(e2-e1) = lam2-lam3
width(e2)    = min(mu1-mu2, lam3-lam4)      width(e3-e1) = nu2-nu3
width(e3)    = min(mu3-mu4, nu3-nu4)        width(e3-e2) = mu2-mu3
```

> **Corollary.** `dim Q = 3` forces `lam`, `mu`, `nu` all **strict** as length-4 vectors
> (`lam1 > lam2 > lam3 > lam4 >= 0`, likewise `mu`, `nu`).

Every degenerate shape — empty partition, repeated positive part (so every rectangle `a^k`, `k >= 2`,
and every column `1^k`, `k >= 2`), and every hook `(a, 1^k)` including single rows and the single
column — fails strictness. Hence **band 12 has `dim Q <= 2` at every weight, and a negative
coefficient is impossible there, unconditionally, not merely in the enumerated window.** Verified:
0 of the 398,946,777 dim-3 triples in the exhaustive `W <= 60` census violates strictness; the dim-3
count inside band12 is exactly 0 at every weight `1..60`; a high-weight spot check of 300,000 random
band-12 triples with `61 <= W <= 400` found dim-3 count 0.

**(d) Homogeneity, and what an exhaustive box actually settles.** `Q(t*g) = t*Q(g)` up to lattice
translation, so `a_k(t*g) = t^k a_k(g)` and the sign of `a_1` is constant along every integer ray in
gap space. `{g : a_1(g) < 0}` is therefore a cone, and an exhaustive census of a box or ladder settles
every ray through it, at every weight. Verified exactly on 224 `(g,t)` pairs at `t = 2,3` (band10 w2)
and on 40 dim-3 directions at `t = 2,3` (band11).

## 7. How far the data sits from the negativity criterion

Three exact distance measures, all computed in integer arithmetic.

**(i) The `6a_1` slack.** Negativity needs `6a_1 <= -1`. Observed `min 6a_1 = 11` — in band1,
band2, band3, band4, band5, band6, band7, band8, band9, band10 (every box, ladder, slab and random
run) and band11 (every exhaustive region and every climb). Equivalently
`max(h*_2 - 2h*_1 - 2h*_3) = 0`, against the requirement `> 11`. The slack is **uniform, integral,
and never once decreased below 11 anywhere in ~2e12 enumerated objects.**

Band4's dim-3 `6a_1` histogram, for shape: `11: 200675, 12: 225, 13: 117257, 14: 4107, 15: 110359,
16: 17520, ..., 30: 9, 31: 1` — the distribution moves away from 11, not toward 0.
Band9's `wbox 32/32/140` histogram runs `11 .. 62` with `neg: 0` and `>=200: 0`.

**(ii) The Reeve channel, `c = 4`.** Requirement `V >= 13`. Observed `max V at h*_1 = 0 = 1`,
everywhere, at every weight. Distance: a factor of 13, and by §6(a) a factor of at least 3.25 is
provably unbridgeable.

**(iii) The scale-free ratio `V/(c + i)`.** Requirement `> 3`. The closest approach anywhere in the
run, produced by a hill-climb explicitly maximizing this ratio at `K = 600`:

```
gaps a = (383,600,362), b = (377,599,442), c = (491,514,533)
V = 195,853,712   c = 32,878,208   i = h*_3 = 32,407,849
V/(c+i) = 195853712/65286057 = 2.9999317...  < 3
3*(c+i) - V = 6*a_1 = 4459   (a POSITIVE integer, not a rounding artifact)
```

The exact deficit is a positive integer 4,459; the ratio is bounded by 3 from below in exact
arithmetic, and the barrier was not crossed by a directed search that was optimizing precisely for
crossing it.

**Maximum `V/c` reached anywhere** (a different, non-discriminating ratio):
`97878716/16430979 = 5.95696...` (band11 climb, `K = 600`); the theoretical ceiling along dilates is
6, and `6a_1 = 4457 > 0` there. Elsewhere the exhaustive moduli box (gaps `<= 8`) achieves
`max V/c = 3888/832 = 4.673`.

**Achieved `max V` at fixed small `c`** over the complete moduli box (gaps `<= 8`), 59,727,768 shapes,
confirmed independently by band8's `W ∈ [61,90]` exhaustive band:

```
c :   4   5   6   7   8   9  10  11  12  13  14  15  16
V :   1   3   4   6   7   9  11  13  18  20  22  25  27
```

Against the requirement `V > 3(c + i) >= 3c`. This table is **not** a proven upper bound for
unbounded weight; no bound `V <= f(c)` is proven for general `c`.

## 8. Honesty statement

**No counterexample to the King-Tollu-Toumazet conjecture was found in the `r = 4` cell.**

An empty census is not evidence for the conjecture and must never be reported as such. Absence of a
counterexample in an enumerated window proves exactly one thing: that window is closed. Every band
manifest in `runs/band*/manifest.json` carries this statement, and it is repeated here.

The only unconditional positive results produced by this run are the three theorems of §6: the
empty-simplex bound `V <= 4` (hence `q <= 4`, closing the classical Reeve mechanism at `r = 4`), the
width lemma forcing strictness for `dim Q = 3` (hence unconditional positivity on all degenerate
shapes at every weight), and the homogeneity of `a_k` in the gap vector. None of these is a proof of
KTT, at `r = 4` or anywhere else. `a_1 < 0` remains possible in principle for `c >= 5` at `r = 4`:
the run exhibits no proof excluding it.

No anomaly was tuned away. The single `ANCHOR: FAIL` produced in the run (§3) is reported with its
cause.

## 9. What remains unenumerated

Precisely, and without hedging:

1. **Weights `W ∈ [91,140]`.** 94.84 % of the band's triples and 99.28 % of its gap classes are
   unenumerated. Only the nine listed subregions are exhausted; the remainder is covered by
   sampling and climbs only.
2. **Weights `W > 140`.** No weight-indexed census exists at all above 140. Such triples are reached
   only through the gap-space regions of bands 10 and 11, and then only if their gap vector lies in
   one of those regions.
3. **Gap space outside the scanned regions.** Exhaustively settled (at every weight, by homogeneity
   and (M)): the cube `[0,12]^9`, the `L1`-ball `Σg <= 52`, the cube `[0,10]^9`, the ladders
   `{0,1,2,3,5,8,13,21,34}`, `{0,1,2,4,8,16,32,64,128}`, `{0,1,3,10,32,100,316}`, and the slabs
   `MAXUV ∈ {4,8,10,12}` with ladders up to `1e9`. **Everything else in `Z_{>=0}^9` is unenumerated**,
   in particular any gap vector with some `g_i >= 13` that is outside `Σg <= 52` and off every ladder
   and slab. The two regions that would have extended this — `Σg <= 64` (97,082,021,465 vectors) and
   `[0,16]^9` (118,587,876,497 vectors) — were launched and killed; `[0,14]^9` (38,443,359,375
   vectors) was left in flight. None contributes to any conclusion here.
4. **Weights `W ∈ [46,60]` outside band12's filters.** Closed by band12's exhaustive `W <= 60`
   census, subject to (S1) and (S2). Band7 alone covers only 707 structured `nu` shapes.
5. **The integrality hypothesis.** Vertex integrality of `r = 4` hive polytopes is verified over
   everything scanned (max denominator 1) but **not proved**; 49 of 517 nonsingular row triples admit
   non-integral Cramer points. The `V = 1` sharpening of §6(b) rests on it. The remaining work is a
   finite exact-LP decision over 37 non-unimodular triples.
6. **Any bound `V <= f(c)` for general `c`** is unproven. Only the `c = 4` case is a theorem.
7. **`r >= 5`.** Out of scope for this report. The earlier four-wave, ~398,000,000-triple swarm over
   `r = 5,6,7,8,9` was itself not exhaustive and found nothing.

---

### Artifacts

- Manifests: `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/r4_reeve/runs/band{1..12}/manifest.json`
- Polytope engine: `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/r4_reeve/hive4.py`
- Cone/normal-fan atlas and the `V <= 4` theorem: `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/r4_reeve/cone_atlas.py`
- Vertex/multiplicity scan: `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/r4_reeve/vcheck.cpp`
- LR engine A: `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/engine/lr_hive.exe`
- LR engine B: `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/engine/engineB_lrrule.py`
- Band11 anchor log incl. the one FAIL: `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/r4_reeve/runs/band11/anchor_records.txt`
