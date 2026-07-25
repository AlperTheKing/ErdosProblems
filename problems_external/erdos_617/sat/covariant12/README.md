# Twelve-class translation-covariant family

Let the vertices be `F_5^2` together with `infinity`, and let
`ell(x,y)=x`. For each of the 12 nonzero difference classes
`[d]={d,-d}`, choose `h_[d] in F_5`. Define

```
colour({u,v}) = ell((u+v)/2) + h_[v-u]   for u,v in F_5^2,
colour({infinity,u}) = ell(u).
```

Translation by `t` fixes `infinity`, maps old vertices by `u -> u+t`, and
adds the constant `ell(t)` to every edge colour. Therefore the five colour
graphs are isomorphic. It is necessary and sufficient to require that every
six-set contain colour zero.

The CNF uses one-hot variables for the 12 values of `h`, with no symmetry
breaker. For each six-set not already containing a fixed zero-colour
infinity edge, its colour-zero condition is a disjunction of equalities
`h_[v-u] = -ell((u+v)/2)` over its old-old edges.

`audit_covariant_cnf.cpp` independently hard-codes the 12 canonical
difference representatives and reconstructs the complete clause multiset.
SAT must be materialized to a raw 325-edge list and exhaustively replayed.
Proof-checked UNSAT excludes only this covariant family.
