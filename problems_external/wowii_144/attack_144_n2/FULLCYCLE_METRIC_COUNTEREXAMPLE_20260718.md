# Counterexample to the unrestricted W144 full-cycle metric lemma

Date: 2026-07-18.

This note refutes the exact `W144-MW` frontier displayed in
`APPROACH_REGISTRY.md`.  It does **not** refute Conjecture 144 or the registered
ordinary inequality restricted to a nonempty window cover.

## Graph

Let `G` consist of the cycle

    K = 0-1-2-3-4-5-6-0

together with the pendant path

    0-7-8-9-10-11

and the pendant edge `3-12`.  Thus `G` is a finite connected simple graph on
13 vertices, with graph6 encoding

    LhCKK?@?G?_@C?

Its unique cycle is `K`, so its girth is `g=7`.  Vertex `0` has eccentricity
five.  Also `d(11,12)=9`, so every graph center has eccentricity at least
`ceil(9/2)=5`.  Hence `r=rad(G)=5` and

    lambda = 2r+1-g = 4.

## Full-cycle record

Take the component `H={12}` of `G-K` and reserve `z=0`.  The only attachment
of `H` is cycle vertex `3`, which lies in `K-{z}`, so this is a legal record.
The apex graph `J_z(H)` is the single edge `rho-12`.  Consequently

    p(12)=1,
    P_z(H)=p(12)+p(12)+d_J(12,12)=2.

For every `sigma in K`,

    d_G(sigma,12)=d_K(sigma,3)+1 <= 4 <= r.

Therefore

    E_H^K={sigma in K : some y in H has d_G(sigma,y)>=r+1}=emptyset.

The proposed inequality has left side

    |E_H^K|+lambda = 0+4 = 4 > 2 = P_z(H).

Its exact slack is `-2`.

The counterexample occurs at order 13, immediately beyond the exhaustive
order-12 audit.  Its mechanism is structural: the long pendant path raises the
ambient radius, while the unrelated shallow component has empty far cover and
fixed rooted triameter.  Thus the unrestricted statement cannot be repaired
without restoring a nonempty-cover/residual hypothesis; that would be a
different frontier and is not pursued on this dead route.

Run `verify_fullcycle_metric_counterexample.py` to reconstruct the graph and
check every displayed invariant and inequality exactly.
