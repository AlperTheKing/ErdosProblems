# Independent referee report (root)

**Manuscript:** `PROOF.md`  
**Decision:** ACCEPT, conditional only on the separate priority search.

## Statement audit

The denominator-free inequality is exactly
[
  g(G)+1le t(G)delta'(G).
]
For a finite connected nontrivial graph every degree is positive. Thus the split
(delta'=1) versus (delta'ge2) is exhaustive, and (delta'=1) means that
the degree sequence begins with two 1s, hence there are two distinct leaves.

## Case (delta'ge2)

A shortest cycle is chordless: either arc cut off by a chord is a strictly
shorter cycle. Removing one cycle vertex therefore gives an induced path of
order (g-1). The arithmetic
[
  tdelta'ge2(g-1)ge g+1
]
uses only (gge3), with equality in the last step at (g=3). This case is
complete.

## Two-leaf lemma audit

1. The class maximized over is nonempty: a shortest path between the two leaves
   is induced and is a tree.
2. A maximum member exists because the ambient vertex set is finite.
3. Such a tree cannot be spanning in a cyclic graph, since an induced spanning
   subgraph is the whole graph.
4. Connectedness and properness give an edge crossing from its vertex set to
   the complement, so the boundary vertex (z) exists.
5. If (z) had exactly one neighbor in the tree, adding (z) would preserve
   inducedness, connectedness, acyclicity, and both selected leaves. This
   contradicts maximality. The chosen (z) already has at least one neighbor,
   so zero neighbors is irrelevant.
6. Two distinct neighbors (a,b) and the unique tree path between them give a
   simple cycle through (z). Extra (z)-path edges add chords but do not
   remove that cycle.
7. The path has at least two vertices. Its endpoints each have a path neighbor
   and (z), and its internal vertices have two path neighbors. Thus neither
   degree-one vertex lies on it.
8. The cardinality estimate counts the path and two distinct off-path leaves,
   yielding (|T|ge |P|+2ge g+1).

No step assumes that the two leaves lie near a shortest cycle, and no hidden
induced-cycle claim is used.

## Edge cases and conventions

For cyclic simple graphs, (gge3), including the triangle case. Under
Mathlib's convention that an acyclic graph has girth zero, a connected tree on
a nontrivial finite type satisfies the statement because the whole graph is an
induced tree and (delta'ge1). The hypothesis excluding one-vertex graphs in
the formal statement removes the only degree-sequence corner case.

## Sharpness audit

A (g)-cycle with two pendant vertices has (g+2) total vertices and
(delta'=1). Since at most two cycle vertices support the leaves, some cycle
vertex supports neither; deleting it gives a connected induced tree of order
(g+1). The full graph is cyclic, so no induced tree has order (g+2).
Therefore the claimed equality family is valid for every (gge3).

## Scope

The atlas computation is a falsification check, not a logical premise. The
proof is self-contained. This report does not certify bibliographic novelty;
that is handled by the separate novelty gate.

