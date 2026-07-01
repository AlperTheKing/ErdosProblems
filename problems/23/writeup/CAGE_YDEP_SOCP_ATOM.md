# Y-dependent CAGE SOCP atom

This is a proof target and exact-test format, not a closure theorem.

The fixed-ratio CAGE certificate is stronger than needed because it asks for
one routing and one set of gate ratios that work for every nonnegative test
vector `y`.  The LPD/CORR inequality only needs a certificate after `y` is
known.

## Objects

Fix a connected-`B` gamma-minimal maximum-cut configuration.  For each bad edge
`f`, layer pair `i<j`, and gate `g=(f,t,e)` with `i<=t<j`, use the usual CAGE
variable

```text
alpha_{f,i,j,g} >= 0.
```

It must satisfy the marginal equations

```text
sum_{g between i,j} alpha_{f,i,j,g} = 1,
```

and

```text
sum_{i<=t<j} alpha_{f,i,j,g} = H_{f,t} pi_{f,t,e}.
```

For a fixed rational `y>=0`, define

```text
A_g^y = sum_v A_g(v) y_v,
B_g^y = sum_v B_g(v) y_v,
cap^y = sum_v (N-S(v)) y_v.
```

where `A_g(v),B_g(v)` are computed from `alpha` exactly as in
`CAGE_certificate_note.md`.

## Exact certificate

For this one `y`, a y-dependent CAGE-SOCP certificate is:

```text
alpha_{f,i,j,g} >= 0,     z_g >= 0
```

with all values rational, satisfying the CAGE marginal equations and

```text
z_g^2 >= 4 A_g^y B_g^y       for every gate g,
```

and

```text
sum_g z_g <= cap^y.
```

This is Fraction-checkable: after rational `alpha,y,z` are supplied, all
conditions are polynomial inequalities over the rationals.

## Implication

For fixed `y`,

```text
2 sqrt(A_g^y B_g^y) <= z_g.
```

Thus the certificate gives

```text
sum_g 2 sqrt(A_g^y B_g^y) <= cap^y.
```

Expanding the usual CAGE routing identity gives the CORR inequality for this
particular `y`.  Therefore the universal atom

```text
for every rational y>=0, a y-dependent CAGE-SOCP certificate exists
```

implies CORR/LPD for all rational `y`, and then all real `y>=0` by continuity.

## Why this avoids the retracted Schur-current subtree

The atom has no fixed positive coefficient such as

```text
rho_o >= c (A-2a_o)
```

and no fixed finite inverse/Jacobi depth.  The routing `alpha` and the
gate-wise square-root upper bounds may vary with `y`, so the C5 blow-up family
`[k+1,k,k+1,k,k+1]` only tests scale-stability of the actual LPD functional.
In the odd-cycle blow-up equality case, the natural symmetric routing has
`A_g^y=B_g^y` on positive-mass gates for the extremal directions, and the
certificate is tight rather than forced to spend a scale-dependent Schur
current.

## Finite gate to run

For each exact instance and each rational test vector `y` produced by the LPD
or CAGE dual search:

1. Build the CAGE marginal system from `_h.py` objects:
   `info["M"]`, `info["ell"]`, `info["cyc"]`, and the layer distributions
   `p_{f,i}`.
2. Search for rational `alpha,z` satisfying the displayed equations and
   inequalities.
3. Verify all equalities and inequalities with `Fraction`.

A falsifier is a rational `y>=0` for which no rational certificate can be
found and an exact lower-bound certificate proves

```text
inf_alpha sum_g 2 sqrt(A_g^y B_g^y) > cap^y.
```

The useful first stress set is the existing hard directions from
`_codex_cage_ydep.py`, the N=22 witness, Mycielskian N=23, and the large
C5 blow-up family that killed fixed-coefficient Schur-current strengthenings.
