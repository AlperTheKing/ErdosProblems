# WOWII / Graffiti.pc Conjecture 144 — Angle B (split route)

**Date:** 2026-07-18.  **Scope:** the open branch of C144 (`G` connected, cyclic, `e ≥ 1`).
**Deliverables:** (1) a complete proof of **P2**: `tree(G) ≥ diam(G) + ⌈g/2⌉ − 1`;
(2) the residual lemma (`e > diam − ⌊g/2⌋ ⟹ ∃ shortest cycle K with e ≤ M(K)`), developed
as a chain of proved lemmas plus an assembly step; the assembly is **fully proved in the
conflict-free, single-conflict and affordable-truncation regimes** and is **not yet closed
in general** — every remaining configuration is stated precisely in §II.9 (Gap list) with
its exact verification status.  Piece (1) is complete; piece (2) is not fully closed.

Mechanical verification (exact integer arithmetic throughout):
- `proverB/verify_P2_construction.py` — the P2 construction re-executed and checked on
  22 231 (K, diametral-pair) instances over 5 501 corpus graphs with g ≥ 5, D > ⌊g/2⌋
  (atlas + families + adversarial + traps + random + forced-girth + sharp instances):
  **0 failures**, all six proof branches exercised (A: 153, B1: 21 594, B2: 284,
  B3-01/10/11: 80/47/73), 1 498 exhaustive cross-checks of `tree(G)` itself.
- `proverB/residual_probe3.py`, `proverB/residual_probe4.py` — every lemma of Part II
  checked on 8 797+ corpus graphs (734 residual-case graphs, 869 residual K-instances):
  P0/R0 0 failures, window/tent/capacity 0 failures, girth cross-edge laws 0 violations,
  assembly search 547/547.

Throughout, `G = (V,E)` is a finite simple connected graph with a cycle, `g = girth(G) ≥ 3`,
`s := ⌊g/2⌋`, `d` the graph distance, `D = diam(G)`, `r = radius(G)`, `C = center(G)`
(min-eccentricity vertices), and — following the FC formalization —
`e := ecc(G, C) = max_{v∉C} d(v, C)` (`0` if `C = V`).  `t := tree(G)` is the largest number
of vertices of an induced subgraph that is a tree.  `K` always denotes a *shortest* cycle,
`V(K)` its vertex set, and for `x, y ∈ V(K)`, `d_K(x,y)` the arc-distance along `K`.

## 0. Accepted background facts

These are proved in the compiled Lean skeleton / intel packet and re-proved here briefly
for self-containment.

**T1 (geodesics).** Any shortest `u–v` path `P = p_0 … p_L` induces a path: if
`p_i ~ p_j` with `j − i ≥ 2` then `d(p_i, p_j) = j − i ≥ 2` would be `≤ 1`, a
contradiction.  Hence `t ≥ D + 1` and `t ≥ L + 1` for every geodesic of length `L`.

**T2 (cycle minus a vertex).** `K` is chordless (a chord splits `K` into a strictly
shorter cycle), so `K − z` induces a path with `g − 1` vertices; hence `t ≥ g − 1`.

**T3 (isometry).** Every shortest cycle is isometric: `d(x,y) = d_K(x,y)` for
`x, y ∈ V(K)`.  (A shorter outside route between two `K`-vertices would close a cycle
shorter than `g` with the shorter arc.)  In particular every arc of `K` with at most
`⌊g/2⌋ + 1` vertices is a geodesic.

**F1 (girth–radius).** `g ≤ 2r + 1`.  *Proof.*  Let `c` be a central vertex and `T` a BFS
tree from `c` (depth ≤ r).  `G` has a cycle, so it has an edge `xy ∉ T`.  The `T`-paths
from `x` and from `y` to `c` first meet at some vertex `w`; together with `xy` they close
a (simple) cycle of length `≤ (r − d(c,w)) + (r − d(c,w)) + 1 ≤ 2r + 1`. ∎
Consequently `r ≥ s` for every cyclic graph, since `2r+1 ≥ g ≥ 2s`.

**F2.** `e ≤ r` (for any `v`, `d(v,C) ≤ d(v,c₀) ≤ ecc(c₀) = r`), and if `e ≥ 1` then
`C ≠ V`, some vertex has eccentricity `≥ r+1`, so `D ≥ r + 1`.

**Lemma M** (accepted tool; proof from the intel packet).  For a shortest cycle `K` let
`M(K)` be the maximum of `|F|` over sets `F ⊆ V ∖ V(K)` such that `G[F]` is a forest and
for some `z ∈ V(K)` **every** connected component of `G[F]` sends **exactly one** edge
into `K − z` (edges counted with multiplicity over vertex pairs; edges into `z` itself
are unrestricted; every component must send at least one edge into `K − z`).  Then

    t ≥ (g − 1) + M(K).

*Proof.*  `G[V(K) ∖ {z}]` is an induced path with `g−1` vertices and `g−2` edges (T2).
Let `F` attain `M(K)` with witness `z`, with components `F_1, …, F_c`.  The induced
subgraph on `(V(K) ∖ {z}) ∪ F` has `(g−1) + |F|` vertices, and its edges are: the `g−2`
path edges, the edges inside the components (`|F| − c` in total, each component being a
tree — a component with a cycle is impossible since `G[F]` is a forest), and exactly `c`
edges between `F` and the path (one per component).  Total `(g−1) + |F| − 1`, and the
graph is connected (each component hooks onto the path).  A connected graph with vertex
count minus one edges is a tree; it is induced by construction. ∎

---

# Part I.  P2:  `t ≥ D + ⌈g/2⌉ − 1` for every connected cyclic `G` — COMPLETE

**Theorem P2.**  Let `G` be connected with a cycle, `g = girth`, `D = diam`.  Then
`t ≥ D + ⌈g/2⌉ − 1`.

### I.1  Trivial regimes

*If `g ∈ {3,4}`*: `⌈g/2⌉ − 1 = 1`, and `t ≥ D + 1` is T1. ∎
*If `D ≤ s`*: `D + ⌈g/2⌉ − 1 ≤ s + ⌈g/2⌉ − 1 = g − 1 ≤ t` by T2 (using
`s + ⌈g/2⌉ = g`). ∎

For the rest of Part I assume `g ≥ 5` and `D ≥ s + 1`.  Since
`(g−1) + (D−s) = D + ⌈g/2⌉ − 1`, by Lemma M it suffices to produce, for a shortest
cycle `K`, a valid pair `(F, z)` with `|F| ≥ D − s`.  We prove this for **every**
shortest cycle `K` and **every** diametral geodesic `P = p_0 … p_D` (`d(p_0,p_D) = D`).

### I.2  Two local lemmas (g ≥ 5)

**Lemma N′ (unique cycle neighbour).**  If `g ≥ 5` and `w ∉ V(K)`, then `w` has at most
one neighbour on `K`.
*Proof.*  Suppose `w ~ x, y`, `x ≠ y ∈ V(K)`, and let `c = d_K(x,y) ≤ s`.  If `c = 1`,
`{w,x,y}` is a triangle, so `g ≤ 3`.  If `c ≥ 2`, the short arc from `x` to `y` plus the
path `x w y` is a simple cycle of length `c + 2 ≤ s + 2 < g` (since `g ≥ 5` gives
`s + 2 ≤ g − 1`, as `s ≤ g − 3` for `g ≥ 5`... explicitly: `g − (s+2) = ⌈g/2⌉ − 2 ≥ 1`
for `g ≥ 5` unless `g = 5`, where `⌈g/2⌉ − 2 = 1 ≥ 1` as well).  Contradiction. ∎

*(At `g = 4`: the same argument shows a vertex outside `K` has at most two neighbours on
`K` and, if two, they are antipodal on the 4-cycle — used only in Part II.)*

**Lemma N (unique geodesic neighbour).**  If `g ≥ 5`, `P` is a geodesic and `w ∉ P`,
then `w` has at most one neighbour on `P`.
*Proof.*  If `w ~ p_i, p_j`, `i < j`, then `j − i = d(p_i,p_j) ≤ 2` through `w`.
`j − i = 1` gives a triangle; `j − i = 2` gives the 4-cycle `w p_i p_{i+1} p_{i+2}`
(its four vertices are distinct and all four edges present, regardless of whether
`w ~ p_{i+1}`, which would give a triangle).  Both contradict `g ≥ 5`. ∎

### I.3  The construction

Fix `K`, `P` as above.  Let `I := { i : d(p_i, K) ≤ 1 }`.

**Case A: `I = ∅`.**  Let `δ := d(P, K) = min_{i} d(p_i, K) ≥ 2`, attained at `p* = p_{i*}`,
and let `R = r_0 r_1 … r_δ` be a geodesic from `r_0 = p*` to a nearest `K`-vertex
`r_δ = k*`.  Minimality of `δ` forces `d(r_j, P) = j` and `d(r_j, K) = δ − j` for all `j`
(otherwise `d(P,K) < δ`).  Consequences: `r_1, …, r_{δ−1} ∉ P ∪ V(K)`; `r_j` (`1 ≤ j ≤ δ−1`)
has no neighbour on `P` except (for `j = 1`) exactly one, namely `p*` (Lemma N, and
`r_1 ~ r_0 = p*`); no `r_j` with `j ≤ δ−2` has a neighbour on `K`; `r_{δ−1}` has exactly
one `K`-neighbour, `k*` (Lemma N′); and `R` is an induced path (a geodesic).

Set `F := P ∪ {r_1, …, r_{δ−1}}`.  Then `G[F]` is connected — it is the induced path `P`
with the induced path `r_1 … r_{δ−1}` pendant at `p*` — and acyclic: the only `P`-to-`R`
adjacency is `p* r_1` and `R` is induced.  Thus `G[F]` is a single induced tree with
`(D+1) + (δ−1) = D + δ ≥ D + 1` vertices whose **only** edge into `K` is `r_{δ−1} k*`
(for `δ = 2` this reads `F = P ∪ {r_1}` with the single edge `r_1 k*`).  Choose any
`z ∈ V(K) ∖ {k*}`.  The pair `(F, z)` is valid for Lemma M and
`|F| ≥ D + 1 > D − s`. ∎ (Case A)

**Case B: `I ≠ ∅`.**  Let `l := min I`, `ρ := max I`, `δ_l := d(p_l, K) ∈ {0,1}`,
`δ_ρ := d(p_ρ, K) ∈ {0,1}`.

*Observation B0.*  `δ_l = 0` forces `l = 0`: if `l ≥ 1` and `p_l ∈ V(K)` then
`d(p_{l−1}, K) = 1`, contradicting minimality of `l`.  Symmetrically `δ_ρ = 0` forces
`ρ = D`.

Define `k_a` and `k_b`:  if `δ_l = 1`, `k_a` is the *unique* (Lemma N′) `K`-neighbour of
`p_l`; if `δ_l = 0` (so `l = 0`), `k_a := p_0 ∈ V(K)`.  Symmetrically `k_b` from `p_ρ`.

*Observation B1 (hug-span).*  `ρ − l = d(p_l, p_ρ) ≤ δ_l + d(k_a, k_b) + δ_ρ
≤ δ_l + s + δ_ρ`, using T3 (`d(k_a,k_b) = d_K(k_a,k_b) ≤ s`).

**Subcase B1: `ρ − l ≥ 2`.**  Put

    C1 := p_0 … p_l   if δ_l = 1   (l+1 vertices);    C1 := ∅  if δ_l = 0  (then l = 0)
    C2 := p_ρ … p_D   if δ_ρ = 1   (D−ρ+1 vertices);  C2 := ∅  if δ_ρ = 0  (then ρ = D)

and `F := C1 ∪ C2`, `z :=` any vertex of `V(K) ∖ {k_a, k_b}` (exists, `g ≥ 5 > 2`).

Validity.  Vertices `p_i` with `i < l` or `i > ρ` have `d(p_i,K) ≥ 2`, hence no
`K`-edges; `p_l` (when `δ_l = 1`) has exactly the edge to `k_a`; likewise `p_ρ`.  So each
nonempty `C_i` is an induced subpath of `P` sending exactly one edge into `K`, at
`k_a ≠ z` resp. `k_b ≠ z`.  `C1` and `C2` are non-adjacent: their index gap on the
induced path `P` is `≥ ρ − l ≥ 2`.  Hence `G[F]` is a forest whose components are exactly
the nonempty `C_i`, and `(F, z)` is valid.  Count, using B1 and `x − [x=1] = 0` for
`x ∈ {0,1}`:

    |F| = (l + [δ_l = 1]) + (D − ρ + [δ_ρ = 1])
        = D − (ρ − l) + [δ_l=1] + [δ_ρ=1]
        ≥ D − s − (δ_l − [δ_l=1]) − (δ_ρ − [δ_ρ=1]) = D − s.        ∎ (B1)

**Subcase B2: `ρ = l`.**  If `δ_l = 0` then `l = 0 = ρ = D` (B0), i.e. `D = 0`, absurd.
So `δ_l = 1`: the single near vertex `p_l` is at distance 1.  Take `F := P` (one
component; its only `K`-edge is `p_l k_a`) and `z ∈ V(K) ∖ {k_a}`.  Valid, and
`|F| = D + 1 > D − s`. ∎ (B2)

**Subcase B3: `ρ = l + 1`.**  Four sign patterns:

- `(δ_l, δ_ρ) = (1,1)`.  `k_a ≠ k_b`, else `p_l p_{l+1} k_a` is a triangle (`g = 3`).
  Take `F := P`, `z := k_a`.  `P` is one component; its edges into `K` are `p_l k_a`
  (into `z`, unrestricted) and `p_{l+1} k_b` — exactly one into `K − z`.  Valid;
  `|F| = D + 1`. ∎
- `(0,1)`: `l = 0`, so `p_0 ∈ V(K)`; `p_1`'s unique `K`-neighbour is `p_0`.  Take
  `F := p_1 … p_D` (one component, single `K`-edge `p_1 p_0`), `z ≠ p_0`.  `|F| = D`. ∎
- `(1,0)`: mirror image.  `|F| = D`. ∎
- `(0,0)`: `l = 0` and `ρ = D` force `D = 1`; but a connected graph of diameter 1 is
  complete, so `g = 3 < 5`.  Impossible. ∎ (B3)

All cases produce a valid `(F, z)` with `|F| ≥ D − s`; Lemma M gives
`t ≥ (g−1) + (D−s) = D + ⌈g/2⌉ − 1`.  **Theorem P2 is proved.** ∎

**Corollary P2′.**  For `g ≥ 5`, *every* shortest cycle `K` satisfies
`M(K) ≥ D − ⌊g/2⌋` (the construction above never chose `K` or `P` specially).

**Verification.**  `proverB/verify_P2_construction.py` re-runs exactly this construction
(including all internal assertions: Lemma N, N′, B0, the `(1,1)` triangle exclusion, the
`(0,0)` impossibility) on every (shortest cycle, diametral pair) combination of the
corpus and validates the resulting `(F,z)` and the induced tree `(K−z) ∪ F` directly:
**22 231 instances, 0 failures**; on all graphs with `n ≤ 15` the final inequality was
also cross-checked against the exhaustive `tree(G)`.

---

# Part II.  The residual case — proved skeleton, assembly not fully closed

## II.0  Arithmetic reduction and the shape of the residual case

**Proposition A.**  Let `G` be connected cyclic with `e ≥ 1`.  If `e ≤ D − s`, then C144
holds:  by Theorem P2, `t ≥ D + ⌈g/2⌉ − 1 = (g−1) + (D − s) ≥ (g−1) + e`. ∎

So exactly the following **residual case** remains:

    (R)    e ≥ 1   and   e ≥ D − s + 1.

**Proposition B (rigidity of (R)).**  In case (R):
`r + 1 ≤ D ≤ e + s − 1` and `r − s + 2 ≤ e ≤ r` (F2).  Consequently:
- (R) is **empty for `g = 3`** (`s = 1` gives `e ≥ r + 1 > r`);
- for `g ∈ {4,5}` (`s = 2`): `e = r` and `D = r + 1` exactly. ∎

Everything below fixes an arbitrary shortest cycle `K` (the data indicate every `K`
works for `g ≥ 4`, matching the tested `E_forall`), writes `h(v) := d(v, V(K))`,
and calls the components of `G − V(K)` *branches* (each branch's neighbourhood lies in
`V(K)`).

## II.1  Deterministic tails

For `v ∉ V(K)` with `h(v) ≥ 2` let `desc(v)` be the minimum-index neighbour `w` of `v`
with `h(w) = h(v) − 1` (exists: `v` lies on a geodesic to `K`).  The **tail**
`T(v) := (v, desc(v), desc²(v), …)` down to a vertex of height 1; `|T(v)| = h(v)`.
Let `Katt(v) ⊆ V(K)` be the set of `K`-neighbours of the bottom vertex of `T(v)`.

**Lemma T (tail basics).**  For `g ≥ 4`:
1. Heights are 1-Lipschitz: `u ~ w ⟹ |h(u) − h(w)| ≤ 1`.
2. `T(v)` is an induced path, contains exactly one vertex of each height `1..h(v)`, and
   its only edges into `K` are from its bottom vertex; `|Katt(v)| = 1` if `g ≥ 5`
   (Lemma N′), and at `g = 4`, `|Katt(v)| ∈ {1,2}` with a 2-element `Katt` being an
   antipodal pair of the 4-cycle.
3. (Suffix coherence)  If `u ∈ T(v)` then `T(u)` is the bottom part of `T(v)`.  Hence two
   tails that share any vertex share their bottom vertex, and so have equal `Katt`.
4. (Automatic disjointness)  Tails whose `Katt` sets differ are vertex-disjoint; for
   `g ≥ 5`, tails with distinct attachments `ρ ≠ ρ′` are vertex-disjoint.
*Proofs.* 1 is trivial.  2: consecutive tail vertices differ by one in height; two tail
vertices with height gap ≥ 2 are non-adjacent by 1; heights `p, p−1` occur once each, and
those two vertices are consecutive.  A non-bottom vertex has height ≥ 2, so no
`K`-neighbour.  3: `desc` is a function of the vertex alone.  4: from 3. ∎

**Lemma R0 (single tail; all `g ≥ 4`).**  If some vertex has `h(y) ≥ e`, then
`M(K) ≥ e`, hence `t ≥ g − 1 + e`.
*Proof.*  `F := T(y)` is one induced-path component (Lemma T.2).  Its edges into `K` all
leave the bottom vertex: one edge (`g ≥ 5`, or `|Katt| = 1`), or two edges into an
antipodal pair `{κ, κ̄}` (`g = 4`).  Choose `z ∉ Katt(y)` in the first case, `z := κ` in
the second; in both cases the component sends exactly one edge into `K − z`.  Lemma M
applies; `|F| = h(y) ≥ e`. ∎  *(Verified: probe3 "P0", 0 failures across all girths.)*

From here on assume **(R1): every vertex has `h(v) ≤ e − 1`.**

## II.2  Realizer, window, tents

Fix an `e`-realizer `x*` (i.e. `d(x*, C) = e`) of **maximum height** `h := h(x*)`; note
`h ≥ 0` (the realizer may lie on `K`, in which case its "tail" is empty).  Let `m` be a
nearest `K`-vertex to `x*` (for `h ≥ 1` take `m ∈ Katt(x*)`; for `h = 0`, `m = x*`), and

    δ* := e − h ≥ 1        (by (R1)).

**Lemma W (window).**  Every `σ ∈ V(K)` with `d_K(σ, m) ≤ δ* − 1` is noncentral.
Moreover if `C ∩ V(K) ≠ ∅` then `δ* ≤ s` — in fact then *every* realizer `x` satisfies
`e − h(x) ≤ s`.
*Proof.*  If `σ ∈ C`: `e = d(x*,C) ≤ d(x*,σ) ≤ h + d(m,σ) ≤ h + d_K(σ,m) ≤ e − 1`,
absurd (T3 for `d(m,σ) ≤ d_K`).  If `q ∈ C ∩ V(K)`: `e ≤ d(x, q) ≤ h(x) + d_K(m_x, q)
≤ h(x) + s`. ∎

Define the **window** `W := { σ ∈ V(K) : d_K(σ,m) ≤ δ* − 1 }`.  When `δ* ≤ s`,
`|W| = 2δ* − 1 ≤ 2s − 1 ≤ g − 1`: an honest arc.  *(The case `δ* > s`, only possible when
`C ∩ V(K) = ∅`, is Gap R1b, §II.9.)*

**Lemma S6′ (the x-tail never covers).**  For every `σ ∈ W`,
`d_K(σ, m) ≤ δ* − 1 < r + 1 − h`; equivalently `h < r + 2 − δ*` — indeed
`h + δ* = e ≤ r` (F2).  (Interpretation: in the covering language of Lemma CAP below,
the tail of `x*` itself is never a tent for any window position.  A *deeper* vertex
attached at `m` can be one; see Gap M4.) ∎

**Lemma TENT.**  For every `σ ∈ W` there exists `y ∉ V(K)` with

    d_K(σ, ρ) ≥ r + 1 − h(y)     for every ρ ∈ Katt(y).

*Proof.*  `σ` is noncentral (Lemma W), so `ecc(σ) ≥ r+1`: pick `y` with
`d(σ,y) ≥ r+1`.  `y ∉ V(K)` since `d(σ, k) ≤ s ≤ r` for `k ∈ V(K)` (T3, F1).  For any
`ρ ∈ Katt(y)`: `d(σ,y) ≤ d(σ,ρ) + 1 + (h(y) − 1) = d_K(σ,ρ) + h(y)`. ∎

## II.3  Posts, capacity, cover counting

For `ρ ∈ V(K)` let `H(ρ) := max{ h(y) : ρ ∈ Katt(y) }` (0 if none), and let `Y(ρ)` be a
maximizer (the **post** at `ρ`).  Say the post at `ρ` **covers** `σ ∈ W` iff
`d_K(σ,ρ) ≥ r + 1 − H(ρ)`.  Lemma TENT says: **the posts cover `W`.**

**Lemma CAP (capacity).**  A post `(ρ, H)` with `H ≤ r` (automatic under (R1):
`H ≤ e − 1 ≤ r − 1`) covers at most
`max(0, 2H − (2r + 1 − g)) ≤ 2H` positions of the whole cycle.
*Proof.*  Covered positions form the complement of the arc-ball of radius `r − H`
around `ρ`, which has `min(g, 2(r−H)+1)` vertices; the complement has
`max(0, g − 2(r−H) − 1)` and `g ≤ 2r+1` (F1). ∎

**Lemma COVER (counting).**  If `δ* ≤ s`, then for every set `R ⊆ V(K)` of posts
covering `W`:  `Σ_{ρ∈R} H(ρ) ≥ δ*`.
*Proof.*  `Σ_{ρ∈R} |cov(ρ) ∩ W| ≥ |W| = 2δ* − 1` and each term is `≤ 2H(ρ)` (Lemma CAP);
divide by 2 and round up (`H` integers). ∎

In particular, choosing an inclusion-minimal cover `R` **not using the post at `m`**
(possible in every observed instance — "cover_needs_mpost = 0"; the corner where it might
fail is Gap M4) and adding the post at `m` (height `H(m) ≥ h`, by definition since
`x*` itself is attached at `m` when `h ≥ 1`; when `h = 0`, i.e. the realizer lies on `K`,
no `m`-tail is needed at all because then `e = δ*` and the cover alone already counts
`Σ H ≥ δ* = e`), the **full-height total** of the family

    𝔉 := { deepest tail at m } ∪ { deepest tail at ρ : ρ ∈ R }

is `H(m) + Σ_{ρ∈R} H(ρ) ≥ h + δ* = e`.  By Lemma T.4 these tails are pairwise
vertex-disjoint (distinct attachments; `g ≥ 5`).  What can fail is **edge interference**
(cross edges between tails) and the choice of `z`.  The next section gives the exact
laws governing interference.

## II.4  Cross-edge laws

Let `T_i, T_j` be disjoint tails attached at `ρ_i ≠ ρ_j`, and let a **cross edge** be
`ab ∈ E` with `a ∈ T_i, b ∈ T_j`; write `α = h(a), β = h(b)`.

**Lemma X1 (girth law).**  Every cross edge satisfies
`α + β ≥ g − 1 − d_K(ρ_i, ρ_j)`.
*Proof.*  Walk from `ρ_i` up `T_i` to `a` (α edges, counting the attachment edge),
cross to `b`, down `T_j` to `ρ_j` (β edges), and back along a shortest arc
(`d_K(ρ_i,ρ_j)` edges).  All vertices are distinct (tails disjoint, tails avoid `V(K)`,
arc inside `V(K)`), so this is a simple cycle of length `α + β + 1 + d_K(ρ_i,ρ_j) ≥ g`. ∎

**Lemma X2 (diagonality).**  `|α − β| ≤ 1` (Lemma T.1). ∎

**Lemma X3 (matching).**  For `g ≥ 5` a vertex `a ∈ T_i` has at most one neighbour on
`T_j`:  two neighbours `b, b′ ∈ T_j` satisfy `|h(b) − h(b′)| ≤ 2` (through `a`), so they
are within two steps along the path `T_j`, and the cycle through `a` and the `T_j`-path
has length `≤ 4 < g`. ∎

**Lemma X4 (multi-cross forces bulk).**  If there are two distinct cross edges
`(α₁,β₁), (α₂,β₂)` between `T_i` and `T_j`, then `H_i + H_j ≥ g`, where `H_i = |T_i|`.
*Proof.*  The cycle through the two cross edges and the two tail segments has length
`|α₁ − α₂| + |β₁ − β₂| + 2 ≥ g`; and `|α₁−α₂| ≤ H_i − 1`, `|β₁−β₂| ≤ H_j − 1`. ∎
*(Under (R1), `H ≤ e − 1`, so multi-cross pairs require `e ≥ (g+2)/2`; none occurred in
8 797 corpus graphs.)*

## II.5  The two repair tools

**Lemma U (union).**  Let `T_i, T_j` be disjoint tails (attachments `ρ_i ≠ ρ_j`,
`g ≥ 5`) with **exactly one** cross edge.  Then `G[T_i ∪ T_j]` is an induced tree with
`H_i + H_j` vertices whose edges into `K` are exactly the two bottom edges (at `ρ_i` and
`ρ_j`).  Consequently, in a Lemma-M family it is a single component that is valid for
any `z ∈ {ρ_i, ρ_j}` (the other attachment edge is the component's unique edge into
`K − z`).
*Proof.*  Vertices `H_i + H_j`; edges `(H_i −1) + (H_j −1) + 1` = vertices − 1;
connected; induced because the tails are induced, non-`K` adjacencies between them are
exactly the one cross edge, and only bottoms touch `K` (Lemma T.2). ∎

**Lemma TR (truncation).**  For `u ∈ T(v)`, the bottom part `T(u) ⊆ T(v)` is again a
tail with the same attachment.  If tails `T_i, T_j` have all cross edges at height pairs
`(α, β)` with `α + β ≥ L` (e.g. `L = g − 1 − d_K(ρ_i,ρ_j)`, Lemma X1 — or the exact
minimum over their cross edges), then the truncations to heights `t_i, t_j` with
`t_i + t_j ≤ L − 1` have **no** cross edge:  a surviving cross edge would have
`α ≤ t_i, β ≤ t_j`, so `α + β ≤ L − 1 < L`.  Truncation never creates edges. ∎

## II.6  Choice of `z`

The family uses attachments `{m} ∪ R` (all distinct: `m ∉ R` by the choice of `R` in
II.3, and cover posts have distinct positions).  `|R| ≤ |W| = 2δ* − 1` (minimality: each
post covers a position not covered by the others), so `|{m} ∪ R| ≤ 2δ* ≤ 2s ≤ g`.  If
`2δ* < g` — in particular whenever `g` is odd, or `δ* < s` — a free
`z₀ ∈ V(K) ∖ ({m} ∪ R)` exists.  The corner `g` even, `δ* = s`, `|R| = g − 1` is Gap Z
(never observed; largest observed minimal cover: 3). ∎(partial)

## II.7  Assembly — proved regimes

**Theorem R-partial.**  Assume (R), (R1), `g ≥ 5`, `δ* ≤ s`, a minimal cover `R`
avoiding the `m`-post, and a free vertex `z₀ ∈ V(K) ∖ ({m} ∪ R)` (II.6).  Let `𝔉` be the
family of deepest tails at `{m} ∪ R` and let its **conflict graph** have an edge `{i,j}`
when a cross edge joins `T_i, T_j`.  Then `M(K) ≥ e` holds in each of the following
regimes:

**(AL0) No conflicts.**  Take `F = ⋃𝔉`, `z = z₀`.  Every component is a tail with its
single bottom edge into `K − z₀`; `|F| = H(m) + Σ_R H(ρ) ≥ h + δ* = e` (II.3). ∎

**(AL1) Exactly one conflict pair, single-cross.**  Let the pair be `{T_i, T_j}` with
one cross edge.  Take `F = ⋃𝔉` but with `T_i ∪ T_j` as one component (Lemma U) and
`z := ρ_i`.  All other components are tails attached at their own `ρ ∉ {ρ_i}` (distinct
attachments), each sending its one edge into `K − z`; the union component sends exactly
one (at `ρ_j`).  `|F|` is the same full total `≥ e`. ∎

**(AL2) Affordable truncation.**  If the conflict pairs `{i,j}` (with exact caps
`L_{ij} := min over their cross edges of (α+β)`) admit heights `t_i ≤ H_i` with
`t_i + t_j ≤ L_{ij} − 1` for each conflict pair and `Σ t ≥ e`, take truncated tails
(Lemma TR) and `z = z₀`.  Sufficient explicit criterion: the full-height total exceeds
`e` by at least the sum over conflict pairs of `(H_i + H_j) − (L_{ij} − 1)` (each pair's
truncation loss).  Note `L_{ij} − 1 ≥ g − 2 − d_K(ρ_i,ρ_j) ≥ g − 2 − s ≥ s − 1 ≥ δ* − 1`:
a single conflict pair alone already supports `δ* − 1`. ∎

**(AL3) One multi-cross pair, nothing else.**  A multi-cross pair has `H_i + H_j ≥ g`
(X4), so `max(H_i,H_j) ≥ ⌈g/2⌉ ≥ s ≥ δ*`.  Keep the taller tail alone from the pair (its
full height), drop the other; if the rest of the family is conflict-free this loses
`min(H_i,H_j)` from a total that exceeds `e` by ... — this regime closes only when the
slack covers `min(H_i,H_j)`; otherwise it falls under Gap AL. ∎(partial)

**Verification of the assembly search** (`residual_probe4.py`): over all 547 residual
R1 K-instances in the corpus, the exact search over truncations plus at most one union
(exactly the toolbox above) reached `e` in **547/547** cases (7 needed the union;
all 37 conflict pairs observed were single-cross; multi-cross never occurred;
minimal covers had size ≤ 3; a free `z` always existed).

## II.8  What Part II proves unconditionally

Putting §II.0–II.7 together:  in the residual case (R), with `K` any shortest cycle,

- `g = 3`: vacuous (Prop. B). **Closed.**
- Any `g ≥ 4` with some `h(v) ≥ e`: **closed** (Lemma R0).
- `g ≥ 5`, (R1), `δ* ≤ s`, cover avoiding the `m`-post, free `z`, and conflict structure
  in regimes AL0 / AL1 / AL2: **closed**, giving `M(K) ≥ e` and (with Lemma M)
  `t ≥ g − 1 + e`.

Together with Part I this proves C144 on every graph whose residual data fall in the
above regimes — and the probes indicate that this covers the entire tested corpus.

## II.9  GAP LIST (what is NOT yet proved)

Stated exactly, each with verification status (0 violations unless noted):

- **Gap AL (general assembly).**  Conflict graphs with ≥ 2 conflict pairs where
  truncation losses exceed the counting slack and the single union budget (one absorbed
  attachment per family, since `z` is global) cannot cover two vertex-disjoint
  conflicted pairs.  Includes all configurations with a multi-cross pair plus other
  conflicts (would need `H_i + H_j ≥ g`, hence `e ≥ (g+2)/2`).  *Observed frequency: 0
  of 547 instances (probe4: every instance fell in AL0/AL1/AL2).*
- **Gap R1b (no center on the cycle).**  If `C ∩ V(K) = ∅` the bound `δ* ≤ s` is not
  proved.  Sketched route: all of `V(K)` is then noncentral, take `W = V(K)`
  (`ΣH ≥ ⌈g/2⌉ ≥ s`) and add the tail of a center-nearest vertex (height `h_c ≥ 1`,
  `δ* ≤ s + h_c`); the interference/absorption bookkeeping for the extra tail is not
  done.  *Observed: 1 instance in 562, which nevertheless had `δ* ≤ s` and assembled.*
- **Gap M4 (cover needs the `m`-post).**  If some window position is coverable only by
  the post at `m` itself.  Constraints derived: it needs `H(m) ≥ r + 2 − δ*` together
  with (R1) `H(m) ≤ e − 1`, forcing `h ≥ r + 3 − 2δ*` and `δ* ≥ 3`; and if
  `δ* ≥ s` the accounting `total ≥ δ* + r − s ≥ e` closes it — open only for
  `3 ≤ δ* ≤ s − 1` with `h > r − s`.  *Observed: 0 of 547 (the 3 instances where the
  `m`-post could cover a window position still had `m`-free covers).*
- **Gap Z (no free `z`).**  `g` even, `δ* = s`, and a minimal cover of size `g − 1`
  whose attachments together with `m` exhaust `V(K)`.  *Observed: 0 (covers had ≤ 3
  posts).*
- **Gap G4 (girth-4 endgame).**  For `g = 4` under (R1) the engine's disjointness
  bookkeeping changes (`|Katt| = 2` possible: one tail can serve two posts, and `z` must
  be chosen inside a double attachment).  Prop. B pins `e = r`, `D = r + 1`, `s = 2`,
  `δ* ≤ 2`, so this is a small finite-window regime; not written down.  *Observed: all
  g=4 residual instances passed the probe4 assembly (which models double attachments
  exactly).*
- **Gap G5′ (`δ* > s` wrap window).**  Subsumed by Gap R1b (requires `C ∩ V(K) = ∅`).

Everything else in this document is complete.

---

## Appendix: file inventory

- `proverB/verify_P2_construction.py` — P2 constructive verifier (Part I).  Output:
  22 231 instances, 0 failures.
- `proverB/residual_explore.py` — TAILS(K) ≥ e feasibility (708/708 residual graphs).
- `proverB/residual_branch_probe.py` — branch-disjoint probe (isolates the ear/theta
  same-branch phenomenon: 3 failures ⇒ same-branch double tails are necessary).
- `proverB/residual_probe3.py` — R0 at all girths (P0: 0 fail), `δ* ≤ s` (P2: 0 fail),
  girth cross-edge law (P4: 0 violations), rigid family probe (P3: 9 misses → analysis).
- `proverB/analyze_failures.py` — dissection of the 9 misses (representative choice /
  truncation / union patterns).
- `proverB/residual_probe4.py` — full assembly probe of Part II (C1 cover exists: 0
  fail; C5 assembly: 547/547; conflicts all single-cross; unions needed: 7).
