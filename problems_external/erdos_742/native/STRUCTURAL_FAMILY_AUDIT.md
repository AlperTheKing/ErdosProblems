# Structural construction-family audit

## Family tested

Let \(H\) be a triangle-free graph of diameter two. Replace each vertex
\(i\) by a nonempty independent part of size \(a_i\), and replace every edge
\(ij\) by the complete bipartite graph between its two parts.

This is a direct D2C construction, not merely a surrogate:

- the blow-up still has diameter two;
- it is triangle-free; and
- after deleting any edge \(xy\), its endpoints have no common neighbor, so
  their distance becomes greater than two.

Thus every member has an immediate per-edge criticality certificate.

## Exact obstruction to the target

Every graph in this family is triangle-free.  Mantel's theorem therefore
gives
\[
  |E(G)|\le \left\lfloor |V(G)|^2/4\right\rfloor.
\]
At order 25 this is 156, whereas route R1 requires at least 157 edges.
Consequently the entire triangle-free blow-up family is dead for direct
refutation.

For the canonical non-bipartite base \(H=C_5\), exhaustive enumeration of the
positive integer compositions
\[
  a_0+\cdots+a_4=25
\]
maximizes
\[
  \sum_{i\pmod 5} a_i a_{i+1}
\]
at 145, for example at the cyclic part sizes \((1,1,1,11,11)\).

## Exit

`DEAD: exact family bound 156 < 157 (and the non-bipartite C5 subfamily
maximizes at 145).`

No denser triangle-free construction family can bridge to the required
counterexample certificate.
