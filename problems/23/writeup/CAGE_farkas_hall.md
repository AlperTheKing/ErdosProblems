# Fixed-Ratio CAGE Farkas/Hall Form

This note rewrites fixed-ratio CAGE feasibility as an exact family of
weighted transport inequalities.  It is a proof target, not a universal
proof.

## Fixed Ratios

Fix positive gate ratios `r_g`.  CAGE asks for nonnegative `alpha` satisfying
the marginal constraints `(R1),(R2)` and

```text
sum_g (r_g A_g(v) + r_g^{-1} B_g(v)) <= cap(v) := N-S(v)
```

for every vertex `v`.

Let `lambda_v >= 0` be arbitrary.  Define the lambda-cost of assigning a
layer pair `p=(f,i,j)` to a gate `g=(f,t,e)` with `i<=t<j` by

```text
c_lambda(p,g)
 =
r_g       * sum_v lambda_v p_{f,i}(v)
+
r_g^{-1} * sum_v lambda_v p_{f,j}(v).
```

For a fixed bad edge `f`, define `OT_f(lambda,r)` to be the minimum transport
cost from the layer-pair side to the gate side:

```text
minimize   sum_{i<j} sum_{g between i,j} alpha_{i,j,g} c_lambda((i,j),g)

subject to sum_{g between i,j} alpha_{i,j,g} = 1
           for every layer pair i<j,

           sum_{i<=t<j} alpha_{i,j,g} = m_g
           for every gate g=(f,t,e),

           alpha >= 0,
```

where

```text
m_g = H_{f,t} pi_{f,t,e}.
```

The marginal totals match because

```text
sum_{i<j} 1 = binom(ell(f),2)
```

and

```text
sum_g m_g
= sum_t H_{f,t} sum_e pi_{f,t,e}
= sum_t H_{f,t}
= binom(ell(f),2).
```

## Theorem

For fixed positive ratios `r_g`, the CAGE budget inequalities are feasible
if and only if

```text
sum_f OT_f(lambda,r)
<=
sum_v lambda_v (N-S(v))
```

for every `lambda >= 0`.

Equivalently, after normalizing

```text
sum_v lambda_v (N-S(v)) = 1,
```

fixed-ratio CAGE is feasible iff

```text
sum_f OT_f(lambda,r) <= 1
```

for every nonnegative `lambda`.

## Proof

The forward implication is immediate: multiply each vertex budget inequality
by `lambda_v`, sum over vertices, and then minimize over all alpha transports
with the same marginals.

For the converse, use LP duality/Farkas.  The fixed-ratio alpha LP is

```text
minimize eta
subject to alpha satisfies (R1),(R2), alpha>=0,
           used_v(alpha,r) <= eta cap(v) for every v.
```

Its dual has variables `lambda_v >= 0`, normalized by

```text
sum_v lambda_v cap(v) = 1,
```

and free potentials for the pair and gate marginal equations.  Eliminating
the marginal potentials gives exactly the transport dual for
`sum_f OT_f(lambda,r)`.  Hence the optimum `eta(r)` is

```text
eta(r) =
max_{lambda>=0, sum lambda cap=1}
sum_f OT_f(lambda,r).
```

Thus `eta(r)<=1` is equivalent to the displayed family of inequalities.

## Universal CAGE Target

Universal CAGE existence is therefore equivalent to finding positive gate
ratios `r_g` such that

```text
max_{lambda>=0}
  [ sum_f OT_f(lambda,r) / sum_v lambda_v (N-S(v)) ]
<= 1.
```

The exact CAGE certificates found by `_codex_cage_exact.py` supply such
ratios for finite instances.  A proof must explain why triangle-free
shortest-geodesic corridor structure always permits such ratios.

The total-surplus identity in `CAGE_surplus_identity.md` gives only the
case `lambda=1`; the real obstruction is an interior `lambda` for which
transport cost concentrates on a small vertex set.
