# R9 — the odd-K5 complement: what is actually true there

Round 9, 2026-07-26. Everything on an acceptance path is `fractions.Fraction` or exact
integer arithmetic. Floating point appears only inside the local-search max-cut routine,
whose output is a **cut**, re-counted exactly before use, and inside the two grid sweeps of
§8 that are explicitly labelled as searches for a falsifier, never as an acceptance.

Reproduce: `python R9_oddk5_selftest.py` (26/26 PASS, reproduces `bip(K5)=4`, `Λ(K5)=10/3`,
`ψ(subK5,unif)=4/625`, `Λ(subK5,unif)=2/375` — i.e. every number the brief quotes), then
`R9_oddk5_sim.py`, `R9_oddk5_srg.py`, `R9_oddk5_cert.py`, `R9_oddk5_petersen.py`,
`R9_oddk5_minorder.py`, `R9_oddk5_sums.py`, `R9_oddk5_profile.py`, `R9_oddk5_extra.py`.

---

## 0. Verdicts, most consequential first

1. **A premise of the brief is false.** The **Petersen graph is not weakly bipartite**: it
   has an explicit odd-K5 minor, and the weight `w = 1` on the ten outer/inner edges, `w = 5`
   on the five spokes has `τ_w = 4 > 10/3 = τ*_w`, an integrality gap of exactly `6/5`
   (§2, exact). Guenin's theorem therefore does **not** cover Petersen. Wagner's `V8` and
   planar triangle-free graphs really are covered; `C5` and `C5[2]` are (re-verified).
   *Attribution:* the round-7 **auditor** had already recorded Petersen as carrying an odd-K5
   minor (`round7/audit_Q5.md` line 140, witness `{0,1}{2,7}{3,4}{5,8}{6,9}`, marked "not
   covered"); the brief contradicts the ledger, not me. New here: a hand-checkable switching
   and contraction that needs no search, and — the object weak bipartiteness is actually
   about — an **explicit rational weight realising the gap**, which nobody had produced and
   which makes the falsification independent of Guenin's theorem entirely.

2. **Minimum order of the open class (new theorem, §3).** A triangle-free graph carrying an
   odd-K5 minor has **at least 10 vertices and at least 15 edges**, and **the Petersen graph
   is the unique triangle-free graph on at most 10 vertices carrying one**. Hand proof + two
   exhaustive computations (all `4^10` branch configurations on 10 vertices → 192 labelled
   witnesses, a single isomorphism class `= SRG(10,3,0,1)`; all 1897 triangle-free 9-vertex
   graphs → zero hits). Consequently **`ψ = Λ ≤ 1/25` for every weight on every triangle-free
   graph with `N ≤ 10` except Petersen**, and the genuinely open part of the conjecture starts
   at `N = 10`, not at `N = 11` (`And(4) = Γ_11`) as the ledger had it.

3. **The gap-quantification direction is DEAD, and for a sharper reason than "unbounded"
   (§4).** *Lemma SIM*: for **every** graph `G` and **every** rational cost vector `c`, the
   twice subdivision of `G` is triangle-free and carries a **product** weight `x` with
   `ψ = bip_c(G)` and `Λ = Λ_c(G)` exactly. Triangle-freeness plus product weights is
   therefore **no restriction at all** on the odd-cycle-cover integrality gap: the two
   suprema are equal. Hence no constant `c` with `ψ ≤ c·Λ` exists on triangle-free graphs,
   and this is not an asymptotic statement — it is an exact finite reduction, verified on 12
   weighted instances.

4. **New exact record ratios (§5).** The brief records `6/5` as the largest known
   `ψ/Λ`. Exact new values, all with two-sided rational certificates and all at **odd girth
   5**, the conjecture's own regime:

   | graph | `N` | `ψ·N²`( = `bip`) | `Λ·N²` | `ψ/Λ` |
   |---|---|---|---|---|
   | Higman–Sims | 100 | **350** | **220** | **35/22 = 1.590909…** |
   | Gewirtz | 56 | 84 | 56 | **3/2** |
   | Hoffman–Singleton | 50 | 50 | 35 | **10/7** |
   | M22 | 77 | ∈[193,196] | 616/5 | ∈[965/616, 35/22] |
   | twice-subdivided `K_7` | 49 | 9 | 7 | 9/7 |

   plus the closed-form family `ψ/Λ = 3(n−1)/(2n) → 3/2` on the twice subdivision of `K_n`
   (`N = n²`), and the asymptotic statement that **even at odd girth exactly 5** the ratio
   tends to `5/2` along triangle-free Ramanujan graphs of growing degree.

5. **"Does the odd-K5 minor force `ψ` to be small?" — NO (§6).** Petersen and `Γ_11` both
   carry odd-K5 minors and both contain an induced `C5`, so `max_x ψ ≥ 1/25` for both by the
   accepted plateau. No bound below `1/25` can hold on the class. The small value
   `ψ = 4/625` of the twice-subdivided `K5` is a **uniform-weight** value and an artefact of
   odd girth 9; that same graph has `max_x ψ ≥ 1/81` at an induced `C9`.

6. **The restriction to the odd-K5 class is not a restriction (§7).** For every triangle-free
   `H` there is a triangle-free `H*` with an odd-K5 minor and `max ψ(H*) ≥ max ψ(H)` (adjoin a
   zero-weight Petersen). The honest, non-vacuous form of the reduction is
   > **(†)** for every triangle-free `G` with an odd-K5 minor and every `x > 0` with
   > `Σx = 1`, `ψ(G,x) ≤ 1/25`,
   which **is** equivalent to the conjecture (support-locality + Guenin + Theorem A), and is
   the correct statement of "the exact complement".

7. **Gluing (§8).** `bip` is additive over blocks, so the unweighted conjecture reduces to
   2-connected graphs (`n₁² + n₂² ≤ N²` because `2(n₁−1)(n₂−1) ≥ 0`). For weights, `ψ` is
   additive over 1-sums and the pentagon bowtie has `max ψ = 1/25` exactly (exhaustive exact
   sweep to denominator 25 + the continuous profile). 2-sums are the only gluing that can
   gain, `ψ = min(p₁+p₂, q₁+q₂) ≥ ψ₁+ψ₂`; the natural averaged bound that would close them,
   `(p+q)/2 ≤ W²/25`, is **false** (path `u−a−w`, `x = (1/4,1/2,1/4)`: `1/16 > 1/25`).

8. **Retraction of my own intermediate claim (§8.1).** I first asserted the C5 profile
   `f(u) = min(u,(1−u)/4)·(1−u)/4`; the exact grid falsified it at `u = 1/12`
   (`1/40 > 11/576`). Corrected profile below; it is irrational at rational `u`.

9. **A counterexample's own gap is bounded BELOW (§9).** An upper bound `ψ ≤ cΛ` is
   impossible, but the accepted `ψ ≤ e − 4e²` with `4e² − e + 1/25 = 4(e−1/20)(e−1/5)` forces
   any counterexample to have weighted edge density `e ∈ (1/20, 1/5)` and integrality gap
   `> 1/(5e) ∈ (1,4)`. Every exact witness of this round sits **below** its own requirement
   (Higman–Sims: has `35/22`, would need `20/11`, short by `8/7`); only `C5` sits on the line.
   That says the hunt belongs at `e` near `1/5` — dense configurations — not among the
   high-gap sparse graphs.

10. **Bug found and fixed by my own verifier (recorded, not hidden).** The exact
    min-odd-cycle oracle returns a minimum odd closed *walk*, which on `And(5) = Γ_14` repeated
    an edge; the LP built the row with set semantics while `verify_Lambda` charged the packing
    with multiset semantics, and the verifier refused the certificate. Fixed by storing rows as
    sets of distinct edges and by *proving* row validity inside the verifier — every accepted
    row must induce a non-bipartite subgraph, so `y(row) ≥ 1` is implied by the odd-cycle
    constraints. No previously accepted number changed (all of them had passed the stricter
    multiset test, which dominates the set test); the self-test still returns 26/26 and the
    Petersen gap is unchanged.

11. **Adversarial audit (`R9_oddk5_audit.py`, ALL PASS).** Every load-bearing claim
    re-checked by a route that does not reuse the machinery it checks: the Petersen cover by
    full cycle enumeration (spectrum `{5,6,8,9}`, 12 pentagons + 20 nonagons, every odd cycle
    carrying `≥ 3` non-spoke edges) and `τ_w = 4` by a fresh loop over all `2^10` colourings;
    Higman–Sims by direct verification of `SRG(100,22,0,6)` from set intersections, a
    re-counted 750-edge cut, and hand arithmetic for `λ_min = −8`; Lemma SIM on `K5` with
    three cost vectors (gaps `6/5`, `12/11`, `6/5`) brute-forced on the 25-vertex
    subdivision; `Λ(K_n) = m/3` by re-counting the triangle-packing load for `n = 5,6,7,9`.

---

## 1. Setting

`G` finite simple. `bip_w(G) = min` over bipartitions `S` of `w(mono(S))`;
`Λ_w(G) = min { Σ w_e y_e : y ≥ 0, y(C) ≥ 1 for every odd cycle C }`. Always `Λ_w ≤ bip_w`.
For `x ≥ 0` on `V`, `ψ(H,x) = bip_w(H)` and `Λ(H,x) = Λ_w(H)` with `w_uv = x_u x_v`.
The signature is `Σ = E(G)` (all edges odd), so "odd cycle" = odd length.
`ψ(H,x) = ψ(H[supp x], x)`: zero-weight vertices are invisible.

---

## 2. FALSIFIER: the Petersen graph is not weakly bipartite

The brief's item (C) asserts that Guenin's theorem "covers `C5` and ALL its blow-ups, all
planar triangle-free graphs, the Wagner graph and the Petersen graph". The last is false.

**Odd-K5 minor in Petersen.** Label the outer 5-cycle `a_0…a_4`, the inner pentagram
`b_i ∼ b_{i+2}`, spokes `a_i b_i`. Switch at `B = {b_0,…,b_4}`: an edge changes sign iff it
has exactly one end in `B`, so the five spokes become **even** while the five outer edges
(no end in `B`) and the five inner edges (two ends in `B`) stay **odd**. Contract the five
even spokes. The classes are `{a_i,b_i}`, `i ∈ Z_5`; the outer edges give the pairs
`{i,i+1}` and the inner edges the pairs `{i,i+2}` — all ten pairs of `K5`, all odd. That is
the all-odd `K5`. (Checked literally, edge by edge, in `R9_oddk5_petersen.py`; an
independent branch-set decider written from the parity criterion of §3 finds a *different*
witness `{0,1},{2,3},{5,7},{6,8},{4,9}`.)

**Explicit integrality gap.** `w = 1` on the ten outer/inner edges, `w = M` on the five
spokes. For `M ∈ {4,5,6,10}`, exhaustively over all `2⁹` cuts and by exact row generation
with a two-sided certificate:

```
  M=  4:  tau_w = 4   tau*_w = 10/3   gap = 6/5
  M=  5:  tau_w = 4   tau*_w = 10/3   gap = 6/5
  M=  6:  tau_w = 4   tau*_w = 10/3   gap = 6/5
  M= 10:  tau_w = 4   tau*_w = 10/3   gap = 6/5
```

Why `τ_w = 4`: for `M ≥ 4` every optimal cut separates each spoke, i.e. `b_i = ¬a_i`; then a
mono outer edge means `a_i = a_{i+1}` and a mono inner edge means `b_i = b_{i+2}`, i.e.
`a_i = a_{i+2}`. So `τ_w` = the minimum number of monochromatic **pairs** of a 2-colouring of
`{a_0..a_4}` = `min_k [C(k,2)+C(5−k,2)] = 4 = bip(K5)`. Why `τ*_w ≤ 10/3`: `y = 1/3` on the
ten non-spoke edges is feasible because a cycle of Petersen uses an even number of spokes,
so every 5-cycle has at least 3 non-spoke edges and every 9-cycle at least 5.

**Consequence.** The round-brief sentence "This covers … the Petersen graph" must be struck,
and with it the belief that the open class begins at `Γ_11`. Note that **the gap weight alone
falsifies the premise**: weak bipartiteness *means* `τ_w = τ*_w` for all `w ≥ 0`, so no minor
theory and no appeal to Guenin is needed. The round-7 auditor had already flagged the minor
(`round7/audit_Q5.md`, "Petersen | 10 | YES … | not covered"); the explicit weight is new.

`C5`, `C5[2]` and Wagner `V8 = And(3)` are re-verified as having **no** odd-K5 minor by my
decider (4/4 agreement with the previously gated round-7 decider, which used a different
algorithm). Planar graphs have no `K5` minor at all, so they stay covered. For `C5[n]` the
minor question is moot in any case: `ψ(C5[V_1..V_5],x) = min_i y_i y_{i+1} ≤ 1/25` by AM–GM
with `y_i` the class weights (accepted Theorem B), so blow-ups need no minor theory —
`C5[3]` was left running here only as a curiosity.

---

## 3. Theorem R9-1 (minimum order and size of the open class)

> **Theorem.** Let `G` be triangle-free with an odd-K5 minor. Then `|V(G)| ≥ 10` and
> `|E(G)| ≥ 15`. The Petersen graph attains both, and is the **unique** triangle-free graph
> on 10 vertices and 15 edges with an odd-K5 minor.

**Parity criterion used throughout.** An odd-K5 minor is five disjoint sets `V_1..V_5`, each
inducing a connected *bipartite* subgraph (WLOG a tree), pairwise joined, plus a choice of
one joining edge per pair, such that the contracted signed `K5` is switching-equivalent to
the all-odd `K5`. Writing `d_i : V_i → {0,1}` for the 2-colouring of `G[V_i]` (unique up to
flip) the minor edge realised by a joining edge `ab` (`a∈V_i, b∈V_j`) has sign
`σ_ij = 1 + d_i(a) + d_j(b) (mod 2)` — a cycle of the minor pulls back to a cycle of `G`
whose length is the number of joining edges plus the parities of the paths traversed inside
the branch sets. A signed `K5` is switching-equivalent to the all-odd `K5` iff **all ten of
its triangles are odd**, equivalently iff `∃ ε ∈ GF(2)^5` with `σ_ij = 1 + ε_i + ε_j` for
all `i<j` (flipping `ε_i` is exactly flipping the reference colour of `d_i`).

**Proof of the theorem.**
*At most two branch sets are singletons*: three pairwise adjacent singletons form a triangle.

*Exactly two singletons `u,v`.* They are joined, so `u ∼ v`; triangle-freeness gives
`N(u) ∩ N(v) = ∅`, so each other branch set `V_i` contains **distinct** `a_i ∼ u` and
`b_i ∼ v`. The triangle `{u,v,i}` has
`σ_uv + σ_vi + σ_iu = 3 + d_i(a_i) + d_i(b_i)`, which must be odd, forcing
`d_i(a_i) = d_i(b_i)`: the tree-distance from `a_i` to `b_i` is even and non-zero, hence
`≥ 2`, hence `|V_i| ≥ 3`. Total `≥ 2 + 3·3 = 11`.

*Exactly one singleton `u`.* Root each `V_i` at the end `a_i` carrying the joining edge to
`u`, so `σ_{ui} = 1`. The triangle `{u,i,j}` gives
`σ_{ui}+σ_{uj}+σ_{ij} ≡ 1 + d_i(p) + d_j(q) ≡ 1`, i.e. **`d_i(p) = d_j(q)`** for the chosen
`ij`-joining edge `pq`. For a branch set of size 2 the only even-parity vertex is `a_i`
itself, so a joining edge between two size-2 sets is `a_i a_j` or `b_i b_j`; and
`a_i, a_j ∈ N(u)` are non-adjacent by triangle-freeness, so it must be `b_i b_j`. Hence **any
three size-2 branch sets force a triangle `b_i b_j b_k`.** With one singleton at most two
branch sets can have size 2, so the sizes are `≥ 1+2+2+3+3 = 11`.

*No singleton.* `≥ 5·2 = 10` vertices, with equality iff all five branch sets are single
edges.

Hence `|V| ≥ 10`, and **at `|V| = 10` the five branch sets are forced to be five disjoint
edges**. For the size: the branch sets contribute `Σ(|V_i|−1) ≥ 5` internal edges and the ten
pairs `≥ 10` joining edges, so `|E| ≥ 15`. Petersen attains `(10,15)`; §2 gives its minor.

*Uniqueness on 10 vertices.* By the previous paragraph the five branch sets form a perfect
matching (5 edges) and each of the ten pairs gets exactly one joining edge — 15 edges, no
freedom. Fixing the matching to `{01,23,45,67,89}` by relabelling, all `4^10 = 1 048 576`
choices were enumerated: **192 labelled witnesses that are triangle-free and satisfy the
parity condition, forming exactly one isomorphism class, with `srg` parameters `(10,3,0,1)` —
the Petersen graph** (`R9_oddk5_minorder.log`). A 10-vertex triangle-free graph with an
odd-K5 minor therefore *contains a spanning Petersen subgraph*; but Petersen has girth 5 and
diameter 2, so every non-adjacent pair has a common neighbour and adding any edge creates a
triangle. **So it is Petersen.** ∎

> **Corollary.** For every triangle-free graph `G` on at most 10 vertices other than the
> Petersen graph, and every `w ≥ 0`, `τ_w(G) = τ*_w(G)`; in particular `ψ = Λ ≤ 1/25` there
> for every weight. The "exhaustive search on small vertex counts" asked for in the brief is
> therefore finished for `N ≤ 10` with a one-line answer: the only object in the class is
> Petersen.

**Independent redundancy.** All **1897** triangle-free graphs on 9 vertices (the complete
census, each re-verified triangle-free by my own decoder) were run through the decider:
**zero** odd-K5 minors, in agreement with the hand proof.

---

## 4. Lemma S and Lemma SIM: triangle-freeness is worth nothing to the LP gap

> **Lemma S (weighted odd subdivision).** Let `H` arise from `G` by replacing every edge `e`
> with a path `P_e` of **odd** length, and let `w ≥ 0` be edge weights on `H`. Put
> `c_e := min_{f ∈ P_e} w_f`. Then `bip_w(H) = bip_c(G)` and `Λ_w(H) = Λ_c(G)`.

*Proof.* Internal path vertices have degree 2, so cycles of `H` correspond bijectively to
cycles of `G`, and the corresponding lengths agree mod 2 because each `ℓ_e` is odd.
For `bip`: given a cut of `G`, 2-colour each path properly if its ends differ (0 mono, possible
exactly because `ℓ_e` is odd) and otherwise properly except at the cheapest edge (cost `c_e`);
conversely any cut of `H` restricted to `V(G)` has, on every mono `e`, a path with equal ends
and odd length, hence at least one mono edge, of weight `≥ c_e`, and the paths are disjoint.
For `Λ`: with `Y_e := Σ_{f∈P_e} y_f`, the constraints of `H` are exactly
`Σ_{e∈C} Y_e ≥ 1` over odd cycles `C` of `G`, and for fixed `Y_e` the cheapest `y` puts all
the mass on the cheapest edge of `P_e`, giving objective `Σ_e c_e Y_e`. So the two LPs
coincide. ∎

> **Lemma SIM (simulation).** Let `G` be any graph and `c : E(G) → (0,1] ∩ Q`. Let `H` be the
> **twice** subdivision of `G` (`u — a_e — b_e — v`), triangle-free, and put
> `x ≡ 1` on `V(G)`, `x_{a_e} = 1`, `x_{b_e} = c_e`. Then with product weights
> `w_{uv} = x_u x_v`,
> `ψ(H,x) = bip_c(G)` and `Λ(H,x) = Λ_c(G)`, hence `ψ(H,x)/Λ(H,x) = bip_c(G)/Λ_c(G)`.

*Proof.* The three path weights are `1·1 = 1`, `1·c_e = c_e`, `c_e·1 = c_e`, so
`min = c_e`; apply Lemma S. Normalising `x` by `Σx` divides `ψ` and `Λ` by `(Σx)²` and does
not change the ratio; scaling `c` scales both `bip_c` and `Λ_c`, so every positive rational
cost vector is realised. ∎

**Verified exactly** on 12 weighted instances (`G ∈ {K4, C5, K33+e}`, unit and random
denominator-12 costs; `N(H) ∈ {15,16,26}`), by brute force over all cuts of `H` and by exact
row generation with two-sided certificates on both sides — all 12 agree
(`R9_oddk5_sim.py`, TEST B). Lemma S itself was checked on `C5, K4, K5, K33, K33+e` for
paths of length 3 and 5, with the even subdivision as a control (`bip` collapses to 0).

> **Corollary (gap verdict).**
> `sup { ψ(H,x)/Λ(H,x) : H triangle-free, x ≥ 0 } = sup { bip_c(G)/Λ_c(G) : G any graph, c ≥ 0 }`.
> The right-hand side is the integrality gap of the odd-cycle covering LP (MinUnCut) over all
> weighted instances, which is unbounded. **No constant `c` with `ψ ≤ c·Λ` holds on
> triangle-free graphs**, and triangle-freeness contributes *exactly nothing* to this
> question: the class of instances is the same.

A self-contained unboundedness proof (this is registry entry **A22**, recorded there with the
same mechanism; re-derived here to keep the round self-contained and to sharpen it to odd
girth 5):

> **Proposition.** For `d`-regular `G` on `n` vertices with least adjacency eigenvalue
> `λ_min` and odd girth `g`: `bip(G)/Λ(G) ≥ (g/2)(1 − |λ_min|/d)`.
> *Proof.* `maxcut = max_{s ∈ {±1}^n} (m/2 − sᵀAs/4) ≤ m/2 − nλ_min/4`, so
> `bip ≥ m/2 + nλ_min/4 = (nd/4)(1 − |λ_min|/d)`; and `y ≡ 1/g` is feasible, so
> `Λ ≤ m/g = nd/(2g)`. ∎

With LPS Ramanujan graphs (`|λ_min| ≤ 2√p`, `girth ≥ (2/3)log_p n`) this gives ratios
`→ ∞`. **Sharpening (new here):** the ratio already grows at **odd girth exactly 5**, where
the whole difficulty of the conjecture lives — take triangle-free Ramanujan graphs of growing
degree, `(5/2)(1 − 2√(d−1)/d) → 5/2`. A22's construction needs `g → ∞`; this one does not,
and it is confirmed by the finite exact values of §5, which climb `1 → 10/7 → 3/2 → 35/22`
along the triangle-free strongly regular graphs.

---

## 5. Exact gap witnesses

### 5.1 The subdivided complete graphs (closed form)

Let `S(K_n)` be the twice subdivision of `K_n`: triangle-free, girth 9, `N = n + 2·C(n,2) = n²`.
By Lemma S, `bip(S(K_n)) = bip(K_n) = C(n,2) − ⌊n²/4⌋` and `Λ(S(K_n)) = Λ(K_n) = n(n−1)/6`,
the latter with the two-sided certificate: cover `y ≡ 1/3` (cost `m/3`) and packing
`z_T = 1/(n−2)` on all `C(n,3)` triangles (load `= 1` on each edge, value
`C(n,3)/(n−2) = m/3`). Hence at uniform `x`:

```
  n   N=n^2  |E|  bip  Lambda   ratio          psi              Lambda(x)
  5     25    30    4    10/3     6/5          4/625            2/375
  6     36    45    6       5     6/5          1/216            5/1296
  7     49    63    9       7     9/7          9/2401           1/343
  9     81   108   16      12     4/3         16/6561           4/2187
 11    121   165   25    55/3   15/11         25/14641          5/3993
```

`ratio = 3(n−1)/(2n)` for odd `n` → `3/2`. The `n = 5` row reproduces the brief's
`ψ = 4/625, Λ = 2/375, ratio 6/5` exactly; `n = 7` already beats it (`9/7` at `N = 49`).
The closed forms were re-verified by brute force for `n = 4,5` (`N = 16, 25`).

### 5.2 Triangle-free strongly regular graphs (the exact record)

Constructed from scratch: `GF(4)` → `PG(2,4)` → the 168 6-arcs → the `PSL(3,4)`-class of 56
hyperovals → the Steiner system `S(3,6,22)` (verified: 77 blocks of size 6, all 1540 triples
covered exactly once) → the `M22`, Gewirtz and Higman–Sims graphs; plus Hoffman–Singleton
(pentagon/pentagram) and Clebsch (folded 5-cube). Each is verified strongly regular by exact
integer counting, which pins `λ_min` exactly through `θ² − (λ−μ)θ − (k−μ) = 0`.

`Λ = m/5` is certified **two-sided and without any automorphism input**: the cover `y ≡ 1/5`
is feasible (odd girth 5), and every edge lies in the same number `p` of 5-cycles (counted
exactly), so `z ≡ 1/p` on the pentagons is a feasible packing of the same value `#C5/p = m/5`.

```
graph              n     m   λ_min  5-cyc/edge   Λ (exact)   bip (exact)   ψ/Λ (exact)
Petersen          10    15    -2        4             3            3          1
Clebsch           16    40    -3       24             8            8          1
Hoffman-Singleton 50   175    -3       36            35           50         10/7
Gewirtz           56   280    -4      144            56           84          3/2
M22               77   616    -6      720         616/5     [193,196]   [965/616, 35/22]
Higman-Sims      100  1100    -8     2016           220          350         35/22
```

`bip` is pinned exactly because the spectral lower bound `m/2 + nλ_min/4` is *attained* by an
explicit cut found by local search and re-counted exactly (Petersen 12, Clebsch 32,
Hoffman–Singleton 125, Gewirtz 196, Higman–Sims 750 cut edges).

**`ψ/Λ = 35/22` on the Higman–Sims graph is the exact record of this round**, at odd girth 5,
with `bip = 350` and `Λ = 220` both certified. By Guenin's theorem in the contrapositive
direction, `ψ/Λ > 1` *proves* that Hoffman–Singleton, Gewirtz and Higman–Sims all carry
odd-K5 minors — no minor search needed.

All of them satisfy the conjecture with room: `bip/N²` is `0.0300, 0.03125, 0.0200, 0.0268,
≤0.0331, 0.0350` against `0.04`. Higman–Sims at `7/200` is the closest of the six, at 87.5 %
of the ceiling — comparable to the `N=14` extremal pattern (`7/196 = 0.0357`).

### 5.3 The families the brief asked for (Andrásfai, Mycielskian, Kneser)

Exact `bip` (all cuts) and exact `Λ` (row generation with a two-sided certificate) at uniform
`x`, plus the odd-K5 decision (`R9_oddk5_named.log`):

```
                 graph   n    m  og   bip  Lambda  ratio  psi=bip/N^2  odd-K5 minor
        And(2)=Gamma_5   5    5   5     1       1      1        1/25       NO
        And(3)=Gamma_8   8   12   5     2       2      1        1/32       NO
       And(4)=Gamma_11  11   22   5     4       4      1       4/121       YES
       And(5)=Gamma_14  14   35   5     6       6      1        3/98       YES
```

**The Andrásfai family shows that class membership is invisible at uniform weights**:
`And(4)`, `And(5)` and Petersen all carry odd-K5 minors yet have `ψ = Λ` at uniform `x`; the
gap appears only at other weights (Petersen: `6/5` at the spoke weights of §2). Conversely the
strongly regular witnesses of §5.2 already show a gap at the *most natural* weight. So the
uniform ratio is a one-sided detector, and any search for large `ψ/Λ` that only looks at
uniform weights systematically misses part of the class.

---

## 6. Does an odd-K5 minor force `ψ` to be small? No.

* Petersen (`N=10`) and `Γ_11 = And(4)` both carry odd-K5 minors and both contain an induced
  `C5`, so by the accepted plateau (base (4)) `max_x ψ ≥ 1/25` for both, attained at the
  `C5`-concentration. Verified: `ψ(C5 ⊔ Petersen, C5-concentration) = 1/25` exactly.
  Hence **no bound `ψ ≤ c` with `c < 1/25` can hold on the class**, and the only possible
  statement is `ψ ≤ 1/25` — the conjecture itself.
* The brief's intuition rests on `ψ(twice-subdivided K5) = 4/625`. That is the **uniform**
  weight. The same graph has `max_x ψ ≥ 1/81 = 0.0123` at an induced `C9` (its 9-cycles
  through three original vertices are induced). What makes `4/625` small is odd girth 9 and
  `N = 25`, not the minor: the members of the class with odd girth 5 sit at `1/25`.
* Sharp form of what *is* true: an odd-K5 minor forces `ψ > Λ` to be *possible*, not `ψ`
  to be small. The two are independent — Petersen has `ψ = Λ` at uniform weights and a `6/5`
  gap at the spoke weights of §2.

---

## 7. The complement class is the whole problem

> **Proposition (no free lunch).** For every triangle-free `H` there is a triangle-free `H*`
> with an odd-K5 minor and `max_x ψ(H*,·) ≥ max_x ψ(H,·)`; take `H* = H ⊔ Petersen` and give
> the Petersen copy weight 0. Therefore
> `sup{max ψ : triangle-free with an odd-K5 minor} = sup{max ψ : triangle-free}`.

(If a connected witness is wanted, join the two parts by one edge at a zero-weight endpoint;
`ψ` is unchanged for the same reason.)

> **Reduction (†) — the correct statement of "the exact complement".** The conjecture is
> **equivalent** to: for every triangle-free `G` **with an odd-K5 minor** and every `x > 0`
> with `Σ x = 1`, `ψ(G,x) ≤ 1/25`.
> *Proof.* `ψ(G,x) = ψ(G[supp x], x)`, so we may assume `x > 0`. If `G[supp x]` has no odd-K5
> minor, Guenin gives `ψ = Λ` there and Theorem A gives `Λ ≤ 1/25`. ∎

So the hypothesis one may add for free is **`x` has full support and `G` has an odd-K5
minor** — nothing weaker, nothing stronger. By §3 the smallest such `G` is Petersen, and by
§6 the extremal value `1/25` is already achieved (in the limit of full-support weights) inside
the class. Any route that hopes to gain from the odd-K5 hypothesis must use the *interaction*
of the minor with a full-support optimum, not the minor alone.

---

## 8. Gluing calculus

**1-sums.** If `V(G_1) ∩ V(G_2) = {v}` then for every `x`,
`ψ(G,x) = ψ(G_1, x|_{G_1}) + ψ(G_2, x|_{G_2})` (given the side of `v`, the two halves
optimise independently, and flipping all of `G_2` is a symmetry). Consequences:
`bip` is additive over blocks, so if the conjecture holds for the blocks it holds for `G`:
`n_1² + n_2² ≤ (n_1+n_2−1)² = N²` since `2(n_1−1)(n_2−1) ≥ 0`. **The unweighted conjecture
reduces to 2-connected graphs.**
The weighted statement does not follow from that arithmetic, since the cut vertex is paid
for in both halves. For the pentagon bowtie (two `C5` sharing a vertex, `N = 9`) the exact
answer is `max_x ψ = 1/25`: exhaustive over all integer weightings of total `D` with zeros
allowed,

```
  D= 10: max = 4  at z=2, (0,0,0,0)|(2,2,2,2)   psi = 1/25
  D= 15: max = 9                                psi = 1/25
  D= 20: max = 16                               psi = 1/25
  D= 25: max = 25                               psi = 1/25
```

and the continuous optimisation over the profile below returns `1/25` at `z = 1/5, s = 1/5,
t = 1` — the `C5`-concentration, with the cut vertex *inside* the active pentagon.

**8.1 The `C5` profile (with a retraction).** `ψ(C5,x) = min over the five edges of x_u x_v`
(delete one edge and the rest is a path). Fix `x_v = u`, `Σx = 1`, and maximise:
I first claimed `f(u) = min(u,(1−u)/4)·(1−u)/4`, assuming the other four weights equal. **That
is wrong**: the exact rational grid at denominator 60 returns `1/40 = 0.025` at `u = 1/12`
against the claimed `11/576 = 0.0191`. Correct profile (`C5 = v,a,b,c,d`, `a=d=p`, `b=c=q`):

```
 u <= 1/5 :  q = (sqrt(2u − u²) − u)/2,   p = q²/u,   f(u) = q²
 u >= 1/5 :  f(u) = ((1−u)/4)²
 f(1/5) = 1/25 is the maximum;  f is irrational at rational u,
 which is exactly why no rational grid attains it.
```

Verified against the exhaustive grid at 13 values of `u` (grid `≤ f` everywhere, with
equality at the grid-representable optima `u = 1/3, 2/3`).

**2-sums.** Glue `G_1, G_2` along two terminals `{u,w}`. With `p_i` / `q_i` the optimum over
cuts keeping the terminals together / apart, `ψ(G,x) = min(p_1+p_2, q_1+q_2)`, which is
`≥ ψ_1 + ψ_2`. So **2-sums are the only gluing that can gain**, and they are exactly where the
odd-K5 obstruction can be assembled. The natural averaged closure,
`φ := (p+q)/2 ≤ W²/25` per part (which would give `ψ(2-sum) ≤ φ_1 + φ_2 ≤ 1/25`), is
**false**: the two-terminal path `u−a−w` with `x = (1/4,1/2,1/4)` has `p = 0`, `q = 1/8`,
`φ = 1/16 > 1/25`. Any 2-sum theory must therefore carry the *pair* `(p,q)` and not any
symmetric average of it.

---

## 9. The gap a counterexample must have (the one non-blocked "quantify the gap")

An **upper** bound `ψ ≤ cΛ` is impossible (§4). A **lower** bound on the gap that any
counterexample must have is not blocked, and follows from two accepted results. Write
`e = Σ_{uv∈E} x_u x_v` (weighted edge density; `e ≤ 1/4` on triangle-free graphs by
Motzkin–Straus).

> **Proposition (density window + forced gap).** Accepted base gives `ψ ≤ e − 4e²`, and
> `4e² − e + 1/25 = 4(e − 1/20)(e − 1/5)`. Hence
> **`ψ > 1/25` forces `e ∈ (1/20, 1/5)`.** On that window `Λ ≤ e/5 < 1/25`, so a
> counterexample must have odd-cycle integrality gap
> `ψ/Λ > (1/25)/(e/5) = 1/(5e) ∈ (1, 4)`.

So a counterexample is squeezed from both sides: it cannot be sparse (`e ≤ 1/20` is
excluded outright), and the sparser it is inside the window the more odd-K5 structure it
must carry, in the precise sense of a larger LP gap:

```
   e =  1/20  1/15  1/12  1/10   1/8   1/6  9/50  19/100   1/5
 gap >    4     3    2.4     2   1.6   1.2  1.11   1.053     1
```

Where the round's exact witnesses sit (uniform `x`; `gap` is the exact value of §5):

```
              graph      e        psi      Lambda    gap     gap needed at that e
                 C5     1/5       1/25       1/25      1            1
           Petersen    3/20      3/100      3/100      1          4/3
            Clebsch    5/32       1/32       1/32      1         1.28
  Hoffman-Singleton   7/100       1/50      7/500   10/7        20/7 = 2.857
            Gewirtz    5/56      3/112       1/56    3/2         2.24
        Higman-Sims   11/100      7/200     11/500  35/22       20/11 = 1.818
```

**Only `C5` sits on the line.** Every other exact object of this round has a gap strictly
below what its own density would require of a counterexample — Higman–Sims, the largest gap
known here, is short by a factor `(20/11)/(35/22) = 8/7`. This is a cheap, exact, non-
circular screen for future counterexample hunts, and it says where to hunt: at `e` close to
`1/5`, where the required gap is barely above 1, i.e. among **dense** triangle-free
configurations, not among the high-gap sparse ones this round has been collecting.

## 10. Ledger: what this round blocks, and what it leaves open

**BLOCKED / DEAD.**

* *Quantify the integrality gap by a constant* — dead, and by Lemma SIM not merely
  asymptotically: the triangle-free product-weight gap problem **is** the general weighted
  gap problem. Blocking statement, verbatim: *"there is no constant `c` with
  `ψ(H,x) ≤ c·Λ(H,x)` for all triangle-free `H` and all `x ≥ 0`; the two suprema
  `sup ψ/Λ` over triangle-free product-weight instances and over all weighted instances on
  all graphs are equal, and both are infinite."*
* *Odd-K5 forces `ψ` small* — dead: Petersen and `Γ_11` are in the class with
  `max ψ ≥ 1/25`.
* *Restricting the conjecture to the odd-K5 class* — not progress: it is the conjecture
  (§7). Any lemma proved "on the class" is a lemma of strength `≥` the conjecture unless it
  also uses full support in an essential way.
* *Averaged two-terminal bound `(p+q)/2 ≤ W²/25`* — falsified by `u−a−w`, `1/16 > 1/25`.
* *My own C5-profile formula `min(u,(1−u)/4)(1−u)/4`* — retracted, falsified at `u = 1/12`.

**OPEN / usable.**

* `(†)` is the sharp form of the open problem: full-support `x` on a triangle-free graph with
  an odd-K5 minor, starting at `N = 10` (Petersen).
* The 2-sum pair calculus `(p,q)` is untouched by any dead entry in the registry; a correct
  two-terminal strengthening would close all 2-sums, and the falsifier above says it must be
  a statement about the pair, e.g. a bound on `min(p+p', q+q')` over *matched* parts.
* Higman–Sims (`bip/N² = 0.035`, exact) is the densest exact approach to `1/25` known here
  outside `C5`-blow-ups and the `N=14` pattern, and it is in the open class; its `ψ/Λ = 35/22`
  is the exact record.

## 11. Files

```
R9_oddk5_lib.py        exact library: graph6, bip (all cuts), exact rational simplex,
                       odd-cycle covering LP by row generation with a two-sided certificate,
                       exact min-odd-cycle oracle (double cover + Dijkstra over Fractions)
R9_oddk5_selftest.py   26 reference values, all PASS
R9_oddk5_sim.py        Lemma S and Lemma SIM verification; subdivided-K_n table
R9_oddk5_srg.py        GF(4) -> PG(2,4) -> S(3,6,22) -> M22/Gewirtz/Higman-Sims; spectral bounds
R9_oddk5_cert.py       exact Lambda = m/5 certificates, exact bip, exact ratios
R9_oddk5_petersen.py   the Petersen falsifier (odd-K5 minor + tau=4 > 10/3 = tau*)
R9_oddk5_minor.py      odd-K5 minor decider from the parity criterion
R9_oddk5_minorder.py   4^10 enumeration on 10 vertices; all 1897 triangle-free 9-vertex graphs
R9_oddk5_sums.py       1-sums, bowtie sweep, 2-sum falsifier, class equivalence
R9_oddk5_profile.py    corrected C5 profile + 1-sum continuous optimisation
R9_oddk5_extra.py      M22 pinning, odd-K5 status of C5 blow-ups
R9_oddk5_dichotomy.py  density window and the gap a counterexample must have
R9_oddk5_audit.py      adversarial re-check of every load-bearing claim (ALL PASS)
logs: R9_oddk5_minorder.log R9_oddk5_sums.log R9_oddk5_extra.log R9_oddk5_audit.log
      R9_oddk5_dichotomy.log
```
