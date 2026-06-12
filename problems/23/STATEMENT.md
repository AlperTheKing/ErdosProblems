# Erdos problem #23 statement

Let `G` be a triangle-free graph on `n` vertices. Define

`beta(G) = e(G) - maxcut(G)`,

the minimum number of edges that must be deleted from `G` to make it bipartite.
Let

`a(n) = max beta(G)`,

where the maximum is over all triangle-free graphs on `n` vertices.

Erdos conjectured that

`a(n) <= n^2 / 25`

for all `n`; in particular

`a(5m) <= m^2`.

The conjecture is sharp for `n=5m` by the balanced blow-up of `C5` with five
parts of size `m`, which has `beta=m^2`.

Current target in this folder:

1. Verified finite result: `a(25)=25`.
2. Active next finite target: `a(30)=36`, via the certificate
   no triangle-free graph on 29 vertices has `beta >= 33` and `e <= 139`.
