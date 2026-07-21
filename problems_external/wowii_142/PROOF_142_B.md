# PROOF_142_B — WOWII / Graffiti.pc Conjecture 142, hard branch (Angle B)

**Claim proved here (hard branch).** Let `G` be a finite simple **connected**
graph that contains a cycle, let `g = girth(G) >= 3`, `D = diam(G)`,
`B = {v : ecc(v) = D}` (periphery), and `f = max_v d(v, B) >= 1`. Then

    tree(G) >= f + ceil(2g/3).                                    (*)

Since `tree(G)` and `f` are integers and `ceil(2g/3) >= 2g/3`, (*) implies the
FC-faithful real form `tree(G) >= (2/3)*girth(G) + eccSet(periphery)`. The
complement of the hard branch (acyclic, or `f = 0`) is already closed in the
compiled skeleton `problems_external/wowii_142/wave1/skeletons.lean`.

Throughout, `t := tree(G)` = maximum number of vertices of an induced subgraph
of `G` that is a tree; `d(.,.)` = graph distance; for a nonempty `S ⊆ V`,
`d(v,S) = min_{s in S} d(v,s)`. All arithmetic is exact integer arithmetic;
we use the identity

    ceil(2g/3) = g - floor(g/3)                                    (A0)

(check the three residues; verified for `g in [3,3000]` in
`proverB/arith_checks.py`). Write `m := floor(g/3)` and

    q := f + 1 - m ,

so that (*) is equivalent, via Lemma M below, to producing `M(K) >= q`.

------------------------------------------------------------------------
## 1. Toolkit

**T1.** `t >= d(u,v) + 1` for all `u,v`; in particular `t >= D + 1`.
*Proof.* A geodesic is an induced path (a chord would shortcut it). ∎

**T2.** `G` cyclic implies `t >= g - 1`. *Proof.* A shortest cycle is
chordless (T3); delete one vertex. ∎

**T3.** Every shortest cycle `K` is chordless, and any two vertices of `K`
are at `G`-distance equal to their arc distance on `K` (isometric); in
particular consecutive arcs realize distances. (Standard; proved in the wave1
skeleton. Chord: it splits `K` into a shorter cycle. Isometry: a shorter
outside path plus the shorter arc would close a cycle of length `< g`.)

**T4.** `f <= D - 1`. *Proof.* Suppose `d(x, B) = D` for some `x`. Every
`b in B` then satisfies `d(x,b) >= D`, hence `= D`; picking one `b` gives
`ecc(x) >= D`, so `ecc(x) = D`, so `x in B`, so `d(x,B) = 0 < D`
(`D >= 1` since `n >= 2`) — contradiction. Since always `d(v,B) <= D`,
the maximum `f` is `<= D - 1`. ∎

**T5 (diametral ends are peripheral).** `d(b,w) = D` implies
`ecc(b) = ecc(w) = D`, i.e. `b, w in B`. ∎

**T6 (small diameter is vacuous).** If `G` is cyclic and `f >= 1`, then
`D >= 3` or `g = 3`.
*Proof.* `f >= 1` gives an `x` with `ecc(x) <= D - 1`. `D = 1` makes `G`
complete (`B = V`, `f = 0`, excluded). If `D = 2` then `ecc(x) = 1`, i.e. `x`
is adjacent to all other vertices. `G` has a cycle `C`; `C` has an edge `uv`
with `x not in {u,v}` (any cycle has >= 3 vertices), and then `x,u,v` is a
triangle, so `g = 3`. ∎

**Lemma M (cycle base; rigorous, statement as in INTEL_144).** Let `K` be a
shortest cycle. Define `M(K)` as the maximum `|F|` over sets
`F ⊆ V \ V(K)` such that `G[F]` is a forest and **there exists** `z in K`
such that every connected component of `G[F]` sends **exactly one** edge
(counted with multiplicity over vertex pairs) into `K \ {z}` (edges into `z`
itself are unrestricted). Then

    t >= (g - 1) + M(K).

*Proof.* `G[K \ {z}]` is an induced path with `g-1` vertices and `g-2` edges
(K chordless). Let `F` have `c` components. The vertex set
`W = (K \ {z}) ∪ F` induces: the `g-2` path edges, the `|F| - c` forest
edges, and exactly `c` component-to-path edges — no others (components are
pairwise non-adjacent by definition of components of `G[F]`, `F` avoids `K`,
and each component has exactly one edge into `K \ {z}`; edges into `z` do not
appear since `z not in W`). So `|W| = g - 1 + |F|`, `e(G[W]) = |W| - 1`,
and `G[W]` is connected (each component hooks onto the path). Hence `G[W]`
is a tree. ∎

**Lemma M-P (path base; rigorous).** Let `P` be an induced path in `G` and
let `F ⊆ V \ V(P)` be such that `G[F]` is a forest and every component of
`G[F]` sends exactly one edge into `P`. Then `t >= |P| + |F|`.
*Proof.* Identical count with base path `P`. ∎

------------------------------------------------------------------------
## 2. Attachment and descent lemmas

Fix a shortest cycle `K` with vertex set `V(K)`, `|V(K)| = g`.

**L3 (single attachment).** Let `v not in V(K)`.
(i) If `g >= 5`, `v` has at most one neighbour on `K`.
(ii) If `g = 4`, `N(v) ∩ K` is empty, a single vertex, or an antipodal pair
`{k_i, k_{i+2}}`.
*Proof.* If `v` is adjacent to `k_i != k_j` at arc distance
`s = d_K(k_i,k_j) in [1, floor(g/2)]`, the short arc plus the two edges at
`v` closes a cycle of length `s + 2 <= floor(g/2) + 2 < g` whenever
`g >= 5`; contradiction. For `g = 4`: `s = 1` gives a triangle (`< g`),
impossible, so `s = 2`; three neighbours would contain a pair at `s = 1`. ∎

**L4 (descent).** Let `S` be `V(K)` or the vertex set of a path, and let
`u` have `h := d(u,S) >= 1`. Fix a geodesic
`u = t_h, t_{h-1}, ..., t_1, t_0` with `t_0 in S`. Set
`T_u := {t_h, ..., t_1}` (the *descent*, `h` vertices, disjoint from `S`).
Then (i) `d(t_j, S) = j` for all `j`; (ii) `T_u` induces a path (any chord
`t_i t_j`, `i >= j+2`, would give `d(t_i,S) <= 1 + j < i`); (iii) for
`j >= 2`, `t_j` has no neighbour in `S`. Each descent has exactly one vertex
at each depth `1..h`. ∎

**L5 (attachment to a geodesic base).** Let `P = p_0 ... p_L` be a geodesic
and `v not in V(P)` a vertex with a neighbour in `P`. If `v` has two
neighbours `p_a, p_c` (`a < c`), then `c = a + 2`: indeed `c - a =
d(p_a,p_c) <= 2` (through `v`), and `c = a + 1` would make a triangle
(`g = 3`). Three neighbours are impossible (they would contain a pair at
index distance `>= 3` but `G`-distance `<= 2` through `v`, contradicting
geodesy — actually already two pairs at distance 2 would force indices
`a, a+2, a+4` with `d(p_a, p_{a+4}) = 4 > 2`). Moreover `c = a + 2` closes a
4-cycle `v p_a p_{a+1} p_{a+2}`, so for `g >= 5` the neighbour is unique. ∎

**L6 (three-arc inequality).** Let `K` be any cycle of length `g`, let
`u_1, u_2, u_3` be any vertices with `h_i := d(u_i, K)`. Then

    d(u_1,u_2) + d(u_1,u_3) + d(u_2,u_3) <= 2(h_1 + h_2 + h_3) + g.

*Proof.* Pick nearest cycle vertices `π_i` (so `d(u_i, π_i) = h_i`). The
three points `π_1, π_2, π_3` cut `K` into three (possibly empty) consecutive
arcs of total length `g`, and each pairwise distance `d(π_i, π_j)` is at
most the length of the arc joining them, so
`Σ_{i<j} d(π_i, π_j) <= g`. Now apply the triangle inequality
`d(u_i,u_j) <= h_i + d(π_i,π_j) + h_j` and sum the three. ∎

------------------------------------------------------------------------
## 3. The splice lemma

Two vertex sets *interact* if they share a vertex or some edge of `G` joins
them. Note that adjacent vertices have depths (`d(., K)`) differing by at
most 1, and vertices of a descent `T_u` at depth `j` are unique (L4).

**L7 (splice).** Let `g >= 5`, `K` a shortest cycle, `u != v`,
`u, v not in V(K)`, with fixed descents `T_u, T_v` (to `K`). Then:

**(a)** If `T_u` and `T_v` do not interact, then `F = T_u ∪ T_v` is an
induced forest whose components are exactly the two induced paths
`T_u, T_v`, each sending exactly one edge into `K` (L3, L4), and choosing
`z` outside the two attachment vertices (possible: `g >= 5 > 2`) shows
`M(K) >= h_u + h_v`.

**(b)** If they interact, then `M(K) >= d(u,v) + 1`.

*Proof of (b).* Write `T_v = v = t_{h_v}, ..., t_1` and let

    ν := max { j : t_j interacts with T_u },

i.e. `t_j in T_u` or `t_j` has a neighbour in `T_u`; the set is nonempty.
Put `s' := t_ν`.

*Case A: `v in T_u`.* Since `d(v, K) = h_v`, `v` is `T_u`'s unique depth-
`h_v` vertex, and the sub-path of `T_u` from `u` down to `v` shows
`d(u,v) <= h_u - h_v`. Take `U := T_u`: an induced path with exactly one
edge into `K` (L3/L4), and `|U| = h_u >= d(u,v) + h_v >= d(u,v) + 1`.
Choosing `z` off the single attachment gives the claim.

*Case B: `v not in T_u`.* First, `s'` cannot lie in `T_u` unless `ν = h_v`:
if `s' in T_u` and `ν < h_v`, then `t_{ν+1}` is adjacent to `s' in T_u`, an
interaction at depth `ν + 1 > ν`, contradicting maximality. If `ν = h_v`
then `s' = v not in T_u` by assumption. So in all remaining cases
`s' not in T_u`, and `s'` has a neighbour `s in T_u`, at depth
`ν_u := d(s,K) in {ν-1, ν, ν+1}`.

`s'` has **exactly one** neighbour in `T_u`: two neighbours of `s'` on the
path `T_u` lie within depth window `[ν-1, ν+1]`, so they are at path
distance 1 or 2 on `T_u`; distance 1 closes a triangle, distance 2 closes a
4-cycle — both impossible for `g >= 5`.

Let `U := T_u ∪ { t_j : j >= ν }`. Then:
* the two parts are disjoint (a shared vertex would be an interaction at
  depth `> ν` — for depths `> ν` — or `s' in T_u` at depth `ν`, both
  excluded);
* the only edge between the parts is `s s'` (a vertex `t_j`, `j > ν`,
  interacting with `T_u` contradicts maximality; `s'` has exactly one
  `T_u`-neighbour);
* hence `G[U]` is a tree (two induced paths joined by exactly one edge);
* K-edges of `U`: exactly one from the bottom `t^u_1` of `T_u` (L3/L4);
  vertices `t_j` with `j >= max(ν, 2)` have none; if `ν = 1`, `s' = t_1`
  contributes exactly one more, ending at `a' != a` (the attachment of
  `t^u_1`): otherwise `a = a'` closes the cycle
  `a, t^u_1, ..., s, s', a` of length `ν_u + 2 <= ν + 1 + 2 = 4 < g`
  (using `ν_u <= ν + 1 = 2` and that `s` is at depth `ν_u` on `T_u`,
  so the `T_u`-segment from `t^u_1` to `s` has `ν_u - 1` edges).
* So with `z :=` (the attachment `a'` of `s'`) if `ν = 1`, else any
  non-attachment vertex of `K`, the single component `U` sends exactly one
  edge into `K \ {z}`.

Finally `d(u,v) <= (h_u - ν_u) + 1 + (h_v - ν)` (walk down `T_u` from `u`
to `s`, edge `s s'`, up `T_v` from `s'` to `v`), so

    |U| = h_u + (h_v - ν + 1) >= d(u,v) + ν_u >= d(u,v) + 1 .   ∎

------------------------------------------------------------------------
## 4. The three-point lemma (main engine, `g >= 5`)

**L8.** Let `G` be connected and cyclic with `g >= 5` and `f >= 1`, and let
`K` be **any** shortest cycle. Then

    M(K) >= min( f + 1 , ceil( (2f + D - g) / 2 ) ).

*Proof.* Fix an `f`-realizer `x` (`d(x,B) = f`), and a diametral pair
`(b0, w0)`; by T5 `b0, w0 in B`, hence `d(x,b0) >= f`, `d(x,w0) >= f`,
and `x not in {b0, w0}` (as `x not in B`), `b0 != w0`. For each of
`x, b0, w0` not on `K` fix a descent (L4); members on `K` have empty
descents (depth 0).

*Case 1: some two of the (nonempty) descents interact.* By L7(b),
`M(K) >= d(pair) + 1 >= f + 1`, since every pairwise distance among
`{x, b0, w0}` is `>= f` (`d(b0,w0) = D >= f + 1` by T4).

*Case 2: no two interact.* Let `F` be the union of the nonempty descents:
components are exactly those descents (pairwise disjoint and non-adjacent),
each an induced path with exactly one `K`-edge (L3, L4). Choose `z` outside
the at most 3 attachment vertices (`g >= 5`). Lemma M's condition holds, so
`M(K) >= S := h_x + h_{b0} + h_{w0}`. By L6 applied to `(x, b0, w0)`:

    2f + D <= d(x,b0) + d(x,w0) + d(b0,w0) <= 2S + g ,

so `S >= ceil((2f + D - g)/2)`. ∎

**C8 (main-range closure).** If `g >= 5` and `f >= g - 2*floor(g/3)`, then
`t >= f + ceil(2g/3)`.
*Proof.* With `m = floor(g/3)`, `q = f + 1 - m`: first `f + 1 >= q + 1 > q`
(`m >= 1`). Second, using `D >= f + 1` (T4),

    ceil((2f + D - g)/2) >= ceil((3f + 1 - g)/2) >= q
        <=>  3f + 1 - g >= 2q - 1 = 2f + 1 - 2m
        <=>  f >= g - 2m ,

which is the hypothesis. So L8 gives `M(K) >= q`, and Lemma M gives
`t >= (g-1) + q = f + g - m = f + ceil(2g/3)` by (A0). ∎

Remark. `g - 2*floor(g/3) = m, m+1, m+2` for `g ≡ 0, 1, 2 (mod 3)`
respectively. So C8 covers **all** `f >= m` when `3 | g`, and leaves only
`f = m` (when `g ≡ 1`) and `f in {m, m+1}` (when `g ≡ 2`) — Section 6.

------------------------------------------------------------------------
## 5. The `g = 4` endgame

**L9.** If `g = 4` and `f >= 1`, then `t >= f + 3 = f + ceil(2*4/3)`.

*Proof.* By T4, `f <= D - 1`. If `f <= D - 2`, T1 closes:
`t >= D + 1 >= f + 3`. So assume `f = D - 1`. By T6, `D >= 3` (the case
`D = 2` would force `g = 3`).

Fix a diametral pair `(b0, w0)` (in `B` by T5), a geodesic
`P = p_0 p_1 ... p_D` from `b0` to `w0`, and an `f`-realizer `x`. For every
`i`, `d(x, p_i) >= max(d(x,p_0) - i, d(x,p_D) - (D-i))
>= max(f - i, f - D + i)`, whose minimum over `i in [0,D]` is
`f - floor(D/2) = ceil(D/2) - 1 >= 1` (`D >= 3`). Hence
`δ := d(x, P) >= 1` and `x not in P`. Fix a descent (L4) from `x` to `P`:
`x = u_δ, ..., u_1` (`u_1` adjacent to `P`, `u_j` for `j >= 2` not).

*Case (i): `u_1` has exactly one neighbour in `P`.* Then `F = {u_1}`
satisfies Lemma M-P for the induced path `P`, so
`t >= (D + 1) + 1 = f + 3`.

*Case (ii): `u_1` has two neighbours `p_a, p_{a+2}` (L5; no other patterns
exist).* If `δ = 1`, i.e. `u_1 = x`: then `d(x, p_0) <= a + 1` and
`d(x, p_D) <= (D - a - 2) + 1 = D - a - 1`; both are `>= f = D - 1`, giving
`a >= D - 2` and `a <= 0`, i.e. `D <= 2` — contradiction. So `δ >= 2`.
Reroute: `P' := p_0 ... p_a u_1 p_{a+2} ... p_D` is a `b0`–`w0` walk of
length `D = d(b0,w0)`, hence a geodesic, hence an induced path, with
`|P'| = D + 1`. The vertex `u_2` exists (`δ >= 2`), `u_2 not in P'`
(`d(u_2,P) = 2`), and `N(u_2) ∩ P' = {u_1}` (no `P`-neighbours since
`d(u_2, P) = 2`; and `u_2 ~ u_1`). So `F = {u_2}` satisfies Lemma M-P for
`P'`, and `t >= (D + 1) + 1 = f + 3`. ∎

------------------------------------------------------------------------
## 6. Leftover cases (`g >= 5`, `g not ≡ 0 mod 3`, `q in {1,2}`)

**L10.** If `g >= 5` and `m <= f <= g - 2m - 1` (so `q = f + 1 - m
in {1, 2}`, by the width computation in the remark of Section 4), then
`t >= f + ceil(2g/3)`.

*Proof.* Fix any shortest cycle `K`. Since `f >= 1`, `V != V(K)` (otherwise
chordlessness forces `G = C_g`, whose periphery is everything and `f = 0`).
Pick `u not in V(K)` and let `t_1` be the depth-1 vertex of its descent.

*`q = 1`.* `F = {t_1}` has exactly one `K`-edge (L3), `z` any other cycle
vertex: `M(K) >= 1 = q`, so `t >= g - 1 + q = f + ceil(2g/3)` (arithmetic
as in C8).

*`q = 2`* (here `g ≡ 2 (mod 3)` and `f = m + 1`).
If some vertex has depth `>= 2`, its descent's top two vertices
`{t_2, t_1}` form one component with exactly one `K`-edge (L3, L4):
`M(K) >= 2`. Otherwise every vertex outside `K` has depth exactly 1.

  - If `n = g + 1`: the unique outside vertex `y` has exactly one neighbour
    on `K` (L3, connectivity), so `G = tadpole(g,1)`, i.e. `C_g` plus a
    pendant. By L11 below, its `f` equals `ceil(floor(g/2)/2) <= m` (L12),
    contradicting `f = m + 1`. So this case is vacuous.
  - If `n >= g + 2`: there are `>= 2` depth-1 vertices. No three of them are
    pairwise adjacent (triangle). If two are non-adjacent, take
    `F = {v} ⊔ {v'}`: two singleton components with single attachments
    `a, a'` (possibly equal), `z in K \ {a, a'}` (nonempty, `g >= 5`):
    `M(K) >= 2`. Otherwise there are exactly two and they are adjacent,
    `v ~ v'`, with attachments `a != a'` (equality closes a triangle):
    `F = {v, v'}` is one component sending edges to `a` and `a'` only;
    `z := a'` leaves exactly one edge into `K \ {z}`: `M(K) >= 2`.

Then `t >= g - 1 + 2 = (m + 1) + ceil(2g/3) = f + ceil(2g/3)` by (A0). ∎

**L11 (tadpole).** For `g >= 5`, the graph `C_g` plus one pendant `y` at
`k_0` has `D = floor(g/2) + 1`, periphery
`B = {y} ∪ {k_j : minarc(j,0) = floor(g/2)}`, and
`f = max_{0<=a<=floor(g/2)} min(a + 1, floor(g/2) - a) =
ceil(floor(g/2)/2)`.
*Proof.* Distances: `d(k_i,k_j) = minarc(i,j)`, `d(y,k_j) = 1 +
minarc(0,j)`. Hence `ecc(y) = 1 + floor(g/2)` and `ecc(k_j) =
max(floor(g/2), 1 + a_j)` with `a_j := minarc(j,0) <= floor(g/2)`; so
`D = floor(g/2) + 1` and `ecc(k_j) = D` iff `a_j = floor(g/2)`. For
`v = k_j`: `d(k_j, y) = a_j + 1` and the distance to the nearest antipodal
cycle vertex is `floor(g/2) - a_j` (both parities), so
`d(k_j, B) = min(a_j + 1, floor(g/2) - a_j)`; `d(y, B) = 0`. Maximizing
over `a in [0, H]`, `H := floor(g/2)`: `min(a+1, H-a) >= k` iff
`k - 1 <= a <= H - k`, feasible iff `k <= floor((H+1)/2) = ceil(H/2)`. ∎

**L12.** `ceil(floor(g/2)/2) <= floor(g/3)` for all `g >= 5`.
*Proof.* For `g >= 17`: `ceil(floor(g/2)/2) <= (g+3)/4 <= (g-2)/3 <=
floor(g/3)`. For `5 <= g <= 16`: finite check (values
`1,2,2,2,2,3,3,3,3,4,4,4` vs `1,2,2,2,3,3,3,4,4,4,5,5`). (Verified for
`g in [5, 400]` against the exact graph in `proverB/arith_checks.py`.) ∎

------------------------------------------------------------------------
## 7. Assembly

**Theorem (hard branch of C142).** `G` connected, cyclic, `f >= 1` implies
`t >= f + ceil(2g/3)`.

*Proof.*
* `g = 3`: `ceil(2g/3) = 2`, and `t >= D + 1 >= (f + 1) + 1` by T1 and T4.
* `g = 4`: L9.
* `g >= 5`, `f <= floor(g/3) - 1`: T2 gives
  `t >= g - 1 = (floor(g/3) - 1) + ceil(2g/3) >= f + ceil(2g/3)` (A0).
* `g >= 5`, `f >= g - 2*floor(g/3)`: C8.
* `g >= 5`, `floor(g/3) <= f <= g - 2*floor(g/3) - 1`: L10.
The five cases cover all `f >= 1` (Section 4 remark; exact coverage check
in `proverB/arith_checks.py`). ∎

Together with the compiled skeleton branches (acyclic; `f = 0`), this
proves Conjecture 142 in full.

------------------------------------------------------------------------
## 8. Equality structure (what drove the construction)

The exact oracle (4,665 graphs, 0 violations; `oracle/equality_cases.json`)
has 113 tight instances, **girth 3 and 6 only**:

* All girth-3 equality cases satisfy `t = D + 1` and `f = D - 1`: the
  `g = 3` branch (T1 + T4) is tight at both links.
* The **only** girth-6 equality class is `tadpole(6,1)` (`FK_h_` ≅
  `FhEK?`): `n = 7, D = 4, f = 2, t = 6 = f + 4`. Traced through C8:
  `m = 2`, `q = 1`; taking `x` = a cycle neighbour of the attachment,
  `b0` = the pendant tip, `w0` = the antipode, the three depths are
  `(0, 1, 0)`, so `S = 1 = q` — the three-point lemma is exactly tight,
  as is Lemma M (`t = 5 + 1`). This is the equality mechanism that forces
  `3 | g` (equality in (*) over the reals needs `ceil(2g/3) = 2g/3`).
* On all 113 equality cases the cycle-base bridge is exactly sharp:
  `max_K M(K) = max(q, 0)` with **zero slack** (verified:
  `proverB/analyze_equality_results.json`, histogram `{(3,0): 111,
  (6,0): 2}`). The proof spends its budget with zero waste precisely there.

Necessity of the multi-component machinery: the single-tail bridge
"`exists K : ecc(K) >= q`" is **false** (60 corpus violations, worst slack
`-9`, e.g. `cycle_two_tails(4,3,3)` and a 49-vertex `randLegs` with
`g=8, D=20, f=18, q=17`, max tail 8): no proof that hangs one path off the
cycle can work; the splice/three-tail structure of L7–L8 is essential.

------------------------------------------------------------------------
## 9. Numeric-claim ledger (all exact integer arithmetic, no floats)

| # | Claim tested | Result |
|---|---|---|
| 1 | R2 bridge `f <= g/3 - 1 + max_K M(K)` (session bridge oracle) | 10,481 cyclic graphs, **0 violations**, min slack3 = 0; tight on 113/113 equality cases (`bridge_oracle/bridge_oracle_results.json`, sha256 `FB0A...C9BA`) |
| 2 | Equality-case sharpness `max_K M(K) = max(q,0)` | 113/113 exact (`proverB/analyze_equality_results.json`) |
| 3 | Single-tail bridge `exists K: ecc(K) >= q` (g >= 4) | **FALSIFIED**: 60 violations / 6,834 graphs, min slack −9 (same file) — motivates L7/L8 |
| 4 | Draft case-tree guarantees (T-peels, x-tail metric bound, S3 bound, leftovers) | `proverB/case_tree_probe_results.json`: 0 guarantee failures / 10,663 graphs |
| 5 | **The finished proof, executed verbatim** (every branch builds its certificate; certificates re-verified from scratch: forest/tree checks via networkx `is_tree`, exact edge counts into `K\{z}` resp. `P`, size `>= f + ceil(2g/3)`) | `proverB/constructive_validator.py`: 10,776 graphs (10,663 corpus + 113 equality), **0 failures**; branch coverage: P0 g=3: 2,938; P1 T2: 179; P1t1 g=4 T1: 1,103; P3a: 118; P3b (reroute): 15; P4 three-tails: 3,582; P4 splice-B: 776; P4 splice-A: 6; P5 q=1: 410; P6a: 404; P6b: 24; vacuous branches (g=4 D=2; tadpole q=2) never reached |
| 6 | Choice-independence (proof claims ANY shortest cycle, realizer, diametral pair, descent tie-breaks work): re-run of #5 with all free choices randomized, seeds 1 and 2 | 0 failures each (`constructive_validator_results_seed=*.json`) |
| 7 | Arithmetic side-claims: (A0) and coverage for `g in [3,3000]`; S3-chain; tadpole `f`-formula and L12 for `g in [5,400]` (exact graphs); g=4 δ-bound | `proverB/arith_checks.py`: 0 failures |

Machine-verified `M_P`/`M(K)` semantics inherited from the session bridge
oracle (1,513 + 800 brute-force cross-checks, 0 mismatches).

------------------------------------------------------------------------
## 10. Lean 4 formalization notes (hard steps flagged)

Available already (compiled skeleton): T1, T2, T3, the branch split, the
`f = 0` and acyclic branches.

* **Easy:** T4, T5, T6; assembly arithmetic (A0, coverage, C8's chain,
  L12's finite part); L4 (induction on distance); L10's case split.
* **Moderate:** Lemma M / Lemma M-P — pure counting (`|W| - 1` edges +
  connected ⟹ tree); recommend proving a reusable
  `one_edge_per_component_extension` lemma once and instantiating for both
  bases. L3/L5 — short-cycle contradictions; need "closed walk of length
  `< g` contains a cycle `< g`" API (already used by the 141 lane).
* **Hard, flag 1 — L6 (three-arc):** the "three points cut a cycle into
  three arcs" bookkeeping; suggest formalizing on `ZMod g` positions with
  `minarc(i,j) = min((i-j) % g, (j-i) % g)` and pure `omega`-style case
  analysis, avoiding geometry.
* **Hard, flag 2 — L7 (splice):** the extremal choice `ν := max{...}` over
  a finite set, the per-depth uniqueness of descent vertices, and the four
  girth contradictions (triangle, C4, `a = a'`, `s' in T_u`). All finite
  and explicit but the bookkeeping is the densest of the proof. Recommend
  representing descents as `Fin h → V` with `depth (T i) = i + 1` and
  interactions as a decidable predicate.
* **Hard, flag 3 — L11 (tadpole eccentricities):** fully explicit distance
  formulas on `C_g` + pendant; tedious `minarc` case analysis (parities).
  Only needed for the `q = 2, n = g + 1` vacuity; an alternative is to
  formalize the contradiction "`n = g+1` and `ecc(K) = 1` and `f = m+1`"
  directly by computing `d(k_j, B)` on the explicit graph — same content.
* The certificates are all explicitly constructed (no compactness, no
  unquantified extremal choices except finite maxima) — Lean-friendly by
  design.

------------------------------------------------------------------------
## Files

* This proof: `problems_external/wowii_142/PROOF_142_B.md`
* Scratch/validation: `problems_external/wowii_142/proverB/`
  (`analyze_equality.py`, `case_tree_probe.py`, `constructive_validator.py`,
  `arith_checks.py` + result JSONs)
* Session-level bridge oracle (input evidence):
  `problems_external/wowii_142/bridge_oracle/`, report `BRIDGE_REPORT.md`.
