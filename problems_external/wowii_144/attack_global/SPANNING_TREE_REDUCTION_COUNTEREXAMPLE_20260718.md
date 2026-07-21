# Counterexample to a published spanning-tree reduction

Date: 2026-07-18.

Theorem 3.1 of Li, Yu, Ilić and Klavžar, *On the computational complexity
of the Steiner k-eccentricity*, arXiv:2112.01140, states

    e_k(v,G) = min{e_k(v,T) : T is a spanning tree of G}.

As stated, this identity is false. Let `G=C_5`, fix any vertex `v`, and put
`k=4`. Every four-set of cycle vertices induces a path on four vertices, so

    e_4(v,C_5)=3.

Every spanning tree of `C_5` is the path `P_5`. For every placement of `v`
on that path, a four-terminal set containing `v` and both endpoints has the
whole path as its minimum connector. Hence

    e_4(v,T)=4

for every spanning tree `T`, and the claimed right side equals `4`, not `3`.

The proof in the cited paper treats a minimum connector in a spanning tree
as though it were still minimum after the deleted graph edges are restored;
the cycle example shows exactly why that step fails. This reduction must not
be used in the W144 proof.
