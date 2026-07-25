# BUILD_TIER0.md — the tier-0 screen

`tier0_screen.py` is a **copy of the mandated LP-free screen**
`../purged_region/lpfree_screen.py` with **fields added**. The validated
core is not rewritten.

Instrument: `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/tier0/tier0_screen.py`
Validation log: `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/tier0/VALIDATION_TIER0.txt`
Engine A: `../engine/lr_hive.exe` · Engine B: `python ../engine/engineB_lrrule.py`

---

## 1. What tier 0 hunts

`c(nu; lam, mu)` is the number of lattice points of the Knutson–Tao hive
polytope `Q(lam,mu,nu)`. The constraint matrix depends only on `r = #parts`
and the right-hand side is linear and **homogeneous**, so `Q(n·lam,…) = n·Q`
and `P(n) = c(n·nu; n·lam, n·mu)` is the Ehrhart polynomial of `Q`, with
`d := deg P = dim Q`. `Q` is a **rational** polytope, not a lattice
polytope: the verified triple `lam=(2,2,1), mu=(4,3,2,1), nu=(5,4,3,2,1)`
has `dim 4`, `c = 5`, seven vertices, **two of them half-integral**.

Two identities hold always: `h*_0 = 1` and `h*_1 = c − (d+1)`. At Ehrhart
period 1 (Derksen–Weyman gives period 1 for hive polytopes)
Ehrhart–Macdonald reciprocity additionally gives

```
h*_d = (−1)^d · P(−1) = #( interior lattice points of Q )
```

The campaign-wide volume thresholds (`Sum h* ≥ 13` at `d=3`, `27` at `d=4`,
`19` at `d=5`, `37` at `d=6`, `25` at `d=7`) rest **entirely** on
inequalities that are theorems only for **lattice** polytopes: Stanley
monotonicity, Hibi, and `h*_d ≤ h*_1`. Assuming only Stanley nonnegativity
`h*_j ≥ 0`, the cheapest negativity configuration collapses to

```
Sum h* = 3 ,   h* = (1, 0, …, 0, 2) ,   any d ≥ 4
```

which makes `[n^{d−2}]P` strictly negative. That shape needs `h*_d > h*_1`,
i.e. a polytope with exactly `d+1` lattice points **at least one of which is
interior**. For a lattice polytope that is impossible: its `≥ d+1` vertices
are lattice points on the boundary, so an interior lattice point forces
`c > d+1`. For a rational polytope it is not excluded — and hive polytopes
are exactly that. **This configuration has never been searched**; the
campaign only ever flagged the different, stronger condition `h*_1 < 0`.

```
TIER0   :=  (h*_1 == 0)  AND  (h*_d > 0)
JACKPOT :=  (h*_d > h*_1)        # weaker; still fatal to the lattice bounds
```

`r = 4` (`d = 3`) is **not** a target here: at `d = 3`, `h*_1 = 0` forces
(White) `h* = (1,0,q−1,0)`, and an `r=4` empty-simplex hive polytope has
`V ≤ 4 < 13`. Hunt `d ≥ 4`, i.e. `r ≥ 5`.

---

## 2. Pipeline — unchanged

Per triple, exactly as mandated, with **no LP dimension oracle and no
simplex filter** (an earlier campaign screen used both and systematically
purged exactly this population):

1. `D = (r−1)(r−2)/2` — number of interior hive vertices, so `deg P ≤ D`.
2. Exact profile `P(0..D+2)` from engine A in batch mode, explicit cap.
   `CAP_EXCEEDED` is reported as a **SKIP**, never as a math verdict.
3. Exact Newton interpolation over `Q` through `n = 0..D` (Fractions only).
4. `d = deg P` after stripping trailing zero coefficients.
5. **Two held-out points** `n = D+1, D+2` verified against the polynomial.
6. `h*_j = Σ_{i≤j} (−1)^i C(d+1,i) P(j−i)`, with the round-trip check
   `P(n) = Σ_j h*_j C(n+d−j, d)` on every computed `n` and `h*_j = 0` for
   `j = d+1, d+2`.
7. Exact monomial coefficients and the flags.

All arithmetic is `int` / `Fraction`. **No float decides anything.**

Verified mechanically: `parse_partition, fmt_partition, scale, _run_batch,
engineA_batch, engineB_batch, _coerce, newton_interpolate, poly_eval,
poly_degree, hstar_from_profile, profile_from_hstar, screen_triples,
ambient_bound, reeve_count` are **byte-identical** to the originals, and the
body of `screen_profile` is identical up to `rec["status"] = "OK"` (one
added alias line `rec["NEG"] = rec["neg"]`); everything tier-0 is appended
after it.

---

## 3. Added fields (one JSON object per triple / polytope)

| field | meaning |
|---|---|
| `hstar` | full exact `h*`-vector `h*_0 … h*_d` |
| `hstar_sum` | `Σ h*` = normalized volume `d!·vol(Q)` |
| `hstar_1` | `h*_1` (`None` when `d = 0`) |
| `hstar_d` | `h*_d` |
| `INTERIOR` | `= h*_d` = number of **interior** lattice points of `Q` |
| `JACKPOT` | `h*_d > h*_1` |
| `TIER0` | `h*_1 == 0` **and** `h*_d > 0` |
| `u_mean` | `<u>` with `u_j = 2j − (d+1)`, weights `h*_j` (exact, as a string) |
| `u2_mean` | `<u²>` (exact, as a string) |
| `coeffs_low_to_high` | exact monomial coefficients of `P` |
| `NEG` | some monomial coefficient is **strictly negative** |
| `neg_indices` | which ones |
| `hstar_1_identity_ok` | audit: `h*_1 == c − d − 1` |
| `interior_from_reciprocity`, `interior_check_ok` | audit: `(−1)^d P(−1) == h*_d` |
| `moment_criteria`, `moment_criteria_consistent` | audit: the two criteria below reproduce the actual coefficient signs |

Non-OK exits (`EMPTY`, `SATURATION_ANOMALY`, `HELDOUT_MISMATCH`,
`CAP_EXCEEDED`, `SIZE_MISMATCH`) carry `NEG = JACKPOT = TIER0 = false` and
`None` for the numeric tier-0 fields — a skipped triple is never a hit.

### The two negativity criteria (exact)

With `u_j := 2j − (d+1)` and `<·>` the `h*`-weighted average:

```
[n^{d−1}]P = −( d / (2·d!) ) · Σh* · <u>            < 0  iff  <u> > 0
[n^{d−2}]P =  ( d(d−1) / (8·d!) ) · Σh* · ( <u²> − (d+1)/3 )
                                                    < 0  iff  <u²> < (d+1)/3
```

(the linear-in-`u` part of the second elementary symmetric function of the
roots of `C(n+d−j, d)` cancels identically). Both are **recomputed against
the interpolated coefficients on every record**: `moment_criteria_consistent`
must be `true` or the record is suspect. It is `true` on every record
produced in this build, including all 20 Reeve tetrahedra, which straddle
the sign change.

---

## 4. Modes

```
python tier0_screen.py --triple "2,2,1" "4,3,2,1" "5,4,3,2,1"
python tier0_screen.py --batch FILE            # lines "lam;mu;nu", 1 JSON/line
python tier0_screen.py --prefilter FILE        # cheap TIER0 decision
python tier0_screen.py --prefilter FILE --stage1-only
python tier0_screen.py --reeve 13              # lattice control polytope
python tier0_screen.py --synthetic             # built-in RATIONAL controls
python tier0_screen.py --rsimplex="-1,-1;0,2;2,0" --den 2
python tier0_screen.py --validate --validate-log VALIDATION_TIER0.txt
```
Options: `--cap N`, `--dbound D`, `--out FILE`, `--tier0-only` (print only
records with `TIER0` or `JACKPOT` true).

### Fast pre-filter — and its scope

`h*_1 = c − d − 1` needs only `c` and `d`, and `d ≤ D` always. Stage 1
therefore spends **one engine call per triple** (`n = 1`, giving `c`):

* `c = 0` → `REJECT_EMPTY`
* `c > D + 1` → `h*_1 ≥ c − D − 1 > 0` → `REJECT_HSTAR1_POSITIVE`
* otherwise `SURVIVOR` → full `D+3`-call screen

`c = 1` triples stay survivors: they can never be TIER0 (either `d = 0`, a
point, or `d ≥ 1` and then `h*_1 = −d < 0`) but they are strong JACKPOT
candidates via `h*_1 < 0`, so they are not dropped. Records carry
`stage1_calls` / `stage2_calls` / `tier0_possible`.

> **WARNING, and the reason this file exists.** The pre-filter decides
> **TIER0 only**. A triple with `c > D + 1` has `h*_1 > 0` but may still
> satisfy `h*_d > h*_1`. Those records carry `jackpot_undetermined: true`.
> **The JACKPOT hunt must run the full `--batch` screen.** A previous
> campaign screen purged a whole population with a cheap pre-test; a
> pre-filter rejection is not a mathematical verdict.

Measured on a 4000-triple random pool (`r ∈ {5,6}`, `|nu|` 12–40),
stage 1 alone: 3192 `REJECT_EMPTY`, 47 `REJECT_HSTAR1_POSITIVE`,
761 `SURVIVOR` — i.e. one engine call disposes of 80.8% of the pool, and of
the 808 nonempty triples 5.8% are rejected without a profile.

---

## 5. Validation — all four mandated checks pass

`python tier0_screen.py --validate` → exit 0, **zero `FAIL` tokens**.
Full transcript: `VALIDATION_TIER0.txt`.

### (1) The known refuter, reproduced exactly

`lam=(2,2,1), mu=(4,3,2,1), nu=(5,4,3,2,1)`

```
profile [1, 5, 16, 40, 85, 161, 280, 456, 705]   (held out n=7,8 both match)
d = 4      c = 5 = d+1      h* = (1, 0, 1, 0, 0)      Sum h* = 2
h*_1 = 0   h*_d = 0   INTERIOR = 0
TIER0 = false      JACKPOT = false      NEG = false
<u> = −3   <u²> = 13
P(n) = 1 + 2n + 17/12 n² + 1/2 n³ + 1/12 n⁴ = (n+1)(n+2)(n²+3n+6)/12
```
All 13 inherited checks plus 9 new tier-0 checks PASS. The infinite family
`lam=(2,2,1), mu=(k,3,2,1), nu=(k+1,4,3,2,1)`, `k = 4..9`, reproduces the
identical record (inherited check V1b).

This triple has `h*_1 = 0` but **no interior lattice point**, so it is a
near miss, not a tier-0 hit — exactly as specified.

### (2) Reeve tetrahedron `T_q` fed directly as a polytope, `q = 1..20`

`T_q = conv{(0,0,0),(1,0,0),(0,1,0),(1,1,q)}`, counted by direct exact
lattice-point enumeration (no hives, no LR engine).

```
h* = (1, 0, q−1, 0)      Sum h* = q      <u²> = 16/q      <u> = −4/q
linear coefficient:  q=11 → +1/6 ,  q=12 → 0 (exactly) ,  q=13 → −1/6
NEG = true exactly for q ∈ {13,…,20}, and for no q < 13
```

`h*_1 = 0` and `h*_d = 0` here, so `JACKPOT = TIER0 = false` — the lattice
**negative control**: a lattice polytope cannot fire the detector.
`<u²> < (d+1)/3 = 4/3 ⟺ 16/q < 4/3 ⟺ q > 12` matches the actual coefficient
sign on all 20 values.

### (3) An own rational (non-lattice) polytope — does JACKPOT fire?

**Yes. The JACKPOT detector fired.**

Both controls were found by exhaustive exact search over half-integral
triangles (nondegenerate, `2·Area` integral, non-lattice, ≤ 2 boundary
lattice points, ≥ 1 interior lattice point, `Σh* = b + 2i − 2`), then
period-1–verified against the interpolated polynomial on `n = 0..20`.

**S1 — the tier-0 configuration itself, one dimension down**

```
S1 = conv{ (−1/2, −1/2), (0, 1), (1, 0) }        NOT a lattice polytope
lattice points: (0,0) INTERIOR ; (1,0), (0,1) on the boundary  → c = 3
P(n) = n² + n + 1        d = 2       c = 3 = d + 1
h* = (1, 0, 1)   Sum h* = 2   h*_1 = 0   h*_d = 1   INTERIOR = 1
JACKPOT = TRUE      TIER0 = TRUE       NEG = false
```

This is precisely the configuration that is **impossible for a lattice
polytope**: `d+1 = 3` lattice points, one of them interior. A rational
polytope realises it, and the screen reports it.

**S2 — a JACKPOT that is not a TIER0**

```
S2 = conv{ (−2, −2), (−3/2, 3/2), (3, 1) }       NOT a lattice polytope
c = 10 , 8 interior , 2 boundary
P(n) = 8n² + n + 1 ,  h* = (1, 7, 8) ,  h*_1 = 7 < 8 = h*_d
JACKPOT = TRUE      TIER0 = FALSE
```

Both records additionally pass: `interior_direct_matches_hstar_d` (the
reported `INTERIOR` equals a direct enumeration of interior lattice points
at `n = 1`), `reciprocity_ok` (`(−1)^d P(−n)` equals the enumerated interior
count for `n = 1..4`), `extra_period1_ok` (the polynomial matches direct
enumeration at `n = 5..12`, well past the two mandated held-out points),
`hstar_roundtrip_ok`, `hstar_tail_zero`, `moment_criteria_consistent`.

Negative control inside the same test: Reeve `T_17`, a **lattice** polytope
with the same `h*_1 = 0`, gives `h* = (1,0,16,0)` and `JACKPOT = false`.
So the detector is not firing on everything.

### (4) Engine A vs engine B, 200 random triples, `n = 1, 2, 3`

```
200 nonzero random triples (pool 238); 600 (triple, n) evaluations
mismatches = 0
```

### (5, extra) Pre-filter vs full screen

124 triples (the refuter, three family members, 60 random triples and their
2-dilates): 122 survivors, 2 rejected, **0 TIER0 disagreements**, and no
pre-filter JACKPOT that the full screen does not confirm. The test fails
loudly if it becomes vacuous in either direction.

```
RESULT V1=True V1b=True V2=True V3=True V4=True V5=True -> ALL PASS
```

---

## 6. Standing rules for anything built on this file

* **A null census proves nothing about the KTT conjecture and must never be
  phrased as support for it.** `581,713` nonempty hive polytopes screened
  with the LP-free instrument gave `0` negative coefficients, `0` negative
  `h*_j` and `0` violations of `h*_d ≤ h*_1` / Stanley monotonicity / Hibi.
  No theorem forces hive polytopes to obey any of those, and the
  half-integral refuter proves they are not lattice polytopes.
* Never add an LP dimension oracle or a simplex filter to the decision path.
* `CAP_EXCEEDED` is a skip, not a verdict; `SATURATION_ANOMALY` (`c = 0`
  with a nonzero dilate, contradicting Knutson–Tao saturation) must be
  reported loudly, never tuned away.
* Any `TIER0` or `JACKPOT` hit must be re-verified independently: engine B
  at `n = 1, 2, 3`, and direct lattice-point enumeration of the hive
  polytope before anything is claimed.
