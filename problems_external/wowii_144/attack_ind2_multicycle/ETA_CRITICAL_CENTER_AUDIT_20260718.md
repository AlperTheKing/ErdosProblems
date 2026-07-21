# W144-IND2 eta-critical center audit

## Exact frontier

For a connected cyclic graph `X`, write

```text
g(X)   = girth(X),
C(X)   = the full ordinary center set,
eta(X) = max_x d_X(x,C(X)),
Phi(X) = g(X)+eta(X).
```

The unresolved direct lemma says that every connected multicyclic simple
graph `G` with `g(G)>=5` has a vertex `v` for which `H=G-v` is connected and
cyclic and `Phi(H)>=Phi(G)`.  This note does not claim that lemma.  It records
the exact center-set consequence that any counterexample must satisfy.

## Bad-deletion center lemma

Let `H=G-v` be connected and cyclic.  Put

```text
g=g(G), g'=g(H), r=rad(G), r'=rad(H),
C=C(G), C'=C(H), e=eta(G), e'=eta(H).
```

If `Phi(H)<Phi(G)`, then

```text
e' <= e-(g'-g)-1.                                      (1)
```

In particular `e>=1`.  If `x!=v` and `d_G(x,C)=e`, then some `u in C'`
satisfies

```text
d_G(x,u) <= d_H(x,u) <= e' < e,
```

and hence `u` is not in `C`.  Thus every surviving eta-realizer forces a
genuinely new center after a bad deletion.

If in addition `r'<=r`, then every `u in C'-C` satisfies the sharper exact
description

```text
r'=r,
ecc_G(u)=r+1,
v is the unique eccentric vertex of u in G.             (2)
```

Proof of (2): every vertex `y!=v` obeys
`d_G(u,y)<=d_H(u,y)<=r'<=r`.  Since `u` is not central in `G`, its
eccentricity is at least `r+1`, so the only possible eccentric vertex is
`v`.  If `w` is the neighbor of `v` on a shortest `u-v` path, then
`d_G(u,v)-1=d_G(u,w)<=d_H(u,w)<=r'<=r`.  Hence
`d_G(u,v)=r+1`; the same chain forces `r'=r`.

Consequently, for distinct bad vertices `v,w` with nonincreasing deletion
radius,

```text
(C(G-v)-C(G)) intersect (C(G-w)-C(G)) = emptyset.
```

no vertex can have both `v` and `w` as its unique eccentric vertex.  If `R`
is the eta-realizer set, at most one deletion removes all of `R`; every other
such deletion has new centers of eccentricity exactly `r+1`, and for each
surviving realizer at least one of those new centers lies within the bound
(1).

There is one useful automatic source of the hypothesis `r'<=r`.  If `v` is
an eccentric vertex of an old center `c` and `G-v` is connected, no shortest
`c-y` path for `y!=v` can use `v`, since that would put `y` farther than
`r` from `c`.  Therefore `ecc_H(c)<=r` and `r'<=r`.

## Exact finite evidence and failed shortcuts

The unrestricted eta-preserving strengthening

```text
exists admissible v with eta(G-v)>=eta(G)
```

holds for all 38,066 multicyclic girth-at-least-five graphs of order 13.
Together with the earlier orders, the direct `Phi` lemma has no exact failure
through order 13.  A separate mutation search evaluated 15,736 exact graphs
of orders at most 35, starting from tight records; its minimum best deletion
slack was zero, not negative.  These are falsification results, not proofs.

The center lemma cannot be closed by any of the following shortcuts.

* ``FCR`o`` has `g=5`, `r=2`, `eta=1`, and
  `C={2,5,6}`.  Its only admissible central deletion is `v=2`, which gives
  `(g',r',eta')=(6,3,0)`.  Its other good deletions preserve eta while moving
  or enlarging the center, so center containment is not a necessary witness.
* ``G?`e_w`` has `g=5`, `r=2`, `eta=2`, and unique center `7`, but no
  admissible central vertex.
* `K??CA?_sDOEg`, `v=4`, has `r'=r=3` and deletes a non-realizer, but
  `C'={2,3,10}` is not contained in `C={2,10}` and eta drops from `3` to `2`.
  This is the exact reason that `r'<=r` alone does not control the center.
* `H?ABE_]`, `v=5`, shows that even a vertex which is not the unique
  eccentric point of any old vertex can be a bad deletion: `Phi` drops from
  `7` to `6` while the radius rises from `2` to `3`.
* ``I?`@f?[Q_`` with `v=9` hits every shortest cycle, but
  `(g,eta)=(5,2)` becomes `(6,0)`.  Thus a shortest-cycle transversal is not
  automatically good.

## Remaining unsupported implication

In a hypothetical `Phi`-critical multicyclic graph, every admissible
radius-nonincreasing deletion other than a possible deletion of the sole
eta-realizer must therefore create a distinct vertex of eccentricity `r+1`
whose unique eccentric point is the deleted vertex, and those new centers
must cover every surviving eta-realizer within the strict bound (1).

What is not proved is that this simultaneous family of unique-eccentric-point
witnesses is impossible in a girth-at-least-five multicyclic graph.  Exact
examples above show that center expansion, radius increase, deletion on a
shortest cycle, and deletion off it all genuinely occur.  Any claim that the
witness family forces cycle rank one needs an additional global block/ear
argument; no such argument is currently established.  This is the first
unsupported implication, so no further restricted deletion hierarchy is
opened here.
