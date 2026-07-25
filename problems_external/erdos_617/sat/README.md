# Erdős 617 exact one-vertex extension lane

`verify_a.cpp` is a raw edge-list verifier. Its accepted format is:

```
p edgecolor N Q
e U V C
```

There must be exactly one canonical record (`U < V`) for every unordered
edge, and `0 <= C < Q`. It exhausts every `(Q+1)`-vertex set and requires
every colour to occur.

`encode_one_extension.cpp` fixes the calibrated affine-plane colouring on
vertices `0,...,24` and encodes the colours of the 25 edges incident with a
new vertex. Variable `5*v+c+1` says that edge `{v,25}` has colour `c`.
Pairwise at-most-one plus one five-literal at-least-one clause gives exact
one-colour semantics. For every old five-set `S` and every colour absent
inside `S`, the encoding adds `OR_(v in S) x(v,c)`.

No symmetry breaker is used. Therefore SAT gives a full `K_26` certificate
extending this particular `K_25`; checked UNSAT excludes only this exact
one-vertex extension family, not arbitrary colourings of `K_26`.

`audit_one_extension_cnf.cpp` independently parses the base and CNF and
reconstructs the entire expected clause multiset.
