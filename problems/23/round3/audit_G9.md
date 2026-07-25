# AUDIT of G9 — adversarial re-verification

Target: `round3/G9.md` and `round3/G9_*`.
Method: every central computation re-implemented from scratch in `round3/audit_G9_*`
(own graph6 decoder, own exhaustive max-cut by side-mask popcount, own blow-up bip by
FULL cut enumeration of the 5-vertex pattern — the "odd subset of C5" shortcut used by the
target is never assumed, it is *checked*). Target scripts were executed only to compare
outputs. All arithmetic is exact `int` / `Fraction` / `long long`.

Bottom line: **the two positive theorems (A, B) and all of the W_t arithmetic survive intact;
two of the four obstruction theorems are REFUTED at the level at which the report states them,
by explicit exact falsifiers inside the report's own witness family.** The report proves
statements about the *greedy re-insertion cost* `cost(S)` and then states them as statements
about the *deletion mechanism* `bip(G) − bip(G−S)`. On `W_t` the two differ by a factor > 2,
and the mechanism fires where the report says it is defeated.

---

## 1. REFUTED — Theorem E: "arbitrary-set deletion is defeated by the same witness"

Report, §3b: *"Theorem E (arbitrary-set deletion is defeated by the same witness). For every
nonempty S ⊆ V(W_t), cost(S) > (N² − (N−s)²)/25 … Hence the arbitrary-set mechanism also has
ceiling 4/25."* Final summary: *"Theorem E (arbitrary-set deletion also defeated)."*

The set-deletion induction step is
`bip(G) = bip(G−S) + drop(S) ≤ (N−s)²/25 + drop(S)`, so it **fires iff
`drop(S) := bip(G) − bip(G−S) ≤ budget(s) := (2Ns − s²)/25`**. `cost(S)` is only an upper
bound for `drop(S)`.

**Falsifier (exact, W_1 = C5[7,2,7,7,2], N = 25, triangle-free, maximal, δ = 4 = 4N/25):**

| S | \|S\| | bip(W_1) | bip(W_1−S) | drop | budget | fires? |
|---|---|---|---|---|---|---|
| 5 vertices from each of P_0,P_2,P_3 | 15 | 14 | 4 (`= C5[2]`) | **10** | 21 | **YES**, margin −11 |
| `P_2 ∪ P_3` | 14 | 14 | 0 | **14** | 504/25 = 20.16 | **YES** |
| `P_0 ∪ P_2` (independent) | 14 | 14 | 0 | **14** | 504/25 | **YES** |

`bip(W_1) = 14`, `bip(W_1 − P_2 − P_3) = 0`, `bip(W_1 − P_0 − P_2) = 0`,
`bip(W_1 − 5·3) = 4` were each obtained twice: by exhaustive enumeration of all `2^(n−1)`
cuts of the explicit graph (`audit_G9_exh.exe W1`, `2^24` cuts for the full graph) and by
full cut enumeration of the weighted 5-cycle (`audit_G9_witness.py`).

Exhaustively over **all** part-wise `S` (all vertices of a part are twins, so this is all `S`
up to automorphism): the true-drop mechanism fires on **4177 of the 4607** nonempty
`S ⊆ V(W_1)` (90.7 %), **78953 of 84374** for `W_2`, **489999 of 521751** for `W_3`.
Most negative margin `drop − budget = −11 t²` at `S = (5t,0,5t,5t,0)`, i.e. exactly the
deletion that reduces `W_t` to the balanced blow-up `C5[2t]`.

So `W_t` is **not** an obstruction to set deletion; it is an obstruction only to the greedy
re-insertion *bound*, which on this graph overestimates the truth by a factor
`32/14 ≈ 2.3` at `S = P_2 ∪ P_3` and by `≈ 3` at `S = P_0 ∪ P_2` (greedy `Σ⌊d/2⌋ = 42`
vs. true drop `14`). Consequently §3d's derived "absolute limit `δ ≲ 0.33N`" is also a
statement about the greedy bound only, not about set deletion.

The *literal* inequality of Theorem E — `cost(S) > budget(s)` for every nonempty `S`,
`t = 1,2,3` — is **CONFIRMED** by my own part-wise DP (0 violations), as is the auxiliary
claim that the crude bound `(E(S)−s)/2` survives only on `S ⊆ P_0` (7 survivors at `t=1`,
12 at `t=2,3`, all inside `P_0`).

Sanity check that the mechanism-level framing is the right one: on the genuine extremal
family `C5[n]` the true-drop mechanism fires on **0** sets strictly and on exactly `n` sets
with equality (`s_i ≡ k`, `drop = budget = 2nk − k²`). `C5[n]`, not `W_t`, is the real
obstruction to set deletion.

## 2. REFUTED — Theorem D's stated consequence

Report, §3b: *"This settles the first mechanism suggested in the assignment: **deleting an
independent set can never beat the single-vertex version**, for any graph, at any N."*

**Falsifier:** `G = W_1`, `A = P_0 ∪ P_2`, `|A| = 14`. `A` is independent (verified on the
explicit 25-vertex adjacency matrix). The single-vertex mechanism does **not** fire on `W_1`
(`min_v drop = 2 > 49/25 = (2N−1)/25`); the independent-set deletion **does**
(`drop = 14 − 0 = 14 ≤ 504/25 = 20.16`). Same for `A = P_0 ∪ P_3`, and for every `t`.

The *literal* inequality of Theorem D (`Σ_{u∈A}⌊d(u)/2⌋ > a(2N−1)/25 ≥ (2Na−a²)/25`, from
`a² ≥ a`) is **CONFIRMED**; it is a statement about `Σ⌊d/2⌋`, which is the greedy cost, not
the drop. Here `Σ_{u∈A}⌊d(u)/2⌋ = 7·2 + 7·4 = 42` against a true drop of `14`.

## 3. UNSUPPORTED / OVERSTATED — Theorem C.2 and the blocking lemma

Verbatim blocking lemma from the report:

> To improve the constant `4/25` one must exhibit a function `h` with
> `bip(G) − bip(G−v) ≤ h(N, d(v))` for all triangle-free `G` and `h(N, d) ≤ (2N−1)/25` for all
> `d ≤ cN` with some `c > 4/25`. This is false for every `h`: `W_t = C5[7t,2t,7t,7t,2t]` is
> maximal triangle-free on `N = 25t` vertices with a vertex `v` of degree `4t = 4N/25` and
> `bip(W_t) − bip(W_t − v) = 2t = ⌊d(v)/2⌋`.

The second sentence is **CONFIRMED** exactly (see §5 below). The first sentence is a scope
claim and is **false as written** on two counts:

1. "one must exhibit a function `h`" — only if one insists on single-vertex deletion. Nothing
   in the report bears on any other mechanism, and §1 of this audit shows set deletion is not
   blocked by this witness.
2. `h` need only be valid on graphs that can be minimal counterexamples, i.e. on triangle-free
   `G` with `bip(G) > N²/25`. **`W_t` is not such a graph**: `bip(W_t) = 14t² = 0.0224 N² <
   N²/25 = 0.04 N²`. The counterexample hypothesis is free in the induction, so the witness
   does not constrain the bound that an actual proof would need.

Theorem C.2 as stated — *"no matter which vertex is deleted and no matter what auxiliary
potential is added"* — is proved only for (a) `h(N, d(v))` valid on **all** triangle-free `G`
and (b) additive potentials `g(|H|)` depending on the vertex count alone. Graph-dependent
potentials, and any bound reading `bip(G)`, `m`, `Δ` or local structure, are untouched. The
report concedes exactly this in §5, which therefore contradicts its own Theorem C.2 statement.
Verdict: the *proved* content is "the single-vertex bound `⌊d/2⌋` is attained at `d/N = 4/25`",
which is genuine and new-to-this-ledger; the *stated* content overreaches.

"no vertex choice helps" **is** correct on `W_t`: `min_v drop = 2t > (2N−1)/25` (all five
per-part drops verified: `2t, 7t, 2t, 2t, 7t`).

## 4. REFUTED — §3d "W_t's densest induced subgraph is P_2 ∪ P_3, e/s = 3.5t = 0.14N"

Exhaustive part-wise maximisation of `e(S)/|S|` (`audit_G9_density.py`):

| t | max `e(S)/|S|` | argmax | as a fraction of N | claimed |
|---|---|---|---|---|
| 1 | 77/18 = 4.2778 | `(0,2,7,7,2)` = `P_1∪P_2∪P_3∪P_4` | 0.1711 N | 3.5 = 0.14 N |
| 2 | 77/9 = 8.5556 | `(0,4,14,14,4)` | 0.1711 N | 7 = 0.14 N |
| 3 | 77/6 = 12.8333 | `(0,6,21,21,6)` | 0.1711 N | 10.5 = 0.14 N |

Even `S = V(W_t)` gives `m/N = 4.2t = 0.168 N > 3.5t`. The claim is false; it is a descriptive
error and does not affect the (independently confirmed) exhaustive greedy-cost scan.

## 5. CONFIRMED — Theorem A and its corollaries

`bip(G) ≤ m − max_v vol(N(v)) ≤ m − 4m²/N²` for triangle-free `G`.

Proof re-checked line by line and correct: `N(v)` is independent **because** `G` is
triangle-free, so the cut `(N(v), V∖N(v))` is monochromatic exactly on `E(G[V∖N(v)])` and
`e(V∖N(v)) = m − vol(N(v))` (no edge from `v` leaves `N(v)`, so this also equals `e(B_v)`);
`Σ_v vol(N(v)) = Σ_w d(w)²` by double counting; `max ≥ average ≥ (2m)²/N²` by Cauchy–Schwarz.
Valid for disconnected `G`, isolated vertices, every `N`.

Independent verification (`audit_G9_exh.exe A`, own decoder + own exhaustive max-cut):

```
triangle-free graphs checked = 102405 (n=5:6, 6:19, 7:59, 8:267, 9:1380, 10:9832, 11:90842)
ThmA strong failures = 0 ; ThmA Cauchy-Schwarz failures = 0 ; strong form TIGHT on 33891
```

Both counts (102405 graphs, 33891 tight) reproduce the report exactly. Additional edge cases
all pass: `C5 + k` isolated vertices, `C5+C5`, `C5+C7`, `C5+C4`, `C7+C7` (disconnected, odd
`N`, `N ∤ 5`), unbalanced and zero-part blow-ups, and the Clebsch graph
(`N=16, m=40, bip = 8` — reproduces accepted fact 8, an independent calibration of my
max-cut routine).

Corollaries verified as exact rational algebra: `μ − 4μ² ≤ 1/25 ⟺ 4μ² − μ + 1/25 ≥ 0 ⟺
μ ≤ 1/20 or μ ≥ 1/5`; sharp at `μ = 1/5` (`C5[n]`, `N²/5 − 4N²/25 = N²/25 = bip`) and
`μ = 1/4` (`K_{N/2,N/2}`, bound `0 = bip`).

Caveats (not errors):
* `A2` (`m ≤ 2N²/25 ⟹ bip ≤ N²/25`) is just `maxcut ≥ m/2`, textbook; and for a *minimal*
  counterexample the lower end was already implied by accepted fact 7
  (`δ > (4N−2)/25 ⟹ m > 2N²/25 − N/25`). The genuinely new exclusion is the **upper** end
  `m < N²/5`.
* `A4` (`δ ≥ 2N/5 ⟹ conjecture`) is strictly weaker than Häggkvist (`3N/8`), as the report
  itself says. So Theorem A moves nothing on the min-degree axis.
* Novelty against the literature could not be checked offline. The argument is folklore-grade
  elementary; treat "new here" as "new to this ledger", not "new to the literature".

## 6. CONFIRMED — Theorem B (`O(1)` sharpening)

`δ ≥ L(N) := 2(⌊N²/25⌋ + 1 − ⌊(N−1)²/25⌋)` for a minimal counterexample. Proof correct
(integrality on both sides; `⌊d/2⌋ ≥ k ⟹ d ≥ 2k`). Independent recomputation over
`2 ≤ N ≤ 100000`:

* `L(N) − (⌊(4N−2)/25⌋+1)` distribution = `{0: 12000, 1: 39999, 2: 36000, 3: 12000}`; never negative.
* `L(25t) = 4t + 2 = 4N/25 + 2` for `t = 1..8`.
* `min/max of 25·L(N) − 4N = 6 / 90`, i.e. `L(N) = 4N/25 + O(1)` — **the coefficient `4/25` is
  unchanged**, exactly as the report states.

## 7. CONFIRMED — the witness family `W_t`

`W_t = C5[7t,2t,7t,7t,2t]`, verified independently for `t = 1..8`:
`N = 25t`, `m = 105t²`, degrees `(4t,14t,9t,9t,14t)`, `δ = 4t` with `25δ = 4N` exactly,
`bip = 14t²`, per-part drops `(2t,7t,2t,2t,7t)`, `min_v drop = 2t = ⌊δ/2⌋ > (2N−1)/25 =
2t − 1/25`, and `25·bip = 350t² < 625t² = N²` (so `W_t` is **not** a counterexample).
`W_1` verified triangle-free **and maximal** triangle-free on the explicit 25-vertex matrix.

Second, fully independent confirmation for `t = 1` by exhaustive enumeration of all `2^24`
cuts (`audit_G9_exh.exe W1`), which also agrees with the target's own binary:

```
W1: N=25 m=105 delta=4 triangle_free=1
W1: bip = 14   [exhaustive over 2^24 cuts]
W1 - (one vertex of part 0, deg 4): bip = 12     (drop 2)
W1 - (one vertex of part 1, deg 14): bip = 7     (drop 7)
W1 - (one vertex of part 2, deg 9): bip = 12     (drop 2)
```

The C5-blow-up identity `bip(C5[a]) = min_i a_i a_{i+1}` was not assumed: my blow-up routine
enumerates all `2^4` cuts of the pattern and the two agree on every vector tested, and agrees
with the explicit-graph brute force.

## 8. CONFIRMED — §3c "ceiling exactly 4/25", with the zero-weight gap closed

General half: any graph defeating the single-vertex mechanism has `⌊δ/2⌋ > (2N−1)/25`, hence
`δ > (4N−2)/25`; for `N ≡ 0 (mod 25)` integrality forces `δ ≥ 4N/25`, so `4/25` is the exact
infimum. Correct and unconditional.

Finite half: the target's `G9_ceiling_search.py` loops `a_i ∈ [1, …]`, i.e. it **silently
excludes zero part sizes** (an explicitly listed failure mode). I re-ran the search with
zeros included: **0** blow-ups with a zero part defeat the mechanism (they are `P_4`
blow-ups, hence bipartite, `bip = 0`, all drops `0`), the minimum ratio is `4/25`, attained by
exactly the 10 vectors `(2,7,2,7,7)`, `(2,7,7,2,7)`, `(7,2,7,2,7)`, `(7,2,7,7,2)`,
`(7,7,2,7,2)` and their doubles at `N = 50`. Conclusion unaffected — the exclusion is harmless
and is now verified rather than assumed.

## 9. CONFIRMED — §4 assignment-mandated checks

* `bip(C5[n]) = n²` for `n = 1..8`; single-vertex drop `= n = ⌊d/2⌋` against budget
  `(10n−1)/25`; failure factor `25n/(10n−1) → 5/2`.
* `N[v]`-peeling: `C5[n] − N[v] = C5[n−1,0,n,n,0]`, `bip = 0`, drop `n²` against budget
  `(16n²+6n−1)/25`; fails for every `n = 1..8` (checked exactly).
* Extremal table, every tuple reproduced with my own decoder + exhaustive max-cut:

| graph6 | N | m | bip | δ | min drop | maximal tf? | Thm A |
|---|---|---|---|---|---|---|---|
| `K?ABBBwerwBw` | 12 | 25 | 5 | 3 | 1 | yes | tight `5 = 25−20` |
| `K?BD@g]Qvo^?` | 12 | 25 | 5 | 4 | 1 | yes | tight `5 = 25−20` |
| `L??ED@_~?~^_Fw` | 13 | 30 | 6 | 4 | 2 | **no** | tight `6 = 30−24` |
| `M?AE@bH{AYN_LgBs?` | 14 | 32 | 7 | 4 | 1 | yes | slack `7 ≤ 32−23 = 9` |

  `bip = 5, 6, 7` matches accepted `a(12), a(13), a(14)`. Two nits: the third graph is not
  maximal triangle-free (the report does not claim it is, but accepted fact 6 restricts a
  counterexample to that class); and no script on disk *produces* these four graphs — only
  checks them — so their extremality/provenance is not reproducible from the deliverables.
* Drop scan `B(n,δ) = max{min_v drop : |G| = n, δ(G) = δ}` reproduced by my own scan over
  `geng -t -c`:

| n | δ=1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 7 | 0 | 1 | 0 | — | — |
| 8 | 0 | 1 | 1 | 0 | — |
| 9 | 0 | 1 | 1 | 0 | — |
| 10 | 0 | 1 | 1 | 2 | 0 |
| 11 | 0 | 1 | 1 | 2 | 0 |

  i.e. `B(n,δ) = ⌊δ/2⌋` for `δ ≤ ⌊n/2⌋−1` and `0` for `δ ≥ ⌊n/2⌋`, as claimed; and at `n = 11`
  the maximal-triangle-free witnesses are the same three strings the report names:
  `J??FFB_~?~?` (δ=2), `J??FF?^Fvw?` (δ=3), `` J?bFF`wN?{? `` (δ=4). Note the `B = 0` half is
  not a discovery: for `7 ≤ n ≤ 11` and `δ ≥ ⌊n/2⌋` one has `δ > 2n/5`, so
  Andrásfai–Erdős–Sós makes those graphs bipartite and `bip = 0`.

## 10. Mandated failure-mode checklist

| failure mode | finding |
|---|---|
| floating point on an acceptance path | **none**. Every comparison in `G9_*` uses `Fraction` / `int` / `long long`; `float()` appears only inside print formatting (`G9_witness.py` records, `G9_ceiling_search.py`, `G9_sharp_constant.py`). |
| max cut confused with greedy/local cut | **none**. All `bip` values come from exhaustive enumeration of all `2^(n−1)` cuts (or all `2^4` cuts of the C5 pattern). Independently reproduced. |
| ψ below 1/25 reported as a maximum on an odd-girth-5 graph | **N/A** — G9 never computes ψ. |
| integer-weight enumeration excluding zero weights | **present** in `G9_ceiling_search.py` (parts start at 1). **Harmless**, verified by re-running with zeros (§8). |
| triangle-freeness assumed but unused / used where false | used exactly once and correctly (`N(v)` independent, Theorem A). Inequality (I) correctly flagged as not needing it. `W_t` verified triangle-free. |
| N odd, `N ∤ 5`, disconnected, isolated vertices, unbalanced blow-ups | Theorems A and B are proved for all `N`; verified on explicit disconnected / isolated / odd-`N` / zero-part instances (§5). The censuses are `-c` (connected) only, but that restricts the *verification*, not the proofs. |
| constant weakened to `1/25 + ε`, hidden "N large" | **none**. Theorem C's "`t` large enough that `4t ≤ cN`" is vacuous: `4t ≤ 25ct ⟺ c ≥ 4/25`, so every `t ≥ 1` works. All statements are exact at every `N`. |
| circularity (a step of strength ≥ the conjecture) | **none**. A, D are unconditional; B and C are correctly stated as conditional on the conjecture at `N−1`, which is the standard minimal-counterexample setup, not an assumption of the conjecture itself. |
| finite verification presented as a general argument | **none of substance**. §3c is finite but is correctly paired with the general `δ > (4N−2)/25` bound; §1 and §4 census claims are correctly scoped to `n ≤ 11`. |
| quoted literature whose hypotheses do not match | Mantel (`e(S) ≤ s²/4`) and Häggkvist (`δ > 3n/8 ⟹ hom to C5`) are used correctly and only for comparison; `3/8 < 2/5`, so "weaker than Häggkvist" is right. |
| counterexample to the conjecture claimed | **none claimed**, and none present: `25·bip(W_t) = 350t² < 625t² = N²`. |
| rounding slip | `bip/N² ≤ 0.89·(1/25)` in §5: for `N = 14` it is `7/196 ÷ (1/25) = 25/28 = 0.8929 > 0.89`. Cosmetic. |

## 11. Net effect on the open problem

* Min-degree axis: **unchanged**. Accepted fact 7 already is the `4/25` statement; Theorem B
  moves it by an additive `O(1)` (`≤ 3`, and `+2` at `N ≡ 0 mod 25`); Theorem A's min-degree
  corollary `2N/5` is weaker than Häggkvist's `3N/8`. The open band `0.16N < δ ≤ 0.375N`
  is not shrunk.
* Edge-density axis: **new exclusion** `m < N²/5` for any counterexample (Corollary A1),
  unconditional, exact, tight at `C5[n]`. This is the one deliverable of the report that
  changes the state of the problem, and it is correct.
* Obstruction: real but narrow. Proved: no bound of the form `h(N, d(v))` valid on all
  triangle-free graphs, and no `|H|`-only potential, can push the single-vertex deletion
  induction past `4/25`. Not proved and stated anyway: anything about set deletion,
  independent-set deletion, or potentials that see the graph.

## Files written by this audit

* `audit_G9_core.py` — independent graph6 decoder, exhaustive max-cut/bip, blow-up builder,
  blow-up bip by full cut enumeration, triangle-free/maximality tests.
* `audit_G9_witness.py` — `W_t` data `t = 1..8`; part-wise TRUE-drop scan vs greedy `cost(S)`;
  the `S = P_2∪P_3` falsifier; independent `cost(S)` DP.
* `audit_G9_setfalsifier.py` — the exact falsifier tables for Theorems D and E, plus the
  `C5[n]` control showing the mechanism never fires strictly there.
* `audit_G9_exh.cpp` / `audit_G9_exh.exe` — modes `W1` (all `2^24` cuts of `W_1`),
  `A` (Theorem A over a graph6 stream), `MINDROP` (the `B(n,δ)` table).
* `audit_G9_misc.py` — extremal-graph table, `L(N)` over `N ≤ 100000`, `C5[n]` baseline and
  `N[v]`-peeling, ceiling search **including zero parts**, corollary algebra.
* `audit_G9_density.py` — densest-induced-subgraph refutation and the crude-bound survivor list.
* `audit_G9_edgecases.py` — Theorem A on disconnected / isolated-vertex / odd-`N` / zero-part
  instances and on the Clebsch graph.
* `audit_G9_tf_5_11.g6` — the 102 405 graph census used (regenerated, not reused).
* `audit_G9_mindrop_n11.txt` — the `n = 11` drop-scan output.
