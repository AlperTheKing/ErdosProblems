# PROOF 144 — Angle A: Lemma E (exists-form) by generalizing the class-P proof

**Target.** Lemma E (exists-form): for every finite simple connected cyclic graph `G`
with `e := ecc(G.center) >= 1` there is a shortest cycle `K` with `e <= M(K)`.
Together with Lemma M (accepted tool, restated and re-proved in §1.4) this closes the
single open branch of WOWII/Graffiti.pc Conjecture 144
(`tree(G) >= girth(G) - 1 + e(G)`), all other branches being closed in the compiled
Lean skeleton (see INTEL_144.md).

**Status summary (honest).**
* The proof is COMPLETE for `g >= 5` **modulo two bridges** (Bridge A-wide, Bridge B),
  each stated exactly in §5 and falsifier-tested with 0 violations
  (1949/1949 rigid-regime instances; no counterexample in 8385 graphs).
* `g = 4` : same architecture goes through **modulo Bridges A4/B4/C4** (§6);
  end-to-end mechanical validation 630/630 instances, for EVERY shortest cycle.
* `g = 3` : switch lemma proved; assembly validated 3114/3114 in exists-K form;
  the K-selection argument is Bridge D3 (§7). Per-K form is genuinely false at
  `g = 3` (41 corpus graphs need the switch), consistent with INTEL.
* Consequently `complete = false`; the remaining unproved content is exactly the
  five bridges listed in §8, none of which has a counterexample.

All numeric claims below were exact-integer falsifier-tested BEFORE being relied on;
scripts and JSON outputs live in `problems_external/wowii_144/proverA/`
(battery1..battery5, inspect1/inspect2). Corpus: `networkx` atlas (all connected
graphs on <= 7 vertices), the wave-2 family/random/adversarial/trap generators,
subdivided multigraphs, webbed annuli, cycle+legs/trees, chorded cycles, thetas,
forced-girth randoms — 8385 distinct connected cyclic graphs with `e >= 1`
(seed 20260718; see §9 for per-claim counts).

---

## 0. Notation and standing facts

`G` finite simple connected, cyclic; `g = girth(G) >= 3`; `dist = d = d_G`;
`r = radius`, `C = center = {v : ecc(v) = r}`, `e = max_v d(v, C) >= 1`.

* (T1) every geodesic induces a path, hence an induced tree.
* (T3) every shortest cycle `K` is chordless and isometric: for `a, b ∈ V(K)`,
  `d_G(a,b) = d_K(a,b)`, the cycle metric. (Standard; in the accepted toolset.)
* (F0) `e <= r`: for any `v` and any `c0 ∈ C`, `d(v, C) <= d(v, c0) <= ecc(c0) = r`.
* (F1) every vertex `y` with `d(x*, y) <= e - 1`, where `d(x*, C) = e`, is
  noncentral: otherwise `d(x*, C) <= e - 1`. Noncentral means `ecc(y) >= r + 1`,
  so `y` has a *far vertex* `u` with `d(y, u) >= r + 1`.

Fix a shortest cycle `K`, `V(K) = {k_0, .., k_{g-1}}` in cyclic order.
For `v ∉ V(K)`: `h(v) := d(v, V(K)) >= 1`.
**Branches** are the connected components of `G - V(K)`.
For a branch `B`, its **doors** are `A(B) := N(B) ∩ V(K)`.
`B` is **narrow** if `|A(B)| = 1` (single door `a_B`), **wide** if `|A(B)| >= 2`.
Note every branch has at least one door (`G` connected).

### 0.1 Lemma R (girth–radius). `g <= 2r + 1`; hence `⌊g/2⌋ <= r`, and if `g` is even, `2r + 1 - g >= 1`.

*Proof.* Let `c0 ∈ C` and let `T` be a BFS tree of `G` rooted at `c0`; every vertex has
`d_T(c0, v) = d(c0, v) <= r`. Since `G` is cyclic, some edge `{u, v} ∈ E(G) \ E(T)`.
Let `w` be the last common vertex of the `T`-paths from `u` and from `v` to `c0`.
The `T`-paths `u→w`, `v→w` are internally disjoint and do not use the edge `{u,v}`,
so together with `{u,v}` they form a cycle of length
`d_T(u,w) + d_T(v,w) + 1 <= r + r + 1`. Hence `g <= 2r + 1`.
For the corollary: `⌊g/2⌋ <= ⌊(2r+1)/2⌋ = r`. If `g` is even then `g ≠ 2r + 1`
(parity), so `g <= 2r`, i.e. `2r + 1 - g >= 1`. ∎

Throughout set `κ := 2r + 1 - g >= 0` (and `κ >= 1` for even `g`).

*Tested:* battery1 `TR`: 0 violations on 7979 cyclic graphs.

### 0.2 Lemma TA (attachment). Let `q ∉ V(K)` have two distinct neighbours `x, y ∈ V(K)`. Then `d_K(x,y) <= 2` and `d_K(x,y) >= g - 2`. Consequently:
* `g >= 5`: impossible — every vertex outside `K` has at most one neighbour on `K`;
* `g = 4`: `N(q) ∩ V(K)` is contained in one antipodal pair `{k_i, k_{i+2}}`
  (three K-neighbours are impossible);
* `g = 3`: any two K-neighbours `x, y` of `q` are adjacent, so `{q, x, y}` induces
  a triangle, i.e. ANOTHER shortest cycle (the *switch* cycle).

*Proof.* `x–q–y` is a path of length 2, so `d_G(x,y) <= 2`; by isometry (T3)
`d_K(x,y) <= 2`. The shorter K-arc from `x` to `y` together with `x–q–y` forms a
cycle of length `d_K(x,y) + 2 >= g`. For `g >= 5` the two constraints conflict.
For `g = 4`: `d_K(x,y) = 2`, an antipodal pair; a third K-neighbour would be at
K-distance 1 from one of them. For `g = 3`: `d_K(x,y) = 1`. ∎

*Tested:* battery1 `TA5/TA4`: 0 violations over 201322 attachment checks.

---

## 1. The donation calculus

All witness forests below are built from three primitives. Fix `K` and `z ∈ V(K)`.
Recall (Lemma M below): a valid witness is `F ⊆ V \ V(K)` inducing a forest such
that every component of `G[F]` sends exactly one edge (with multiplicity) into
`K \ {z}` — edges into `z` itself are unrestricted.

### 1.1 τ-tails

For `u ∉ V(K)` let `τ_z(u) := d_{G−z}(u, V(K) \ {z})` (possibly `∞`).

**Lemma τ (validity, `g >= 5`).** If `τ_z(u) = t < ∞`, let
`P = (u = w_0, w_1, .., w_{t-1}, a)` be a shortest path in `G − z` from `u` to the
set `V(K) \ {z}`. Then `T(u,z) := {w_0, .., w_{t-1}}` (the **τ-tail**) induces a
path, is disjoint from `V(K)`, is contained in the branch `B(u)`, and as a single
component sends exactly one edge into `K \ {z}`. Hence `M(K) >= τ_z(u)`.

*Proof.* Shortest ⟹ induced (a chord would shorten it; all vertices ≠ z, so the
chord survives in `G − z`). Only the endpoint `a` lies in `V(K) \ {z}` (a path to a
set meets the set only at its end), and no interior vertex equals `z` (we are in
`G − z`); so `T(u,z) ∩ V(K) = ∅` and, being connected in `G − V(K)`, `T ⊆ B(u)`.
For `i <= t - 2`, `w_i` has no neighbour in `V(K) \ {z}` (it would shorten the
path); it may be adjacent to `z`, which is allowed. The last vertex `w_{t-1}` is
adjacent to `a`, and by Lemma TA (`g >= 5`) it has no other K-neighbour; also
`w_{t-1}` is not adjacent to `z` (TA again). So the component sends exactly one
edge into `K \ {z}`. Apply Lemma M with `F = T(u,z)`. ∎

For `g ∈ {3,4}` the same construction is valid provided the terminal vertex has
exactly one neighbour in `K \ {z}`; define `τ'_z(u)` as the number of vertices of a
shortest such *valid* tail: a path in `G − z` whose interior vertices have no
neighbours in `K \ {z}` and whose last vertex has exactly one (computed exactly in
`battery5.valid_tau`). All uses at `g <= 4` below use `τ'`.

### 1.2 Strands (wide branches)

**Lemma S.** Let `B` be a wide branch, `a ∈ A(B)`. In `G[B ∪ {a}]` let
`s = s(B,a) := min { d(a, w) : w ∈ B, N(w) ∩ (V(K) \ {a}) ≠ ∅ }` (finite since `B`
is wide and connected). Let `P = (a, v_1, .., v_s = w)` realize it. Then for
`g >= 5`, `{v_1, .., v_s}` is a valid single-component witness for `z = a`, and

    s(B, a) >= g - 1 - d_K(a, b) >= ⌈g/2⌉ - 1,

where `b` is any element of `N(w) ∩ (V(K) \ {a})`. Hence `M(K) >= s(B,a)`.

*Proof.* Validity: `P` is a shortest path in `G[B ∪ {a}]`, hence induced there;
interior vertices `v_1..v_{s-1}` have no neighbours in `V(K) \ {a}` (minimality of
`s`), and may be adjacent to `a = z` (free). The terminal `w` is adjacent to some
`b ∈ V(K) \ {a}` and, by TA (`g >= 5`), to no other K-vertex; in particular not to
`a`, so the component sends exactly one edge into `K \ {a}` (the edge `w–b`).
Since the vertex set lies in `B`, `G[{v_1..v_s}] = the path` (an edge between
non-consecutive `v_i, v_j` would be a chord in `G[B ∪ {a}]`).
Size bound: `a → v_1 → .. → w → b` is a path of length `s + 1` whose interior
avoids `V(K)`; together with the shorter K-arc from `b` to `a` (length
`d_K(a,b) <= ⌊g/2⌋`) it forms a cycle, so `s + 1 + d_K(a,b) >= g`. ∎

*Tested:* battery4 `STRAND-LB`: 0 violations, minimum slack 0 (the bound is sharp).

### 1.3 Narrow branches (the class-P pendant trees, generalized)

**Lemma N (funnel).** Let `B` be narrow with door `a`. Then for every `u ∈ B`:
(i) every path from `u` to any vertex outside `B` passes through `a`;
(ii) `d(u, V(K)) = d(u, a)`, and `d(σ, u) = d_K(σ, a) + d(a, u)` for every `σ ∈ V(K)`;
(iii) for every `z ≠ a`: `τ_z(u) = d(u, a)`, and the τ-tail is a geodesic
`u → a` minus `a`, whose terminal has exactly one K-neighbour, namely `a` — so the
tail is valid **for every girth** `g >= 3` under the single constraint `z ≠ a`.

*Proof.* (i) The only edges leaving `B` end at `a`. (ii) immediate from (i) plus
isometry of `K`. (iii) A shortest `u → (K \ z)` path first meets `V(K)` at `a`
(by (i)), and `a ∈ K \ {z}`; the prefix is a `u→a` geodesic inside `B ∪ {a}`, and
being a geodesic its interior is not adjacent to `a`; the terminal is adjacent to
`a` by exactly one edge (simple graph) and to no other K-vertex (narrowness — ALL
K-edges of `B` end at `a`, regardless of girth). ∎

Define the **depth** `D_B := max_{u ∈ B} d(u, a_B)`. A narrow branch donates a
single component of size `D_B` under any `z ≠ a_B`.

### 1.4 Lemma M (accepted tool; restated for self-containment)

    M(K) := max |F| : F ⊆ V \ V(K), G[F] a forest, ∃ z ∈ K such that every
            component of G[F] sends exactly one edge into K \ {z}.

**Lemma M.** `tree(G) >= (g - 1) + M(K)` for every shortest cycle `K`.

*Proof.* `K` is chordless, so `G[V(K) \ {z}]` is an induced path with `g - 1`
vertices and `g - 2` edges. Components of `G[F]` are pairwise non-adjacent; each
attaches to that path by exactly one edge (edges to the deleted `z` disappear).
Vertex count `(g-1) + |F|`; edge count `(g-2) + (|F| - c) + c = (g-1) + |F| - 1`;
connected (each component hooks to the path); hence a tree, and it is induced
because all its vertices avoid `z` and the edge count matches. ∎

Consequently **Lemma E ⟹ Conjecture 144** on the open branch.

### 1.5 The master donation and Step 1

Define `ρ̂(K) := max` over all finite `τ_z(u)` (`z ∈ K`, `u ∉ K`; `τ'` for `g <= 4`)
and, when `g >= 5`, all strands `s(B, a)` (`B` wide, `a ∈ A(B)`).

**Proposition 1 (Step 1).** `M(K) >= ρ̂(K)`. In particular, if `ρ̂(K) >= e` for some
shortest cycle `K`, Lemma E holds for `G`. (Immediate from Lemmas τ, S, N.)

Note `ρ̂(K) >= h(v)` for every `v ∉ V(K)` (choose `z` avoiding a door of `B(v)`;
`τ_z(v) >= h(v)` — for narrow `B(v)` this is Lemma N(iii); for wide, `τ_z(v)` is
finite for every `z` and always `>= h(v)`). Also `ρ̂(K) >= hx := d(x*, K)` where
`x*` is any realizer of `e`.

*Tested:* battery1 `C1` (`M(K) >= max_v d(v,K)`, direct M-enumeration): 3364
checks, 0 violations, min slack 0. Step 1 disposed of 3711 of the 5660 tested
(K, graph) instances at `g >= 5` (battery4 `STEP1`).

---

## 2. The rigid regime and the window

From now on fix a shortest cycle `K` and assume the **rigid regime**:

    ρ̂(K) <= e - 1.

(If not, Proposition 1 finishes.) Fix a realizer `x*` (`d(x*, C) = e`) and a
nearest center `c` (`d(x*, c) = e`). Let `hx = d(x*, K)`, let `m ∈ V(K)` be a
nearest K-vertex to `x*` (for narrow `B_x := B(x*)` necessarily `m = a_{B_x}`),
and set

    δ := e - hx.

**Fact 2.1.** In the regime, `δ >= 1`. (*`hx <= ρ̂ <= e - 1` by §1.5.*)

**Window.** If `1 <= δ <= ⌊g/2⌋`, set `W0 := {σ ∈ V(K) : d_K(m, σ) <= δ - 1}`,
an honest arc with exactly `2δ - 1` vertices (`2(δ-1) + 1 <= g` since
`δ <= ⌊g/2⌋`).

**Fact 2.2 (noncentrality).** Every `σ ∈ W0` satisfies
`d(x*, σ) <= hx + d_K(m, σ) <= hx + δ - 1 = e - 1`, hence is noncentral (F1) and
has a far vertex `u` with `d(σ, u) >= r + 1`.

**Fact 2.3 (far vertices are outside K).** If `u ∈ V(K)` then
`d(σ, u) = d_K(σ, u) <= ⌊g/2⌋ <= r` (Lemma R). So far vertices lie in branches.

*Tested:* battery1 `WIN-noncentral`, `WIN-devK`, `WINLEN`: 0 violations.

---

## 3. Coverage, capacity, counting (g >= 5, rigid regime)

Say a branch `B` **covers** `σ ∈ W0` if some `u ∈ B` has `d(σ, u) >= r + 1`.

**Lemma CAP (narrow capacity).** Let `B` be narrow with door `a` and depth `D_B`,
and suppose `B` is a branch of the rigid regime (`D_B = τ_{z≠a} <= e - 1 <= r - 1`).
Then

    cov(B) ∩ W0  =  S_B ∩ W0,   where  S_B := {σ ∈ V(K) : d_K(σ, a) >= r + 1 - D_B},

and `|S_B| <= max(0, g - 2r - 1 + 2 D_B) = max(0, 2 D_B - κ) <= 2 D_B`.

*Proof.* By Lemma N(ii), `d(σ, u) = d_K(σ, a) + d(a, u)`, so `B` covers `σ` iff
`d_K(σ, a) + D_B >= r + 1`. `S_B` is the complement in the cycle of the K-ball of
radius `r - D_B >= 1` around `a`, which is an arc with
`min(g, 2(r - D_B) + 1)` vertices. ∎

**Bridge B (coverage; TESTED, unproved).** In the rigid regime (`g >= 5`,
`1 <= δ <= ⌊g/2⌋`), every `σ ∈ W0` has a far vertex lying in a **narrow branch
different from `B_x`**.

*Tested:* battery5 `BR-B`: 1949/1949 rigid-regime windows, 0 violations; moreover
no wide branch hosted a far vertex of any window position in the regime
(battery4: `R-CAPw` never fired). Without the regime restriction the claim is
FALSE (battery2 `TENT5`: 725 failures, all rescued by `ρ̂ >= e`, battery3
`FALLBACK-BX` 725/725 — which is exactly why the regime split is the right one).

**Lemma COUNT.** Assume Bridge B. Let `J` be any family of narrow branches
(≠ `B_x`) covering `W0` (one exists by Bridge B). Then `Σ_{B ∈ J} D_B >= δ`.

*Proof.* Covering plus Lemma CAP give
`Σ_{B∈J} max(0, 2 D_B - κ) >= Σ_{B∈J} |S_B ∩ W0| >= |W0| = 2δ - 1`,
so `2 Σ D_B >= 2δ - 1 + |J| κ >= 2δ - 1`, i.e. `Σ D_B >= δ - 1/2`, and by
integrality `Σ D_B >= δ`. ∎

**Lemma Z (choice of z and assembly).** Assume Bridge B and let `J` be an
inclusion-minimal cover as above. Then there exist `z ∈ V(K)` and a sub-family
`J' ⊆ J` with `Σ_{B ∈ J'} D_B >= δ` such that:
`z ∉ {a_B : B ∈ J'}`, and if `hx >= 1` and `B_x` is narrow, `z ≠ a_{B_x} = m`.
Consequently

    M(K) >= τ_z(x*) + Σ_{B ∈ J'} D_B >= hx + δ = e.

*Proof.* Minimality gives `|J| <= |W0| = 2δ - 1`. The forbidden set is
`Φ = {a_B : B ∈ J} ∪ {a_{B_x}}` (the latter only if `hx >= 1` and `B_x` narrow;
if `B_x` is wide, `τ_z(x*)` is finite for every `z` and `>= hx`). So
`|Φ| <= |J| + 1 <= 2δ <= 2⌊g/2⌋`.

*Odd `g`*: `2⌊g/2⌋ = g - 1 < g`, so some `z ∈ V(K) \ Φ` exists; take `J' = J`.

*Even `g`*: `|Φ| <= g`, with equality only if `δ = g/2`, `|J| = 2δ - 1 = g - 1`,
and all the listed doors are pairwise distinct. If `|Φ| < g` pick `z ∉ Φ`,
`J' = J`. In the exhaustion case, `κ >= 1` (Lemma R, even `g`), so by Lemma CAP
every `B ∈ J` has `2 D_B - 1 >= |S_B ∩ W0| >= 1`, i.e. `D_B >= 1`. Drop one
branch `B_0 ∈ J` and set `J' = J \ {B_0}`, `z := a_{B_0}`; all doors being
distinct, `z ∉ Φ \ {a_{B_0}}`. Then
`Σ_{J'} D_B >= |J| - 1 = g - 2 >= g/2 = δ` (as `g >= 4`). 

Assembly: `F := T(x*, z) ∪ { deepest-vertex tail of B, B ∈ J' }` (for `hx = 0`
omit the x*-tail). The x*-tail is valid with `|T(x*,z)| = τ_z(x*) >= hx`
(Lemma τ; Lemma N(iii) if `B_x` narrow, using `z ≠ a_{B_x}`). Each `B ∈ J'`
donates its depth-`D_B` tail (Lemma N(iii), `z ≠ a_B`). All components lie in
pairwise distinct branches, hence are pairwise non-adjacent, and each sends
exactly one edge into `K \ {z}`. Lemma M applies. ∎

*Tested:* battery4 `R-O3` (exists `z` with min-cover donation mass `>= δ`):
1949/1949, min slack 0. battery5 `ASM` end-to-end on the sub-population where a
1–2-branch cover exists: 1688/1688, min slack 0.

---

## 4. The BIG case (δ > ⌊g/2⌋) cannot occur in the rigid regime — modulo Bridge A-wide

Suppose `δ >= ⌊g/2⌋ + 1`. Let `q ∈ V(K)` be nearest to `c`, `h_c := d(c, q)`.
Since `e = d(x*, c) <= hx + d_K(m, q) + h_c <= hx + ⌊g/2⌋ + h_c`, we get

    h_c >= δ - ⌊g/2⌋ >= 1,

so `c ∉ V(K)`; let `B_c` be its branch.

**Proposition 4.1 (narrow `B_c`).** If `B_c` is narrow (door `a`), then
`ρ̂(K) >= r >= e` — contradicting the rigid regime. Hence in the rigid regime,
`δ <= ⌊g/2⌋` whenever `B_c` is narrow.

*Proof.* `ecc(a) >= r`, so some `y` has `d(a, y) >= r`. If `y ∉ B_c` then by
Lemma N(i) every `c → y` path exits through `a`, so
`d(c, y) = d(c, a) + d(a, y) >= h_c + r > r = ecc(c)`, absurd. So `y ∈ B_c`, and
by Lemma N(iii) `τ_z(y) = d(y, a) >= r` for any `z ≠ a`. With (F0), `r >= e`. ∎

(The same proof, using Lemma N(iii)'s all-girth validity, works verbatim for
`g = 3, 4` with `τ'`.)

**Bridge A-wide (TESTED, unproved).** In the rigid regime with `B_c` wide,
`δ <= ⌊g/2⌋` still holds.

*Tested:* battery5 `BR-A` recorded every rigid-regime instance with
`δ > ⌊g/2⌋`: there were **none** in 8385 graphs (so a fortiori none with wide
`B_c`). Outside the regime the BIG case is real and is closed by Step 1:
battery2/`BIG-T` (exists `z, u ∈ B_c`: `τ_z(u) >= e`): 1181/1181, min slack +1;
battery1 `BIG-hc` (the inequality `h_c >= δ - ⌊g/2⌋`): 0 violations.

---

## 5. Theorem (g >= 5)

**Theorem 5.1.** Let `G` be connected cyclic with `g >= 5` and `e >= 1`, and let
`K` be ANY shortest cycle. Assume Bridge A-wide and Bridge B. Then `e <= M(K)`.

*Proof.* If `ρ̂(K) >= e`, Proposition 1. Otherwise the rigid regime holds; then
`δ >= 1` (Fact 2.1) and `δ <= ⌊g/2⌋` (Prop. 4.1 + Bridge A-wide). Build the
window `W0` (§2); every `σ ∈ W0` is noncentral with far vertices in branches
(Facts 2.2, 2.3); Bridge B supplies a narrow cover avoiding `B_x`; Lemmas
CAP/COUNT/Z assemble a witness of mass `>= e`. ∎

Note the per-K quantification — consistent with the observed truth of the
`E_forall` variant at `g >= 4` (INTEL; wave2 0 violations).

**Bridge statements to close later.**
* **Bridge A-wide** — §4. Candidate route: in the regime, every K-vertex should
  have a center within `⌊g/2⌋` (then `e <= hx + d(m, C) <= hx + ⌊g/2⌋` directly);
  this reformulation is what battery data suggests but is unproved for wide `B_c`.
* **Bridge B** — §3. Two independent sub-claims:
  (B1) no window position has ALL far vertices inside `B_x`
  (outside the regime this fails 725 times and is exactly compensated by
  `ρ̂(B_x-donation) >= e`, battery3 725/725 — the dichotomy is razor-sharp);
  (B2) in the regime, wide branches host no far vertex of any window position.

---

## 6. g = 4

Architecture identical; all donations use `τ'` (§1.1). `K = k_0 k_1 k_2 k_3`,
antipodal pairs `P_0 = {k_0, k_2}`, `P_1 = {k_1, k_3}`; `r >= 2`, `κ = 2r - 3 >= 1`.

Component constraint sets (from TA): a valid tail whose terminal is
single-attached at `a` requires `z ≠ a`; a tail whose terminal is pair-attached
(pair `P_i`) requires `z ∈ P_i`. Narrow-branch tails are always of the first kind
(Lemma N(iii) holds at every girth).

* **Step 1**: if some valid single donation has `τ'_z(u) >= e`, done
  (Lemma M with the single component).
* **BIG (δ >= 3)**: `h_c >= δ - 2 >= 1`; narrow `B_c` closed by Prop. 4.1
  (all-girth version). Wide `B_c`: **Bridge A4** (analog of A-wide).
* **δ = 1**: `W0 = {m}`; a far vertex in a narrow branch `B ≠ B_x`
  (**Bridge B4**) forces `d_K(m, a_B) + D_B >= r + 1` (Lemma N(ii)), so
  `D_B >= r + 1 - d_K(m, a_B) >= r - 1 >= 1`, and the mass is
  `hx + D_B >= hx + 1 = e`.
* **δ = 2**: `|W0| = 3`; Lemma CAP + COUNT verbatim
  (`Σ max(0, 2D_B - κ) >= 3` with `κ >= 1` forces `Σ D_B >= 2 = δ`).
* **z-compatibility (Bridge C4, TESTED unproved)**: the `<= 3` used components
  each impose `z ≠ a` (3 allowed values) or `z ∈ P_i` (2 allowed values); two
  pair-constraints with different pairs conflict. The battery shows a valid
  selection of tails/z always exists — for EVERY shortest cycle `K`; the written
  resolution (rerouting a tail, or exploiting that a pair-attached vertex `w`
  yields the alternative shortest cycle `(K \ {k_j}) ∪ {w}`) remains to be
  proved.

*Tested:* battery5 `G4-existsK` **and** `G4-allK`: 630/630 graphs, 0 failures
(the whole g=4 case tree, end-to-end, per-K, with exact `τ'` donations and
z-enumeration). Also INTEL: `E_forall` at `g = 4`: 0 violations corpus-wide.

## 7. g = 3

`K` a triangle; `K \ {z}` is a single edge `{p, q}`. Valid components send
exactly one edge into `{p, q}`; a vertex adjacent to all of `K` can never appear
in a witness `F`; a vertex adjacent to exactly `{p, q}`... a terminal adjacent to
two of `K` requires `z` to be one of them (as in g=4). `⌊g/2⌋ = 1` so `δ <= 1`
in the (bridged) rigid regime and `W0 = {m}`.

* **Switch Lemma (proved = Lemma TA, g=3 case).** If `w ∉ V(K)` has two
  neighbours `x, y ∈ V(K)`, then `{w, x, y}` is another shortest cycle.
* **Step 1 / BIG / δ=1** exactly as in §6 with `τ'` (narrow branches again fully
  well-behaved by Lemma N).
* **Bridge D3 (K-selection; TESTED unproved).** There EXISTS a shortest triangle
  `K` for which the assembly succeeds. Per-K this is FALSE (41/3114 corpus
  graphs have a bad triangle; INTEL's `E_forall` counterexample F~AGO confirms);
  the proof must iterate the Switch Lemma to a good triangle. A natural
  candidate potential (maximize `Σ` of donations reachable from `K`; each switch
  strictly increases it) is validated implicitly by the exists-K data but not
  yet by a written monotonicity argument.

*Tested:* battery5 `G3-existsK`: 3114/3114 graphs, 0 failures;
`G3-allK` fails on exactly 41 graphs (the expected sharp edge).

---

## 8. Remaining gaps (all falsifier-tested, no counterexample known)

| Bridge | Statement (exact) | Evidence |
|---|---|---|
| A-wide | rigid regime, `B_c` wide ⟹ `δ <= ⌊g/2⌋` (`g >= 5`) | 0 rigid-regime BIG instances / 8385 graphs |
| B | rigid regime ⟹ every `σ ∈ W0` has a far vertex in a narrow branch ≠ `B_x` (`g >= 5`) | 1949/1949 windows, 0 viol |
| A4/B4 | the `g = 4` analogues of A-wide/B | subsumed in 630/630 end-to-end |
| C4 | `g = 4` z-compatibility resolution | 630/630 per-K end-to-end |
| D3 | `g = 3` K-selection via Switch Lemma | 3114/3114 exists-K |

Everything else in this document is fully proved: Lemmas M, R, TA, τ, S, N, CAP,
COUNT, Z, Facts 2.1–2.3, Proposition 1, Proposition 4.1, the `h_c` inequality,
and Theorem 5.1 modulo the bridges.

## 9. Test evidence index (all seeds 20260718/20260719/20260720, exact integer arithmetic)

Scripts in `problems_external/wowii_144/proverA/`:
* `battery1.py` / `battery1_results.json` — TR, TE, TA, C1, CASE0, BIG-hc,
  naive-generalization falsifiers (S6g/TENT/CAP/MASS — these falsified the
  pendant-tree abstraction and motivated §1). 7062 cyclic `e>=1` graphs.
* `battery2.py`, `battery3.py` — τ-machinery at `g>=5`: SUCC 6288 / min slack 0;
  TENT5 725 failures ⟹ FALLBACK-BX 725/725; BIG-T 1181 / min slack +1.
* `battery4.py` — rigid regime: STEP1 3711; R-O1/R-O2/R-O3 1949 each, 0 viol,
  min slack 0; STRAND-LB sharp; R-WIDE (`wide in regime ⟹ e >= ⌈g/2⌉`) 0 viol.
* `battery5.py` / `battery5_results.json` — BR-A (0 instances), BR-B 1949/1949,
  ASM 1688/1688 min slack 0, G4 630/630 (exists-K = all-K), G3 3114/3114
  exists-K, 41 all-K failures.
* `inspect1.py`, `inspect2.py` — structure discovery (optimal witness forests;
  BIG/FBX statistics that identified `T >= r + 1` and `T >= hx + h_c + ⌊g/2⌋`,
  both min-slack-0 candidates for closing Bridge A-wide).

Reference M(K) implementation: `wave2/lemma_e_tests.py::M_of_cycle` (exact
subset enumeration); `E_exists` baseline: 0 violations / 8219 graphs (wave2).

## 10. Lean-formalization notes (hardest steps)

1. `Lemma R` — easy (BFS tree = `SimpleGraph.dist` + fundamental cycle).
2. `Lemma TA` — easy given the isometry API for shortest cycles (T3 exists in
   the 141/143 toolkit).
3. `Lemma τ/S/N` — medium: "shortest path to a set in `G − z`" needs a small
   `distToSet`-style API on induced subgraphs; the validity checks are local.
4. `Lemma M` — already compiled in spirit (tree-attach primitive was prestaged
   for 144; vertex/edge counting argument).
5. `CAP/COUNT/Z` — the arc/ball arithmetic on `ZMod g` plus a finite counting
   argument; medium, all decidable-finite.
6. The bridges (once proved on paper) and the g=3 switch induction (needs a
   termination measure) will be the hard Lean steps; everything else is
   assembly.
