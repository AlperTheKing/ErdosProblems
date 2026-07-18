# Referee note: total domination in the two structural branches

Date: 2026-07-18

Scope: lemmas `L4` and `L5` in `APPROACH_REGISTRY.md`, together with an
independent correctness audit of `compute/exhaustive_small.py` and its stored
order-nine report.  The structural dichotomy `L314-Structure` itself is not
proved here.

Verdict: **no flaw found in `L4`, `L5`, or the exhaustive enumeration.**  The
classifications below are stronger than the cardinality statements needed by
the conjecture and explicitly cover `K2`, `C5`, multiple universal false
twins, and multiple vertices in a blow-up bag.

## Definitions used

A total dominating set (TDS) of a loopless graph `G` is a vertex set `S` such
that every vertex, including every member of `S`, has a neighbor in `S`.  It is
minimal when no proper subset is a TDS.  Total domination is upward monotone:
if `T` is a TDS and `T subseteq S`, then `S` is a TDS.  Consequently, for a
finite `S`, minimality is equivalently tested by requiring `S \ {s}` not to be
a TDS for every `s in S`.  This justifies the single-deletion test in
`minimal_tds`.

## L4: connected chain graphs

### Exact classification

Let `G` be a finite connected bipartite graph with at least two vertices, with
bipartition `X disjoint_union Y`.  Suppose the neighborhoods of vertices in
each of `X` and `Y` are linearly ordered by inclusion.  Put

```
U_X = {x in X : N(x) = Y},
U_Y = {y in Y : N(y) = X}.
```

Then `U_X` and `U_Y` are nonempty, and the minimal total dominating sets of
`G` are **exactly**

```
{x,y},  where x in U_X and y in U_Y.
```

In particular every minimal TDS has cardinality two.

### Proof

Because `G` is connected and has at least two vertices, both bipartition
classes are nonempty and every vertex has a neighbor.  The finite chain
`{N(x) : x in X}` has a largest member, say `N(x_*)`.  Every `y in Y` belongs
to `N(x_y)` for some `x_y in X`; maximality gives
`N(x_y) subseteq N(x_*)`.  Hence `N(x_*) = Y`, so `U_X` is nonempty.  The same
argument with the two sides exchanged shows that `U_Y` is nonempty.

For an arbitrary set `S`, bipartiteness gives the exact decomposition

```
S is a TDS
iff every y in Y has a neighbor in S intersect X
    and every x in X has a neighbor in S intersect Y.
```

Let `S` now be a minimal TDS.  The set `S intersect X` is nonempty.  Choose
`x in S intersect X` whose neighborhood is largest among the neighborhoods
of the selected `X`-vertices.  Since those neighborhoods form a chain,

```
union {N(z) : z in S intersect X} = N(x).
```

The left side is all of `Y`, by total domination, so `x in U_X`.  If a second
vertex `z` belonged to `S intersect X`, deleting `z` would leave `x`, which
still dominates all of `Y`; domination of `X` depends only on
`S intersect Y` and is unchanged.  Thus `S \ {z}` would remain a TDS,
contrary to minimality.  Therefore `S intersect X = {x}` with `x in U_X`.
The symmetric argument gives `S intersect Y = {y}` with `y in U_Y`, proving
the necessary form.

Conversely, if `x in U_X` and `y in U_Y`, then `{x,y}` totally dominates `G`.
Every TDS must meet both nonempty bipartition classes, so no proper subset of
`{x,y}` is a TDS.  Hence the pair is minimal.

### Edge cases

* For `K2`, both sides are singletons and the classification gives its unique
  minimal TDS, the two vertices.
* A side may contain several universal vertices (necessarily false twins).
  There is no uniqueness claim: every choice of one universal vertex from
  each side gives a different minimal TDS, and these are all of them.
* A connected one-vertex graph has no TDS, but it is excluded by the target's
  `Nontrivial` hypothesis.  The two-vertex argument therefore has no hidden
  empty-side case.

## L5: nonempty `C5` blow-ups

### Exact classification

Let the vertex set be partitioned into five nonempty independent bags
`A_0,...,A_4`, with all possible edges between `A_i` and `A_{i+1}` (indices
modulo five) and no other edges.  Then the minimal total dominating sets are
exactly

```
{a_i, a_(i+1), a_(i+2)}
```

where `i` is taken modulo five and one arbitrary vertex is chosen from each of
the three displayed bags.  In particular every minimal TDS has cardinality
three.  Their exact number is

```
sum_i |A_i| |A_(i+1)| |A_(i+2)|.
```

### Support reduction

For `S subseteq V(G)`, define its occupied-bag support by

```
I(S) = {i in Z/5Z : S intersect A_i is nonempty}.
```

For any `v in A_i`, the selected neighbors of `v` lie precisely in
`(S intersect A_(i-1)) union (S intersect A_(i+1))`.  Since every bag is
nonempty, it follows in both directions that

```
S is a TDS of G  iff  I(S) is a TDS of C5.
```

Vertices in one bag are false twins.  If a TDS `S` contains distinct
`u,v in A_i`, then `S \ {u}` has the same occupied-bag support and is still a
TDS.  Thus a minimal TDS contains at most one vertex from each bag.  Under
this restriction, taking occupied-bag support is a bijection between subsets
of `S` and subsets of `I(S)`, and the displayed TDS equivalence proves

```
S is minimal in G  iff  I(S) is minimal in C5.
```

This deals directly with the false-twin/minimality issue; merely observing
that bag vertices are false twins would not by itself be enough without the
support equivalence.

### Minimal TDSs of `C5`

Let `I` be a TDS of `C5`.  Every selected vertex must itself have a selected
neighbor, so the subgraph induced by `I` has no isolated vertex.

No set of at most two vertices is a TDS.  A one-vertex set cannot dominate its
selected vertex.  If a two-vertex set totally dominated its selected
vertices, the two vertices would have to be adjacent; an adjacent pair in
`C5` leaves the vertex opposite that edge undominated.

If `|I| = 3`, the induced subgraph on `I` has no isolated vertex.  Since `C5`
is triangle-free, it must contain a two-edge path, and hence its three
vertices are consecutive on the cycle.  Conversely, any three consecutive
vertices form a TDS: the middle selected vertex and the two selected endpoints
dominate one another, while the two remaining cycle vertices are dominated by
the endpoints.  Such a triple is minimal because no two-set is a TDS.

Every four- or five-vertex subset of `C5` contains three consecutive vertices,
which already form a TDS, so no such set is minimal.  The minimal TDSs of
`C5` are therefore precisely its five consecutive triples.  Combining this
with the support reduction proves the classification for every nonempty
blow-up.  When all bags are singletons this specializes to `C5` itself and
gives its five minimal TDSs.

## Audit of `exhaustive_small.py`

### Soundness of generated graphs

The induction starts from the empty graph.  When a new vertex is attached,
its neighbor mask is required to be independent in the parent.  Since the
parent is triangle-free, this excludes every old triangle and every triangle
using the new vertex.  The resulting child is then rejected whenever
`has_induced_p5` succeeds.

On five vertices, a connected graph with degree multiset
`[1,1,2,2,2]` has degree sum eight and therefore four edges.  It is a tree,
and that degree sequence makes it exactly `P5`.  Hence `has_induced_p5` is an
exact test, not only a necessary test.  Every retained graph is consequently
triangle-free and induced-`P5`-free.

### Completeness of hereditary vertex extension

Both forbidden properties are hereditary.  Let `H` be any graph of order
`n` in the class and delete an arbitrary vertex `v`.  By induction, an
unlabeled representative of `H-v` occurs among the parents.  Pull the
neighborhood of `v` back along an isomorphism from that representative to
`H-v`.  It is an independent mask because `H` is triangle-free.  Adding a
vertex with exactly that mask reconstructs a graph isomorphic to `H`, and the
induced-`P5` test cannot reject it because `H` is in the class.  Thus every
unlabeled graph in the class is generated.

### Exactness of the isomorphism quotient

Every component of `invariant_key` is invariant under graph isomorphism:
order, edge count, component sizes, sorted degrees, per-vertex triangle
counts, and the Weisfeiler--Lehman hash.  Therefore isomorphic candidates
cannot be placed in different buckets.  Within a bucket the code calls
`networkx.is_isomorphic`, an exact test, before accepting a candidate.  A WL
hash collision is harmless because it merely causes more exact comparisons.
The NetworkX warning that the hash implementation changed in version 3.5
affects cross-version hash strings, not correctness within a run or the exact
quotient.

As an additional check independent of the buckets, every pair of retained
graphs of each order through nine was compared directly with
`networkx.is_isomorphic`; no isomorphic pair was found.

### Correctness of the property checks

* `minimal_tds` examines every vertex subset.  The total-domination predicate
  is exact, and testing every one-vertex deletion is equivalent to inclusion
  minimality by upward monotonicity.
* `chain_graph` first checks bipartiteness and then checks pairwise
  comparability of all open neighborhoods on both sides.  On the connected
  graphs passed by `audit_order`, this is exactly the chain-graph description
  used in `L4`.
* `c5_blowup` partitions vertices by equality of open neighborhoods.  Each
  such class is independent: two adjacent vertices cannot have identical open
  neighborhoods in a loopless graph.  Adjacency between two distinct classes
  is uniform, again by equality of neighborhoods.  Thus obtaining five
  nonempty classes with quotient `C5` is equivalent to being a nonempty
  `C5` blow-up; there is neither a false positive nor a false negative.
* `audit_order` intentionally excludes the singleton by requiring `n > 1`.
  Every connected nontrivial graph has a TDS and therefore a minimal one, so
  an empty TDS-size profile cannot hide a WTD failure in the audited range.

## Independent count checks

A fresh in-memory regeneration recomputed every stored non-timing field and
matched `compute/exhaustive_n9.json`.  Direct all-pairs isomorphism checks also
confirmed that each order contains exactly one representative per generated
isomorphism class.  The stored counts are:

| `n` | all class graphs | connected nontrivial | chain | `C5` blow-up | TDS profiles |
|---:|---:|---:|---:|---:|:---|
| 1 | 1 | 0 | 0 | 0 | none |
| 2 | 2 | 1 | 1 | 0 | `1 x (2)` |
| 3 | 3 | 1 | 1 | 0 | `1 x (2)` |
| 4 | 7 | 3 | 3 | 0 | `3 x (2)` |
| 5 | 13 | 5 | 4 | 1 | `4 x (2), 1 x (3)` |
| 6 | 29 | 11 | 10 | 1 | `10 x (2), 1 x (3)` |
| 7 | 57 | 19 | 16 | 3 | `16 x (2), 3 x (3)` |
| 8 | 125 | 41 | 36 | 5 | `36 x (2), 5 x (3)` |
| 9 | 254 | 74 | 64 | 10 | `64 x (2), 10 x (3)` |

There are no WTD failures and no dichotomy failures in the report.

Three separate cross-checks support these numbers:

1. Filtering NetworkX's independent graph atlas gives total-class counts
   `1,2,3,7,13,29,57` and connected counts `1,1,1,3,5,11,19` through order
   seven (the first connected count includes the singleton), exactly matching
   the report.
2. Connected chain graphs can be counted independently as Ferrers diagrams.
   For bipartition sizes `p,q`, connectedness gives a partition `lambda` of
   length `p` with `lambda_1=q` and all parts positive; quotienting by
   conjugation accounts for swapping the bipartition sides.  This gives chain
   counts `1,1,3,4,10,16,36,64` for orders two through nine.  Positive
   five-part compositions modulo the dihedral action on the cycle give
   blow-up counts `1,1,3,5,10` for orders five through nine.
3. With connected counts `c_1=1` and, for `n>=2`, the sum of the preceding two
   branch counts, the component-multiset identity

   ```
   A(x) = product_{k>=1} (1-x^k)^(-c_k)
   ```

   gives coefficients `1,2,3,7,13,29,57,125,254` through order nine, again
   exactly the reported totals.

Finally, the stronger classifications proved above were checked directly on
all connected generated graphs through order nine: all 135 chain graphs had
precisely the universal-opposite-side pairs as their minimal TDSs, and all 20
`C5` blow-ups had precisely the one-per-bag consecutive triples.

## Lean-facing lemma boundary

The cleanest formal decomposition is:

1. prove total domination in a bipartite graph is equivalent to the two
   opposite-side domination conditions;
2. prove a finite nonempty inclusion chain whose union is the whole opposite
   side has a selected member equal to that whole side;
3. derive the exact universal-pair classification for chain graphs;
4. define the occupied-bag support for a blow-up and prove the TDS equivalence
   with `C5`;
5. prove minimality forbids two selected vertices from one bag;
6. classify the five minimal TDSs of `C5` and lift them through support.

These are finite, load-bearing lemmas that directly yield cardinalities two
and three in the two branches.  No additional graph-family search or
surrogate invariant is needed for `L4` or `L5`.
