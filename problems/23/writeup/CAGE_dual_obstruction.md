# CAGE Dual Obstruction

This note records the dual object produced by a hypothetical failure of the
CAGE certificate.  It is a proof target, not a closure theorem.

## CAGE Primal

Fix a connected-`B` max-cut configuration.  Let `g=(f,t,e)` denote a gate:
bad edge `f`, geodesic gap `t`, and a `B`-edge `e` used at that gap by a
shortest `f`-geodesic.

For every interval pair `i<j` with `i<=t<j`, CAGE has nonnegative variables

```text
alpha_{f,i,j,t,e}.
```

They obey the pair and gate marginal equations:

```text
(R1)  sum_{t=i}^{j-1} sum_e alpha_{f,i,j,t,e} = 1
      for each f,i<j,

(R2)  sum_{i<=t<j} alpha_{f,i,j,t,e} = H_{f,t} pi_{f,t,e}
      for each f,t,e.
```

For a gate `g`, define routed endpoint loads

```text
A_g(v) = sum alpha_{f,i,j,t,e} p_{f,i}(v),
B_g(v) = sum alpha_{f,i,j,t,e} p_{f,j}(v),
```

where the sums are over variables using gate `g`.  CAGE asks for `alpha`
and positive ratios `r_g` such that

```text
sum_g (r_g A_g(v) + r_g^{-1} B_g(v)) <= cap(v) := N-S(v)
```

for every vertex `v`.

The proof in `CAGE_certificate_note.md` shows that this implies CORR/LPD.

## Fixed-Ratio Alpha LP

For a fixed positive ratio vector `r`, let `eta(r)` be the optimum of

```text
minimize eta
subject to alpha satisfies (R1),(R2), alpha>=0,
           sum_g (r_g A_g(v)+r_g^{-1}B_g(v)) <= eta cap(v)
           for every v.
```

The exact checker verifies certificates by finding `r` with `eta(r)<=1`.

The dual of this LP has nonnegative vertex weights `lambda_v`, normalized by

```text
sum_v lambda_v cap(v) = 1,
```

together with unrestricted dual variables for the pair and gate marginal
equations.  Complementary slackness gives

```text
lambda_v > 0
  => sum_g (r_g A_g(v)+r_g^{-1}B_g(v)) = eta(r) cap(v).
```

For every positive `alpha_{f,i,j,t,e}`, the corresponding reduced cost is
zero.  Written informally, the transported interval pair uses only gates that
are cheapest under the dual vertex measure `lambda`, after adding the pair
and gate marginal potentials.

This is the finite "KKT core" seen by `_codex_cage_kkt.py`: only a subset of
vertices has positive `lambda`, and positive alpha variables live on
zero-reduced-cost corridors.

## Hypothetical Tight Obstruction

Suppose CAGE fails, and let `(alpha,r)` minimize the CAGE value with optimum
`eta*>1`.  At a regular interior optimum, there is a dual `lambda` as above
such that, additionally, every free gate ratio is stationary:

```text
r_g^2 * sum_v lambda_v A_g(v)
  =
sum_v lambda_v B_g(v).
```

Equivalently, each gate ratio balances the dual-weighted mass routed through
the two sides of that gate.

Thus a genuine obstruction consists of:

1. A nonnegative dual measure `lambda` with `sum lambda_v cap(v)=1`.
2. A feasible alpha-transport satisfying (R1),(R2).
3. Vertex budget tightness on the support of `lambda`.
4. Zero reduced cost on every used interval-pair/gate route.
5. Gate balance `r_g^2 A_g^lambda = B_g^lambda` for every nondegenerate gate.
6. Objective value `eta*>1`.

The observed exact certificates suggest that such an obstruction should not
exist.  The equality cases `Gamma=N^2` are degenerate: many vertex budgets
are tight, the dual is non-unique, and CAGE can have `eta=1`.  In strict
non-extremal examples, exact CAGE certificates have slack, so the obstruction
KKT equations need not hold.

## Total-Surplus Constraint

The identity in `CAGE_surplus_identity.md` adds a global constraint to any
candidate obstruction.  Let

```text
m_g = H_{f,t} pi_{f,t,e}
```

for a gate `g=(f,t,e)`.  For every CAGE certificate,

```text
sum_v [
  cap(v) - sum_g (r_g A_g(v) + r_g^{-1} B_g(v))
]
=
N^2 - Gamma
-
sum_g m_g (r_g + r_g^{-1} - 2).
```

Thus feasibility can fail only for distributional reasons.  The total
available capacity exceeds the minimum total CAGE mass by exactly `N^2-Gamma`,
and the chosen gate ratios spend part of that surplus through the nonnegative
ratio-waste term.

In the equality case `Gamma=N^2`, every feasible certificate must have
`r_g=1` on every positive-mass gate and every vertex budget tight.  Therefore
any nontrivial ratio structure belongs only to strict cases `Gamma<N^2`.

For an optimal obstruction with value `eta>1`, summing the vertex inequalities
gives the necessary lower bound

```text
eta >=
(Gamma - sum_f ell(f) + ratio_waste)
/
(N^2 - sum_f ell(f)).
```

This lower bound is not by itself enough to prove `eta<=1`, because in strict
cases the right-hand side may be below one.  It does show that a genuine KKT
core must concentrate a globally adequate surplus onto the wrong vertices.

## Proof Target

A proof of CAGE existence can be phrased as:

> Every CAGE KKT obstruction satisfying the conditions above is an odd-cycle
> blow-up equality configuration.  Therefore no obstruction with `eta*>1`
> exists.

Triangle-freeness should enter through the separated-corridor structure:
bad-edge endpoints have disjoint `B`-neighbourhoods, and interval-pair
transport can only cross the corresponding `B`-edge gates.  The remaining
work is to turn this separation into a contradiction for the dual core.

An even sharper equality target suggested by exact data is:

> If the optimal CAGE value is exactly `1`, then `T(v)=N` for every vertex
> that lies in the relevant connected component; hence `Gamma=N^2`.

Exact CAGE logs for all load-bearing `N=8,9,10` cases have zero slack only
for the two `Gamma=N^2` rows.  In those rows `T` is identically `N` and
`S` is constant.  This is not a proof, but it gives a concrete equality case
to aim for when analyzing the KKT system.

## Diagnostic Files

```text
_codex_cage_exact.py        exact Fraction checker for fixed certificates
_codex_cage_exact_batch.py  batch exact repair/check
_codex_cage_structure.py    routing/gate-ratio structure dump
_codex_cage_kkt.py          fixed-r alpha-LP dual diagnostic
```

The KKT diagnostic is intentionally floating-point only.  It is used to
identify the shape of candidate obstructions; all closure claims must still
go through exact rational verification.

## Relation To The LPD KKT Vector

The CAGE alpha-LP dual measure `lambda` is not identical to the optimizer
`y` in the LPD/CORR dual problem.  The diagnostic
`_codex_cage_lpd_compare.py` compares them after normalizing both to the
same simplex scale.  In named cases the two vectors are correlated but
distinct:

```text
I?BD@g]Qo[1]:       cos(lambda,y) ~= 0.91
J???E?pNu?[2]:      cos(lambda,y) ~= 0.61
```

Thus the CAGE obstruction should be treated as its own minimax object.  The
LPD KKT vector remains useful intuition for where the hard vertices are, but
a proof of CAGE existence must use the alpha/gate marginal structure directly.
