# WOWII / Graffiti.pc Conjecture 142 — Complete proof of the hard branch

**Statement proved.** Let `G` be a finite simple connected graph which contains a
cycle, and let `f := eccSet(G, B) ≥ 1`, where `B` is the periphery of `G`.
Then

    tree(G) ≥ (2/3)·girth(G) + f.

Together with the branches already closed in the compiled Lean skeleton
(`problems_external/wowii_142/wave1/skeletons.lean`: acyclic `G`, and cyclic
`G` with `f = 0`), this completes WOWII Conjecture 142 for all connected
graphs.

Author lane: Prover A (Angle A). Date: 2026-07-18.
Machine validation: every lemma and every branch of this proof has an
executable twin which was run on 10,663 corpus graphs plus a 20k+ fresh-seed
adversarial sweep with **zero failures**; see §10.

---

## 0. Conventions

`G = (V,E)` finite, simple, connected, `n = |V| ≥ 2`, containing a cycle.
`d(u,v)` = graph distance, `d(u,S) = min_{s∈S} d(u,s)`,
`ecc(v) = max_u d(v,u)`, `D = diam(G) = max ecc`, `r = radius`.
`B = {v : ecc(v) = D}` (periphery; `B ≠ ∅`),
`f = max_v d(v,B)` (the FC-faithful `eccSet G (maxEccentricityVertices G)`;
vertices of `B` contribute `0`).
`g = girth(G) ≥ 3`. `tree(G) = t` = maximum number of vertices of an induced
subgraph that is a tree.

A *geodesic* is a shortest path between its two endpoints. Every subpath of a
geodesic is a geodesic; every geodesic is an induced path.

Throughout, `K` denotes a **shortest cycle** of `G` (length `g`), identified
with its vertex set when convenient. For `v ∈ V` put `h(v) = d(v, V(K))`
(the *height* of `v`; `h(v) = 0` iff `v ∈ V(K)`).

**Hard branch hypothesis (standing).** `G` cyclic, connected, `f ≥ 1`.

**Target (integer form).** Since `t ∈ ℤ`, the claim `t ≥ (2/3)g + f` is
equivalent to

    t ≥ f + ⌈2g/3⌉ = f + g − ⌊g/3⌋.

(The identity `⌈2g/3⌉ = g − ⌊g/3⌋` holds for all integers `g`.)

Define the two *deficiency parameters*

    s := f + ⌈2g/3⌉ − (D+1)      (what is missing from the geodesic bound),
    m := f + 1 − ⌊g/3⌋           (what is missing from the cycle bound).

If `s ≤ 0` the target follows from T1 below; if `m ≤ 0` it follows from T2.
So we may and do assume `s ≥ 1` and `m ≥ 1`; the latter is equivalent to
`f ≥ ⌊g/3⌋`.

---

## 1. Base tools (all with complete proofs)

**T1.** `t ≥ D + 1`, and more generally `t ≥ d(u,v) + 1` for all `u,v`.
*Proof.* A geodesic from `u` to `v` is an induced path, which is an induced
tree with `d(u,v)+1` vertices. ∎

**T2.** `t ≥ g − 1`.
*Proof.* Let `K` be a shortest cycle and `z ∈ K`. `K` is chordless (T3), so
`G[K∖{z}]` is an induced path with `g−1` vertices. ∎

**T3.** Every shortest cycle `K` is chordless and isometric
(`d_G(a,b) = d_K(a,b)` for `a,b ∈ K`, where `d_K` is the distance along the
cycle).
*Proof.* A chord splits `K` into two cycles, the shorter of which has length
`< g`. If `d_G(a,b) < d_K(a,b)` for some `a,b ∈ K`, take a shortest such
witness path `Q`; `Q` meets `K` only in `a,b` (else a shorter witness pair
exists), and `Q` together with the longer `K`-arc between `a` and `b` —
wait, take the *shorter* arc `A` with `|A| = d_K(a,b) ≤ ⌊g/2⌋`; `Q ∪ A` is a
closed walk of length `d_G(a,b) + d_K(a,b) < 2·d_K(a,b) ≤ g` which contains
a cycle, since `Q ≠ A` (`Q` is shorter) and both are paths meeting only at
their common endpoints; that cycle has length `≤ |Q| + |A| < g`,
contradiction. ∎

**T4 (key mini-lemma).** If `D ≥ 1` then `f ≤ D − 1`.
*Proof.* Suppose some `x` has `d(x,B) ≥ D`. Pick any `b ∈ B` (nonempty).
Then `D ≤ d(x,B) ≤ d(x,b) ≤ D`, so `d(x,b) = D`, hence `ecc(x) ≥ D`, hence
`ecc(x) = D`, i.e. `x ∈ B` and `d(x,B) = 0 < D` — contradiction. ∎

**T5.** `D ≥ ⌊g/2⌋`.
*Proof.* `K` isometric (T3) contains two vertices at cycle-distance
`⌊g/2⌋`. ∎

**T6.** Both endpoints of any diametral pair are peripheral: if
`d(b,w) = D` then `ecc(b) = ecc(w) = D`, so `b, w ∈ B`. In particular a
diametral pair `(b,w) ∈ B × B` exists. ∎

**Windows.** Let `Q = (q_0, …, q_L)` be a geodesic and `v ∉ V(Q)`.
- **W2 (g ≥ 5).** `v` has at most one neighbour on `Q`.
- **W3 (g = 4).** `v` has at most two neighbours on `Q`, and if two, they
  are `q_i, q_{i+2}` for some `i`.

*Proof.* If `v ~ q_i, q_j` with `i < j`, then `j − i = d(q_i,q_j) ≤ 2`.
`j − i = 1` gives a triangle (needs `g = 3`); `j − i = 2` gives the 4-cycle
`v q_i q_{i+1} q_{i+2}` (needs `g ≤ 4`). For three neighbours
`q_i < q_j < q_k` we would need pairwise index gaps `≤ 2` with no gap `1`,
i.e. `{i, i+2, i+4}`, but then `d(q_i,q_{i+4}) = 4 > 2`, impossible. ∎

- **W1.** The same statements hold with `Q` replaced by a shortest cycle
  `K` and `d_Q` by `d_K` (using T3: `d_G = d_K` on `K`); for `g = 4` the two
  neighbours form an antipodal pair of the 4-cycle. ∎

**Lemma M (cycle base; rigorous, from the 144 lane, proof included).**
For a shortest cycle `K` let `M(K)` be the largest `|F|`, `F ⊆ V∖V(K)`,
such that `G[F]` is a forest and **there exists** `z ∈ K` such that every
connected component of `G[F]` sends **exactly one** edge (counted with
multiplicity) into `K∖{z}` (edges into `z` are unrestricted). Then

    t ≥ (g − 1) + M(K).

*Proof.* `G[K∖{z}]` is an induced path `P0` with `g−1` vertices and `g−2`
edges (T3). Consider `H = G[(K∖{z}) ∪ F]`. Its edges are: the `g−2` path
edges, the edges inside `G[F]` (`|F| − c` of them, `c` = number of
components of `G[F]`, since `G[F]` is a forest), and the `F`-to-base edges
(exactly `c` in total). So `H` has `(g−1+|F|) − 1` edges. `H` is connected
(each component of `G[F]` attaches to the connected `P0`). A connected graph
on `N` vertices with `N−1` edges is a tree; `H` is induced by construction.
Hence `t ≥ g − 1 + |F|`. ∎

**Lemma M-P (path base; same proof).** If `P` is an induced path and
`F ⊆ V∖V(P)` induces a forest whose every component sends exactly one edge
into `P`, then `t ≥ |P| + |F|`. ∎

---

## 2. Case `g = 3`

Here `⌈2g/3⌉ = 2`. Since `f ≥ 1`, `D ≥ 1`, so T4 gives `f ≤ D − 1`, and T1
gives

    t ≥ D + 1 ≥ (f + 1) + 1 = f + 2 = f + ⌈2g/3⌉.  ∎

*(This closes the entire `g=3` case; no bridge, no cycle-side work.)*

---

## 3. Case `g = 4`

Here `⌈2g/3⌉ = 3` and `⌊g/3⌋ = 1`, so the target is `t ≥ f + 3` and
`m = f`, `s = f + 2 − D`.

**3.0 Rigidity.** In the hard case `s ≥ 1` gives `f ≥ D − 1`; T4 gives
`f ≤ D − 1`. Hence `f = D − 1` and `s = 1`: **we need exactly one vertex on
a diametral geodesic base.** Also `D = f + 1 ≥ 2`.

Fix notation: diametral geodesics have `D+1` vertices and their endpoints
are peripheral (T6).

**3.1.** If some diametral geodesic `P` has a vertex `u ∉ V(P)` with exactly
one edge into `V(P)`, then `F = {u}` is a Lemma M-P forest, so
`t ≥ (D+1) + 1 = f + 3`. **Done.**

So assume from now on: for **every** diametral geodesic `P`, every vertex
outside `P` has `0` or exactly `2` edges into `V(P)`; by W3 a 2-attached
vertex attaches at `{p_i, p_{i+2}}` for some `i`.

**3.2 Swap branch.** Fix one diametral geodesic `P = (p_0,…,p_D)`. Suppose
some vertex is at distance `≥ 2` from `V(P)`. Walking along a shortest path
toward `V(P)`, pick `v` with `d(v, V(P)) = 2` and a neighbour `u` of `v`
with `d(u, V(P)) = 1`. By assumption `u` is 2-attached: `u ~ p_i, p_{i+2}`.
Let

    P' = (p_0, …, p_i, u, p_{i+2}, …, p_D).

`P'` is a walk from `p_0` to `p_D` with exactly `D` edges, and
`d(p_0,p_D) = D`, so `P'` is again a **diametral geodesic** (in particular
an induced path with `D+1` vertices). Now `F = {v}` works for `P'`:
`v ~ u ∈ P'` (one edge), and `v` has no other neighbour in `P'` because a
neighbour `p_j` would give `d(v,V(P)) ≤ 1`. Lemma M-P:
`t ≥ (D+1) + 1 = f + 3`. **Done.**

**3.3 Endgame.** Otherwise every vertex is within distance `1` of `V(P)`,
and every outside vertex is 2-attached to `P`.

*Claim: `D ≤ 2`.* Take a realizer `x` with `d(x,B) = f = D − 1 ≥ 1`; note
`p_0, p_D ∈ B`.
- If `x = p_j ∈ P`: `d(x,p_0) = j ≥ D−1` and `d(x,p_D) = D−j ≥ D−1` force
  `D ≤ 2`.
- If `x ∉ P`: `x ~ p_i, p_{i+2}` for some `i`, so
  `d(x,p_0) ≤ i+1` and `d(x,p_D) ≤ D−i−1`. From
  `i+1 ≥ D−1` and `D−i−1 ≥ D−1` we get `i ≥ D−2` and `i ≤ 0`, so `D ≤ 2`. ∎

So `D = 2`, `f = 1`, `m = f = 1`. We close on the cycle side with Lemma
M and the singleton forest below (Lemma 7.1, `m = 1` case, valid for all
`g ≥ 4`): `t ≥ (g−1) + 1 = 4 = f + 3`. **Done.** ∎ *(Case `g = 4` closed.)*

---

## 4. Tails and contacts (`g ≥ 5`)

For the rest of the proof `g ≥ 5`. Fix an arbitrary shortest cycle `K`.

**4.1 Tails.** Let `v ∈ V` with `h(v) = h ≥ 1`. Fix a shortest path from
`v` to `V(K)` and index it **by height**:

    v = q_h, q_{h−1}, …, q_1, q_0 ∈ K.

The *tail* of `v` is `T_v = {q_1, …, q_h}` (so `|T_v| = h`), with *foot*
`q_1` and *attachment* `a_v := q_0 ∈ K`.

**Lemma 4.2 (tail properties).** (i) `d(q_j, K) = j` and `d(v,q_j) = h − j`
for `1 ≤ j ≤ h`. (ii) `T_v` induces a path. (iii) For `j ≥ 2`, `q_j` has no
neighbour in `K`. (iv) `q_1` has exactly one neighbour in `K`, namely `a_v`.

*Proof.* (i) Subpaths of the geodesic `v→q_0` are geodesics, and
`d(q_j,K) < j` would shortcut it. (ii) Subpath of a geodesic. (iii) A
`K`-neighbour of `q_j` gives `d(q_j,K) ≤ 1 < j`. (iv) W1 with `g ≥ 5` gives
at most one; `a_v` is one. ∎

**4.3 Contacts.** For two vertices `u ≠ v` with tails `T_u = (q_j^u)`,
`T_v = (q_i^v)` (heights as indices), a *contact* is a pair of tail vertices
that coincide or are adjacent:

    (j, i, 0)  if q_j^u = q_i^v      (shared contact),
    (j, i, 1)  if q_j^u ~ q_i^v      (cross contact),

with `1 ≤ j ≤ h(u)`, `1 ≤ i ≤ h(v)`.

**Lemma 4.4 (contact structure).**
(a) In a shared contact, `i = j` (a common vertex has one height).
(b) In a cross contact, `|i − j| ≤ 1` (heights of adjacent vertices differ
by at most 1).
(c) **Contact inequality:** every contact satisfies

    i + j ≤ h(u) + h(v) + d − d(u,v),    d ∈ {0,1} its type.

*Proof.* (a),(b): `h` is 1-Lipschitz. (c): walk from `u` down `T_u` to
`q_j^u` (`h(u) − j` edges), across the contact (`d` edges), then up `T_v`
from `q_i^v` to `v` (`h(v) − i` edges):
`d(u,v) ≤ (h(u)−j) + d + (h(v)−i)`. ∎

---

## 5. The Merge Lemma (`g ≥ 5`)

**Lemma 5.1 (Merge).** Let `g ≥ 5`, `K` a shortest cycle, `u ≠ v` with
`h(u), h(v) ≥ 1` and fixed tails `T_u, T_v`. Suppose **some contact
exists**. Then there are `z ∈ K` and `O ⊆ V∖V(K)` such that:

1. `G[O]` is a tree (induced),
2. `O` sends exactly one edge into `K∖{z}`,
3. `|O| ≥ d(u,v) + 1`.

Consequently (Lemma M with the single-component forest `F = O`):

    t ≥ (g − 1) + d(u,v) + 1.

*Proof.* Write `h_u = h(u)`, `h_v = h(v)`, `φ = d(u,v)`. Let

    j₁ = max { j : (j,i,d) is a contact }.

**Branch S (a shared contact at level `j₁`).** By 4.4(a) it is
`(j₁, j₁, 0)`, i.e. `q_{j₁}^u = q_{j₁}^v`. We first observe that
maximality forces `j₁ = h_u`: if `j₁ < h_u`, then `q_{j₁+1}^u` exists and is
adjacent (path edge of `T_u`) to `q_{j₁}^u = q_{j₁}^v ∈ T_v`, so
`(j₁+1, j₁, 1)` is a contact at level `j₁+1 > j₁` — contradiction. Hence
`u = q_{h_u}^u = q_{j₁}^v ∈ T_v`: **`u` lies on `v`'s tail.** Put

    O = T_v,    z = any K-vertex ≠ a_v.

`G[O]` is an induced path (4.2 ii), a single component with exactly one edge
into `K∖{z}` (4.2 iii–iv). *Mass:* the contact inequality at
`(h_u, h_u, 0)` gives `2h_u ≤ h_u + h_v − φ`, i.e.
`|O| = h_v ≥ φ + h_u ≥ φ + 1` (as `h_u ≥ 1`).

**Branch X (only cross contacts at level `j₁`, `j₁ ≥ 2`).** Let
`(j₁, i₁, 1)` be a contact at the top level. Since `q_{j₁}^u` is not on the
geodesic `(q_0^v, …, q_{h_v}^v)` (a shared vertex would be a shared contact
at level `j₁`, and `q_{j₁}^u ∉ K`), W2 gives it **at most one** neighbour on
that geodesic; since `j₁ ≥ 2` it has no `K`-edges, so its unique neighbour
is `q_{i₁}^v` and `(j₁, i₁, 1)` is the **only** contact at level `j₁`. Put

    O = T_v ∪ { q_j^u : j₁ ≤ j ≤ h_u },    z = any K-vertex ≠ a_v.

Disjointness and edge audit as in Branch S (contacts above `j₁`: none; at
`j₁`: exactly the one cross edge). `G[O]` is two vertex-disjoint induced
paths plus exactly one cross edge: an induced tree with
`|O| = h_v + (h_u − j₁ + 1)`. K-edges: only `q_1^v a_v` (the kept upper part
starts at height `j₁ ≥ 2`). Mass: the contact inequality
`j₁ + i₁ ≤ h_u + h_v + 1 − φ` with `i₁ ≥ 1` gives `j₁ ≤ h_u + h_v − φ`, so

    |O| = h_u + h_v − j₁ + 1 ≥ φ + 1.

**Branch F (`j₁ = 1`, only cross contacts at level 1).** All contacts have
`j = 1`. Consider `i₁' = max { i : (1,i,d) is a contact }`.

- *(F-S)* If `(1, i, 0)` exists then by 4.4(a) `i = 1`: the two feet
  coincide, `q_1^u = q_1^v`; this is a shared contact and `j₁ = 1` puts us
  in Branch S (with `j₁ = 1`), already handled. So assume all contacts are
  cross.
- *(F1)* If `i₁' ≥ 2`: run Branch X **with the roles of `u` and `v`
  swapped**, merging at the topmost level on the `v`-side:
  `O = T_u ∪ { q_i^v : i₁' ≤ i ≤ h_v }`, `z =` any K-vertex `≠ a_u`.
  The unique-contact argument now uses W2 for `q_{i₁'}^v` (height `≥ 2`,
  hence no K-edges) against the geodesic `(q_0^u, …, q_{h_u}^u)`; the kept
  `v`-part contains no foot, so the single K-edge is `q_1^u a_u`. Mass:
  `1 + i₁' ≤ h_u + h_v + 1 − φ` gives
  `|O| = h_u + (h_v − i₁' + 1) ≥ φ + 1`.
- *(F2)* Otherwise the contact set is exactly `{(1,1,1)}`: the two feet are
  adjacent. Then `a_u ≠ a_v` (otherwise `q_1^u, q_1^v, a_u` is a triangle,
  impossible for `g ≥ 5`). Put

      O = T_u ∪ T_v,    z = a_v.

  `G[O]` = two disjoint induced paths (`T_u ∩ T_v = ∅`: a shared vertex is a
  shared contact, excluded) plus the single cross edge `q_1^u q_1^v` (any
  other cross edge is a contact `≠ (1,1,1)`): an induced tree. K-edges of
  `O`: `q_1^u a_u` and `q_1^v a_v`; with `z = a_v` exactly one edge goes
  into `K∖{z}`. Mass: contact inequality at `(1,1,1)`:
  `2 ≤ h_u + h_v + 1 − φ`, so `|O| = h_u + h_v ≥ φ + 1`. ∎

**Corollary 5.2.** In the hard branch (`g ≥ 5`, `f ≥ 1`), if the tails of
any two of `x, b, w` (see §6) have a contact, then `t ≥ f + ⌈2g/3⌉`.

*Proof.* For the pairs `(x,b), (x,w)`: `d ≥ f` (definition of `f`, `b,w ∈
B`); for `(b,w)`: `d = D ≥ f + 1` (T4). Lemma 5.1 + Lemma M give
`t ≥ (g−1) + f + 1 = f + g ≥ f + ⌈2g/3⌉`. ∎

*(Note: Corollary 5.2 is zone-free — any contact closes the hard branch.)*

---

## 6. The Perimeter Lemma and the good zone (`g ≥ 5`)

**Lemma 6.1 (three points on a cycle).** For any three vertices
`κ₁, κ₂, κ₃` on a cycle `K` of length `g` (not necessarily distinct):

    d_K(κ₁,κ₂) + d_K(κ₁,κ₃) + d_K(κ₂,κ₃) ≤ g.

*Proof.* Let the three vertices have cyclic positions splitting `K` into
three arcs of lengths `α, β, γ ≥ 0`, `α + β + γ = g` (in cyclic order:
`κ₁→κ₂` is `α`, `κ₂→κ₃` is `β`, `κ₃→κ₁` is `γ`). Then
`d_K(κ₁,κ₂) = min(α, β+γ) ≤ α`, `d_K(κ₂,κ₃) ≤ β`, and
`d_K(κ₁,κ₃) = min(γ, α+β) ≤ γ`. Sum ≤ `g`. ∎

**Lemma 6.2 (Perimeter).** Let `K` be any shortest cycle and `u₁,u₂,u₃`
any three vertices. Then

    h(u₁) + h(u₂) + h(u₃) ≥ ⌈( d(u₁,u₂) + d(u₁,u₃) + d(u₂,u₃) − g ) / 2⌉.

*Proof.* Let `κ_i ∈ K` be a *gate* of `u_i`: `d(u_i, κ_i) = h(u_i)` (for
`h(u_i) = 0`, `κ_i = u_i`). Walking `u_i → κ_i → (arc) → κ_j → u_j`:

    d(u_i,u_j) ≤ h(u_i) + d_K(κ_i,κ_j) + h(u_j)      (uses T3: arcs are paths in G).

Summing the three inequalities and applying Lemma 6.1:

    Σ_{i<j} d(u_i,u_j) ≤ 2(h(u₁)+h(u₂)+h(u₃)) + g.

Rearrange; the left side is an integer, so the ceiling holds. ∎

**Definition (zones).** The *good zone* is `D ≥ g + 1 − 2⌊g/3⌋`, the *bad
zone* is `D ≤ g − 2⌊g/3⌋`.

**Theorem 6.3 (good zone, `g ≥ 5`).** In the hard branch with
`D ≥ g + 1 − 2⌊g/3⌋`: `t ≥ f + ⌈2g/3⌉`.

*Proof.* Fix any shortest cycle `K`, a realizer `x` (`d(x,B) = f`), and a
diametral pair `(b,w)` (T6). Note `x ∉ B` (as `f ≥ 1`), so `x ∉ {b,w}`.
Give each of `x, b, w` with positive height its tail (4.1); vertices with
`h = 0` get no tail.

**Case C (some contact between two of the tails):** Corollary 5.2. Done.

**Case NC (no contact between any two tails):** Let `F` be the union of the
(at most three) tails. The tails are pairwise vertex-disjoint (a common
vertex is a shared contact) and pairwise non-adjacent (an edge is a cross
contact), so the components of `G[F]` are exactly the tails — induced paths
(4.2 ii). Each tail's K-edges: exactly one, from its foot (4.2 iii–iv).
Choose `z ∈ K` outside the set of attachments `{a_x, a_b, a_w}` (at most 3
vertices; `g ≥ 5 > 3`). Then every component of `G[F]` sends exactly one
edge into `K∖{z}`, so Lemma M gives `t ≥ (g−1) + (h(x)+h(b)+h(w))`.

By Lemma 6.2 with `d(x,b) ≥ f`, `d(x,w) ≥ f`, `d(b,w) = D`:

    h(x)+h(b)+h(w) ≥ ⌈(2f + D − g)/2⌉ = f + ⌈(D−g)/2⌉.

The good-zone hypothesis `D ≥ g + 1 − 2⌊g/3⌋` gives
`⌈(D−g)/2⌉ ≥ ⌈(1−2⌊g/3⌋)/2⌉ = 1 − ⌊g/3⌋`, hence
`h(x)+h(b)+h(w) ≥ f + 1 − ⌊g/3⌋ = m` and

    t ≥ (g−1) + m = f + g − ⌊g/3⌋ = f + ⌈2g/3⌉.  ∎

---

## 7. The bad zone (`g ≥ 5`): a finite list of parameter boxes

**Lemma 7.0 (zone arithmetic).** For `g ≥ 5`, the bad zone
`⌊g/2⌋ ≤ D ≤ g − 2⌊g/3⌋` (left inequality is T5) is nonempty only for

    (g, D) ∈ { (5,2), (5,3), (7,3), (8,4), (11,5) }.

*Proof.* For `g ≥ 12`: `2⌊g/3⌋ + ⌊g/2⌋ ≥ 2(g−2)/3 + (g−1)/2 =
(7g−11)/6 > g`, so `g − 2⌊g/3⌋ < ⌊g/2⌋` and the zone is empty. For
`5 ≤ g ≤ 11` check directly: `g−2⌊g/3⌋` = 3,2,3,4,3,4,5 for g = 5..11 and
`⌊g/2⌋` = 2,3,3,4,4,5,5; the zone is nonempty exactly for
g = 5 (D ∈ {2,3}), g = 7 (D = 3), g = 8 (D = 4), g = 11 (D = 5). ∎

**Lemma 7.0' (box parameters).** In the hard branch (`f ≥ ⌊g/3⌋` from
`m ≥ 1`, `f ≥ D + 2 − ⌈2g/3⌉` from `s ≥ 1`, `f ≤ D − 1` from T4), the
possible `(g, D, f)` in the bad zone are:

    (5,2,1): m=1   (5,3,1): m=1   (5,3,2): m=2   (7,3,2): m=1
    (8,4,2): m=1   (8,4,3): m=2   (11,5,3): m=1  (11,5,4): m=2

*Proof.* Direct arithmetic from the three `f`-constraints; `m = f+1−⌊g/3⌋`. ∎

So in the bad zone `m ∈ {1,2}` always.

**Lemma 7.1 (`m = 1`; stated for all `g ≥ 4`).** In the hard branch, for
every shortest cycle `K`: `M(K) ≥ 1`, hence `t ≥ g`.

*Proof.* If `V(K) = V` then, `K` being chordless (T3), `G = C_n`; but then
every vertex has eccentricity `⌊n/2⌋`, so `B = V` and `f = 0`,
contradicting `f ≥ 1`. So `V ≠ V(K)`, and by connectivity some `u ∉ V(K)`
has a neighbour in `K`. By W1, `u` has at most two `K`-neighbours (one if
`g ≥ 5`). If one neighbour `a`: `F = {u}`, `z` = any other K-vertex. If two
(`g = 4`), say `a, a'`: `F = {u}`, `z = a`. Either way every component of
`G[F]` sends exactly one edge into `K∖{z}`: Lemma M gives
`t ≥ (g−1) + 1`. ∎

For the `m = 1` boxes this closes the target:
`t ≥ g = (g − 1) + m ≥ f + ⌈2g/3⌉`. For `(g,D) = (4,2)` (used in §3.3) the
same computation gives `t ≥ 4 = f + 3`.

**Lemma 7.2 (`m = 2` boxes).** In the boxes `(5,3,2)`, `(8,4,3)`,
`(11,5,4)`: `t ≥ (g−1) + 2 = f + ⌈2g/3⌉`.

*Proof.* Fix any shortest cycle `K`. We find a Lemma-M forest of size `2`.

**(A) Some vertex has `h(v) ≥ 2`.** Its tail `T_v` (4.1–4.2) is a single
component with exactly one K-edge (from its foot); `z` = any K-vertex other
than `a_v`. `|T_v| = h(v) ≥ 2`. Done.

**(B) Every vertex has `h ≤ 1`.** Then every `u ∉ V(K)` (the *outside*
vertices) has exactly one `K`-neighbour `a(u)` (W1, `g ≥ 5`).

*Claim: there are at least two outside vertices.* If none, `f = 0` as in
7.1. If exactly one, `G = C_g` plus one pendant vertex, whose parameters we
compute directly:
- `g = 5`: eccentricities are (pendant) 3, (attachment) 2, (its neighbours)
  2, (far pair) 3 — so `D = 3`, `B` = {pendant} ∪ {far pair}, and every
  vertex is within distance 1 of `B`: `f = 1 ≠ 2`. Contradiction.
- `g = 8`: the pendant-to-antipode distance is `1 + 4 = 5 ≠ D = 4`.
  Contradiction.
- `g = 11`: pendant-to-antipode `1 + 5 = 6 ≠ D = 5`. Contradiction. ∎(claim)

*Sub-case (B1): two outside vertices `u₁, u₂` are non-adjacent.*
`F = {u₁}, {u₂}` (two singleton components, no edge between them), `z` =
any K-vertex `∉ {a(u₁), a(u₂)}` (`g ≥ 5 > 2`). Each component sends exactly
one edge into `K∖{z}`. `|F| = 2`. Done.

*Sub-case (B2): the outside vertices form a clique.* Girth `≥ 5` forbids
triangles, so there are exactly two, adjacent: `u₁ ~ u₂`. Their attachments
differ (`a(u₁) = a(u₂)` gives a triangle), and the cycle
`u₁ u₂ a(u₂) (arc) a(u₁)` has length `3 + d_K(a(u₁),a(u₂)) ≥ g`, so
`d_K(a(u₁),a(u₂)) ≥ g − 3`. Since `d_K ≤ ⌊g/2⌋`, this needs
`g − 3 ≤ ⌊g/2⌋`, i.e. `g ≤ 6`: **impossible for the boxes `g = 8, 11`**
(so (B2) does not arise there), and for `g = 5` we get the *ear*:
`F = {u₁, u₂}` (one component, a single edge), `z = a(u₁)`. Its edges into
`K∖{z}`: only `u₂ a(u₂)` (note `u₁`'s K-edge goes to `z`). Exactly one.
`|F| = 2`. Done. ∎

---

## 8. Assembly

Let `G` be connected, cyclic, with `f ≥ 1`. If `s ≤ 0`, T1 closes; if
`m ≤ 0`, T2 closes. Otherwise:

- `g = 3`: §2.
- `g = 4`: §3 (using Lemma 7.1 in the endgame §3.3).
- `g ≥ 5`, `D ≥ g + 1 − 2⌊g/3⌋`: Theorem 6.3.
- `g ≥ 5`, `D ≤ g − 2⌊g/3⌋`: Lemmas 7.0–7.2.

Every case yields `t ≥ f + ⌈2g/3⌉ ≥ f + (2/3)g`. **∎ (hard branch of C142)**

---

## 9. Remarks for the Lean formalization

1. **Consumers.** Only Lemma M and Lemma M-P are consumed (plus T1); both
   have one-line edge-counting proofs and Lemma M is already formalized in
   the 144 lane (`problems_external/wowii_144/lean/lemmaM.lean`). The
   generalization "tree base" is not needed.
2. **Explicitness.** Every construction is an explicit vertex set: tails are
   BFS paths; the merge object is `T_v ∪ {q_j^u : j ≥/> j₁}`; the g=4 swap
   replaces one vertex of a geodesic. No compactness, no extremal choice
   beyond `max`/`min` over finite sets.
3. **Expected hard steps.**
   - Lemma 5.1 case analysis (topmost contact + W2 uniqueness): most
     invariants are equalities about BFS distances; suggest formalizing
     tails as `List` with an invariant `d(q_j, K) = j`.
   - Lemma 6.1: cyclic-order arithmetic; suggest positions in `ZMod g` or a
     3-case `min` analysis on sorted positions.
   - §3.3 and Lemma 7.2(B) classification `G = C_g + pendant`: on `≤ 12`
     vertices this can be `decide`d, or proved directly from `V = K ∪ {u}`,
     chordlessness, and the unique attachment.
   - T3 (isometric shortest cycle) exists in the 141/144 lanes' API.
4. **Integer arithmetic.** All targets use `⌈2g/3⌉ = g − ⌊g/3⌋`;
   the zone split `D ≥ g+1−2⌊g/3⌋` vs `D ≤ g−2⌊g/3⌋` is exhaustive; Lemma
   7.0's finite list is verified by `interval_cases`-style enumeration
   `5 ≤ g ≤ 11` plus the `g ≥ 12` inequality.

---

## 10. Machine validation (exact arithmetic; no floats anywhere)

Scripts in `problems_external/wowii_142/proverA/`:

- `verify_construction.py` — executable twin of THIS proof: for every
  corpus graph it runs the exact branch the proof dictates (g=3 arithmetic;
  g=4 direct/swap/endgame; g≥5 bad-zone boxes with the 7.1/7.2
  constructions; g≥5 good zone with tails, contact detection, Branch
  S/X/F merges, and the no-contact three-tail forest), asserts every
  intermediate claim used in the proof (windows, contact inequality,
  contact-level structure 4.4(a,b), unique-cross-at-top, `a_u ≠ a_v` in
  F2, forest validity under the exact Lemma-M predicate, all mass
  inequalities, cycle-perimeter `Σd_K ≤ g`), and finally checks
  `g − 1 + |F| ≥ f + ⌈2g/3⌉` (resp. `D + 1 + |F|` on the path base).
  **Result: 10,663 corpus graphs (10,481 cyclic), 0 failures.**
  Branch counts: g3 3647, T1 2907, T2 194, g4-direct 133, m1 13, m2-ear 3,
  good-zone three-tails 3364, good-zone merges 220 (all validated for
  EVERY shortest cycle, up to 50 per graph).
- `harden_sweep.py` — fresh-seed (987654321) sweep: 20k+ additional graphs
  (forked/eared cycles designed to force tail contacts and merge corners,
  forced-girth randoms, bipartite blocks), iterating over ALL realizers
  (≤6), ALL diametral pairs (≤8), ALL shortest cycles (≤25) per graph, and
  unit-testing the §3.2 swap on every 2-attached vertex of every diametral
  geodesic of every girth-4 graph encountered. **Result: 0 failures.**
  (Counts in the run log `harden_sweep.log`.)
- Earlier route/bridge evidence: `bridge_oracle/` (R1/R2 exact, 10,481
  graphs, 0 violations, tight on all 113 equality cases) — superseded by
  the complete proof above but kept as independent corroboration.

Corner cases that never occurred in either corpus (`g=4` swap-endgame with
`D = 2` fallback, boxes `(5,2,1)`, `(7,3,2)`, `(8,4,*)`, `(11,5,*)`,
merge Branch F on the trio) are covered by the proofs above and, where
constructible, by the unit tests; several are likely vacuous (no graph
attains them), which the proof does not need to decide.
