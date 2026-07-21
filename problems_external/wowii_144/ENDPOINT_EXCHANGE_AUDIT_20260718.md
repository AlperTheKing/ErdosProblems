# Endpoint-ciliate exchange audit

This note does **not** prove Conjecture 144.  It records two exact obstructions
to local endpoint augmentation and identifies what remains if the ciliate
route is used.

## 1. A fixed path endpoint cannot merely be enlarged

For every `r >= 2`, let `L_r` be obtained from the odd cycle `C_(2r+1)` by
adding one leaf `u` at a cycle vertex `a`.  Then

* `rad(L_r)=r`;
* `girth(L_r)=2r+1`;
* the center consists of the cycle vertices at distance at most `r-1` from
  `a`, and consequently `ecc(L_r,center(L_r))=1`.

Delete `a` from the cycle and let `H` be the remaining induced `P_(2r)`.
The Conjecture-144 target is

    girth(L_r)-1+ecc(L_r,center(L_r)) = 2r+1,

one more than `|H|`.  But `V(L_r)\V(H)={a,u}`.  Adding `a` alone closes the
odd cycle, adding `u` alone leaves it isolated, and adding both leaves the
cycle.  Hence no nonempty outside set can be appended to this fixed `H` while
preserving an induced tree.  A genuine exchange is necessary: delete any
cycle vertex other than `a`, and retain `a,u`.

Thus a statement of the form “every induced path endpoint can be augmented
while retaining all of its vertices” is false for an infinite family.

## 2. One outside component is not enough: the family `G_m`

Let `m >= 1`.  Form `G_m` from a cycle `K=C_(10m)` by choosing roots `a,b`
at cycle distance `2m` and attaching at each root a pendant path of `2m`
edges.  This is a connected unicyclic graph of order `14m`.

Its parameters are

    girth(G_m)=10m,  rad(G_m)=5m,  diam(G_m)=7m,
    ecc(G_m,center(G_m))=3m.

Here is a direct verification of the non-immediate center parameter.  A cycle
vertex is central exactly when it lies on the short `a`--`b` arc or within
`m` further cycle edges of one of its ends along the long arc.  Every such
vertex is at distance at most `5m` from the cycle and from both pendant-path
ends, while the cycle itself forces eccentricity at least `5m`.  The
complementary open interval on the long arc has length `6m`; its midpoint is
at distance `3m` from the center.  Pendant-path vertices are at distance at
most `2m` from their central roots.  Thus the displayed set is the center and
its set-eccentricity is `3m`.  The diameter `7m` is realized by a pendant-path
end and the cycle vertex antipodal to its root.

Take the Fajtlowicz endpoint `H=K=C_(2r)`, where `r=5m`.  Deleting one cycle
vertex gives only `10m-1` vertices, whereas the exact target is

    10m-1+3m = 13m-1.

The two components of `G_m-H` each have only `2m` vertices.  Therefore an
exchange using either one outside component has order at most

    (10m-1)+2m = 12m-1 < 13m-1.

Moreover every `e`-realizer is a midpoint of the long cycle interval and lies
in `H`, so an `e`-realizer-to-`H` geodesic contributes no outside vertex at
all.  This disproves, with an unbounded deficit, both a one-component endpoint
exchange and an exchange based only on the component of an `e`-realizer.

The full theorem is not contradicted: deleting a non-root cycle vertex and
retaining **both** pendant paths gives an induced tree on `14m-1` vertices.
The example instead shows that any endpoint proof must combine several
outside components and account for their compatibility.

## 3. Exact remaining bridge

Fajtlowicz's theorem supplies the endpoint `P_(2r)` or `C_(2r)`, but it gives
no lower bound on the total order of a compatible family of induced forests
in distinct components of `G-H`.  Section 2 shows that neither one component
nor the component containing an `e`-realizer can replace that missing total.
The required multi-component statement is the same capacity assertion as the
registered Residual Admissible-Forest Lemma.  Consequently the ciliate
endpoint route does not close a smaller independent lemma; it returns to that
frontier.

As falsification evidence only, an exact atlas check and 160,000 generated
endpoint extensions (fixed seed `1440718`) found no counterexample to the much
stronger assertion that the target can be obtained after deleting at most one
endpoint vertex and choosing an arbitrary outside set.  Of the generated
graphs, 6,361 passed the connected/radius/girth/uncovered filters.  This
computation is not a proof of that stronger assertion.
