# Schur SPEC Proof Draft

This is a proof draft for the Schur certificate.  The live certificate is the
full Schur-inverse / open-capacity formulation below.

**Retraction, 2026-06-28.** The former "explicit two-step supersolution"
candidate at the end of this file is false: Claude's exact gate found a
Myc2(C5), N=23 violation at overloaded vertex 22 (margin `-0.723...`).  Do not
use any finite two-step Neumann truncation as a closure claim; only the full
inverse potential is still alive.

## Setup

Let `P[v,f]=p_f(v)`, `K=P P^T`, and `T=K 1`.  Set

```text
A = N I - K.
```

Let

```text
O = {v : T(v) > N},          Q = V \ O.
```

The target `(SPEC)` is `A >= 0`.

## Principal Underload Block

The matrix `A_QQ` is a symmetric Z-matrix.  For `q in Q`,

```text
sum_{q' in Q} A[q,q']
  = N - T(q) + sum_{o in O} K[q,o] >= 0.
```

Also

```text
A[q,q] = N - K[q,q] >= sum_{q' in Q, q' != q} K[q,q'],
```

because `sum_{q' in Q} K[q,q'] <= T(q) <= N`.  Thus every connected
component of `A_QQ` is weakly diagonally dominant with nonpositive
off-diagonal entries.

If a component has a positive row sum somewhere, it is a nonsingular
Stieltjes block, hence has entrywise nonnegative inverse.  If a component has
zero row sums everywhere, then it has no `K`-connection to `O` and every
vertex in it has `T=N`; this component decouples from the Schur complement and
is PSD with null vector `1`.

Thus, after deleting decoupled zero-row components, `A_QQ` is nonsingular
Stieltjes.

## Schur Off-Diagonal

Let

```text
E = A_OO - A_OQ A_QQ^{-1} A_QO.
```

Since `A_OQ=-K_OQ <= 0` and `A_QQ^{-1} >= 0`, the correction term

```text
A_OQ A_QQ^{-1} A_QO
```

is entrywise nonnegative.  Therefore, for distinct overloaded vertices
`o != o'`,

```text
E[o,o'] = -K[o,o'] - (nonnegative correction) <= 0.
```

So `E` is again a symmetric Z-matrix.

## Open Capacity Lemma

It remains to prove that every row sum of `E` is nonnegative.

Equivalently, let `g` solve

```text
A_QQ g = (N-T)_Q.
```

Then `0 <= g <= 1` by the Stieltjes maximum principle, and the row-sum claim
is

```text
N - T(o) + sum_{q in Q} K[o,q] g(q) >= 0       for every o in O.
```

Equivalently, put `phi(o)=1` on `O` and `phi(q)=1-g(q)` on `Q`.  Then

```text
K phi = N phi       on Q,
K phi <= N phi      on O.
```

Thus the certificate constructs a positive `N`-superharmonic vector for the
geodesic-overlap matrix `K`.

## Consequence

If the capacity lemma holds, then `E` is a weakly diagonally dominant
symmetric Z-matrix, hence PSD.  The nonsingular part of `A_QQ` is PSD, and
the decoupled zero-row components are PSD.  By Schur complement, `A=N I-K` is
PSD, proving `(SPEC)`.

## Retracted: Explicit Two-Step Supersolution Candidate

This section is kept only to document the dead route.  It is not a valid proof
candidate.

The exact tests do **not** support the following stronger statement; it fails
on the N=23 Mycielski stress instance mentioned above.

Let

```text
u(v) = max(N-T(v), 0).
```

Define

```text
phi(o) = 1                                             for o in O,
phi(q) = 1 - u(q)/N - (K_QQ u)(q)/N^2                  for q in Q.
```

Equivalently, `phi = 1 - g_2` on `Q`, where

```text
g_2 = u_Q/N + K_QQ u_Q/N^2
```

is the two-step Neumann truncation of the Schur potential.

The candidate lemma is:

```text
phi(v) >= 0,
K phi <= N phi.
```

Moreover, whenever `phi(v)=0` in tested graphs, the whole `K`-row of `v` is
zero, so it lies in a trivial zero-eigenvalue component.

If this lemma held, `(SPEC)` would follow immediately: on every nonzero
irreducible component of the nonnegative symmetric matrix `K`, the vector
`phi` is positive and satisfies `K phi <= N phi`; Perron-Frobenius gives
`rho(K_component) <= N`.

Two parts are immediate on `Q`.

First, `phi(q)>=0` because `u<=N` and

```text
(K_QQ u)(q) <= N * sum_{q' in Q} K(q,q') <= N*T(q).
```

Thus

```text
phi(q) = T(q)/N - (K_QQ u)(q)/N^2 >= 0.
```

Second, for `q in Q`, the supersolution margin is automatic:

```text
N*phi(q) - (K phi)(q) = (K_QQ^2 u)(q)/N^2 >= 0.
```

Therefore the only nontrivial inequality is on overloaded vertices:

```text
T(o)-N <= (K_OQ u)(o)/N + (K_OQ K_QQ u)(o)/N^2.
```

Equivalently,

```text
N - T(o) + (K_OQ u)(o)/N + (K_OQ K_QQ u)(o)/N^2 >= 0.
```

This candidate has been exact-stressed and rejected.  The surviving target is
the full-inverse open capacity lemma:

```text
A_QQ g = (N-T)_Q,       0 <= g <= 1,
N - T(o) + sum_{q in Q} K[o,q] g(q) >= 0   for every o in O.
```
