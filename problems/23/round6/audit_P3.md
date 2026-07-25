# AUDIT of round6/P3.md (Vega graphs) — ADVERSARIAL, FINAL

Auditor: independent re-implementation in `round6/audit_P3_*.py|cpp`.  Nothing imported from
`P3_*.py`; own Vega construction from the Brandt–Thomassé text, own graph6 decoder, own max-cut
(full `2^(n-1)` enumeration / Gray-code walk), own weight enumerator, own arc families.
Exact integer / `Fraction` arithmetic on every acceptance path.  Mandatory regression run against
`round5/claude_witness_regression.py`.

**Bottom line.**  P3's computations are, with one exception, reproducible and correct — several are
*stronger* than the report claims, and I extended them into regions P3 never tested and they still
hold.  **No counterexample to Erdős 23 exists in anything I ran.**  But two stated results are
false: the headline of section (e) ("max ψ over the δ-polytope is 29/841, attained at ω_reg,
uniform 13.8 % margin") is **REFUTED** by 11 exactly-verified points inside P(H), and the open
statement **V3 does not have the Vega graphs as instances**, so "V3 ⟹ V1" is false as written.

---

## Verdicts, most consequential first

### 1. REFUTED — (e) "the maximum over the whole Vega family is 29/841, attained at the regular weight function; V1′ has a uniform 13.8 % margin and is not tight"

P3 ran its `P3_delta.exe` engine **only on the four i = 2 graphs**, at denominators 29/58/87/116
(and 32/64, 35/70).  For i ≥ 3 **only the single point ω_reg was ever evaluated**.  There is also
**no log file for any DELTA run** — the table in P3.md has no recorded evidence (I reproduced the
q = 29/58/87 rows myself; they are correct).

My hill-climber (`audit_P3_deltamax.cpp`, exact int64 Gray-code bip, exact feasibility
`3·a(N(v)) > D`) finds points strictly inside P(H) above 29/841 on **11 of the 12** Vega graphs with
n ≤ 19.  Every falsifier below was re-verified from scratch in Python with `Fraction` arithmetic,
my own construction, and `bip` by exhaustive `2^(n-1)` enumeration (`audit_P3_delta_verify.py`).

**Strongest exact falsifier — Υ₃−{2i}, n = 15, D = 11800**, order `1,2,3,4,5,7,8,x,y,a,b,c,u,v,w`

```
a = 336 625 207 562 597 634 525 265 254 1409 1225 1291 1367 1226 1277      (sum = 11800)
min_v omega(N(v)) = 1967/5900 = 0.3333898... > 1/3          -> INSIDE P(H), verified exactly
psi = 4898341/139240000 = 0.035179122 >  29/841 = 0.034482759            *** exceeds the claim ***
                                       <  1/25  = 0.04                   (Erdos 23 NOT violated)
```

**Second, on Υ₃ itself, n = 16, D = 12400**, order `1..8,x,y,a,b,c,u,v,w`

```
a = 34 606 608 578 634 32 588 627 280 294 1434 1445 1170 1457 1441 1172
min_v omega(N(v)) = 2067/6200 > 1/3 ;  psi = 67387/1922000 = 0.035060874 > 29/841
```

**Grötzsch itself refutes "attained at ω_reg"** — Υ₂−{y,4}, n = 11, D = 5800, order
`1,2,3,5,x,a,b,c,u,v,w`

```
a = 383 463 564 567 429 864 558 547 573 452 400                            (sum = 5800)
min_v omega(N(v)) = 1951/5800 = 0.3363793... > 1/3      -> INSIDE P(H), verified exactly
psi = 145111/4205000 = 0.034509156  >  1/29 = 29/841 = 0.034482759
```

(The excess is only 8×10⁻⁴ relative, which is exactly why P3's coarsest grid, denominator 116,
could not see it: 0.0345091·116² = 464.35, and an integer grid can only report 464 = 116²/29.)

Full table — **every one of the 11 rows re-verified in Python with `Fraction` arithmetic, my own
construction and my own exhaustive `2^(n-1)` max-cut** (`audit_P3_delta_verify2.py`,
`audit_P3_delta_verify2.log`); all feasible = True, all < 1/25:

| graph | D | ψ found | vs 29/841 | ψ(ω_reg) |
|---|---|---|---|---|
| Ups_3-2i | 11800 | 4898341/139240000 = 0.035179122 | **>** | 0.0327492 |
| Ups_3 | 12400 | 67387/1922000 = 0.035060874 | **>** | 0.0327784 |
| Ups_2 | 7000 | 1710869/49000000 = 0.034915694 | **>** | 0.0342857 |
| Ups_3-y-2i | 11200 | 68371/1960000 = 0.034883163 | **>** | 0.0322066 |
| Ups_3-y | 11800 | 1208813/34810000 = 0.034726027 | **>** | 0.0321747 |
| Ups_2-2i | 6400 | 355059/10240000 = 0.034673730 | **>** | 0.0332031 |
| Ups_2-y | 6400 | 56807/1638400 = 0.034672241 | **>** | 0.0332031 |
| Ups_4-2i | 17200 | 638553/18490000 = 0.034535046 | **>** | 0.0320443 |
| Ups_4-y-2i | 16600 | 951639/27556000 = 0.034534729 | **>** | 0.0316447 |
| Ups_4 | 17800 | 10936143/316840000 = 0.034516295 | **>** | 0.0321929 |
| Ups_2-y-2i | 5800 | 145111/4205000 = 0.034509156 | **>** | 0.0344828 |
| Ups_4-y | 17200 | 5082479/147920000 = 0.034359647 | no | 0.0317739 |

(The i = 5 graphs, n = 20..22, were also searched and did **not** exceed 29/841 — best 0.0338354 on
Υ₅ — but there the exact `2^(n−1)` evaluation is 100–1000× more expensive, so the hill-climber gets
far fewer iterations; absence of a falsifier at i = 5 is not evidence of one not existing.)

**What is false, precisely:**
* "the maximum of ψ over P(H) is attained at the (unique) regular weight function in every case
  tested" — false on **all twelve** graphs (the regular point is not even a local max).
* "The maximum over the whole Vega family is 29/841 = 0.0344828 (Grötzsch)" — false; ≥ 0.0351791,
  and that is only a **lower** bound (hill-climbing), so the true maximum is higher still.
* "V1′ has a uniform 13.8 % margin" — the demonstrated margin is at most **12.05 %**, and since my
  number is a lower bound on the max the true margin is ≤ that.  "13.8 %" is not established.
* "**V1′ ... is not tight** ... the Vega graphs are **not** the hard case" — the *direction* may well
  survive (everything I found is still below 1/25), but the quantitative statement supporting it is
  wrong, and the margin is not uniform in i: my best value at i = 3 (0.03518) is **larger** than at
  i = 2 (0.03492), so the report's "decreasing monotonically in i" picture — true at ω_reg — does
  **not** transfer to the maximum over P(H).  Whether sup over the family stays below 1/25 as
  i → ∞ is open and P3 supplies no evidence for it.

Erdős 23 itself is untouched: every point found is < 1/25.

### 2. REFUTED — V3 (VEGA-∞): "Every Vega graph is the atomic instance of V3 … Conversely V3 ⟹ V1 for every i"

V3 is stated with the six special atoms "at circle position 2/3, 0, 1/3 … joined to that position's
far-arc", the arcs being `X = (0,1/3)`, `Y = (1/3,2/3)`, `Z = (2/3,1)`, and μ = the uniform measure
on the (3i−1)-th roots of unity.  Those two halves are incompatible: the roots of unity `j/(3i−1)`
do not straddle 1/3 and 2/3 where Υᵢ needs them.  Computed (`audit_P3_v3.py`, `audit_P3_v3.log`;
0 of 6 tested i give the right graph, including i = 20):

```
i=2  V3-literal  X={1}      Y={2,3}      Z={4}        (sizes 1,2,1)   vertex 5 gets NO attachment
     Upsilon_2   X={1,2}    Y={3,4}      Z={5}        (sizes 2,2,1)
i=3  V3-literal  X={1,2}    Y={3,4,5}    Z={6,7}      (sizes 2,3,2)
     Upsilon_3   X={1,2,3}  Y={4,5,6}    Z={7,8}      (sizes 3,3,2)
general: V3-literal gives (i-1, i, i-1);  Upsilon_i needs (i, i, i-1)
```

So the "atomic instance" of V3 is a **different graph** from Υᵢ for every i ≥ 2, and V3 ⟹ V1 does
not hold.  The defect is purely definitional and is **contradicted by P3.md's own section (a)**,
which states the correct rule: a,u sit at circle position **2i**, b,v at **1**, c,w at **i+½**, and
are joined to the far arc *of that position*.  I verified that rule reproduces X, Y, Z exactly for
i = 2,3,4,5,8 — i.e. with positions `2i/(3i−1)`, `1/(3i−1)`, `(i+½)/(3i−1)` (which are **not**
2/3, 0, 1/3) the instance is right.  V3 needs restating with the positions as parameters; as
written it is the wrong limit object.

### 3. UNSUPPORTED — the "1.9 × 10¹¹ integer weightings" figure

P3.md's summary point 2 and V1's status line both cite **1.9 × 10¹¹**.  Its own `P3_sweep.log`
gives, over the 68 runs, `sum(leaves) = 262 546 079 404 = 2.6255 × 10¹¹` and
`sum(orbitreps) = 90 148 588 274 = 9.015 × 10¹⁰`.  Neither equals 1.9 × 10¹¹, and the (c) section
and the one-line answer say 2.63 × 10¹¹ / 2.6 × 10¹¹.  Internal inconsistency; the correct figures
are 2.6255 × 10¹¹ enumerated and 9.015 × 10¹⁰ processed.

### 4. UNSUPPORTED-AS-FILED, CONFIRMED-ON-RERUN — the (e) DELTA table and the Result-3 ARCFREE/ARC3 numbers had no logs

* No `DELTA` line exists in any file in `round6/`.  I re-ran and reproduced q = 29/58/87 for
  Grötzsch exactly (feasible = 1, maxBip = 29/116/261, ψ = 29/841 each time).
* No `ARC3` line exists in any log, and the only `ARCFREE` lines are the Γ₂..Γ₈ EXACTCHK runs.
  I re-ran both quoted numbers and they are exactly right:
  `ARCFREE Ups_2-y-2i q=20: reps=3016019 certified=313322 FAILED=2702697` and
  `ARC3 Ups_2-y-2i q=20: reps=3016019 certified=2975797 FAILED=40222`.

### 5. CONFIRMED — (a) the definition, and every paper quote is verbatim-accurate

Checked against the extracted `P3_bt_text.txt`: the Vega construction (p.4), the Γᵢ definition
(p.3), the four regular weight functions (Theorem 3), and **Corollary 4.1** ("The twin-free,
maximal triangle-free, weighted graphs with δ > 1/3 are the 3-colorable graphs Γᵢ for i ≥ 1 and the
4-chromatic Vega graphs") are all present word-for-word.  The hypotheses match the use: I
re-derived the reduction (spanning maximal-triangle-free supergraph → ψ monotone under edge
addition → twin contraction is exact because `mono_S` is **linear** in the split fraction of a twin
class, so the min is at an undivided extreme point → Corollary 4.1), and it is sound.  So
**V1′ is genuinely the statement the δ > N/3 case needs** — that part of section (e) is a correct
and useful sharpening, independent of the false quantitative claim in §1.

Γᵢ = And(i) = the circle graph on `3i−1` points with `d > 1/3` — verified.  Infinite family, one
parameter i ≥ 2, four members per i (three at i = 2) — verified.

### 6. CONFIRMED — (b) all 28 graphs, rebuilt from scratch and matched byte-for-byte

`audit_P3_build.py`: 28/28 rows, **0 failures**.  For every graph: triangle-free, maximal
triangle-free, twin-free, χ = 4, odd girth 5, **induced C₅ present**, the paper's weight function is
regular, δ = (9i−6)/(27i−19) etc. with `3·degree = total + 1` exactly, and the graph6 string in
`P3_vega.g6` decodes to **exactly my edge set on the declared vertex order** (not merely up to
isomorphism).  `Ups_2-y-2i ≅ Grötzsch` ✓; `Ups_2-y ≅ Ups_2-2i` ✓ and non-isomorphic for i = 3..8 ✓.

### 7. CONFIRMED and STRENGTHENED — (c) no violation of ψ ≤ 1/25, and the equality census

* All 68 runs in `P3_sweep.log`: `leaves = C(q+n−1, n−1)` **exactly in all 68** (completeness
  certificate valid — `leaves` counts every leaf, the Aut reduction only filters what is
  *processed*, so the certificate is not circular).  `GT = 0` in all 68.  All 45 rows with `5 | q`
  report `maxExactBip = q²/25` exactly.
* The `LT` mode is the right design: cache/local-search can certify only when `25·mono < q²`, so
  **every** weighting with `bip ≥ q²/25` is forced onto the exact `2^(s−1)` path.  No floating point
  on any acceptance path in `P3_psi.cpp` — verified by reading the code.
* Equality census independently reproduced (`audit_P3_equality.py`, own enumeration, own max-cut,
  own Aut canonicalisation): Grötzsch q = 10 → **96 weightings in 15 Aut-orbits**, support sizes
  {5,6,7}; Ups_2 q = 10 → **296 in 44 orbits**, supports {5,6,7,8}.  Both match P3's table exactly.
  And **all 96 and all 296 are C₅-quotient weightings**, exactly as P3 claims.
* The lower bound `max ψ ≥ 1/25` (V0) is correct but near-trivial: ψ restricted to a support inside
  an *induced* subgraph H equals ψ_H, so any induced C₅ forces it.  P3 says so.

**Extension P3 never ran.**  P3's largest q is 14 (n = 11) down to 8 (n = 31), so **no weighting
with support > 14 was tested on any Vega graph**, and the uniform weighting was untested for i ≥ 5.
`audit_P3_full.cpp` closes that: exact bip by a Gray-code walk over the **complete** `2^(n−1)` cut
set (up to 2³⁰ cuts at n = 31) — no local search, no cache, no Aut reduction, no support
restriction — for the uniform weighting, the paper's regular weighting, and 6 random **full-support**
weightings of total 90, on all 28 graphs.  **224 tests, 0 Erdős-23 violations, 0 ARCPLUS-exactness
failures.**  As a by-product this upgrades P3's closed-form table for ψ(ω_reg) from "ARCPLUS upper
bound" (all P3 could do for i ≥ 5) to **exact for i = 2..8**: all 28 values match the four closed
forms (with the i = 2 `Υᵢ−{2i}` row excluded, as P3 correctly notes).

### 8. CONFIRMED — (d) Result 4 / V4: the m(b) / bound_k hierarchy fails on Vega

Recomputed from my own construction (`audit_P3_witness.py`), Υ₂, q = 15,
`a = (1,1,1,1,3 ‖ 1,1 ‖ 1,1,1,1,1,1)` on order `(1,2,3,4,5,x,y,a,b,c,u,v,w)`:

```
neighbourhood cut values m(t): 16 10 10 16 12 | 16 16 | 11 11 10 11 11 10   (all N(t) independent)
min over all 13 = 10  ->  10/225 = 2/45 = 0.04444... > 1/25
true bip = 7 -> psi = 7/225 = 0.03111... <= 1/25 ;  ARCPLUS min = 7 (exact)
```

The logical step is valid: `bound_k` is an `x·g^k`-weighted average of the `m(b)`, hence
`≥ min_b m(b) = 10 > 9 = q²/25`, for **every** k ≥ 0.  All four further witnesses quoted in P3.md
reproduce exactly (famMin = 10, trueBip = 7, q = 15 in each).  The systemic overshoot at ω_reg
reproduces too: NBHDmin/(1/25) = 1.3377…1.3729 for i = 2,3,4 while ψ/(1/25) = 0.7911…0.8621.
**V4 belongs on the REFUTED list as P3 asks.**

### 9. CONFIRMED and STRENGTHENED — (d) Result 2 / V2: arc exactness

P3 tested `ARCBOUND = ψ` on the seven Andrásfai circles Γ₂..Γ₈, i.e. `m = 5,8,11,14,17,20,23` —
one residue class of m mod 3 and seven circle sizes.  I tested the **structural** statement instead
(`audit_P3_arcexact.cpp`): a measure on s atoms is s points in cyclic order with gaps summing to m,
adjacency `3·circdist > m`, and the trace of a circle arc on the support is exactly a cyclic
interval of the atoms.  So I enumerated **every circular-threshold adjacency pattern** reachable
with m ≤ 26 (s ≤ 8), m ≤ 30 (s = 9), m ≤ 32 (s = 10) — all three residues of m mod 3, i.e. every
rational atom configuration of denominator ≤ 26/30/32 — and for each, every positive integer
weighting with total ≤ 16 / 13 / 12, comparing `min over cyclic intervals` with `min over all
2^(s−1) cuts`.

```
s        3    4    5    6    7    8    9    10
patterns 3    8   16   37   85  216  553  1494          (2412 total)
configurations tested: 4 588 896      ARC-EXACTNESS FALSIFIERS: 0
```

**Positive control:** re-running with the family cut down to half-arcs only (the family round 5
already refuted) makes the detector fire immediately — so a failure would have been seen.  V2 as an
*empirical* statement is confirmed well beyond P3's own coverage, and it also held at every
full-support weighting in §7.  It remains **unproved**, and P3 says so.

Caveats on the framing:
* "ARCPLUS is a genuine restriction of the full family" is thin at small i: at i = 2, |ARCPLUS| =
  2816 against 2¹² = 4096 total cuts.  It only becomes a real reduction from i ≈ 5 on.
* The stated size `2⁸·((3i−1)(3i−2)+2)` is the count *before* complement-deduplication and is an
  overcount for the `−{2i}` variants (e.g. 14 distinct arc traces at i = 2, not 22).  Cosmetic.
* P3's own conclusion ("proving `25·ARCBOUND ≤ (Σx)²` loses nothing but also gains nothing — the
  arc statement is *equivalent* to the conjecture on those graphs") is correct and is the honest
  reading; I agree with it.

### 10. CONFIRMED — the mandatory regression

`audit_P3_regression.py` (my arc family, my max-cut, my Vega construction; the round-5 file used
only as the witness *data*):

```
R1  all 9 witnesses ARCBOUND <= 1/25, and every quoted value matches exactly:
    W1 1/49  W1' 1/49  W1'' 1/49  W2 1/25 (tight)  W3 1/54  W4 3/100  W5 0  W6 1/49  W7 1/100
R2  ARCBOUND == min over ALL 2^(m-1) cuts on all 9 (0 exactness failures)
R3  20 Vega lifts: ARCPLUSmin <= 1/25 and == true bip on all 20
VERDICT: R1 PASS | R2 PASS | quoted values MATCH | R3 PASS
```

P3's own `P3_regression.py` also re-runs clean.  One immaterial difference: on the two lifts where
the deleted vertex 2i carried mass, P3 keeps the **original** denominator (reporting 9/400 for W4
on Ups_7-2i) while I renormalise the surviving mass to a probability vector (9/361).  Mine is the
stricter test and it also passes.

---

## Failure modes specifically checked, and not found

| checked for | result |
|---|---|
| floating point on an acceptance path | none — `P3_psi.cpp` / `P3_cutfamily.cpp` / `P3_delta.cpp` use int64 throughout; doubles appear only in timing, task-count heuristics and cosmetic printing |
| ψ < 1/25 reported as a *maximum over the simplex* for an odd-girth-5 graph | not done — every sub-1/25 number in P3.md is either at a single ω or a max over the δ-**polytope**, which legitimately excludes the C₅ extremals |
| integer enumeration excluding zero weights | zeros are included (`rec` runs `t` down to 0); the completeness certificate `leaves = C(q+n−1,n−1)` confirms it |
| loop bounds not covering the claimed range | `rec`/`Gen::go` enumerate all compositions; prefix tasks cover sums ≤ q with the tail filled in — complete.  `P3_delta.cpp`'s prune is a valid upper bound on the achievable weighted degree |
| unsound Aut reduction | `perms` = `GraphMatcher(G,G).isomorphisms_iter()`, i.e. genuine automorphisms; `lexMin` keeps lex-minimal orbit representatives — sound (and conservative if the group were under-generated) |
| circularity in the completeness certificate | none: `leaves` is incremented before the `lexMin` filter |
| quoted theorem whose hypotheses do not match its use | Corollary 4.1 is quoted verbatim and applied correctly (the twin-contraction of a maximal triangle-free graph is maximal triangle-free and twin-free — I re-proved it) |
| a claimed proof not tight at the C₅ extremal | the only claimed *proof* is V4 (a negative result) and V0 (induced-C₅ lower bound); neither is an upper-bound proof, so the tightness test does not bite.  P3 makes no claim to have proved V1/V1′/V2/V3 |
| `exactBip` correctness | `mask < 2^(s−1)` fixes one support vertex on side 0 — valid, cuts come in complementary pairs; scratch arrays (512/600) exceed the maximum edge count (151) |

## Coverage limits of P3 that the report does not state

1. Exhaustive (c)/(d) coverage is q ≤ 14 at n = 11 falling to q = 8 at n = 31 — **no weighting with
   more than 14 atoms was tested by P3 on any Vega graph**.  (I filled this in §7; it holds.)
2. The EXACTCHK totals are dominated by large-i runs at tiny q, where the support is ≤ 8 or 9 of up
   to 31 vertices — "424 847 879 orbit representatives" is a much thinner probe of the large graphs
   than the raw number suggests.
3. (e) was computed for i = 2 only, at four denominators, with no log.

---

## Summary

| # | claim | verdict |
|---|---|---|
| 1 | (e) max ψ over P(H) = 29/841, attained at ω_reg, uniform 13.8 % margin, "Vega not the hard case" | **REFUTED** — 11 exact points inside P(H) exceed it; best 4898341/139240000 = 0.0351791 on Υ₃−{2i} |
| 2 | V3 has the Vega graphs as atomic instances; V3 ⟹ V1 | **REFUTED** — literal V3 attaches (i−1, i, i−1), Υᵢ needs (i, i, i−1) |
| 3 | "1.9 × 10¹¹ integer weightings" | **UNSUPPORTED** — the log gives 2.6255 × 10¹¹ leaves / 9.015 × 10¹⁰ orbit reps |
| 4 | (e) DELTA table and Result-3 ARCFREE/ARC3 counts | **UNSUPPORTED as filed** (no logs) but **CONFIRMED on rerun** |
| 5 | (a) family definition, all paper quotes, the V1′ reduction | **CONFIRMED** |
| 6 | (b) 28 graphs and every property, incl. exact g6 round-trip | **CONFIRMED** |
| 7 | (c) 2.6255 × 10¹¹ weightings, completeness, GT = 0, equality census = C₅-quotients | **CONFIRMED**, and extended to full support up to n = 31 |
| 8 | (d) V4: m(b)/bound_k fails on Vega (Υ₂, q = 15, min = 10 > 9, bip = 7) | **CONFIRMED** exactly |
| 9 | (d) V2: ARCPLUS / ARCBOUND exactness | **CONFIRMED** and strengthened (2412 patterns, 4.59 M configs, all m mod 3) |
| 10 | mandatory regression R1/R2/R3 | **CONFIRMED** (all 9 quoted values match exactly) |

**Erdős 23 is not threatened by anything in P3.md or in this audit** — every ψ computed, over
2.6 × 10¹¹ enumerated weightings, 224 full-support exact max-cuts up to 2³⁰ cuts, 4.59 M circular
configurations and 11 δ-polytope falsifiers, is ≤ 1/25.

### Files

| file | what it is |
|---|---|
| `audit_P3.md` | this report |
| `audit_P3_core.py` | independent Vega construction, graph6 decoder, exact bip, arc/ARCPLUS families |
| `audit_P3_build.py` | (a)/(b) audit: 28 graphs rebuilt, all predicates, exact g6 match |
| `audit_P3_witness.py` | V4 witness + regular-point ψ / NBHD table, exact |
| `audit_P3_arcexact.cpp` / `.exe` / `audit_P3_arcexact_s38.log` | structural arc-exactness sweep over all circular-threshold patterns (+ `HALF` positive control) |
| `audit_P3_full.cpp` / `.exe` / `audit_P3_full.log` | Gray-code exact bip at full support, n ≤ 31, vs ARCPLUS and 1/25 |
| `audit_P3_deltamax.cpp` / `.exe` / `audit_P3_deltamax.log`, `_deep.log` | δ-polytope maximiser — produced the §1 falsifiers |
| `audit_P3_delta_verify.py`, `audit_P3_delta_verify2.py` / `.log` | exact `Fraction` re-verification of all 11 §1 falsifiers |
| `audit_P3_v3.py` / `.log` | V3 literal-instantiation test (§2) |
| `audit_P3_rerun_unlogged.log` | reruns of the P3 claims that ship with no log (DELTA table, ARCFREE, ARC3) |
| `audit_P3_equality.py` | (c) equality-census audit: counts, orbits, C₅-quotient property |
| `audit_P3_regression.py` / `.log` | my independent R1/R2/R3 regression |
| `audit_rerun_P3_regression.log` | rerun of P3's own `P3_regression.py` |
