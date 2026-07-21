# Naive componentwise capacity bound: exact counterexample

Graph6: `Fh_gG`.

Exact parameters are

    n=7, g=5, r=2, D=3, e=2,
    K={0,1,2,4,5}, x=m=0, h=0,
    W={0,1,4}, z=2.

The outside component `H={3}` is attached only at `z=2`.  It covers two
window vertices, so `|E_H cap W|=2`, while deletion of `z` removes its only
usable root edge and hence `mu_z(H)=0`.  Thus

    |E_H cap W| = 2 > 0 = 2 mu_z(H).

The graph has a unique shortest cycle.  Changing the cycle is therefore
impossible, but changing the deletion vertex removes this local obstruction:
choosing an unattached cycle vertex as `z` gives `mu_z(H)=1`.

This counterexample refutes only the assertion for an arbitrary fixed `z`;
it does not refute Candidate N2, whose quantifier permits choosing `z`.
