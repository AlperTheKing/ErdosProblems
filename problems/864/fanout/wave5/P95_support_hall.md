# P95: support-fold Hall injection is false

A natural strengthening of C84 asks to match every loose triangle to one of
its three supporting canonical folds. This is false even though the scalar
inequality `T_F<=C_S` survives.

On the exact P94 maximum-ratio row

`(p,h,b,C_S,T_F)=(104,14484,1,142,116)`,

the bipartite incidence graph from loose triangles to their three supporting
folds has maximum matching size 105. Alternating reachability from the 11
unmatched triangles gives an explicit Hall witness with 72 triangles and
only 61 neighboring folds.

Thus no proof of C84 can inject each triangle into one of its own three
folds. Any valid injection or charge must use folds outside the triangle's
support, or a different global resource. Exact verifier:
`compute/p95/verify_support_hall_counterexample.py`.

Adding the fourth low-pair cell of the loose `2 x 2` rectangle does not
repair Hall. Thirty-six of the 116 triangles have that fourth cell as a
fold, but the enlarged support-plus-fourth matching still has size 105.
