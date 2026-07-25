# Vertex-cycle plus one-relocation obstruction

Scope: the verified objective-9 q5 graph, one degree-preserving reversal of a directed triangle or directed four-cycle in the 18-vertex core, followed by one outward root-hole fill `12 -> x` and one core-arc deletion.

Use blocks B_i=(h_i,l_i) in order `(8,1),(0,15),(16,6),(2,9),(11,18),(7,14),(5,17),(10,4),(3,13)`. The quotient rule is `B_i -> B_(i+s)` iff `s in {1,3,5,7} mod 9`. Each low has witness multiplicities `2,2,4,4,6,6,8,8`; its exact two-witness target block is B_(i+2), witnessed by both vertices of B_(i+1).

A directed triangle reversal repairs no old low: outside lows lose at most one of every at-least-two witness set, and a triangle low replaces the departing predecessor target by a new successor target.

For a four-cycle on four distinct blocks, repairing a cycle low would require local quotient steps `1,7,1`; the fourth step would have to be9 because the four odd steps sum to18, impossible. If a four-cycle contains both twins of one block, that block low gains one direct target but also one new second target, raising its penalty by1; at most one other low can be repaired, so old-low penalty stays at least9.

The outward fill changes no nonroot row because vertex12 retains indegree0. The deleted core arc can repair at most one low through its unique exact-two fibre. Its high donor falls to degree8 and retains at least eight second targets, contributing penalty at least1. The exceptional high-gap four-cycle cannot couple its deletion to a low repair.

Therefore every domain-valid graph in this named family has objective at least9. This is scoped; it does not cover multiple cycle switches, multiple relocations, or another non-degree-preserving core mechanism.
