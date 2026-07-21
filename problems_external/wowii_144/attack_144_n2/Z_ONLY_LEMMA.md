# Adjacent-root sole-component lemma

This lemma rigorously removes the `z`-only obstruction from the direct
admissible-forest target.  It does not prove the remaining active-component
capacity sum.

## Lemma

Let `g>=5`, let `K` be a shortest cycle, and choose an `e`-realizer `x` of
maximum height `h=d(x,K)<e`, with anchor `m in K`.  Put `delta=e-h`, and let
`z_-`,`z_+` be the two neighbors of `m` on `K`.

For `i in {-,+}`, suppose there is a component `H_i` of `G-K` which is
attached only at `z_i` and contains a witness `y_i` for a window vertex;
that is, some `sigma_i in W` satisfies

    d(sigma_i,y_i)>=r+1.

Then `M(K)>=e`.

Consequently, unless the exact W144 admissible-forest target is already
closed, at least one of the two adjacent deletion roots is not the sole
attachment of any component that covers `W`.

## Proof

Put `q_i=d(z_i,y_i)`.  Since `H_i` is attached only at `z_i`, every
`sigma_i`--`y_i` path enters `H_i` through `z_i`; isometricity of `K` gives

    d(sigma_i,y_i)=d_K(sigma_i,z_i)+q_i.

As `z_i` is adjacent to `m` and `sigma_i in W`,
`d_K(sigma_i,z_i)<=delta`.  Hence

    q_i >= r+1-d_K(sigma_i,z_i)
        >= r+1-delta
        >= h+1,                                             (1)

where the last inequality uses `e=h+delta<=r`.

The vertex `x` is not in `H_i`: every vertex of a sole-attachment component
has `z_i` as its only nearest-cycle anchor, whereas `x` has anchor `m!=z_i`.

We claim that `H_i` contains a center.  Otherwise every center `c` lies
outside `H_i`, and sole attachment gives

    d(y_i,c)=q_i+d(z_i,c).

Since `x` is an `e`-realizer, `d(x,c)>=e` for every center `c`; while
`d(x,z_i)<=h+1`.  Therefore

    d(z_i,c) >= e-(h+1)=delta-1.

Together with (1), `d(y_i,c)>=e` for every center.  The definition of `e`
then forces `d(y_i,C)=e`, so `y_i` is an `e`-realizer of height
`q_i>h`, contrary to maximality of `h`.  Choose `c_i in C cap H_i`.

The same distance estimate from `x` to `c_i`, now using that every path into
`H_i` enters at `z_i`, gives

    d(z_i,c_i)>=delta-1.                                   (2)

The components `H_-` and `H_+` are distinct.  Every path between them exits
at their sole roots, and the two roots have cycle distance two through `m`.
Thus (2) yields

    d(c_-,c_+)
      = d(c_-,z_-)+2+d(z_+,c_+)
      >= 2 delta.

Since `c_-` is central, its eccentricity is `r`, so `r>=2 delta`.
Now delete `z_-`.  The reserved `x`-tail is a legal component of order `h`
attached at `m`.  In the distinct component `H_+`, a shortest
`z_+`--`y_+` path contributes its `q_+` off-cycle vertices as a legal path
component attached only at `z_+`.  The two components are anticomplete, and

    q_+ >= r+1-delta >= delta+1.

Therefore

    M_{z_-}(K) >= h+q_+ >= h+delta=e.

This is the exact admissible-forest certificate.  Symmetrically one may
delete `z_+`.  QED.
