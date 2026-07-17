# Erdős Problem 128 — Safe finite-search lemmas

All lemmas below preserve the direct `n = 20` certificate problem.

## Lemma 1 — ten-sets suffice

If every induced 10-vertex subgraph has at least 9 edges, then every induced subgraph on at least 10 vertices has at least 9 edges.

**Proof.** Choose any ten vertices inside the larger vertex set. Its at least nine induced edges remain present in the larger induced graph. ∎

## Lemma 2 — any candidate has at least 39 edges

Let `e = |E(G)|` and fix a vertex `v`. Sum the edge counts over all ten-subsets of `V(G) \ {v}`. Every edge not incident with `v` occurs in exactly `C(17,8)` such subsets. Hence

`(e - d(v)) C(17,8) >= 9 C(19,10)`.

Since `C(19,10) / C(17,8) = 19/5`, this gives `e - d(v) >= 171/5`, hence the integral inequality `e - d(v) >= 35`. Summing over all 20 vertices gives

`18e = sum_v (e - d(v)) >= 20 * 35 = 700`,

so `e >= 39`. ∎

## Lemma 3 — maximal triangle-free restriction is lossless

If a triangle-free candidate is not maximal triangle-free, add a missing edge whose addition creates no triangle. This preserves triangle-freeness and cannot decrease any induced edge count. Repeating finitely often yields a maximal triangle-free candidate. Thus a witness search may require that every nonedge has a common neighbour.

## Lemma 4 — degree ordering is safe symmetry breaking

Every labelled graph is isomorphic to one whose vertex degrees are non-increasing in the vertex labels. Therefore constraints

`d(0) >= d(1) >= ... >= d(19)`

do not remove any isomorphism class. No stronger lexicographic symmetry constraint is assumed without a separate proof.
