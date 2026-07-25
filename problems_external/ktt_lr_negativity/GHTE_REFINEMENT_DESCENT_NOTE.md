# GHTE under fan refinement: exact one-way descent

Date: 2026-07-22
Status: proved structural lemma; the hive-specific upward step remains open.

## 1. Cycle and relation spaces

Let `Sigma` be a complete rational fan in the lattice `N`. For fixed `q`,
write

```text
Z_q(Sigma) = Q^{Sigma(q)}
```

for the vector space on the invariant cycles `[V(sigma)]` with
`dim(sigma)=q`. At every `(q-1)`-cone `tau`, the principal-divisor relations
are

```text
sum_{sigma>tau} <m,u_{sigma/tau}> [V(sigma)] = 0
```

as `m` ranges over the dual of the saturated quotient lattice `N/N_tau`.
Consequently, for the quotient-lattice balance matrix used in the GHTE
contract,

```text
R_q(Sigma) = image(B_{Sigma,q}^T)                    (1)
```

is exactly the rational-equivalence subspace of invariant cycles.

The Berline--Vergne vector defines the cycle

```text
t_q(Sigma) = sum_{sigma in Sigma(q)}
                 alpha^BV(sigma) [V(sigma)].          (2)
```

Thus GHTE is precisely the assertion that the class of `t_q(Sigma)` has an
effective invariant-cycle representative:

```text
t_q(Sigma) + r = z,
r in R_q(Sigma), z>=0.                               (3)
```

Equation (3) is the Farkas system `a+B^T y>=0`.

## 2. Refinement pushforward

Let `Sigma'` refine `Sigma` in the same lattice. Define

```text
S_q : Z_q(Sigma') -> Z_q(Sigma)
```

on a basis cone `sigma'` as follows. Let `bar(sigma')` be the smallest cone
of `Sigma` containing `sigma'`.

```text
S_q[V(sigma')] = [V(bar(sigma'))] if dim(bar(sigma'))=q,
                 0                if dim(bar(sigma'))>q.     (4)
```

There is no lattice multiplicity in the first case: `sigma'` and
`bar(sigma')` have the same real span, hence the same saturated lattice
`N intersect span_R(sigma')`.

The map (4) is the invariant-cycle pushforward for the proper birational
toric morphism induced by the refinement. It preserves effectiveness and
rational equivalence:

```text
S_q(Q_+^{Sigma'(q)}) subset Q_+^{Sigma(q)},
S_q(R_q(Sigma')) subset R_q(Sigma).                   (5)
```

The second inclusion can also be checked directly by pushing each
principal-divisor relation in (1).

## 3. BV compatibility

For each coarse `q`-cone `sigma`, the fine `q`-cones contained in `sigma`
form a subdivision of `sigma` in its saturated span. The dual-normal-cone BV
functional is a simple valuation. Therefore

```text
alpha^BV(sigma)
  = sum_{sigma' subset sigma, dim(sigma')=q}
        alpha^BV(sigma').                             (6)
```

Fine `q`-cones lying in the relative interior of a higher-dimensional coarse
cone are sent to zero by (4). Equations (2), (4), and (6) give the cycle-level
identity

```text
S_q t_q(Sigma') = t_q(Sigma).                         (7)
```

The word **normal** is essential here. Berline--Vergne, Definition 23 and
Corollary 24, make the constant term `mu^*_0` a *simple* valuation on the
rational normal cones for the fixed scalar-product complement: a subdivision
by full-dimensional cones adds with coefficient one, while intersections in
proper faces make no extra term. Pommersheim--Thomas, Corollary 1(iii), gives
the same additivity for the corresponding rigid-complement Todd measure and
is exactly the toric pushforward used in (7). This is not the formula for a
subdivision of polar feasible cones, where lower-dimensional inclusion--
exclusion terms can occur. No polar-cone subdivision is used in this proof.

## 4. Descent theorem

**Theorem.** If GHTE holds for `Sigma'` in degree `q`, then it holds for every
coarsening `Sigma` in degree `q`.

**Proof.** Choose `r' in R_q(Sigma')` and `z'>=0` with
`t_q(Sigma')+r'=z'`. Apply `S_q`. By (5)--(7),

```text
t_q(Sigma) + S_q r' = S_q z',
S_q r' in R_q(Sigma),
S_q z' >= 0.
```

This is (3) for `Sigma`. ∎

This theorem is one-way. It can prove all hive fans at a fixed rank from one
GHTE-effective common refinement, but it cannot propagate GHTE from a coarse
wall fan to both adjacent refinements.

## 5. Unconditional ascent is false

The failure is not merely a missing argument. The `d`-dimensional braid fan
refines the normal fan of a lattice simplex: a simplex is a generalized
permutohedron, so its normal fan is a braid-fan coarsening. The simplex fan is
GHTE-effective in every degree because each Chow group is one-dimensional.
Writing `td_q(P^d)=c_q H^q`, Hirzebruch--Riemann--Roch gives

```text
[n^(d-q)] L_Delta(n) = c_q/(d-q)!.
```

The coefficients of

```text
L_Delta(n) = binomial(n+d,d)
```

are positive, so every `c_q` is positive and `c_q H^q` is effective.

Castillo--Liu prove that the Todd class of the permutohedral variety, whose
fan is the braid fan, is **not effective for every `d>=24`**. Hence GHTE can
hold for a coarse fan and fail after refinement. No rank-uniform wall-crossing
proof may use an unconditional coarse-to-fine lift.

This does not refute GHTE for hive normal fans. It imposes the exact remaining
obligation: an upward move must use a hive-specific property and supply an
explicit effective lift across every allowed support-number wall.

Primary sources:

- Pommersheim--Thomas, *Cycles representing the Todd class of a toric
  variety*, arXiv:math/0310036, Corollary 1(iii).
- Berline--Vergne, *Local Euler--Maclaurin formula for polytopes*,
  arXiv:math/0507256, Definition 23 and Corollary 24 (simple valuation under
  normal-cone subdivision).
- Castillo--Liu, *On the Todd Class of the Permutohedral Variety*,
  arXiv:1909.09127, Theorem 1.3 (`d>=24` non-effectivity).
