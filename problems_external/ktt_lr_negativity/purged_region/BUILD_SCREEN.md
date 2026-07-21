# BUILD_SCREEN.md — the corrected, LP-FREE screening instrument

Date: 2026-07-21. Target: **King–Tollu–Toumazet positivity, literature item LR(iv)**
(Gao, arXiv:2101.00984). Saturation, Fulton and polynomiality are theorems;
**positivity is OPEN**. `d = 1` is proved (Ikenmeyer; Sherman); `d = 2` is explicitly
open. Also a FrontierMath open problem.

A counterexample is a triple `(lam, mu, nu)` with `|lam| + |mu| = |nu|` whose stretched
LR polynomial `P(n) = c(n*nu ; n*lam, n*mu)` has a **strictly negative monomial
coefficient**.

## Artifact

| item | path |
|---|---|
| instrument | `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/purged_region/lpfree_screen.py` |
| validation transcript | `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/purged_region/VALIDATION_LOG.txt` |
| engine A | `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/engine/lr_hive.exe` |
| engine B | `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/engine/engineB_lrrule.py` |

`sha256(lpfree_screen.py) = 2d85944fce287e039312872cd1d2423076a8a4248395cb89b89507c399d769a5`
(712 lines, Python 3, standard library only).

## Geometry the instrument relies on

`c(nu; lam, mu)` = number of integer points of the Knutson–Tao hive polytope
`Q(lam, mu, nu)`, living in the space of the `(r-1)(r-2)/2` interior vertices of a
side-`r` triangular array (`r = #parts(nu)`), cut by the three rhombus inequalities,
with boundary given by partial sums of `lam` (left), `mu` (right), `nu` (bottom).

The constraint matrix `A` is a fixed `{0,+1,-1}` matrix depending **only on `r`**, and
the right-hand side `b = C p` is linear and **homogeneous** in `p = (lam, mu, nu)`.
Hence `Q(n*lam, n*mu, n*nu) = n*Q` **exactly**, so `P` is the Ehrhart polynomial of `Q`
and `deg P = dim Q =: d`.

## Why this instrument exists — the purged region

The previous 4-wave, ~405,000,000-triple campaign screened candidates with

1. an **LP dimension oracle** using 14–25 random objectives, and
2. a filter that **discarded every polytope that was not a simplex** before `h*` was
   ever computed.

Both are biased. On

```
lam = (2,2,1)   mu = (4,3,2,1)   nu = (5,4,3,2,1)
```

that oracle reported `dim_lo = 3` and `maxden = 1`, whereas the **true** values are
`dim Q = 4` and `maxden = 2`; the triple was therefore thrown away under the rule
`c > dim_lo + 1`. Its true data — verified by both LR engines and by direct
lattice-point enumeration — is

```
dim 4,  c = 5 = dim + 1  (so h*_1 = 0),  SEVEN vertices (NOT a simplex), two of them
half-integral,  h* = (1,0,1,0,0),  normalized volume 2,
P(n) = (n+1)(n+2)(n^2+3n+6)/12,   P(0..8) = 1,5,16,40,85,161,280,456,705.
```

An infinite family works: `lam=(2,2,1)`, `mu=(k,3,2,1)`, `nu=(k+1,4,3,2,1)` for every
`k >= 4`. So hive polytopes with `h*_1 = 0` **and** volume `> 1` **do exist**; the
campaign's claim that they do not was an **instrument artifact**, not a fact about
hives.

## What negativity actually requires (the corrected criterion)

Ehrhart negativity is a **lattice-polytope** phenomenon.

The Reeve tetrahedron `T_q = conv{(0,0,0),(1,0,0),(0,1,0),(1,1,q)}` has **all vertex
denominators = 1** (it *is* a lattice polytope) and satisfies Stanley's `h* >= 0`, yet

```
T_13 :  h* = (1,0,12,0),   P(n) = 1 - n/6 + n^2 + 13n^3/6
```

has a strictly **negative** linear coefficient. Consequences, both hard-wired into this
build:

- hunting non-lattice polytopes / large vertex denominators is **IRRELEVANT** to
  coefficient signs;
- `h* >= 0` (Stanley) **never** blocks negativity.

The real requirement is a **spiky `h*`-vector**: mass concentrated in the middle/high
entries with `h*_1` tiny. Concretely at `d = 3` negativity needs `h*` like
`(1,0,>=12,0)`, i.e. normalized volume `sum h* >= 13`; at `d = 4` the campaign computed
the requirement as `h* = (1,0,26,0,0)`, i.e. `sum h* = 27`.

**Ladder status.** We stand at `sum h* = 2` with `h*_1 = 0` at `d = 4`, and need
`sum h* = 27` there (or `13` at `d = 3`). The ladder is open.

## The method (LP-free)

For each triple:

1. `D = (r-1)(r-2)/2` = number of interior hive vertices = ambient bound, so
   `deg P <= D`. A certified smaller bound may be supplied with `--dbound`; the source
   is recorded in the output field `degree_bound_source`.
2. Compute the exact profile `P(0), P(1), ..., P(D+2)` with **engine A in batch mode**
   (all `(triple, n)` jobs for the whole input set go out in one call), with an explicit
   count cap.
3. Interpolate **exactly over Q** through the `D+1` nodes `n = 0..D` (Newton divided
   differences, `Fraction` only).
4. `d = deg P` after stripping trailing zero coefficients.
5. Verify the **two held-out points** `n = D+1, D+2` against the interpolated
   polynomial.
6. `h*_j = sum_{i<=j} (-1)^i C(d+1,i) P(j-i)` for `j = 0..d`.
7. Report `sum h*` (normalized volume), `h*_1`, the exact monomial coefficients, and
   `NEG = true` iff some coefficient is strictly negative.

Redundant internal cross-checks, all reported per triple:
`hstar_tail_zero` (`h*_j = 0` for `j = d+1, d+2`), `hstar_0_is_1`, `hstar_nonneg`
(Stanley — informational only, it is never used to reject), and
`hstar_roundtrip_ok` (`P(n) = sum_j h*_j C(n+d-j, d)` re-derived on every computed `n`).

### Hard prohibitions encoded in this build

- **No LP dimension oracle.** There is no LP anywhere in the file.
- **No simplex filter.** Vertices are never enumerated and never counted.
- **Nothing is discarded** for "not a simplex", for a small reported dimension, or for a
  large vertex denominator.
- **All arithmetic exact** (`int` / `Fraction`). No float decides anything, anywhere.
- **`CAP_EXCEEDED` is a SKIP, never a math verdict** — it is emitted with the list of
  failing `n`, the raw engine strings, and an explicit note.
- **Anomalies are never tuned away.** A held-out mismatch is emitted as
  `status = HELDOUT_MISMATCH`; a `c = 0` triple with a nonzero dilate is emitted as
  `status = SATURATION_ANOMALY` (this would contradict Knutson–Tao saturation).
- **A negative census is NOT evidence for the conjecture** and is never described as
  such anywhere in this instrument's output or docs.

### One subtlety, handled explicitly

Engine A returns `1` for the all-empty triple (the LR normalization `c(0;0,0)=1`), so
`P(0) = 1` even when `Q` is empty. Emptiness is therefore tested on `n >= 1` only:
`c = P(1) = 0` with `P(n) = 0` for all `n` in `1..D+2` yields `status = EMPTY`,
`d = -1`, with a note that `P(0)=1` is a normalization artifact and not an Ehrhart
value. (An earlier build mislabelled this case `HELDOUT_MISMATCH`.)

## API + CLI

```
python lpfree_screen.py --triple "2,2,1" "4,3,2,1" "5,4,3,2,1"
python lpfree_screen.py --batch FILE          # lines "lam;mu;nu"  ('#' comments ok)
python lpfree_screen.py --reeve 13            # raw-polytope path, bypasses hives
python lpfree_screen.py --validate [--validate-log FILE]
```

Options: `--cap N` (engine A count cap, default `10**12`), `--dbound D` (certified
degree bound override), `--out FILE` (JSON-lines sink).

Importable API: `screen_triples(triples, cap, dbound)`, `screen_profile(profile, D)`
(works on **any** Ehrhart profile — hives or a raw polytope), `hstar_from_profile`,
`profile_from_hstar`, `newton_interpolate`, `reeve_record(q)`, `engineA_batch`,
`engineB_batch`.

**One JSON line per triple.** Fields: `lam, mu, nu, r, degree_bound,
degree_bound_source, cap, engine, profile, heldout, heldout_ok, c, d,
coeffs_low_to_high, poly, hstar, hstar_tail_must_be_zero, hstar_sum, hstar_1,
hstar_0_is_1, hstar_nonneg, hstar_tail_zero, hstar_roundtrip_ok, neg_indices, neg,
status`.

Example (the known refuter):

```json
{"lam":[2,2,1],"mu":[4,3,2,1],"nu":[5,4,3,2,1],"r":5,"degree_bound":6,
 "degree_bound_source":"ambient_(r-1)(r-2)/2","cap":1000000000000,
 "engine":"A:lr_hive.exe","profile":[1,5,16,40,85,161,280,456,705],
 "heldout":[{"n":7,"engine":456,"poly":"456","match":true},
            {"n":8,"engine":705,"poly":"705","match":true}],
 "heldout_ok":true,"c":5,"d":4,
 "coeffs_low_to_high":["1","2","17/12","1/2","1/12"],
 "poly":"1 + 2*n + 17/12*n^2 + 1/2*n^3 + 1/12*n^4",
 "hstar":[1,0,1,0,0],"hstar_tail_must_be_zero":[0,0],"hstar_sum":2,"hstar_1":0,
 "hstar_0_is_1":true,"hstar_nonneg":true,"hstar_tail_zero":true,
 "hstar_roundtrip_ok":true,"neg_indices":[],"neg":false,"status":"OK"}
```

## Mandatory validation — ALL FOUR PASSED

Command: `python lpfree_screen.py --validate --validate-log VALIDATION_LOG.txt`
(exit code 0). Full transcript in `VALIDATION_LOG.txt`.

### V1 — reproduce the known refuter EXACTLY: PASS (13/13 checks)

`lam=(2,2,1), mu=(4,3,2,1), nu=(5,4,3,2,1)` →
`d = 4`, `c = 5`, `h* = (1,0,1,0,0)`, `sum h* = 2`, `h*_1 = 0`,
`P(0..8) = 1,5,16,40,85,161,280,456,705`, both held-out points matched,
`h*` round-trip OK, tail zero, and the interpolated coefficients
`[1, 2, 17/12, 1/2, 1/12]` are **exactly** the expansion of
`(n+1)(n+2)(n^2+3n+6)/12`. Also confirmed `c = d + 1`.

Independent corroboration (outside the suite): engine B reproduces the **entire**
profile `n = 0..8` — `1,5,16,40,85,161,280,456,705` — identically.

### V2 — the infinite family `k = 4..9`: PASS

`lam=(2,2,1), mu=(k,3,2,1), nu=(k+1,4,3,2,1)` gives for **every** `k` in `4..9` the
same invariants: `d = 4`, `c = 5`, `h* = (1,0,1,0,0)`, `sum h* = 2`, `h*_1 = 0`,
identical profile `1,5,16,40,85,161,280,456,705`, held-out matched, round-trip OK.

### V3 — Reeve tetrahedron `T_q`, `q = 1..20`, fed in as a raw polytope: PASS

`T_q` is fed directly as a polytope, **bypassing hives**: `|n*T_q ∩ Z^3|` is obtained by
exact direct lattice-point enumeration
(`z` ranges over `max(0, q(x+y-n)) <= z <= q*min(x,y)`), and that profile is pushed
through the *same* interpolation + `h*` machinery used on hives.

For every `q` in `1..20`: `d = 3`, `h* = (1, 0, q-1, 0)`, `sum h* = q`, held-out
matched, round-trip OK, tail zero. Linear coefficient `= 2 - q/6`:

| q | 1 | … | 11 | 12 | **13** | 14 | … | 20 |
|---|---|---|---|---|---|---|---|---|
| lin | 11/6 | … | 1/6 | 0 | **−1/6** | −1/3 | … | −4/3 |

**The Reeve unit test DID show negativity at `q >= 13`**: the linear coefficient is
strictly negative for every `q` in `13..20` and for no `q < 13`; `q = 13` reproduces the
textbook `P(n) = 1 - n/6 + n^2 + 13n^3/6` with `h* = (1,0,12,0)` exactly. The instrument
therefore *can* see the textbook negative case — it is fit for purpose.

### V4 — engine A vs engine B on 200 random triples at `n = 1,2,3`: PASS

200 random triples (seed 20260721), all with `c > 0` at `n = 1` so the comparison is
non-vacuous, drawn from `|lam|, |mu| <= 7`, `#parts(lam), #parts(mu) <= 4`,
`#parts(nu) <= 5`. **600 `(triple, n)` evaluations, 0 mismatches.**

Engine A is the Knutson–Tao hive DFS counter; engine B is the classical
Littlewood–Richardson-rule skew-tableau DP. They share no code and no model. Both were
previously cross-calibrated against brute-force Schur products for all `|nu| <= 8`
(4993/4993 exact) and against `c=1 => P==1`, `c=2 => P=n+1`.

## Status

**OK — all four mandated validations pass.** No screening run has been performed with
this instrument yet; this build report covers construction and validation only. No
claim is made about the KTT conjecture in either direction.
