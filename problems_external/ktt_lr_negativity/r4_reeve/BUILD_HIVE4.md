# BUILD_HIVE4.md — direct r=4 hive-polytope engine (the Reeve-dimension cell)

Date: 2026-07-21. Operator: Fable-5 subagent (workflow `ktt-r4-reeve`).
Target: a counterexample to the **King–Tollu–Toumazet (2004) positivity conjecture** —
partitions (λ, μ, ν) with |λ|+|μ|=|ν| whose stretched Littlewood–Richardson polynomial
P(n) = c(nν; nλ, nμ) has a **strictly negative** coefficient. (Also a FrontierMath open problem.)

## VERDICT

| gate | spec | result |
|---|---|---|
| (i) cross-engine L(1) | ≥ 400 random valid r=4 triples, hive4 = engine A = engine B exactly | **PASS 400/400** |
| (ii) stretched dilation identity | ≥ 60 of those, P(n) vs both engines at n = 2,3,4 | **PASS 210/210 checks (70 triples)** |
| (iii) Reeve unit test | T_q, q = 1..20, h\* = (1,0,q−1,0), a₁ < 0 exactly for q ≥ 13 | **PASS 20/20** |
| supplementary | 250 **dim-3** triples × n = 1,2,3,4 vs both engines | **PASS 1000/1000** |
| internal audits | interpolation held-out, volume cross-route, deg P = dim Q | **0 failures on every pool** |

**The Reeve T_q unit test DID detect negativity, exactly at q ≥ 13** (a₁ = 0 at q = 12,
a₁ = −1/6 at q = 13, negative through q = 20 and nowhere below 13). The Ehrhart machinery
therefore demonstrably detects the textbook negative case.

**No KTT counterexample was found** in any window searched. This proves nothing whatsoever
about the conjecture and is not evidence for it; it only closes the enumerated window.

## Artifacts

| file | sha256 |
|---|---|
| `r4_reeve/hive4.py` (module + CLI) | `be35d6a792aaaaeddef093f369f381190bc6f5b59278e281bfd8c7095e577efd` |
| `r4_reeve/validate_hive4.py` (mandated gate) | `70379869c3065b2a3105a9657c5a41e9dce245c4b89f59f2e7942703b1ec50a1` |
| `r4_reeve/validate_dim3.py` (dim-3 gate) | `3182265adc3feb9c0ecf394b8889e1d02c3bdd7a9f4da92ffa09ba64ea784eba` |
| `r4_reeve/census_r4.py` (exhaustive census) | `7cb3503d94fbbf6726c82c2b7786cb946f86ec73fee621584d1e5766cd1bfa01` |
| `r4_reeve/hunt_reeve.py` (Reeve-directed search) | `6315a62afac61b6a8cca4f560220f554d4f27dda392cf34e9fa270361b5f4927` |
| cross-check engine A `engine/lr_hive.exe` | `95d1fea3716756ffc48e662cfca117f04cc354ed598a638134163e50585b8cfc` |
| cross-check engine B `engine/engineB_lrrule.py` | `c7677d041ed184910a4290116b320000e529d70192c7f0cc91ccbfcc924b706c` |

Both engine hashes are **identical to the ones recorded in `engine/CALIBRATION.md`**, i.e. the
already cross-calibrated pair (brute-force Schur products for all |ν| ≤ 8; c=1 ⟹ P ≡ 1;
c=2 ⟹ P = n+1). No stretched-LR counting is used *inside* hive4.py — the engines appear only
as external validators.

Reproduce: `python hive4.py --selftest` (exit 0), `python validate_hive4.py` (exit 0),
`python validate_dim3.py 250` (exit 0), `python hive4.py --reeve 20`.

## Model

Knutson–Tao: c(ν; λ, μ) = #( Q(λ,μ,ν) ∩ Z^D ), D = (r−1)(r−2)/2, Q cut out by the three
rhombus families on a side-r triangular array with boundary fixed by partial sums of λ (left
edge), μ (right edge / hypotenuse), ν (bottom edge). Boundary convention and inequality
orientation are **identical to engine A** (`engine/BUILD_A.md`):

- (A) h(x+1,y)+h(x,y+1) ≥ h(x,y)+h(x+1,y+1), x+y ≤ r−2
- (B) h(x,y)+h(x+1,y) ≥ h(x,y+1)+h(x+1,y−1), y ≥ 1, x+y ≤ r−1
- (C) h(x,y)+h(x,y+1) ≥ h(x+1,y)+h(x−1,y+1), x ≥ 1, x+y ≤ r−1

**r = 4 ⟹ D = 3 exactly**, the interior vertices being (1,1), (1,2), (2,1). The right-hand
side is linear in the boundary data, so stretching by n **dilates** Q by n: P is the Ehrhart
counting function of Q and deg P = dim Q. Dimension 3 is the Reeve dimension — the smallest in
which an Ehrhart polynomial can have a negative coefficient. r = 3 is dim 1 (P linear,
trivially positive), so r = 4 is the minimal live case, and the previous four-wave
~398 000 000-triple campaign (r = 5,6,7,8,9) never entered it.

For r = 4 the constraint matrix A is **18 × 3 with entries in {0, ±1} and is the SAME for every
triple** — only b moves. Q = {h ∈ R³ : A h ≤ b}.

## What the engine computes (all exact: Python `int` / `fractions.Fraction`; no float anywhere)

(a) **emptiness / dim** — Q is certified bounded by an exact recession-cone test
(`is_bounded`: rank A = 3 kills the lineality space, then every 2-subset of rows is tested for
an extreme ray of {A x ≤ 0}); dim = affine rank of the exact vertex set.
(b) **vertices** — every 3-subset of rows is solved by integer Cramer (cached adjugate/determinant
table, exact) and kept iff **exactly** feasible; boundedness makes this enumeration complete.
Denominators are reported.
(c) **normalized volume V = 3!·vol** — exact boundary triangulation: each facet's vertex set is
angularly ordered by exact rational cross-products, fan-triangulated, and coned to the vertex
centroid; V = Σ |det|.
(d) **L(n) = #(nQ ∩ Z³), n = 0..5** — direct exact enumeration; coordinates 0 and 1 are looped
over integer intervals derived from the rows not involving later coordinates, coordinate 2 is
counted in closed form. Pure integer arithmetic.
(e) **Ehrhart polynomial P** — exact Lagrange interpolation of L(0..3), then **verified** to
reproduce the independently enumerated L(4) and L(5).
(f) **h\*-vector** — h\*_j = Σ_{i≤j} (−1)^i C(d+1,i) L(j−i), d = dim Q.
(g) **coefficients as exact Fractions**, with any strictly negative one flagged (`NEG`).

Two independent internal cross-checks are run on every polytope and were never violated:
`6·(leading coeff of P) == V` (triangulated volume vs Ehrhart leading term), and `deg P == dim Q`.

## CLI

```
python hive4.py "lam" "mu" "nu"     # one JSON line, full analysis
python hive4.py --batch FILE        # lines "lam;mu;nu"  ->  dim, c, V, h*, min coeff, NEG
python hive4.py --reeve [QMAX]      # Reeve unit test
python hive4.py --selftest          # exit 0 on pass
```

Batch output (from `demo.batch`):

```
3,2,1;3,2,1;4,4,2,2      | dim=1 c=2 V=0 hstar=[1,0]     minc=1   pos
11,5,1;13,4,3;21,10,5,1  | dim=3 c=6 V=3 hstar=[1,2,0,0] minc=1/2 pos
14,8,2;10,3,2;19,10,6,4  | dim=3 c=8 V=5 hstar=[1,4,0,0] minc=5/6 pos
```

Throughput ≈ 0.5 ms per triple (≈ 2 000 triples/s single-threaded).

## Validation detail

### (iii) Reeve tetrahedron T_q = conv{(0,0,0),(1,0,0),(0,1,0),(1,1,q)} — hives bypassed

Fed to the *same* `analyze_polytope` as the hives, via the exact H-representation
−z ≤ 0, −qy+z ≤ 0, −qx+z ≤ 0, qx+qy−z ≤ q. For every q = 1..20 the engine reproduced,
exactly: the 4 expected vertices, dim 3, L(1) = 4, V = q (both by triangulation and by
6·lead P), **h\* = (1, 0, q−1, 0)**, P = (q/6)t³ + t² + (2 − q/6)t + 1, and the held-out
checks P(4) = L(4), P(5) = L(5).

```
q=12  h*=[1,0,11,0]  a1= 0     NEG=False   V=12
q=13  h*=[1,0,12,0]  a1=-1/6   NEG=True    V=13
q=20  h*=[1,0,19,0]  a1=-4/3   NEG=True    V=20
```

NEG fired for exactly q ∈ {13,…,20} and for no smaller q. **The negativity detector works on the
textbook case.**

### (i)/(ii) cross-engine

Pool: 400 seeded random triples (seed 20260721404), ν with exactly 4 positive parts,
4 ≤ |ν| ≤ 34, λ, μ with ≤ 4 parts — 300 with c > 0, 100 with c = 0 (drawn from 2548 samples).
dim histogram {−1: 100, 0: 255, 1: 29, 2: 13, 3: 3}; max c = 7; max vertex denominator 1.

- (i) hive4 L(1) vs engine A vs engine B: **400/400 exact triple agreement, 0 mismatches.**
- (ii) 70 triples × n ∈ {2,3,4}: **210/210** — hive4's interpolated P(n) equals the *stretched*
  counts c(nν; nλ, nμ) from **both** engines. This validates the dilation-equals-stretching
  identity end to end.

Because dim 3 is rare among uniform random triples (3/400) and is the **only** stratum where
negativity is possible, a supplementary gate was run on a pool of **250 dim-3 triples only**
(seed 20260721303, 8 ≤ |ν| ≤ 60, drawn from 88 251 samples; c ∈ [4, 38], V ∈ [1, 88]):
**1000/1000** agreements with both engines at n = 1,2,3,4; 0 internal failures.

## Searches run (no counterexample found — this closes windows, it proves nothing)

**Structural reduction.** Writing P in the h\*-basis, P(n) = Σ h\*_i C(n+3−i, 3), gives for
dim Q = 3 the exact identities (both verified computationally on every dim-3 sample):

    a₃ = V/6 > 0,   a₂ = 1 + (h*₁ − h*₃)/2,   a₁ = (11 + 2h*₁ − h*₂ + 2h*₃)/6,   a₀ = 1.

So a₃ > 0 always, a₂ ≥ 0 whenever h\*₃ ≤ h\*₁, and **the only Reeve-type coefficient is a₁**:
a KTT counterexample in the r=4 cell requires

    h*₂  >  11 + 2·h*₁ + 2·h*₃

(the Reeve tetrahedron realises h\*₂ = q−1 with h\*₁ = h\*₃ = 0 and crosses at q = 13).

1. **Exhaustive census** (`census_r4.py`, log `census_r4.log`, json `census_r4.json`): every
   triple with ν a partition of N into exactly 4 positive parts and λ, μ of ≤ 4 parts,
   |λ|+|μ| = N, for **4 ≤ N ≤ 22**, using the λ↔μ symmetry — **1 363 713 triples, 779 s**.

   ```
   dim histogram        : {-1 (Q empty): 1093750, 0: 195995, 1: 51736, 2: 18030, 3: 4202}
   internal audit fails : 0        (held-out interpolation / volume route / deg = dim)
   non-lattice Q        : 0        (every vertex integral; max denominator 1 throughout)
   record h*_2          : 3        at λ=(5,3,1), μ=(6,4,2), ν=(9,6,4,2), h* = (1,5,3,0)
   NEGATIVE COEFFICIENTS: 0
   ```

   Only 4202 of the 1.36 M triples are dim-3, i.e. even capable of negativity, and the largest
   h\*₂ anywhere in the window is 3 — against the requirement h\*₂ > 11 + 2h\*₁ + 2h\*₃. The
   window is therefore closed with an enormous margin, and the record-h\*₂ frontier is the
   quantity to push, not |ν|.
2. **Reeve-directed local search** (`hunt_reeve.py`): hill-climbing on the exact score
   6a₁ = 11 + 2h\*₁ − h\*₂ + 2h\*₃ over dim-3 states with unbounded part sizes.
   150 s, 200 383 exact evaluations, 169 restarts, parts up to ~44: **0 negative hits**;
   best 6a₁ = 11 (the unimodular simplex, h\* = (1,0,0,0)); record h\*₂ = 291 reached at
   λ=(37,19,7,3), μ=(33,20,5), ν=(44,38,28,14) with h\* = (1,138,291,38) — but there
   11 + 2·138 + 2·38 = 363 > 291, so a₁ = 12 > 0.
3. **Exhaustive dim-3-restricted minimum** (`_dim3_min.py`, log `_dim3_min.log`), 4 ≤ |ν| ≤ 20,
   610 125 triples, 404 s: **1320 dim-3 hive polytopes**, the first appearing only at |ν| = 12.
   `min 6a₁ = 11` exactly, i.e. **min a₁ = 11/6**, attained at λ = μ = (3,2,1), ν = (5,4,2,1),
   h\* = (1,0,0,0) — the unimodular simplex. Record h\*₂ in that window: 2.
   An independent 60 000-sample sweep (|ν| ≤ 80) found 216 dim-3 polytopes, minimum 6a₁ = 11 again.
4. **Saturation audit** (independent consistency check on the engine, not a search): the
   Knutson–Tao saturation theorem says a nonempty hive polytope always contains a lattice point.
   Over 120 000 random triples, 13 905 had Q ≠ ∅ and **every single one had L(1) ≥ 1** — 0
   violations. A bug in the vertex enumeration or the lattice counter would very likely have
   shown up here as a nonempty Q with L(1) = 0.
5. **Brute-force audit of the pruned lattice counter**: on the record-h\*₂ state
   λ=(37,19,7,3), μ=(33,20,5), ν=(44,38,28,14), a naive unpruned triple loop over the full
   integer bounding box gave L(1) = 142, identical to the pruned counter; there
   h\* = (1,138,291,38), P = 78n³ + 51n² + 12n + 1, V = 468, a₁ = 12 > 0.

**Empirical pattern (a hypothesis, NOT a theorem, NOT evidence for KTT):** across every dim-3
r=4 hive polytope seen — exhaustively for |ν| ≤ 20/22 and in ~200 000 further searched states
with parts up to ~44 — min a₁ = 11/6, attained at the unimodular simplex, and every vertex was
integral (max denominator 1). The r=4 hive polytopes encountered are all lattice polytopes whose
h\*₂ stayed below 11 + 2h\*₁ + 2h\*₃ — i.e. they are far from Reeve-like even when h\*₂ is large
in absolute terms (291), because h\*₁ grows with it.

**Route to a decisive r=4 verdict** (not attempted here): for r = 4 the matrix A is fixed and only
b ∈ Z^{12} moves, so the b-space decomposes into finitely many chambers on which the combinatorial
type of Q and its vertices (fixed integer linear functionals of b divided by fixed 3×3 minors of A,
which are bounded by 4 in absolute value) are constant. On each chamber a₁ is a piecewise
quasi-polynomial of degree ≤ 1 in b, so a **complete** proof or refutation of KTT in the r=4 cell
reduces to a finite chamber enumeration plus a sign analysis per chamber. That is the honest way
to close this cell; the census and the local search only bound the window.
