# Y-Dependent CAGE Form

Fixed CAGE is stronger than CORR: it asks for one routing `alpha` and one
gate-ratio vector `r` that work for all nonnegative vertex weights `y`.
This note records the weaker y-dependent sufficient condition and the first
diagnostics.

## Y-Dependent Certificate

Fix a single nonnegative weight vector `y`.  For a routing `alpha` satisfying
the CAGE marginal equations `(R1),(R2)`, define

```text
A_g^y := sum_v A_g(v)y_v,
B_g^y := sum_v B_g(v)y_v.
```

The best gate ratio for this one `y` is

```text
r_g = sqrt(B_g^y / A_g^y)
```

with the usual limiting convention when one side is zero.  Thus this routing
proves CORR for the fixed `y` if

```text
sum_g 2 sqrt(A_g^y B_g^y)
<=
sum_v (N-S(v)) y_v.
```

Consequently, CORR would follow from the weaker statement:

> For every `y>=0`, there exists an admissible CAGE routing `alpha(y)` such
> that the displayed inequality holds.

This is weaker than fixed CAGE because both `alpha` and the optimal ratios may
depend on `y`.

## Uniform Routing Is Still False

The diagnostic `_codex_cage_ydep.py` maximizes

```text
sum_g 2 sqrt(A_g^y B_g^y) - sum_v (N-S(v))y_v
```

over `y>=0`, normalized by `cap.y=1`, for a fixed routing alpha.

Uniform routing `alpha0` fails even in this y-dependent setting:

```text
I?BD@g]Qo[1]:       alpha0 max y-gap = +0.027634728
J???E?pNu?[2]:      alpha0 max y-gap = +0.144055985
```

The adaptive alpha found by the fixed CAGE solver passes those same tests:

```text
I?BD@g]Qo[1]:       adaptive max y-gap = -0.001489987
I?ABCc]}?[1]:       adaptive max y-gap = -0.103859292
J???E?pNu?[2]:      adaptive max y-gap = -0.083804235
```

The equality case `H?bB@_W[1]` is tight with both alpha choices:

```text
max y-gap = 0.
```

Thus the real mathematical content is adaptive transport, not merely choosing
gate ratios after seeing `y`.

## Proof Target

The most flexible CAGE-style route to CORR is now:

```text
for every y>=0, construct an admissible alpha(y)
with sum_g 2 sqrt(A_g^y B_g^y) <= cap.y.
```

The fixed-ratio Farkas/Hall form in `CAGE_farkas_hall.md` is stronger and
more solver-friendly.  A direct proof may instead work with this
y-dependent conic objective.

## Extreme-Point Reduction

For fixed `y`, the y-dependent optimization over alpha decomposes by bad
edge `f`.  The feasible alpha values for one `f` form a transportation
polytope:

```text
sum_g alpha_{i,j,g} = 1
```

for every layer pair `i<j`, and

```text
sum_{i<=t<j} alpha_{i,j,g} = m_g
```

for every gate `g=(f,t,e)`.

For this fixed `y`, the contribution of `f` is

```text
Phi_f(alpha;y)
 =
sum_{g over f} 2 sqrt(A_g^y B_g^y),
```

where `A_g^y` and `B_g^y` are linear functions of alpha.  Since
`sqrt(xy)` is concave on the nonnegative quadrant, `Phi_f` is concave on the
transportation polytope.  Therefore its minimum is attained at an extreme
point of that polytope.

Thus the y-dependent CAGE target can be sharpened to:

```text
for every y>=0 and every bad edge f, choose an extreme routing
of the f-transportation polytope so that the sum of the Phi_f costs
is at most cap.y.
```

This is still not a proof, but it changes the adaptive routing problem from a
general nonlinear search into an edgewise extreme-routing selection problem.
