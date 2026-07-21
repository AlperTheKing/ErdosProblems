# Exact counterexample to the W144 residual-window Candidate N1

## Status and quantifier audit

This is **not** a counterexample to WOWII Conjecture 144.  It is an exact
counterexample to the proposed auxiliary statement N1.

The GPT consultation stated N1 with quantifiers

> for every shortest cycle `K`, there exists an `e`-realizer `x` such that
> `d(x,K) >= e-floor(g/2)` whenever `D < e+floor(g/2)`.

The assigned weaker reading only asks for some pair `(K,x)`.  The graph below
has one shortest cycle and one `e`-realizer, so it falsifies both readings.

## Explicit graph

Use vertices `0,...,35`.  Start with the cycle

    K = 0-1-2-...-13-0.

Add the leaf edge `12-14`, the 10-edge ear

    10-15-16-17-18-19-20-21-22-23-5,

and the 13-edge ear

    17-26-25-24-35-34-33-32-31-30-29-28-27-22.

Thus `n=36` and `m=38`.  Its graph6 string is

    chCGGC@?G?_@?@_?_?O?O??C??G??G??C??@???G???__?@????????_??_G???O????C????G????G????C????@?????G?????_???O@

Exhaustive simple-cycle enumeration gives exactly six cycle lengths:

    14, 15, 18, 19, 23, 27.

Hence `g=14`, `k=floor(g/2)=7`, and `K={0,...,13}` is the unique shortest
cycle.

## Exact metric certificate

Breadth-first search from every vertex gives the eccentricity vector

    [13,13,13,13,12,11,11,11,11,11,11,12,13,13,14,11,10,9,
     9,9,9,10,10,10,12,11,10,11,12,13,14,14,13,13,13,13].

Therefore

    radius r = 9,
    diameter D = 14,
    center C = {17,18,19,20}.

The distances to the center set are

    [7,8,7,6,5,4,5,6,5,4,3,4,5,6,6,2,1,0,
     0,0,0,1,2,3,3,2,1,3,4,5,6,7,7,6,5,4].

Consequently `e=ecc(G,C)=8`, and the unique `e`-realizer is `x=1`.  Since
`x` lies on the unique shortest cycle,

    h=d(x,K)=0.

The hard-regime hypothesis holds, but the N1 conclusion fails:

    D = 14 < 15 = e+k,
    h = 0 < 1 = e-k.

This proves the counterexample without any ambiguity about either quantifier.

## Exact admissible-forest capacity

For completeness, the graph does not obstruct the actual admissible-forest
target.  Put `O=V(G)-K={14,...,35}`.  Exact enumeration gives

    M_z(K) = 20  if z=12,
             21  otherwise,
    M(K) = 21 >= e.

These values also have short hand certificates.  The component on
`{15,...,35}` is unicyclic, so the full set `O` is not a forest and
`M_z(K)<=21` for every `z`.

* If `z` is not one of `5,10,12`, then `O-{22}` is a 21-vertex legal forest.
  Its three components send their unique cycle edges to `5`, `10`, and `12`.
* If `z` is `5` or `10`, then `O-{35}` is legal: its large tree sends two
  cycle edges, to `5` and `10`, exactly one of which survives deletion of `z`;
  the leaf component sends its edge to `12`.
* If `z=12`, then `O-{14,22}` is a legal 20-vertex forest.  No 21-vertex
  forest can work: omitting `14` leaves the other outside component cyclic,
  while omitting any other vertex retains the component `{14}`, whose only
  cycle edge goes to the deleted vertex `12`.

In particular, for example, `z=0` and `F=O-{22}` give an explicit admissible
forest of order `21`, far above the required order `e=8`.

## N2 on this wide-window instance

Here the unique anchor is `m=x=1`, `h=0`, and `delta=e-h=8>k`.  Thus the
cycle window is all of `K` and has order 14; the narrow-window formula
`2delta-1` is inapplicable, exactly as N1 was intended to prevent.

The two components outside `K` are `H_0={14}` and `H_1={15,...,35}`.  With
the threshold `r+1=10`, exact distances give

    E_(H_0) = empty,
    E_(H_1) = K.

Therefore the N2 coverage sum is 14.  For every permitted `z!=m`,

    14 <= 2(M_z(K)-h),

whose right side is 40 for `z=12` and 42 otherwise.  So this graph falsifies
N1 only; it satisfies N2 and the desired capacity conclusion.

## Reproduction

The verifier uses only the Python standard library.  It reconstructs the
graph from the displayed paths, enumerates every simple cycle, performs all
BFS distance calculations, and exhausts the subset layers of orders 22, 21,
and 20 needed to determine every `M_z(K)`:

    python problems_external/wowii_144/proverC/verify_exact_residual_n1_counterexample.py

It writes the machine-readable certificate
`proverC/exact_residual_n1_counterexample_certificate.json`.
