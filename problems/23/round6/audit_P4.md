# audit_P4 — ADVERSARIAL AUDIT of `round6/P4.md`

Independent auditor, 2026-07-25.  Everything below was re-implemented from the task brief's
definitions in `round6/audit_P4_*.py|cpp` — my own data structures, my own max-cut (brute force over
all `2^{n−1}` bipartitions), my own weight enumerator (C++ integer, cross-validated against a slow
exact Python enumerator).  Nothing is imported from `P4_*.py`; the only shared input is the
mandatory `round5/claude_witness_regression.py`.  Every acceptance path is exact
`fractions.Fraction` / `sympy.Rational` / 64-bit integer.  Floating point appears only inside search
*proposals*; every record is re-verified exactly.

---

## Verdict table (most consequential first)

| # | P4 claim | verdict |
|---|---|---|
| 1 | **item 7 is FALSE**, witnesses W8/W9/W10 on Γ₂₀ | **CONFIRMED** — every number reproduces exactly; I add two further falsifiers of my own on Γ₁₁ and Γ₁₄ |
| 2 | W8/W9/W10 are three witnesses that "only directed max-min search finds", "genuinely asymmetric" | **REFUTED** — all three are the SAME graph (Wagner Γ₈ = And(3)) re-embedded; the hierarchy fails on *every* uniform Andrásfai measure in closed form |
| 3 | (g)/(h) `max_x ψ(C7) = 4/225`, attained at min support degree `4/15` | **REFUTED** — `max_x ψ(C7) = 1/49 = 0.020408 > 4/225 = 0.017778`, attained at the uniform weighting (min degree `2/7`); P4's number is a `q = 30` grid artifact |
| 4 | (g) `max_x ψ(Grötzsch) = 1/25` exactly (Vega branch "tight") | **UNSUPPORTED** — only `≥ 1/25` is proved; `=` is Erdős 23 for that graph.  Same for the other "`max_x ψ = 1/25`" rows (Γ₈, Γ₁₀, Γ₁₁, Γ₁₃, Petersen) |
| 5 | (c) "item 3's bound reproduced independently, 53.8M weightings, 0 violations" | **half CONFIRMED** — I reproduce the counts and the 0 violations exactly with my own enumerator, but this is **not** item 3's claimed range (`q ≤ 15` on 13 graphs = 8.4·10¹⁰ weightings; e.g. Γ₂₆ was run at `q = 7`, not 15).  Verdict on item 3 itself: **UNSUPPORTED at the stated range** |
| 6 | (c) item 3's equality claim is **REFUTED** (6- and 7-atom equalities) | **over-strong / downgraded to CONFIRMED-with-clarification** — I classified all 264 + 36 (+ 2431 more that P4 missed on Γ₁₇): *every* one is a balanced C5 blow-up, i.e. a five-*class* configuration.  P4 also missed the Γ₁₇ `q = 10` equality set |
| 7 | (e) Fourier: coefficients right; decay, absolute convergence, "only n=3,5 positive", and the identity itself all wrong | **CONFIRMED** (all four), including the exact defect `(1/12)·(tie mass)` |
| 8 | (a) blow-up identity, (b) `And(k) ≅ Γ_{3k−1}`, (d) `m(b)` identities + pairing hazard, (f) `bound_k` valid and `A` = exact half-arc average | **CONFIRMED** (all re-derived and machine-checked independently) |
| 9 | recommendation 1: "any future certificate must use arcs of length **strictly between** 1/3 and 1/2" | **REFUTED by P4's own witnesses** — the *exactly*-1/2 family alone closes W8 (7/225), W9 (1/32), W10 (1/32) |
| 10 | (c) flag "the gap `ARCBOUND − ψ` matters" | **UNSUPPORTED** — `ARCBOUND = ψ` on all 12 witnesses and on 379 exact random circle measures; what P4 measured is `min_b m(b) − ψ`, a different object |
| 11 | surviving suggestion `R = min(half-arc, third-arc)` | **NOT REFUTED** — but P4's test is a tautology unless the families are read as *exact* lengths (see §9); under the exact reading I ran it over 53.8M weightings on 13 graphs (0 violations, tight exactly on C5 blow-ups) and 39 directed max searches (max = 1/25).  Still unproven |

---

## 1. The headline: item 7 — CONFIRMED REFUTED (`audit_P4_item7.py`, `audit_P4_core.py`)

Item 7 asserts: for every probability measure on the circle with `W ∈ (0.12, 0.2)`,
`2T < W − 1/25` and `4W² + Var_μ(g) < W − 1/25`, some `bound_k ≤ 1/25`.
Note first (my derivation, not P4's): the two hypotheses are *exactly* `A > 1/25` and
`bound_0 > 1/25`, since `A = W − 2T` and `bound_0 = W − ∫g²dμ = W − 4W² − Var(g)`.  And
`bound_k = Σ_b x_b g(b)^k m(b) / Σ_b x_b g(b)^k` is a convex combination of the `m(b)`, so
`bound_k ≥ min_{b ∈ supp} m(b)` for **every** `k ≥ 0` (indeed for every non-negative reweighting).
Hence any measure with `min_b m(b) > 1/25` satisfying both hypotheses kills item 7 outright.

My engine reproduces P4's table **digit for digit**:

| | `W` | `A = W−2T` | `bound_0` | `min_b m(b)` | `min_supp g` | `ARCBOUND` | `ψ` (all cuts) |
|---|---|---|---|---|---|---|---|
| W8 `(0,3,4,0,1,0,0,2,4,4,0,0,0,0,4,4,3,1,0,0)/30` | `14/75` | `403/9000` | `158/3375` | `2/45` | `1/3` | `7/225` | `7/225` |
| W9 `(0,0,5,5,5,0,0,0,0,5,5,2,0,0,0,3,5,5,0,0)/40` | `3/16` | `3/64` | `3/64` | `3/64` | `3/8` | `1/32` | `1/32` |
| W10 `(0,5,5,0,0,0,0,6,4,5,0,0,0,0,5,4,6,0,0,0)/40` | `3/16` | `73/1600` | `149/3200` | `7/160` | `7/20` | `1/32` | `1/32` |

All three satisfy `W ∈ (0.12,0.2)`, HYP1 and HYP2 exactly, and have `min_b m(b) > 1/25`.  Checks I
ran that P4 did not report: `m(b)` computed from the formula **and** as an explicit cut value agree
at every atom; `A` from `W − 2T` agrees with the direct double integral `∫∫_{d>1/3}(1/2−d)`;
`bound_0 = W − ∫g²dμ`; `bound_k` for `k = 0,1,2,3,5,10,50,200,1000` all `> 1/25`; and the minimum of
`m(b)` over **all** `b ∈ R/Z` (every window of ≤ 7 consecutive grid points, which is exactly the
family `{N(b)}` plus more) is still `2/45`, `3/64`, `7/160`.  `ψ ≤ 1/25` throughout, so Erdős 23 is
untouched; it is the certificate that fails.

**Two further falsifiers, found by my own search on smaller circles** (`audit_P4_rules.cpp`,
mode `j1`, verified exactly by `audit_P4_item7.py`):

* **Γ₁₄ = And(5)**, `(7,6,0,0,5,7,4,0,0,6,6,1,0,3)/45`: `W = 127/675`, `A = 202/4725 > 1/25`,
  `bound_0 = 281/6075 > 1/25`, `min_b m(b) = 86/2025 = 0.042469 > 1/25`, `min_supp g = 16/45 > 1/3`,
  `ψ = ARCBOUND = 62/2025`.
* **Γ₁₁ = And(4)**, `(0,8,5,0,4,7,2,0,8,8,3)/45`: `min_b m(b) = 82/2025 = 0.040494 > 1/25`,
  `A = 83/2025 > 1/25`, `ψ = 62/2025`.  (`min_supp g = 13/45 < 1/3` here.)

A 39-configuration sweep (`Γ_m`, `m = 11..30`, `q ∈ {30,45,60}`) finds item-7 falsifiers on
**Γ₁₁, Γ₁₄, Γ₁₇, Γ₂₀, Γ₂₃, Γ₂₆, Γ₂₉** — precisely the `m ≡ 2 (mod 3)` circles, i.e. the Andrásfai
graphs — and on none of the `m ≡ 0 (mod 3)` ones (`audit_P4_search_j1.log`).  The failure region is
not a needle; it covers the whole Andrásfai family.

## 2. What the falsifiers actually are — P4's framing REFUTED (`audit_P4_structure.py`)

Collapsing twins in the support-induced graph:

* **W9**: 9 atoms → **8 twin classes with equal weights 5/40**, 3-regular, and **isomorphic to Γ₈**,
  i.e. the **Wagner graph = And(3)**.  W9 *is the uniform measure on And(3)*, re-embedded in Γ₂₀.
* **W8**: 10 atoms → 8 classes, weights `(3,4,3,4,4,4,4,4)/30`, again **Γ₈**.
* **W10**: 8 atoms → 8 classes, weights `(5,5,6,4,5,5,4,6)/40`, again **Γ₈**.

So P4's "three independent witnesses … genuinely asymmetric … only directed max-min search finds
them" is wrong: there is **one** witness graph, the campaign's own recorded Wagner graph, in three
weightings, and the asymmetry lives only in the *embedding* into Γ₂₀.

The reason the embedding is needed is worth recording, because it is the real lesson:

```
   W, g, m(b), bound_k, psi, ARCBOUND   depend only on the GRAPH (cut invariants)
   T and A = W - 2T                     depend on the EMBEDDING (the distances)
```

`uniform Γ₈`: `W = 3/16`, `g = 3/8`, `m(b) = bound_k = 3/64 > 1/25` — the hierarchy already fails —
but `A = 1/32 ≤ 1/25`, so HYP1 fails and item 7 does not apply.  Re-embedding the same graph into
Γ₂₀ leaves every cut invariant unchanged and lowers `T/W` from `5/12` to `3/8`, which raises `A` to
`3/64 > 1/25`.  That is the only thing the search had to find.

**Closed form (mine, exact).**  For the uniform measure on a `k`-regular triangle-free graph on `N`
vertices, `m(b) = k(N−2k)/(2N²)` for every `b`, so every `bound_k` equals it.  For
`And(k) = Γ_{3k−1}`:

```
        m(b)  =  k(k−1) / (2(3k−1)²)   =   1/25 (k=2, C5),  3/64, 6/121, 5/98, 15/289, 21/400, …
```

— exactly `1/25` at `C5` (tight at the extremal, as it must be) and **strictly above 1/25 for every
`k ≥ 3`**.  The `bound_k` hierarchy therefore fails on *every* Andrásfai graph; no search is needed
to see it.  This is a stronger and much cleaner statement of P4's finding, and it also shows the
hierarchy could have been killed from the round-5 corpus alone (Γ₈ "Wagner" is in it).

## 3. (g)/(h) `max_x ψ(C7) = 4/225` — REFUTED (`audit_P4_gh.py`)

For an odd cycle `C_{2k+1}` the minimum over cuts is attained by a cut with a single monochromatic
edge, so `ψ(C,x) = min_i x_i x_{i+1}` exactly (verified on 200 random weightings per cycle, plus
brute force over all cuts).  By AM-GM
`min_i x_i x_{i+1} ≤ (Π_i x_i x_{i+1})^{1/n} = (Π x_i)^{2/n} ≤ 1/n²`, with equality iff `x` is
uniform.  Hence

```
        max_x ψ(C5) = 1/25   (this is why 1/25 is the extremal value at all)
        max_x ψ(C7) = 1/49 = 0.020408…   >   4/225 = 0.017778…      <-- P4.md's value is FALSE
```

The falsifier is the uniform weighting on C7 = Γ₇, which is *witness W6 of the mandatory regression
file* (`ARCBOUND = 1/49`).  P4's `4/225 = 16/900` is the best weighting of total `q = 30`
(`30/7 ∉ Z`), i.e. a grid artifact: `P4_gh_scope.py` prints "best psi found" and the report drops the
qualifier.  Consequently P4's "attained at min support degree `4/15`" is also wrong (the true
maximiser is uniform, min degree `2/7`).  P4's *qualitative* point survives — `2/7 < 1/3`, so the
`δ > 1/3` structure theorem still cannot see C7 — but the number and the maximiser are wrong, and
the same script is the sole source for verdict 4 below.

## 4. (g) `max_x ψ(Grötzsch) = 1/25` — UNSUPPORTED

`≥ 1/25` is provable and I verified it: the Grötzsch graph (11 vertices, 20 edges, triangle-free)
has an induced C5, and `ψ` restricted to a support whose induced graph is exactly C5 equals
`ψ(C5, ·)`, whose max is `1/25` by §3.  The `=` direction is an *upper* bound on a max-min over the
simplex — i.e. Erdős 23 for the Grötzsch blow-ups — and nothing in P4 (or in `P4_gh_scope.py`, which
runs `max_psi(..., q=40, tries=25)`, a randomised search) provides it.  The same applies to every
other "`max_x ψ = 1/25`" entry in P4's table (Γ₈, Γ₁₀, Γ₁₁, Γ₁₃, Petersen).  "The Vega branch is
tight" is therefore a conjecture-strength statement, not a verified one — although it is very likely
true and the *direction* P4 uses it in (the branch is not a formality) is unaffected.

## 5. (c) the exhaustive re-verification — reproduced, but not at item 3's range
(`audit_P4_exhaust.cpp`, `audit_P4_xcheck.py`, `audit_P4_exhaust.log`)

My own integer enumerator (mono via `W − Σ_{u∈S} w_u g_u + 2·inside(S)`, `O(1)` incremental arc
sweep, cross-validated against the slow exact Python enumerator on 5 `(m,q)` pairs — identical
weighting counts, violation counts and equality counts) reproduces P4's battery exactly:

```
  Gamma_5  q=20 10626    Gamma_7  q=20 230230   Gamma_8  q=16 245157   Gamma_10 q=16 2042975
  Gamma_11 q=15 3268760  Gamma_13 q=13 5200300  Gamma_14 q=12 5200300  Gamma_16 q=11 7726160
  Gamma_17 q=10 5311735  Gamma_18 q=10 8436285  Gamma_20 q=9  6906900  Gamma_23 q=8  5852925
  Gamma_26 q=7  3365856          TOTAL 53 798 209 weightings, 0 violations of 25·min ≤ q²
```

Zero weights **are** included (the counts are exactly `C(q+m−1, m−1)`), so the protocol's
"enumeration excluding zero weights" hazard does not apply.

**But** item 3's claim is "*all* integer weightings with `q ≤ 15` on thirteen circle graphs".  That
range is `Σ_{q≤15} C(q+m−1,m−1) = C(15+m,m)` summed over the thirteen graphs =
**84 181 598 053** weightings, 1565× more than what was run, and for the large graphs the actual `q`
is far below 15 (Γ₂₆ at `q = 7`, Γ₂₃ at `q = 8`, Γ₂₀ at `q = 9`).  P4 lists its `(m,q)` pairs
honestly but then labels item 3 "CONFIRMED"; the correct label is **item 3's stated range is not
verified** (by P4 or by me), only a much smaller one.

## 6. (c) the equality claim — P4's "REFUTED" is over-strong (`audit_P4_equality.py`)

I dumped and classified every equality configuration:

```
  Gamma_11 q=15 : 264  equalities, atoms {5:33, 6:132, 7:99}
  Gamma_18 q=10 :  36  equalities, atoms {5:18, 6:18}
  Gamma_17 q=10 : 2431 equalities, atoms {5:238, 6:952, 7:952, 8:272, 9:17}   <-- P4 missed this one
```

Every single one of them (2731 configurations) collapses, under the twin relation, to **C5 with
equal class weights** — I verified the quotient is 2-regular, connected, on 5 classes, with all
class weights equal.  So the substantive content of item 3's equality claim ("equality exactly at
the C5 configuration") is **correct**; what is wrong is only the word "atom" (classes may be spread
over several positions).  P4's own classification agrees with mine — but its verdict label
("equality claim is REFUTED") over-states a clarification, and its enumeration of where the
equalities occur is incomplete.

## 7. (e) the Fourier section — CONFIRMED (`audit_P4_fourier.py`)

* `ψ̂(n)` re-derived symbolically with sympy from `2∫_{1/3}^{1/2}(1/2−t)cos(2πnt)dt`:
  `(−πn·sin(2πn/3) + 3cos(2πn/3) − 3cos(πn))/(6π²n²)`, identical to the brief's formula for
  `n = 1..12`; `ψ̂(0) = 1/36`; numeric integration agrees to 8 digits.
* Decay: `n·ψ̂(n) = −0.046704, +0.045792, −0.045936, −0.045945` at `n = 100, 500, 3001, 10⁵`.
  `Θ(1/n)`, not `O(1/n²)` — **P4 right**.
* Positivity: `ψ̂(n) > 0` exactly for `n ≡ 2, 3, 5 (mod 6)`; one-sided `Σ|ψ̂|` = 0.2204, 0.2909,
  0.3827, 0.4532 at `N = 10³…2·10⁶` ≈ `0.0306 ln N`; the positive part diverges — **P4 right**.
  (Bookkeeping nit: P4's "0.4532" is one-sided while its "0.3688" is two-sided `= 2 × 0.1844`.)
* **The tie defect** — reproduced exactly on 7 measures:
  `Σψ̂(n)|μ̂(n)|² − A = (1/12)·(μ⊗μ){d = 1/3}`.  uniform Γ₁₈: `A = 1/54`, series `1/36`, tie mass
  `1/9`, defect `1/108` ✓;  uniform Γ₉: `1/81` vs `5/162`, tie mass `2/9` ✓;  `δ₀+δ_{1/3}+δ_{2/3}`:
  `0` vs `1/18` ✓;  two atoms at `1/3`: `0` vs `1/24` ✓;  tie-free cases (C5, W9): defect `0` ✓.
  So item 6's identity is indeed false with ties, and only the inequality `A ≤ series` survives.
* Item 6's "a purely 3-fold measure has `g` constant and no adjacent pairs at all": P4's correction
  `g(x) = 1/3 − μ({x})` verified on four 3-fold measures (`W = 0, 1/12, 5/36, 7/60`).  **P4 right.**

## 8. (a) (b) (d) (f) — CONFIRMED independently
(`audit_P4_ab.py`, `audit_P4_item7.py`, `audit_P4_misc.py`)

* **(a)** `bip(H[n]) = N²ψ(H, n/N)` on 60 random triangle-free `H` (3–6 vertices, random blob sizes,
  brute force over all `2^{N−1}` cuts of the blow-up): 0 mismatches; `C5[q]`: `bip = q²` for
  `q = 1,2,3`.  Strict adjacency `d > 1/3` is forced (`0, 1/3, 2/3` would be a triangle).
* **(b)** `k·S_And = S_Γ` and `v ↦ k·v` is an isomorphism `And(k) → Γ_{3k−1}`: verified as a full
  adjacency check for `k = 2..9`, both `k`-regular and triangle-free.  `δ(Γ_m) > m/3` iff
  `m ≡ 2 (mod 3)`: verified `m = 5..26`.  Prior-art arithmetic `bip(And_k) = ⌊k²/4⌋`: verified by
  brute-force max-cut for `k = 2..7` (`1,2,4,6,9,12`).
* **(d)** `m(b)` = value of the cut `N(b)` (three ways) and `∫m dμ = W − ∫g²dμ`: exact on every test
  measure.  The pairing hazard is real and reproduces exactly: on Γ₁₁, support `{0,2,4,7,9}`,
  weights `(1,2,3,2,1)/9`, the index-arc differs from `N(b)` at 4 of the 5 atoms
  (`m(0) = 2/81` vs `1/27`).
* **(f)** `bound_k ≥ min_b m(b) ≥ ARCBOUND` for all `k` (this is what kills item 7), and
  `A` **equals** the exact average of `mono([a, a+1/2))` over uniform `a` — verified by exact
  integration (2M cells, rational midpoints) on 10 measures including all three witnesses:
  `A = half-arc average` as rationals, every time.

## 9. The surviving suggestion — not refuted, but P4's test needs restating
(`audit_P4_rules.cpp`, `audit_P4_rules_check.py`, `audit_P4_rules_exhaust.log`, `audit_P4_search_ht.log`)

**Trap I hit first and had to fix (P4 may have hit it too).**  The family of arc cuts is closed
under complementation — a window of `l` points and its complement give the *same* bipartition — so
"min over all windows of size ≤ M/2" is literally `ARCBOUND`.  Testing that version of
`R = min(half, third)` proves nothing.  Under the *exact-length* reading (`HALF` = window sizes
realisable by `[a, a+1/2)`; `THIRD` = sizes realisable by an arc of length exactly `1/3`, including
the closed arc, whose endpoints at distance exactly `1/3` are still non-adjacent) the rule is a
genuine restriction, and:

* it passes the nine recorded witnesses and W8/W9/W10 (exact Python, and my C++ agrees on all 12);
* it passes the **whole 53 798 209-weighting battery on all 13 circle graphs, 0 violations**, with
  equality exactly on the 264/2431/36 C5-blow-up configurations — i.e. it is tight precisely where
  `ARCBOUND` is tight;
* 39 directed max searches (`m = 11..30`, `q ∈ {30,45,60}`, 40 restarts each) never exceed `1/25`;
  the maximum found is exactly `1/25` (Γ₁₁, `q = 30`).

So I could not break it.  It remains an unproved `min` of two families, as P4 says.

**P4's recommendation 1 is refuted by P4's own data.**  "Any future certificate must be able to use
arcs of length strictly between 1/3 and 1/2" — the *exactly*-1/2 family alone gives `7/225`, `1/32`,
`1/32` on W8/W9/W10, all `≤ 1/25`.  What failed on those witnesses was the half-arc **average** `A`,
not the half-arc **minimum**.  The correct lesson is: replace the averaged bounds by minima, which
is exactly the surviving suggestion.

## 10. Other flags

* **`ARCBOUND` vs `ψ`.**  P4 correctly notes `sup ARCBOUND ≤ 1/25` is formally stronger than
  Erdős 23 on circle graphs.  But its supporting sentence ("the gap `ARCBOUND − ψ` matters: on W8/W9
  the neighbourhood family overshoots `ψ` by 43%/50%") conflates two families: the *neighbourhood*
  family is not the *arc* family.  `ARCBOUND = ψ` exactly on all 12 witnesses and on **379 exact
  random circle measures** (`audit_P4_arcgap.py`, 0 gaps).  No instance of `ARCBOUND > ψ` is known,
  so the strengthening is formally real but empirically vacuous so far.
* **Round-5 data error (not P4's).**  The annotation of witness W5 in
  `round5/claude_witness_regression.py` says "`W = 2/9`"; under the strict convention `d > 1/3` used
  by that file's own `gamma()` the true value is `W = 1/9` (positions 0 and 4 of Γ₁₂ are at distance
  exactly `1/3` and are **not** adjacent).  The witness itself is fine; the annotation is wrong.
* **Regression status of the refuted certificate.**  I independently confirm P4's claim that
  `min(A, min_k bound_k)` passes all nine recorded witnesses (values `0.0204, 0.0204, 0.0204, 0.0400,
  0.0185, 0.0300, 0, 0.0204, 0.0100`) and fails only on W8/W9/W10.  W8/W9/W10 (and my Γ₁₄, Γ₁₁
  witnesses) should be added to the regression file.
* **No circularity** was found in P4's own reasoning; its section (h) flags on the campaign's chain
  (the "WLOG δ > 1/3" gap, item 3 as a strengthening, the Heinig prior art) are consistent with what
  I could check, and the Heinig numeric claim `bip(And_k) = ⌊k²/4⌋` checks out for `k ≤ 7`.

---

## Files (all in `E:\Projects\ErdosProblems\problems\23\round6\`)

| file | what it does |
|---|---|
| `audit_P4_core.py` | my independent exact engine: `Γ_m`, `W`, `T`, `A`, `g`, `m(b)`, `bound_k`, `Var(g)`, `ARCBOUND`, `ψ` (brute force), blow-ups, `bip` |
| `audit_P4_item7.py` | the headline: exact profile + both hypotheses + whole hierarchy + circle-wide slide, for any `Γ_m` weighting (`python audit_P4_item7.py 20 0,0,5,...`) |
| `audit_P4_structure.py` | twin collapse of W8/W9/W10 → Wagner Γ₈; embedding-invariance analysis; closed form `m = k(k−1)/(2(3k−1)²)` |
| `audit_P4_gh.py` | odd-cycle maxima (AM-GM + brute force) refuting `4/225`; Grötzsch lower bound |
| `audit_P4_ab.py` | blow-up identity; `And(k) ≅ Γ_{3k−1}`; `bip(And_k) = ⌊k²/4⌋` |
| `audit_P4_fourier.py` | symbolic `ψ̂`, decay, divergence, exact tie defect on 7 measures |
| `audit_P4_exhaust.cpp/.exe` | independent integer exhaustive checker (`25·min_arc ≤ q²`), 8 threads |
| `audit_P4_xcheck.py` | cross-validation of the C++ enumerator against the slow exact Python one |
| `audit_P4_equality.py` | classification of all equality configurations (twin collapse → C5) |
| `audit_P4_rules.cpp/.exe` | exact-length half/third families: `exhaust`, `search`, `eval`, plus the `j1` objective `min(A, min_b m(b))` |
| `audit_P4_rules_check.py` | exact Python evaluation of `R` on the 12 witnesses + C++ cross-check |
| `audit_P4_regression.py` | mandatory nine-witness regression of `A`, `bound_k`, `cert7`, `R`, `ARCBOUND`, `ψ` |
| `audit_P4_misc.py` | `A` = exact half-arc average; pairing hazard; `δ(Γ_m) > m/3`; 3-fold `g`; recommendation-1 test |
| `audit_P4_arcgap.py` | is `ARCBOUND > ψ` ever? (379 exact random measures: no) |
| `audit_P4_exhaust.log`, `audit_P4_rules_exhaust.log`, `audit_P4_search_j1.log`, `audit_P4_search_ht.log`, `audit_P4_eq_*.txt` | outputs |

Reproduce the headline and its structure in three lines:

```
python audit_P4_item7.py                 # W8/W9/W10 exact, both hypotheses, whole hierarchy
python audit_P4_structure.py             # they are all the Wagner graph And(3) re-embedded
python audit_P4_item7.py 14 7,6,0,0,5,7,4,0,0,6,6,1,0,3    # my own falsifier on And(5), delta>1/3
```

## What the campaign should take from this audit

1. **Item 7 is dead, and more decisively than P4 says.**  The right statement is not "three
   asymmetric witnesses on Γ₂₀" but: *for every `k ≥ 3` the uniform measure on `And(k)` has
   `bound_j ≡ k(k−1)/(2(3k−1)²) > 1/25` for all `j`* — the hierarchy is capped below by
   `min_b m(b)`, which exceeds `1/25` on the entire Andrásfai family, with equality exactly at C5.
   Any re-embedding that also lowers `T/W` below `(W − 1/25)/(2W)` kills item 7 as stated; Γ₁₁, Γ₁₄,
   Γ₁₇, Γ₂₀, Γ₂₃, Γ₂₆, Γ₂₉ all admit one.
2. **Add W8/W9/W10 *and* the uniform And(k) measures to the regression file** — the latter are the
   canonical form of the failure and require no search at all.
3. **Fix the two wrong numbers in P4 §(g)/(h)** (`max_x ψ(C7) = 1/49`, min degree `2/7`) and demote
   every "`max_x ψ = 1/25`" in that table to "best found", since the upper bound is the conjecture.
4. **Do not record item 3 as verified at `q ≤ 15`**: what exists (P4's and mine) is `q = 7..20`
   depending on the graph, 5.4·10⁷ of the 8.4·10¹⁰ weightings.
5. **The surviving object is `min(half-arc minimum, third-arc minimum)`**, not "arcs strictly between
   1/3 and 1/2".  It is tight exactly on the C5 blow-ups and survived every test I could run.
