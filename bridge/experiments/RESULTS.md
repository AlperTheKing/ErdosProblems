# Step-2 computational results

## EXP-1 (2026-06-19): exhaustive per-graph Peeling Lemma at n=2 (10 vertices)

Tool: `peel_test.cpp` (brute maxcut, all 5-subsets). Input: all triangle-free
graphs on 10 vertices via `geng -t 10` (12172 graphs).

Definitions: `beta(G)=min monochromatic edges`; `pc(G)=min over 5-subsets S of
(beta(G)-beta(G-S))`. Per-graph (H2) for n=2 asserts `pc(G) <= 2n-1 = 3`.

Result:
```
total graphs            = 12172
a(10) = max beta         = 4        (matches OEIS A389646 -> validates beta code)
max pc over all graphs   = 3        (= increment; H2 holds, tight)
# per-graph H2 failures  = 0
pc distribution (ALL)    : 0:10613  1:1533  2:25  3:1
pc distribution (beta=4) : 3:1
witness of pc=3          : g6 "I?rFf_{N?"  = 4-regular, triangle-free, girth 4,
                           10 vertices = C5[2] (verified)
```

Interpretation (high-value):
- Per-graph (H2) holds for n=2 with **zero exceptions** and constant **exactly
  tight (3)**.
- The **unique** graph achieving `pc = 3` is the **unique** beta-extremal graph
  (beta=4), confirmed to be **C5[2]**. Every non-extremal graph has `pc <= 2`,
  i.e. strictly slack.
- This is exactly the predicted picture: `C5[n]` is the unique binding case for
  the peeling lemma, saturating the `2n-1` increment; all other graphs have
  strict room. Supports both the truth of (H2) and the stability/uniqueness
  hypothesis used by the cleanup route.

Caveat: n=2 is below the `n>=7` regime of (H2); this is confidence/structure
evidence, not a verification of the claimed range. Exhaustive testing is only
feasible at 10 vertices (n=3 -> 15 vertices has ~10^9 triangle-free graphs:
counts confirmed geng -t : n=11:105071, n=12:1262180, n=13:20797002, growing
~16x per step). Larger n must use targeted/structured candidates.

## EXP-2 (2026-06-19): targeted refutation hunt at n=3,4 (15,20 vertices)

Per-graph `pc` on structured triangle-free candidates (`gen_candidates.py`):

n=3 (15 vtx, incr=2n-1=5):
```
C5[3] balanced : beta=9 (=a(15), extremal)  pc=5  (= incr, TIGHT)
C5[1,2,3,4,5]  : beta=2  pc=0
C5[2,2,3,4,4]  : beta=4  pc=0
C5[1,3,3,4,4]  : beta=3  pc=1
C5[2,3,3,3,4]  : beta=6  pc=2
C15 (cycle)    : beta=1  pc=1
```
n=4 (20 vtx, incr=7):
```
C5[4] balanced : beta=16 (=a(20), extremal) pc=7  (= incr, TIGHT)
C5[2,4,4,5,5]  : beta=8   pc=2
C5[3,3,4,5,5]  : beta=9   pc=0
C5[1,4,5,5,5]  : beta=4   pc=0
Petersen[2]    : beta=12  pc=5   (high beta, still slack)
C20 (cycle)    : beta=0   pc=0
Dodecahedron(GP(10,2)): beta=6  pc=3
```

**No refutation.** Across n=2 (ALL graphs), n=3, n=4: every graph has
`pc(G) <= 2n-1`, and equality holds **only** for the balanced `C5[n]`. Even
high-beta non-blow-ups (Petersen[2] beta=12, dodecahedron beta=6) stay strictly
below the increment. This upgrades the working conjecture to:

> **Sharp Peeling Conjecture (SPC):** for every triangle-free G on 5n vertices,
> `pc(G) <= 2n-1`, with equality iff `G ≅ C5[n]`.

Reframing: at an extremal G (beta=a(5n)), `pc(G) <= 2n-1` is equivalent to
`a(5n) <= a(5(n-1)) + 2n-1`; and if a(5n)=n^2, a(5(n-1))=(n-1)^2, then the
needed `beta(G-S) >= (n-1)^2 = a(5(n-1))` forces `G-S` to itself be extremal on
5(n-1) vertices. So SPC at extremal graphs ⟺ "the extremal family is nested
`C5[n] ⊃ C5[n-1] ⊃ ...`", i.e. extremal UNIQUENESS — the standard hard core.

## EXP-4 (2026-06-19): annealing falsification at n=3 (15 vertices)

`peel_anneal.cpp`: simulated annealing over triangle-free graphs on 15 vertices
MAXIMIZING pc(G). 16 independent restarts (12k steps each, from empty graph).
Result: best pc found across all restarts = **4 < 5 = incr** (one restart hit 4,
rest 3). **No graph with pc > 2n-1 found.** (The annealer did not even reconstruct
C5[3]'s pc=5 from scratch, so it under-explores the extremal basin; nonetheless
zero pc>incr across 192k mutation steps is consistent with SPC.) Combined with
EXP-1 (exhaustive n=2) and EXP-2 (structured), no counterexample to per-graph
(H2) at n<=4.

## EXP-5 (2026-06-19): water-filling removal REFUTED as a universal rule

Tested the candidate clean rule "peel 5 vertices from the current-largest parts"
(water-filling) against the optimal removal, over ALL compositions of 5n, n=2..10.
- n<=8: water-filling matches (achieves `pc <= 2n-1`).
- **n=9,10: water-filling FAILS** — 14 compositions overshoot. Worst:
  `m=[7,12,9,10,12]` (n=10): water-filling gives `pc=21 > 19=2n-1`, while the
  optimal removal gives `pc <= 19`.
Conclusion: BU2 is TRUE (optimal `pc <= 2n-1` verified exhaustively n<=10) but
has **no trivial closed-form removal rule**; Case A (near-balanced) is proved,
Case B's removal is the genuine optimum and lacks a slick description. This
mirrors the global difficulty: even the blow-up case is tight and subtle.
[Recorded honestly; earlier hope that water-filling closes Case B is dropped.]

## EXP-6 (2026-06-19): random dense falsification at n=4 (20 vertices)
400 random MAXIMAL (edge-saturated) triangle-free graphs on 20 vertices,
per-graph pc. Result: max pc = 5 < 7 = 2n-1; **0 failures**. (Random maximal
graphs reached only beta<=12 < a(20)=16 — not C5-structured/near-extremal — so
this samples the "generic dense" region, complementary to the structured tests.)
pc dist: 0:87 1:109 2:74 3:76 4:43 5:11. Still no counterexample to per-graph (H2).

## EXP-7 (2026-06-19): C5-free triangle-free graphs have small beta (n=2)

Among all 12172 triangle-free graphs on 10 vertices, 5615 are **C5-free** (no
5-cycle; computed via `#C5 = trace(A^5)/10`, exact in triangle-free graphs).
**Max beta over C5-free = 1**, vs `a(10)=4`. So C5-free triangle-free graphs are
nearly bipartite here; high beta requires an induced C5. Supports the MC3 route.

**Caveat (general scale).** C5-free does NOT force `beta=o(n^2)`: the odd-cycle
blow-up `C7[m]` is `{C3,C5}`-free (odd-girth 7) with `beta(C7[m]) = m^2` (same
multilinear + cut-space argument as BU1). On `5n` vertices (`5n=7m`) this gives
`beta = (5n/7)^2 = 25n^2/49 ≈ 0.51 n^2`. So the BEST one can hope is the
sub-conjecture **"`{C3,C5}`-free triangle-free ⟹ beta < n^2"** (max over odd-cycle
blow-ups `C_{2k+1}[m]`, `k>=3`, is C7's `0.51 n^2 < n^2`); IF true, `beta >= n^2`
forces an induced C5 and the MC3 stability route applies. This sub-bound is itself
an extremal question (weaker than the main conjecture) — posed to GPT Q2.

## EXP-9 (2026-06-20): 4-chromatic triangle-free graphs are NEAR-extremal

Computed `beta` for non-C5-homomorphic triangle-free graphs:
- **Grötzsch** (Mycielskian of C5; 11 vtx, 20 edges, 4-chromatic, NOT 3-colourable):
  `beta = 4`. This EQUALS `a(11)=4` (OEIS) — Grötzsch is an EXTREMAL graph at N=11,
  reaching `82%` of `(N/5)^2 = 4.84`. So C5[2]+isolated and Grötzsch are BOTH
  extremal at N=11 (one C5-homomorphic, one 4-chromatic).
- **Myc(Grötzsch)** (23 vtx, 71 edges, 5-chromatic): `beta = 16` vs `(N/5)^2 =
  21.16` (and `a(23)=20`).

**Implication (caution for the stability route).** Near-extremal triangle-free
graphs need NOT be C5-homomorphic — 4-chromatic graphs (Grötzsch-type) come within
~18% of the bound. So Lemma C5HOM (β<=n² for C5-homomorphic graphs) does NOT
capture the hard near-extremal regime, and the frozen-pair / "G is close to C5[n]"
stability picture must contend with 4-chromatic competitors. At MULTIPLES of 5,
exhaustive n=2 still shows `C5[2]` is the UNIQUE β-maximiser (Grötzsch needs 11
vertices, doesn't fit in 10), but the near-extremal layer is genuinely richer than
C5-blow-ups. This is concrete evidence the medium-density difficulty is real.

**Refinement at multiples of 5 (EXP-9b).** Hill-climb max `beta` over 4-chromatic
(non-C5-hom) triangle-free 15-vertex graphs = **7 < 9 = a(15)** (8 restarts). And
N=10 exhaustive already gave C5[2] as the UNIQUE β-maximiser. So at MULTIPLES of 5
the C5-blow-up appears to STRICTLY dominate 4-chromatic graphs (the extremal is
C5-structured), while the N=11 Grötzsch tie is a non-multiple-of-5 phenomenon.
This is mildly encouraging for the stability route AT MULTIPLES OF 5 — the
extremal `C5[n]` is C5-homomorphic — though the near-extremal layer (within ~20%)
still includes 4-chromatic graphs, so a stability cleanup must tolerate them.
(Caveat: hill-climb under-explores; β=7 is a lower bound on the 4-chromatic max.)

## EXP-3 (done, exhaustive n=2..13): blow-up peeling
For ALL compositions m of 5n with the OPTIMAL removal, worst `pc = 2n-1` exactly,
achieved only at the balanced blow-up `[n,n,n,n,n]`, for every `n=2..13`. So BU2
(`pc(C5[m]) <= 2n-1`, tight iff balanced) holds throughout this range.
(Original wording, n<=6 phase, retained below.)


Verify `pc <= 2n-1` for ALL C5-blow-ups `C5[m0..m4]` (Σm=5n), using the
whole-part maxcut formula `beta = min_{c in {0,1}^5} Σ_i [c_i=c_{i+1}] m_i m_{i+1}`
(validated against brute force on all EXP-2 blow-ups — exact match). If clean for
all n, the blow-up case of SPC is provable analytically (see PEELING_LEMMA §9).


Test `pc` on structured triangle-free candidates likely to stress the lemma:
unbalanced C5 blow-ups, C7/C9 blow-ups, Petersen and its blow-ups, Kneser,
Cayley graphs, Mycielskians (note: Mycielskian of triangle-free is triangle-free
and raises chromatic number — a natural high-beta candidate). Any `pc(G) > 2n-1`
refutes per-graph (H2) and forces the extremal-only form (H2').
