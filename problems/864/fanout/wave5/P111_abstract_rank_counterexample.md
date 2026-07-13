# P111: abstract fold-only rank counterexample

The purely combinatorial projection of P103 is false.  There is a linear
rooted 3-uniform hypergraph on 20 ordered vertices with 51 oriented edges
`(r,x,y)`, where `r<x,y`, for which the 51 rows

`(e_r+e_x+e_y, e_x-e_y, (r+1)(e_x-e_y))`

have rank 50 over `GF(1000003)`.  The exact edge list and verifier are in
`compute/p111/verify_abstract_rank_counterexample.py`.

This does not falsify P103's arithmetic matrix: the abstract system need
not arise from folds, and it omits the formal mark map `Q`.  It proves that
any independence proof must use the additive six-mark relations, not only
linearity and the strict order of the base fold.
