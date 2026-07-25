# Counterexample to the proposed Ramsey--Turan edge lemma

The proposed lemma was:

> If a graph `G` has `r^2+1` vertices and
> `alpha(G), omega(G) <= r`, then
> `e(G) > r(r^2+1)/2`.

It is false already for `r=5`, with equality.

Let `F` be the Groetzsch graph, i.e. the Mycielskian of `C_5`.  Its vertices
are

`v_0,...,v_4, u_0,...,u_4, w`

with indices modulo five, and its edges are

- `v_i v_(i+1)`;
- `u_i v_(i-1)` and `u_i v_(i+1)`; and
- `w u_i`

for every `i`.  Thus `F` has 11 vertices and 20 edges.

The graph `F` is triangle-free.  Also `alpha(F)=5`: the five vertices `u_i`
are independent.  If an independent set contains `w`, it contains no `u_i`
and at most two `v_i`.  If it omits `w`, its `v_i` form an independent set
of the 5-cycle.  Taking zero, one, or two such vertices allows respectively
at most five, three, or two of the `u_i`, so the total is at most five.

Let `H` be the complement of `F`.  Then

`|V(H)|=11`, `e(H)=55-20=35`, `alpha(H)=2`, and `omega(H)=5`.

Finally set

`G = H disjoint_union K_5 disjoint_union K_5 disjoint_union K_5`.

Then

- `|V(G)|=11+3*5=26=5^2+1`;
- `e(G)=35+3*10=65=5(5^2+1)/2`;
- `alpha(G)=2+1+1+1=5`; and
- `omega(G)=max(5,5)=5`.

Hence the strict edge inequality is false.  This does not construct the five
edge-disjoint colour graphs required to refute Erdős Problem 617; it only
closes the proposed R2 route.
