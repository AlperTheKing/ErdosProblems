# Certified exclusion at orders 16 and 17

## Theorem

There is no simple 6-regular `(4,1)`-graph on 16 or 17 vertices. Combined
with Theorem A of [arXiv:2606.18462](https://arxiv.org/abs/2606.18462), every
6-regular `(4,1)`-graph has at least 18 vertices.

This is a lower bound for the 6-regular subproblem. It does not settle the
existence of a 6-regular `(4,1)`-graph or the full `k=4` case of #944.

## Reduction

Let `r` be a vertex and fix a proper 3-colouring of `G-r`. If one colour
occurred on only one neighbour `u` of `r`, deleting `ru` would let `r` receive
that colour. This would make `G-ru` 3-colourable, contrary to the absence of
critical edges. Thus every colour occurs at least twice on `N(r)`, and
6-regularity forces the split `2+2+2`.

Write the sorted colour-class sizes of `G-r` as `a >= b >= c`. Degree sums
then force

```text
e(A,B) = 3n - 4 - 6c,
e(A,C) = 3n - 4 - 6b,
e(B,C) = 3n - 4 - 6a.
```

Nonnegativity and the three bipartite edge capacities leave exactly eleven
cases:

| order | feasible triples |
|---:|---|
| 16 | `(7,6,2)`, `(7,5,3)`, `(7,4,4)`, `(6,6,3)`, `(6,5,4)`, `(5,5,5)` |
| 17 | `(7,7,2)`, `(7,6,3)`, `(7,5,4)`, `(6,6,4)`, `(6,5,5)` |

Every open neighbourhood is bipartite. Otherwise its six vertices contain a
triangle or a 5-cycle, and adjoining the centre gives a 4-chromatic odd wheel
on at most six vertices. Deleting a vertex outside that wheel contradicts
vertex-criticality.

For each triple, a CNF encodes the following necessary conditions:

- degree exactly six at every vertex;
- a proper 3-colouring witness after each vertex deletion;
- at least two neighbours of every witness colour at the deleted vertex;
- a bipartition witness for every open neighbourhood; and
- normalization of `r`, its six neighbours, and the chosen colouring of
  `G-r`.

The root and colouring normalization loses no isomorphism class. Three cases
also use independently reconstructed lex-leader appendices under residual
vertex relabellings. All eleven formulas are UNSAT.

## Certificates

The complete generators, independent encoding verifiers, exact SHA-256
manifests, verification logs, and both DRAT and LRAT certificates are at:

<https://github.com/infinityscroll/dirac-944-orders-16-17>

The 36 large certificate files are in release `v1.0.0`. The release asset has
SHA-256
`855ebd2667b9ba4af3b044e58c434fe59779ac0707bd349ebe0378efd82d8284`.
The package verifier regenerates every CNF byte for byte and independently
replays all eleven proofs through both proof formats.
