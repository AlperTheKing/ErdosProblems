# Counterexample to the maximum-tree center-geodesic boundary lemma

Date: 2026-07-18.

## Proposed direct lemma

Let `x` be an eta-realizer, let `c` be a nearest center, let `Q` be a shortest
`x`--`c` path, and let `T` be a largest induced tree among those containing
`Q`.  The proposed lemma asked for a boundary vertex `z` and two neighbors
`a,b` of `z` in `T` such that the unique `a`--`b` path `T[a,b]` satisfies

```text
|V(T[a,b]) intersect V(Q)| <= 1.                             (MT)
```

The bridge to W144 was exact: maximality gives at least two `T`-neighbors of
every boundary vertex; `z+a--T--b+z` is a cycle, so `T[a,b]` has at least
`g-1` vertices; and (MT) would give

```text
|T| >= |V(T[a,b]) union V(Q)| >= (g-1)+(eta+1)-1 = g-1+eta.
```

The lemma is false even after allowing existential choice of `x,c,Q,T`.

## Smallest multicyclic counterexample

The exact graph is

```text
graph6: I?ABAaIBO
n=10, m=11, beta=2, girth=5,
C(G)={1,4,6,7}, eta(G)=2, eta-realizers={0,5}.
```

Its edges are

```text
05 08 16 17 26 37 48 49 59 68 79.
```

There are exactly four eta-realizer/nearest-center geodesics:

```text
Q1=0-8-4,  Q2=0-8-6,  Q3=5-9-4,  Q4=5-9-7.
```

For `Q1,Q2`, the unique largest induced tree containing `Q` is `G-9`.  It has
order nine.  Its boundary vertex is `9`, with tree-neighbor set `{4,5,7}`.
For every pair in this set, the tree path meets `Q` in at least two vertices.
The minimum is two for both `Q1` and `Q2`.

For `Q3,Q4`, the unique largest induced tree containing `Q` is `G-8`.  Its
boundary vertex is `8`, with tree-neighbor set `{0,4,6}`.  Again every pair
has overlap at least two, with minimum two.

The order-nine trees are maximum because `G` itself is cyclic.  Their
uniqueness can also be seen without enumeration.  An order-nine induced tree
must delete a degree-three vertex.  For `Q1,Q2`, deleting `6` isolates `2`,
deleting `7` isolates `3`, and deleting `8` is forbidden by `Q`; only deletion
of `9` works.  The reflected argument applies to `Q3,Q4`.

Thus the best possible overlap over **all** permitted choices is exactly two,
not at most one.  Notice that W144 is not threatened: these maximum trees
have order nine, while the target is only `5-1+2=6`.  What fails is the
proposed route for certifying their size.

## Smaller unicyclic counterexample

Without the multicyclic restriction, the first obstruction is `F?bao`, a
seven-vertex graph of girth five and eta two.  Exhausting its four
eta-realizers and all constrained maximum trees again gives best overlap two.
The multicyclic record above shows that excluding the already-proved
unicyclic base does not repair (MT).

## Verification

`test_max_tree_geodesic_boundary.py` enumerates every eta-realizer, every
nearest center, every shortest path, and every maximum induced tree containing
that path.  The exact all-choice records are

```text
max_tree_geodesic_boundary.json
max_tree_geodesic_boundary_multicyclic.json.
```

The multicyclic search tested 163 graphs through the first failure and records
all four choices above.  This counterexample closes the maximal-tree boundary
route; weakening (MT) to two common vertices loses exactly one vertex in the
displayed W144 count and is not the claimed bridge.
