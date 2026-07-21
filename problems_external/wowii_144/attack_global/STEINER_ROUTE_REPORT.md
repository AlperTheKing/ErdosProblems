# W144: the `(g-1)`-terminal Steiner route

Date: 2026-07-18.

This note does **not** claim a proof of Conjecture 144.  It records a short
complete reduction for `g>=5`, an exact counterexample to the unrestricted
version at `g=4`, and the one metric implication still missing.

## 1. Definitions

For a nonempty vertex set `S`, let `d_G(S)` be the minimum number of edges in
a connected subgraph of `G` containing `S`.  For `2<=k<=|V(G)|`, put

    e_k(v)=max{d_G(S): |S|=k and v in S},
    sdiam_k(G)=max_v e_k(v).

Let `C` be the ordinary center of `G` and write `d(v,C)` for distance to it.

## 2. The induced-connector step is complete

**Lemma.**  If `G` has girth `g` and `|S|<=g-1`, then `S` is contained in an
induced tree of order at least `d_G(S)+1`.

**Proof.**  Choose an induced connected subgraph `H` containing `S`, minimal
by vertex inclusion.  We first recall the minimal-connector cycle argument.
If `L` is a cycle of `H`, then for every `a in V(L)` the path `L-a` lies in
one component `Q_a` of `H-a`.  Minimality gives a terminal
`s_a in S-V(Q_a)`.  Fix, for each terminal `s`, a shortest path from `s` to
`L`, and let `c(s)` be its first vertex on `L`.  The terminal `s_a` can leave
`Q_a` only through `a`, so `c(s_a)=a`.  Thus `a -> s_a` is injective and

    |V(L)| <= |S| <= g-1,

contrary to the definition of girth.  Hence `H` is a tree.  Since every
connected subgraph containing `S` has at least `d_G(S)` edges,
`|V(H)|=|E(H)|+1>=d_G(S)+1`.  QED.

Consequently the following one-line metric statement would prove W144 for
`g>=5`:

    sdiam_(g-1)(G) >= g-2 + ecc(G,C).                       (SD)

Indeed, apply the lemma to a maximizing `(g-1)`-set.  Its induced connector
has at least `g-1+ecc(G,C)` vertices.

The current exact frontier is the stronger Steiner-radius statement

    srad_(g-1)(G)=min_v e_(g-1)(v) >= g-2+ecc(G,C).          (SR)

Thus every root has a terminal witness meeting the global right side; in
particular (SR) implies (SD) directly.

## 3. The unrestricted girth statement is false

The graph6 graph

    H?zTbbo

has order `9`, girth `4`, radius `2`, diameter `3`, a unique center, and
`ecc(G,C)=2`, but

    sdiam_3(G)=3 < 4=(g-2)+ecc(G,C).

It is `K_{4,5}` with four independent matching edges removed.  More
explicitly, one side is `A={0,1,2,3}` and the other is
`B={4,5,6,7,8}`; vertex `8` is adjacent to all of `A`, while each of
`4,5,6,7` misses a distinct vertex of `A`.  Vertex `8` is the unique center
and the other four vertices of `B` are at distance two from it.

Every triple has a connector with at most three edges: three vertices in
`A` use the star through `8`; three vertices in `B` have a common neighbor
in `A`; and a mixed triple is joined by a three-edge alternating path when
it is not already connected.  A triple of vertices in `A` needs a Steiner
vertex, so its distance is exactly three.  Thus the failure is rigorous,
not merely computational.  It does not affect the registered W144 route,
where `g<=4` is handled separately.

## 4. Exact tests for `g>=5`

`test_steiner_vertex_fast.py` generated every connected triangle-free and
square-free graph of orders `5` through `13` with nauty
`geng -c -t -f` and computed all Steiner distances by an exact superset
minimum transform.  It checked 52,000 cyclic graphs of girth at least five
and 663,650 rooted vertex instances.  There were zero failures of (VE) and
minimum slack zero.  The separate `test_steiner_radius_bound.py` audit found
zero failures of the stronger (SR), again with minimum slack zero.  In
particular, orders `12` and `13` contributed 7,616 and 42,344 graphs.

These computations are evidence only.

## 5. Exact missing implication and failed shortcuts

The single missing implication is (SR):

> If `G` is connected of girth `g>=5`, `k=g-1`, `C` is its ordinary center,
> and `e=max_x d(x,C)`, then every vertex `v` has a `k`-set `S` containing
> `v` for which every `S`-Steiner tree has at least `k-1+e` edges.

Two tempting exchange shortcuts are false.

1. Steiner eccentricity need not increase along an edge directed away from
   the center.  In `ECpo` (a 5-cycle with one leaf), a central vertex and an
   adjacent vertex at center-distance one both have Steiner 4-eccentricity
   four.  Thus (VE) cannot be obtained by summing strict one-edge increases.
2. It is not enough to take `v`, one farthest vertex from `v`, and `g-3`
   vertices of a shortest cycle.  The graph `F?bao` has `g=5` and a vertex
   at center-distance two for which every terminal set of that restricted
   form has Steiner distance at most four, while (VE) requires and attains
   five using a different four-terminal set.

Thus the nearest-center-geodesic exchange still has to explain a global
choice of the other `g-2` terminals.  Once (VE) is proved, no rooted-capacity,
component summation, or deletion-root choice remains: Section 2 completes
the exact conjecture directly.
## 6. Two exact auxiliary reductions

The following tree bound is complete.  If `T` is a tree of order `n`, then

    e_k^T(v) >= min(ecc_T(v)+k-2,n-1)
             >= k-1+min(d_T(v,C(T)),n-k).                  (TL)

For the first inequality, start with a farthest vertex from `v`.  Whenever
the unique hull of the current terminal set is not spanning, add a vertex
outside that hull; the hull gains at least one edge.  The second inequality
uses the tree identity
`ecc_T(v)=rad(T)+d_T(v,C(T))`.  As an independent check, (TL) passed every
tree through order 13: 2,287 trees and 316,484 triples `(T,v,k)`.

If `c` is an ordinary center and `T` is a BFS spanning tree rooted at `c`,
then `rad(T)=rad(G)`, `c in C(T)`, and distances from `c` are preserved.
Thus (TL) supplies the desired bound in `T` once
`d(v,C(G))<=n-g`.  The latter order bound passed all 21,786 rooted exact
instances through order 11, but a proof and, more importantly, control of
the loss caused by non-tree edges are still missing.

There is also a useful exact complement formulation.  Put
`k=g-1` and `p=n-k=n-g+1`.  For a `p`-set `X` avoiding `v`, let

    b(X)=min{|Y|: Y subset X and G[V(G)-(X-Y)] is connected}.

For `S=V(G)-X`, a smallest connector contains exactly `b(X)` vertices of
`X`, and hence

    d_G(S)=k-1+b(X).

Consequently (SR) is equivalent to finding, for every root `v`, a `p`-set
`X` avoiding `v` with `b(X)>=e`.  This is the exact place where a direct
terminal exchange must show that fewer than `e` restored deleted vertices
cannot bypass all separations; girth `g` is the only available control on
those bypasses.

A proposed Steiner-center decomposition does not provide that control.
Writing `R_k=min_v e_k(v)` and `C_k={v:e_k(v)=R_k}`, the inequality
`e_k(v)>=R_k+d(v,C_k)` is false already for graph6 `F?bBo` (`n=7,g=5`):
at vertex 0 its two sides are 5 and 6.  The companion inequality
`d(v,C)<=d(v,C_k)+R_k-(k-1)` passed all 21,786 rooted instances through
order 11, but cannot imply (VE) without the falsified first inequality.

The W144-only weakening of the same split is false as well.  It is not enough
to ask that *some* vertex realizing `ecc(G,C)` satisfy
`e_k(v)>=R_k+d(v,C_k)`.  In graph6 `H?BDA_{` (`n=9,g=5`), the two outer
realizers are vertices 6 and 7; for each, `d(v,C)=2`, `R_k=5`,
`d(v,C_k)=2`, and `e_k(v)=6<7`.  Thus the Steiner-center split is dead even
at the exact W144 maximizers, and the frontier remains (SR) itself.



## 7. Completed total-cover order lemma

The separate note `ORDER_COVER_LEMMA_20260718.md` proves

    ecc(G,C(G)) <= |V(G)|-girth(G)

for every connected cyclic graph.  More precisely, for a shortest cycle
K, an outer realizer at height h, and the cycle witness window W, it proves
the global component budget

    sum_H |E_H| + max(0,2(e-h)-g) <= 2(|V(G)-K|-h).

The proof has been audited through order 13 (52,000 graphs and 31,636
cycle/realizer/anchor cases, zero failures).  It closes the unconstrained
outside-vertex count n-g>=e, but not the conversion of those vertices to an
admissible induced forest or a Steiner complement.  Thus it is a proved
auxiliary fact and does not close (SR) or W144.
