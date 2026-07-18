# WOWII 141 — minimal lemma tree

Target: `floor(g/2) - 1 + L <= t(G)` for finite nontrivial connected `G`,
where `L = max_v alpha(G[N(v)])`.

## L0 — induced-star certificate

For every vertex `v` and independent `I subset N(v)`, the graph induced by
`{v} union I` is a tree on `|I|+1` vertices.

Use: closes `g=0` and `g=3`, and supplies the local part of the main witness.

## L1 — girth/eccentricity bridge

If `G` is connected and cyclic, then for every `v`,
`girth(G) <= 2*ecc(v)+1`.

Certificate: root a BFS tree at `v`; a non-tree edge yields a fundamental
cycle of length at most `2*ecc(v)+1`.

## L2 — frontier: star plus short geodesic

Assume `g >= 4`; put `r=floor(g/2)-1`.  Choose `v` attaining `L`, an
independent `I subset N(v)` of size `L`, and by L1 a `v`-geodesic
`P=(x0,...,xr)`.  Prove `G[I union V(P)]` is a tree and has at least `L+r`
vertices.  Every forbidden cross-edge creates a cycle of length at most
`r+2=floor(g/2)+1<g`.

## L3 — arithmetic and assembly

