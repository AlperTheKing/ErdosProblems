# LADDER_REPORT.md — the corrected (purged-region) KTT hunt

Date: 2026-07-21.
Target: a counterexample to **King–Tollu–Toumazet positivity**, literature item
**LR(iv)** (Gao, arXiv:2101.00984): a triple `(lam, mu, nu)` with
`|lam| + |mu| = |nu|` whose stretched Littlewood–Richardson polynomial
`P(n) = c(n*nu ; n*lam, n*mu)` has a **strictly negative monomial coefficient**.
Saturation, Fulton and polynomiality are theorems; **positivity is open**;
`d = 1` is proved (Ikenmeyer; Sherman), `d = 2` is explicitly open.

**No counterexample was found. Nothing in this report is evidence FOR the
King–Tollu–Toumazet conjecture.** A negative census bounds where a
counterexample can live and nothing else; every "wall" recorded below is a
regularity of the swept data, not a theorem.

Instrument (mandated, LP-free, used verbatim by every family):
`E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/purged_region/lpfree_screen.py`
(sha256 `2d85944fce287e039312872cd1d2423076a8a4248395cb89b89507c399d769a5`) —
exact profile `P(0..D+2)` from engine A, exact Newton interpolation over `Q`,
`d = deg P`, two held-out points verified, `h*_j = sum_{i<=j} (-1)^i C(d+1,i) P(j-i)`,
`h*` round-trip and zero-tail checked. **No LP dimension oracle, no simplex test,
nothing discarded for polytope shape.** All arithmetic `int`/`Fraction`.
Engines: A = `engine/lr_hive.exe`, B = `engine/engineB_lrrule.py`; every headline
record below was recomputed by engine B and agrees exactly.
Instrument self-tests reproduce both calibrators: Reeve `T_13`
(`h* = (1,0,12,0)`, coefficients `1, -1/6, 1, 13/6`, NEG = true) and the hive
refuter `(2,2,1)x(4,3,2,1) -> (5,4,3,2,1)` (`d = 4`, `h* = (1,0,1,0,0)`, `V = 2`).

---

## 1. The exact target table

Write `V := Sum_j h*_j` (normalized volume `d! vol Q`), `s := deg h*`,
`h*_1 = c - (d+1)` (an identity). From
`P(n) = sum_j h*_j C(n+d-j, d)`,

```
[n^k] P  =  (1/d!) * sum_j h*_j * e_{d-k}( d-j, d-j-1, ..., 1-j )
```

(`e_m` = elementary symmetric polynomial). For fixed `(d, h*_1)` the minimum
`V` that admits a strictly negative coefficient is an exact integer program with
a one-line solution: all extra mass goes to the single index minimising the
weight. Recomputed here from scratch in
`purged_region/target_table.py`; it reproduces the campaign's published
numbers (13 at `d=3`, 27 at `d=4`, 19/37/25 at `d=5,6,7` for the relevant degree
caps) and fam6/fam12's independently computed tables.

**These thresholds are necessary, not sufficient**: a realized `h*` with
`V >= threshold` need not be negative (see §2, the `V = 448` record).

### 1a. `s = deg h* <= 2` — the only shape ever observed at `h*_1 <= 2`

| d | h\*_1=0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| 2 | 5 | 7 | 9 | 11 | 13 |
| 3 | **13** | 16 | 19 | 22 | 25 |
| 4 | **27** | 31 | 35 | 39 | 43 |
| 5 | 47 | 52 | 57 | 62 | 67 |
| 6 | 64 | 76 | 87 | 93 | 99 |
| 7 | 87 | 99 | 112 | 124 | 137 |
| 8 | 115 | 128 | 142 | 155 | 169 |
| 9 | 148 | 162 | 177 | 192 | 206 |
| 10 | 186 | 201 | 217 | 233 | 249 |
| 11 | 229 | 246 | 263 | 280 | 297 |
| 12 | 277 | 296 | 314 | 332 | 350 |

The mandate's two headline numbers are the `h*_1 = 0` entries at `d = 3` (13,
the Reeve threshold, witness `h* = (1,0,12,0)`) and `d = 4` (27, witness
`h* = (1,0,26,0,0)`).

### 1b. `s <= 3`

| d | h\*_1=0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| 3 | 4 | 6 | 8 | 10 | 12 |
| 4 | **7** | 11 | 15 | 19 | 23 |
| 5 | 19 | 27 | 35 | 43 | 51 |
| 6 | 37 | 55 | 73 | 91 | 99 |
| 7 | 58 | 80 | 102 | 124 | 137 |
| 8 | 99 | 128 | 142 | 155 | 169 |

### 1c. `s <= d-1`, i.e. `h*_d = 0` (no interior lattice point — observed in **every** record of dimension `d >= 3`, 1,013,185 profiles, fam8)

| d | h\*_1=0 | 1 | 2 | 3 | 4 | cheapest witness at h\*_1=0 |
|---|---|---|---|---|---|---|
| 3 | 13 | 16 | 19 | 22 | 25 | `(1,0,12,0)` |
| 4 | **7** | 11 | 15 | 19 | 23 | `(1,0,0,6,0)` |
| 5 | 5 | 8 | 11 | 14 | 17 | `(1,0,0,0,4,0)` |
| 6 | 4 | 7 | 9 | 12 | 15 | `(1,0,0,0,0,3,0)` |
| 7 | 4 | 6 | 9 | 11 | 14 | `(1,0,0,0,0,0,3,0)` |
| 8 | **3** | 6 | 8 | 11 | 13 | `(1,0,0,0,0,0,0,2,0)` |
| 9 | 3 | 6 | 8 | 10 | 13 | `(1,0,...,0,2,0)` |
| 10 | 3 | 5 | 8 | 10 | 12 | `(1,0,...,0,2,0)` |
| 11 | 3 | 5 | 8 | 10 | 12 | `(1,0,...,0,2,0)` |
| 12 | 3 | 5 | 7 | 10 | 12 | `(1,0,...,0,2,0)` |

### 1d. no constraint on `s`

| d | h\*_1=0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| 2 | 5 | 7 | 9 | 11 | 13 |
| 3 | 4 | 6 | 8 | 10 | 12 |
| >= 4 | 3 | 5 | 7 | 9 | 11 |

The cheapest rungs in 1c/1d require **top-index mass** (`h*_{d-1}` or `h*_d`
nonzero). The cheapest rung anywhere at `h*_1 = 0` is `V = 3` with
`h* = (1,0,...,0,2,0)` at `d >= 8`. **This is the whole difficulty**: volume is
cheap, top-index mass is not (§2, §3).

---

## 2. Records actually achieved

### At `h*_1 = 0` (i.e. `c = d + 1`)

**`V = 2`. Unchanged from the seed refuter; no family moved it.**

| record | triple | d | c | h\* | V |
|---|---|---|---|---|---|
| seed refuter | `lam=(2,2,1)`, `mu=(4,3,2,1)`, `nu=(5,4,3,2,1)` | 4 | 5 | `(1,0,1,0,0)` | 2 |
| infinite family | `lam=(2,2,1)`, `mu=(k,3,2,1)`, `nu=(k+1,4,3,2,1)`, all `k >= 4` (verified `k = 4..396`) | 4 | 5 | `(1,0,1,0,0)` | 2 |
| `d = 5` carrier | `lam=(2,2,1,1)`, `mu=(4,4,3,2,1)`, `nu=(5,5,4,3,2,1)` | 5 | 6 | `(1,0,1,0,0,0)` | 2 |
| `d = 5` carrier | `lam=(2,2,1,1)`, `mu=(7,3,2,1,1)`, `nu=(8,4,3,2,2,1)` | 5 | 6 | `(1,0,1,0,0,0)` | 2 |
| `d = 4`, `r = 6` | `lam=(3,2,2,1)`, `mu=(3,2,2,1)`, `nu=(4,4,3,2,2,1)` | 4 | 5 | `(1,0,1,0,0)` | 2 |
| `d = 6`, `r = 7` | `lam=(2,2,1,1,1)`, `mu=(4,3,2,1,1)`, `nu=(5,4,3,2,2,1,1)` | 6 | 7 | `(1,0,1,0,0,0,0)` | 2 |
| `d = 7`, `r = 8` | `lam=(2,2,1,1,1,1)`, `mu=(4,3,2,2,1,1)`, `nu=(5,4,3,3,2,2,1,1)` | 7 | 8 | `(1,0,1,0,0,0,0,0)` | 2 |

`P(n) = (n+1)(n+2)(n^2+3n+6)/12 = 1 + 2n + 17n^2/12 + n^3/2 + n^4/12` for the
`d = 4` class; profile `1,5,16,40,85,161,280,456,705,...` (engines A and B agree).

731 distinct carriers with `h*_1 = 0` and `V = 2` are banked in
`purged_region/LADDER_CARRIERS_ALL.json` (394 at `d = 4`, 310 at `d = 5`,
27 at `d = 6`). **Every one of them has `V = 2` exactly; not a single carrier
with `h*_1 = 0` and `V >= 3` exists anywhere in ~18.07M exact profiles.**
Ladder position at `h*_1 = 0`: **2 of 13** (`d = 3`), **2 of 7** (`d = 4`,
`s <= 3`), **2 of 3** (`d >= 8`) — but see §3: the missing item is not volume.

Maximum `deg h*` at `h*_1 = 0`, per dimension (fam1, 75,104 triples):
`d=2: 0, d=3: 0, d=4: 2, d=5: 2, d=6: 0`. All mass at `j = 2`.

### At `h*_1 <= 2`

| h\*_1 | best V | triple | d | h\* |
|---|---|---|---|---|
| 0 | 2 | above | 4 | `(1,0,1,0,0)` |
| 1 | **10** | `lam=(5,4,3,2,1)`, `mu=(2,2,1,1)`, `nu=(6,5,4,3,2,1)` | 7 | `(1,1,6,1,1,0,0,0)` |
| 1 | 10 | `lam=(2,2,2,1)`, `mu=(5,5,4,3,2,1)`, `nu=(6,6,5,4,3,2,1)` | 7 | `(1,1,6,1,1,0,0,0)` |
| 2 | 7 | `lam=(4,3,2,1)`, `mu=(3,2,2,1)`, `nu=(6,4,3,2,2,1)` | 6 | `(1,2,4,0,0,0,0)` |
| 2 | 7 | `lam=(3,3,2,1)`, `mu=(3,3,2,1)`, `nu=(5,4,3,3,2,1)` | 5 | `(1,2,3,1,0,0)` |

The `V = 10` record (`P = 1 + 109n/42 + 25n^2/9 + 31n^3/18 + 25n^4/36 + 13n^5/72
+ n^6/36 + n^7/504`, profile `1,9,50,205,675,1886,4644,10350,21285,40975,74646,
129779,216775`, both engines) is the **only** ladder track that moved during this
run: prior record 7, now 10. Required at `(d=7, h*_1=1, s<=3)`: 80.

The first hive polytopes with `deg h* = 3` were found in this run (28 records,
`d = 5`, `h* = (1,2,3,1,0,0)`, `V = 7`, representative
`lam=(3,3,2,1)`, `mu=(4,4,2,2)`, `nu=(6,5,4,3,2,1)`, engine-B confirmed). Before
this run every banked carrier had `deg h* <= 2`.

### Unconstrained `h*_1` (volume is not the scarce resource)

* `V = 448`, `lam=(6,4,2,1)`, `mu=(6,4,2,1)`, `nu=(9,7,5,3,2)`, `d = 6`, `c = 36`,
  `h* = (1,29,163,197,55,3,0)`, all coefficients strictly positive
  (`1 + 259n/60 + 3131n^2/360 + 251n^3/24 + 553n^4/72 + 129n^5/40 + 28n^6/45`).
  The `(d=6, h*_1=29, s<=5)` volume requirement is **81**; this polytope carries
  **448** — 5.5x the necessary volume — and every negativity functional is far
  from zero (`sum_j h*_j e_{d-k}(...)` = 3108, 6262, 7530, 5530, 2322 for
  `k = 1..5`; all need `< 0`). **Volume above threshold buys nothing; the mass
  is in the wrong place.**
* `V = 112`, `lam=(2,2,2,1)`, `mu=(8,5,4,3,2,1)`, `nu=(9,6,5,4,3,2,1)`, `d = 9`,
  `h* = (1,4,31,40,31,4,1,0,0,0)` (largest support index observed anywhere: 6).
* `V = 44` at `d = 4`: `lam=(6,4,2)`, `mu=(7,4,2)`, `nu=(9,7,5,3,1)`,
  `h* = (1,13,24,6,0)` — the previous campaign's `d = 4` record was 5; the 8.8x
  jump came purely from deleting the old `c <= D+1` prune.
* `V = 8192` (`lam=(16,16,8)`, `mu=(32,24,16,8)`, `nu=(40,32,24,16,8)`,
  `h*_1 = 700`) — the 8-fold dilation control, `V(tQ) = t^d V(Q) = 2*8^4`; a
  sanity check, useless for the ladder.

Exhaustive achieved-`V` frontier (fam9, `r <= 5`, `|nu| <= 26`), max `V` per
`(d, h*_1)`:

```
d=3:  h1=0:1  1:3   2:4   3:6   4:7   5:9   6:11  7:13  8:18  9:20  10:22
d=4:  h1=0:2  1:3   2:5   3:8   4:10  5:13  6:16  7:19  8:22  9:25  10:32 ... 16:56
d=5:  h1=0:1  1:2   2:6   3:8   4:14  5:16  6:23  7:26  8:33  9:36  10:50 ... 20:131
d=6:  h1=1:2  3:4   5:20  7:24  9:90  11:112  13:136  15:160  ... 29:448
```

Achieved `V` grows without visible bound in `h*_1`; it is pinned at 2 exactly at
`h*_1 = 0`.

### Minimum monomial coefficient (all strictly positive)

Global minimum over the corpus: `1/120960` — the **leading** coefficient
`V/d!` of `lam=(9,6,5,4,2,1)`, `mu=(6,4,3,2,2,1)`, `nu=(12,11,9,6,4,3)`,
`d = 9`, `h* = (1,2,0,...,0)`. Across all 175,208 re-mined records with `d >= 1`,
the minimum coefficient is the leading coefficient in 173,047 cases and the
constant term 1 in the remaining 2,161 (all `d <= 2`); **no interior coefficient
has ever been the minimum, and none ever approached 0**. Per-dimension, the
minimum of `d! [n^k] P` over `1 <= k <= d-1` was exactly `3, 6, 10, 15, 21` for
`d = 2..6` — precisely `C(d+1,2)`, the unimodular-simplex value.

---

## 3. Does `V` at fixed `h*_1 = 0` grow with weight, or saturate?

**It saturates, exactly and provably-along-the-family. This is the decisive
negative structural finding of the run.**

1. **Weight escalation is literally constant.** Along
   `lam=(2,2,1)`, `mu=(k,3,2,1)`, `nu=(k+1,4,3,2,1)`, `k = 4..396`
   (`|nu|` from 15 to **407**), the entire Ehrhart profile is *identical*:
   `1,5,16,40,85,161,280,456,705`, `d = 4`, `h* = (1,0,1,0,0)`, `V = 2`.
   Engine B independently confirms at `k = 60`. (fam13 wave W1, 105 members.)
2. **First-row growth is a null direction, in general.** Replacing
   `(lam, mu, nu)` by `(lam, mu + t*e_1, nu + t*e_1)` — which drives
   `|lam|/|mu| -> 0` — leaves the whole profile, hence `d`, `h*` and every
   coefficient, invariant for all `t >= 1`: verified on 14/14 carriers for
   `t = 0..6`, and on **7,719 / 7,719** groups of `r5_stab.jsonl` sharing
   `(lam, mu_tail, nu_tail, nu_1-mu_1)` with 2–3 different `mu_1`
   (0 groups varying). "Sweep the asymmetry ratio" is vacuous past
   `mu_1 >= max(mu_2, nu_2) + 1`.
3. **Exhaustively, `h*_1 = 0` forces `V <= 2`.** Over the 7,502,291 triples of
   the exhaustive `r <= 5`, `|nu| <= 26` census, the cells are
   `d=1:V=1 (845,007)`, `d=2:V=1 (333,479)`, `d=3:V=1 (113,127)`,
   `d=4:V=1 (27,169)`, `d=4:V=2 (185)`, `d=5:V=1 (4,816)` — i.e. `h*_1 = 0`
   forces `V = 1` except for exactly **185** triples with `h* = (1,0,1,0,0)`.
   The exhaustive `r = 6`, `|nu| <= 20` census (496,182 profiles) and the
   `|nu| = 21` extension give the same answer: best `V = 2`.
4. **Unbounded-weight hill climbing on the exact functional** (fam13 W4,
   objective "maximise `V` subject to `h*_1 = 0`", no weight ceiling) never left
   `V = 2`.
5. **Contrast**: with `h*_1` merely relaxed to `<= 2`, the record does grow with
   weight and dimension (4 -> 7 -> 10, the last at `|nu| = 21`, `d = 7`); with
   `h*_1` free, `V` reaches 448 (exhaustive band) and 8192 (dilation control).
   So *volume is available in hive polytopes; it is unavailable at `h*_1 = 0`.*

Consequence for the ladder: the climb cannot be bought with weight. Only two
directions remain open in principle — (i) a hive polytope with `h*_1 = 0` and
mass at index `>= 3` (never observed: max support index at `h*_1 = 0` is 2), or
(ii) accepting `h*_1 >= 1` and paying the higher thresholds of §1.

### Two hard walls measured on the way (regularities of the data, not theorems)

* **S-wall / first-moment route.** `[n^{d-1}] P = -S / (2(d-1)!)` with
  `S := sum_j h*_j (2j-(d+1))`, so `[n^{d-1}] < 0` iff `S > 0`. Over 616,485
  re-mined records plus everything profiled this run, `max S = -(d+1)` for every
  `d` — the argmax is always the unimodular simplex. No hive polytope has ever
  pushed any `h*`-mass above the centre; the maximum `h*`-weighted mean of
  `u_j = 2j-(d+1)` is `-1` (fam11, 630,462 records).
  At `d = 2` this is a proof, not a wall: `h*_1 = i + b - 3`, `h*_2 = i`, so
  `S = -b <= 0` identically and `[n^1] P = b/2 >= 0`.
* **`d = 3` margin wall.** At `d = 3` negativity is exactly
  `m := h*_2 - 2h*_1 - 2h*_3 > 11`. Over **216,087** hive polytopes of Ehrhart
  degree exactly 3 (`r = 4` exhaustive for `|nu| <= 32`, plus `r = 5,6`
  dimension-deficient lanes), `max m = 0`, attained by the unimodular simplex.
* **`h*_d = 0` everywhere.** No hive polytope of dimension `>= 3` in the
  1,013,185-record fam8 census has an interior lattice point. This removes every
  target in table 1d.

---

## 4. How large was the old instrument's blind spot? (quantified)

The purged screen used (1) an LP dimension oracle with **14–25** random
objectives and the rule "discard if `c > dim_lo + 1`", and (2) a filter
discarding every polytope that is not a simplex.

New measurement, made for this report:
`purged_region/blindspot_measure.py` -> `purged_region/blindspot_measure.jsonl`
(2,231 hive polytopes with exactly known `d`: all **731** banked ladder carriers
plus **1,500** random nonempty `r = 5` records with `d >= 2`). For each one the
old-style oracle is re-run at `K = 14, 20, 25` objectives, with `K = 400` as
control. Vertices are exactly certified over `Fraction`s, so `nverts > d+1` is a
*proof* of non-simplexhood.

| population | K | `dim_lo < d` (oracle discard fires) | detected non-simplex | either (old screen discards) |
|---|---|---|---|---|
| **ladder carriers (731)** | 14 | 64.3% | 20.9% | **85.2%** |
| | 20 | 48.8% | 41.0% | **89.9%** |
| | 25 | 39.4% | 53.4% | **92.7%** |
| | 400 (control) | 0.1% (1/731) | 99.7% (729/731) | — |
| **general population (1500)** | 14 | 4.9% | 4.4% | 9.3% |
| | 20 | 1.7% | 5.9% | 7.6% |
| | 25 | 0.8% | 6.6% | 7.4% |
| | 400 (control) | 0.0% | 7.4% | 1.6% max-denominator > 1 |

Readings, all exact:

* At its own settings the old screen would have discarded **85–93 %** of the 731
  known ladder carriers, versus **7–9 %** of a general hive population: the bias
  is concentrated on exactly the class that matters by a factor of **9–13x**
  (85.2/9.3 at `K=14`, 89.9/7.6 at `K=20`, 92.7/7.4 at `K=25`).
* **729 of 731 carriers (99.7 %) are provably NOT simplices** (and 729/731 have
  a vertex denominator `> 1`), versus 7.4 % of the general population. The
  simplex filter alone therefore deleted at least 99.7 % of the `h*_1 = 0`,
  `V = 2` class — the single class the ladder is made of. Concentration factor
  **13.5x**.
* The seed miss was not a fluke: on `(2,2,1)x(4,3,2,1)->(5,4,3,2,1)` the old
  oracle reported `dim_lo = 3`, `maxden = 1`; truth is `dim Q = 4`, `maxden = 2`,
  7 vertices, two half-integral.
* Independently: in the exhaustive `r = 5` band, **70,242 of 70,242** fully
  profiled small-`c` triples (100.0 %) are dimension-deficient (`dim Q < D`) —
  the class the LP oracle mis-measures is essentially the entire small-`c`
  population.
* Cost of the other prune: dropping the old `c <= D+1` filter alone raised the
  `d = 4` volume record from **5 to 44** (8.8x).

Per the mandate, denominators and simplexhood are irrelevant to coefficient
signs; they are reported here only to size the deleted region.

---

## 5. Coverage: which families were exhaustive

Fourteen families, ~18.07M exact profile computations (family counts overlap;
this is a sum of per-family work, not of distinct triples).

| fam | scope | exhaustive? | triples enumerated | exactly profiled |
|---|---|---|---|---|
| 1 | refuter cell `mu=(k,3,2,1)`, `k=4..40`, + all 1-box/2-box balanced perturbations (3-box at `k=4`), beam climb from every carrier | exhaustive in the stated ball | 75,104 | 75,104 (64,485 OK / 10,619 empty) |
| 2 | part-growth lift to `r = 6,7`: Block A staircase lift (exhaustive in `lam`), Block B short-vs-long box | Block A yes; Block B triple set yes, full profiling a prioritised subset | 317,244 | 317,244 at `P(1),P(2)`; 86,457 at 3 dilates; 3,414 full |
| 3 | dimension-deficient triples `r = 5,6,7`; exhaustive `r=5`, `len(nu)=5`, `N = 6..19`, band `c <= D+3` | yes in that band | 999,634 | 71,155 (+616,485 corpus records re-mined) |
| 4 | `c = d+1` class incl. non-simplices, `r=4 N<=18`, `r=5 N<=19`, `r=6 N<=17`, + `c > D+1` control lane | yes per lane | 933,333 | 111,846 |
| 5 | beam search, fitness `V` subject to `h*_1 = 0`, 28 generations | **sampled** | 43,957 | 43,957 |
| 6 | beam search, fitness `V` subject to `h*_1 <= 2`, `d = 3..6`, `|nu| <= 30` | **sampled** | 69,049 | 56,556 |
| 7 | `d = 3` exploit: `r = 4` **exhaustive `|nu| <= 32`** (re-swept to 33), `r = 5,6` deficient lanes | yes at `r = 4` | 6,082,801 profiled + 1,802,909 `c`-screened | 6,082,801 (216,087 of degree exactly 3) |
| 8 | `d = 4` exploit, boxes at `r = 5,6,7` | exhaustive in box | 26,241,755 | 1,013,185 (63,725 of degree 4) |
| 9 | **census, `r <= 5`, `|nu| <= 26`, unrestricted `c`** | **yes** | 7,502,291 | 7,502,291 |
| 10 | **census, `r = 6`, `|nu| <= 20`, unrestricted `c`** (+ `|nu| = 21`) | **yes** | 1,068,729 | 496,182 (0 unresolved) |
| 11 | asymmetric weight splits, `r=5 N=21..28`, `r=6 N=19..24`, `r=7 N=15..20`, `|lam| <= 8`; stabilised-tail arm | exhaustive within `(r,N,a<=8)` and tail budgets | 630,462 | 630,024 (438 unresolved) |
| 12 | fat-hook/rectangle/hook `lam` (and `mu`) against long `nu`, `r = 5,6,7` | exhaustive within the box | 769,766 stage-1 | 279,278 |
| 13 | escalation: weight `k=4..396`, shape stretch, exhaustive low-`r`, unbounded hill climb | 1,657,541 of 1,676,245 exhaustive | 1,676,245 | 1,676,245 |
| 14 | **control**: unbiased random triples `r = 4..7`, `N` up to 34 | **sampled** (null model) | 27,018 | 12,517 OK / 14,386 empty / 115 unresolved |

**Negativity-exhaustive regions** (all `c` profiled, nothing pruned but the
theorems `c = 0 => P == 0` and `c = 1 => P == 1`):

* `r <= 4`, `|nu| <= 32` (33 on the re-sweep);
* `r <= 5`, `|nu| <= 26`;
* `r = 6`, `|nu| <= 20` (plus all of `|nu| = 21`).

In those regions **no** stretched LR polynomial has a negative monomial
coefficient, and no `h*`-vector anomaly (negative `h*_j`, nonzero tail, degree
above the ambient bound, held-out mismatch) occurred in any resolved profile:
0 anomalies in ~18.07M profiles, with the 3,118 unresolved records of §6.7
listed as unresolved rather than counted as clean.

---

## 6. What remains untested — precisely

1. **`r >= 8`.** No exhaustive coverage at all. Two isolated `V = 2`,
   `h*_1 = 0` carriers were found at `r = 7,8` (`d = 6,7`); everything else at
   `r >= 7` is sampled or structured.
2. **Weight beyond the frontiers.** `r = 5` above `|nu| = 26`, `r = 6` above
   `|nu| = 21`, `r = 7` entirely — only sampled/structured lanes (fam11 covers
   unbounded `|mu|` only in the *stabilised* direction, where the profile is
   provably constant, so it is not a new test).
3. **`h*`-degree `s >= 4`.** Never observed in ~18.07M profiles (max `s = 3`,
   28 records; max support index 6, at `h*_1 = 4`). Every cheap target of
   tables 1b/1c/1d at `d >= 4` requires mass at index `d-1` or `d`. Untested
   because unrealised — no family produced a candidate to test.
4. **`h*_d > 0`.** Never observed for `d >= 3` (1,013,185 records). Table 1d is
   therefore entirely untested territory rather than excluded territory.
5. **`h*_1 = 0` with `V >= 3`.** Not observed anywhere; not excluded by any
   theorem. This is the ladder's first rung and it is still open.
6. **`c > D+3` triples in the window-pruned families.** fam3, fam5, fam11 and
   fam12 pruned `c > D+3` (sound *only* for the question "`h*_1 <= 2`?", not for
   negativity in general). Those triples are covered exhaustively only inside
   the fam7/fam8/fam9/fam10/fam13-W3 regions listed in §5; elsewhere they are
   untested.
7. **3,118 unresolved records** (search-budget facts, never math verdicts):
   fam2 466 `TIME_BUDGET` + 10 `ERROR` + ~40 probes lost to a temp-file race;
   fam6 2,049 stage-1 effort-capped; fam11 438; fam14 115. Unresolved, not
   negative.
8. **The `[n^{d-2}]` (second-moment) route at large `d`** is the only route the
   data has not walled: `[n^{d-2}] < 0` iff
   `T := sum_j h*_j (3u_j^2-(d+1)) < 0`, `u_j = 2j-(d+1)`. Minimum `T` observed:
   `+8` (fam4) / `+68` at the known carrier; per-`d` minimum second-moment gaps
   `8/7, 8/3, 74/15, 118/15, 196/15, 248/15, 63/2` at `d = 2..8` (fam11) — all
   positive, none trending to 0.

---

## 7. Honesty statement

No negative monomial coefficient was found in any family. **A negative census is
not evidence for the King–Tollu–Toumazet positivity conjecture and is not
described as such anywhere in this report.** The regularities recorded here
(`h*_1 = 0 => V <= 2`; `max S = -(d+1)`; `h*_d = 0` for `d >= 3`;
`h*_2 <= 2h*_1 + 2h*_3` at `d = 3`) are conjectures suggested by the swept data.
None of them is proved, and the seed refuter is a standing demonstration that a
confidently asserted structural claim about hive polytopes ("`h*_1 = 0` implies
volume 1", "hive polytopes are simplices") can be an artifact of the instrument
rather than a fact about hives.

Artifacts: `purged_region/BUILD_SCREEN.md` (instrument + validation),
`purged_region/VALIDATION_LOG.txt`, `purged_region/LADDER_CARRIERS_ALL.json`
(731 carriers), `purged_region/target_table.py` (§1),
`purged_region/blindspot_measure.py` + `.jsonl` (§4),
`purged_region/runs/fam1..fam14/manifest.json` (per-family shard hashes,
counts and records).
