# W144 Steiner complement min--max audit

Date: 2026-07-18.

This note does **not** claim a proof of W144 or of the Steiner frontier.  It
records an exact cut-family reformulation, proves that reformulation, and
gives small exact counterexamples to two natural constructions.

## 1. Exact complement/cut equivalence

Let `G` be connected, let `v` be fixed, let `X` be a `p`-set avoiding `v`,
and put `S=V(G)\X`.  Define

    b(X)=min{|Y| : Y subset X and G[S union Y] is connected}.

Fix an integer `t` with `1<=t<=p`, and put `q=p-t+1`.  Then

> **Cut-family lemma.**  `b(X)>=t` if and only if `G-Z` is disconnected for
> every `q`-set `Z subset X`.

**Proof.**  If `G-Z` is connected for a `q`-set `Z subset X`, then
`Y=X\Z` has size `t-1` and `G[S union Y]=G-Z` is connected, so
`b(X)<=t-1`.

Conversely, suppose `b(X)<=t-1`.  There is `Y subset X`, `|Y|<=t-1`, for
which `G[S union Y]` is connected.  Put `Z_0=X\Y`; then `|Z_0|>=q` and
`G-Z_0` is connected.  While `|Z_i|>q`, connectivity of `G` supplies an
edge from the nonempty connected set `V(G)\Z_i` to `Z_i`.  Restore the
endpoint in `Z_i`.  This produces `Z_(i+1) subset Z_i` with one fewer
vertex and with `G-Z_(i+1)` connected.  At size `q` this contradicts the
displayed cut condition.  QED.

For the registered W144 notation `k=g-1`, `p=n-g+1`, and
`t=d(v,C)`, this says that (VE) is exactly the assertion that some `p`-set
`X` avoiding `v` induces a complete `q`-uniform cut family, where

    q=n-g+2-d(v,C).

The stronger Steiner-radius candidate replaces `t` by
`e=max_x d(x,C)` and requires such an `X` for every excluded root `v`.

## 2. A nearest-center geodesic need not lie in a witness

The graph6 graph

    G?`ad_

has vertices `0,...,7` and edges

    04, 07, 15, 16, 25, 27, 36, 37.

It is unicyclic of girth six, with center `{2,3,7}`.  For `v=1` one has
`d(v,C)=2`, `p=3`, and valid complements include `X={5,6,7}` (indeed every
two-subset of this `X` disconnects the graph).  An exhaustive check of all
valid three-sets `X` shows, however, that none contains all non-`v`
vertices of a shortest `v`--center path.  Thus a BFS proof cannot prescribe
that the deleted complement contain a nearest-center geodesic.

## 3. Articulation reduction is insufficient

The graph6 graph

    G?qa`o

has edges

    04, 05, 14, 16, 25, 27, 36, 37, 47.

It is 2-connected, has girth five and center `{4,7}`, but vertex `5` has
center-distance two.  Hence even the case `t=2` cannot be reduced to two
successive articulation vertices.  Valid complements do exist; for example
`X={2,4,6,7}` has `p=4`, and each of its three-subsets disconnects the
graph.

## 4. Verification and exact remaining bridge

The cut-family statement above is an equivalence, not a new surrogate.  A
fixed-seed exact search additionally checked (VE) on 460 randomly generated
connected girth-at-least-five graphs of orders 14--16 (girths 5--9), with no
failure.  This supplements, but does not replace, the exhaustive audit
through order 13.

The missing implication is now precise: from `d(v,C)=t` (or globally from
`e=max d(.,C)`), construct a `p=n-g+1` set `X` avoiding the prescribed root
such that **all** its `q=p-t+1` subsets are vertex cuts.  Neither a single
center geodesic nor a block-cut chain supplies this family.  No general
separator or greedoid min--max theorem establishing it was found in this
audit.
