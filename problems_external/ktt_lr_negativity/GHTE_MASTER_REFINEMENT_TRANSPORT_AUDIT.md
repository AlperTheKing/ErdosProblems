# GHTE master-refinement transport audit

Date: 2026-07-22

Status: **DEAD for canonical pullback-plus-effective transport to a common
master refinement.**  This is not a counterexample to GHTE or KTT.  The exact
common refinement in the test below is itself GHTE-effective in the audited
degree; what fails is the only canonical inductive lift from either adjacent
hive fan.

## 1. Direct-route question

Refinement descent proves that one GHTE-effective fan refining every intrinsic
hive fan at a fixed rank would prove GHTE for all those hive fans.  The proposed
rank-uniform route was therefore:

```text
effective Todd cycle on a coarse/adjacent hive fan
  -> canonical common refinement with an effective exceptional correction
  -> iterate across the support chambers
  -> one effective master fan
  -> descend to every hive fan.
```

The exact load-bearing step is the upward arrow.  A mere common refinement is
not a proof: its Todd cycle has to be shown effective, and generic GHTE ascent
is already known to be false.  This audit tests the strongest canonical
version of the upward arrow on the smallest actual hive flip.

## 2. The canonical coarsest common refinement

Use the exact side-four hive wall from
`ACTUAL_HIVE_WALL_EHRHART_OBSTRUCTION.md`.  In `N=Z^3` its rays are

```text
a=(-1,1,0), b=(0,0,-1), c=(0,1,0), d=(1,0,-1),
r=(0,-1,1),
a+d=b+c=:e=(0,1,-1)=-r.                                (1)
```

The adjacent complete smooth fans have maximal cones

```text
Sigma_L: arb, arc, brd, crd, abc, bcd,
Sigma_R: arb, arc, brd, crd, abd, acd.                 (2)
```

Their canonical coarsest common refinement is the overlay fan `W`, equivalently
the star subdivision of `bc` on the left or `ad` on the right:

```text
W: arb, arc, brd, crd, abe, ace, bed, ecd.             (3)
```

Indeed, writing a point in the two diagonal cones as
`alpha*b+beta*c=gamma*a+delta*d` forces
`alpha=beta=gamma=delta>=0`.  Hence their intersection is exactly the ray
`R_+e`, which every common refinement must contain; subdividing along that ray
gives precisely (3).

The checker verifies directly that every maximal determinant in (2)--(3) has
absolute value one, every codimension-one cone is incident to two maximal
cones with opposite quotient signs, and every cone in (3) lies in a cone on
each side of (2).  Thus no lattice multiplicity or non-completeness is hidden
in the calculation.

## 3. Exact Todd classes on the common refinement

Let `x,y,z` be the divisor classes of `a,b,e`.  The linear and
Stanley--Reisner relations give

```text
A*(X_W)_Q = Q[x,y,z]/(x^2,y^2,z(x+y+z)).               (4)
```

The six ray divisors are

```text
x, y, y, x, x+y+z, z.
```

Computing `(c_1^2+c_2)/12` in (4) gives

```text
td_2(W) = 13/6 xy + xz + yz
        = 13/6[V(ab)] + [V(ae)] + [V(be)].             (5)
```

This is effective.  Independently, the checker rebuilds the primitive
quotient-lattice balance matrix `B_(W,2)` and the Euclidean BV vector.  In the
cone order

```text
ab, ac, ae, ar, bd, be, br, cd, ce, cr, de, dr,
```

it verifies (5) modulo `im(B^T)`.  It also verifies the strictly positive
balanced weight

```text
w=(1,1,1,2,1,1,2,1,1,2,1,2),       B w=0.            (6)
```

Consequently this local master fan is not a GHTE counterexample.

## 4. The exact obstruction to upward transport

The adjacent Chow rings and Todd classes are

```text
A*(X_L)_Q = Q[x,y]/(x^2,y^2(x+y)),
td_2(L)   = 13/6 xy+y^2,

A*(X_R)_Q = Q[x,y]/(y^2,x^2(x+y)),
td_2(R)   = 13/6 xy+x^2.                               (7)
```

For the two canonical toric blowups `p_L:X_W->X_L` and `p_R:X_W->X_R`,

```text
p_L^*x=x,   p_L^*y=y+z,
p_R^*x=x+z, p_R^*y=y.                                  (8)
```

Using `z^2=-xz-yz`, equations (5)--(8) give

```text
td_2(W)-p_L^*td_2(L) = -1/6 xz = -1/6[V(ae)],
td_2(W)-p_R^*td_2(R) = -1/6 yz = -1/6[V(be)].          (9)
```

Pairing the two classes in (9) with (6) gives `-1/6` in both cases.  Because
balanced weights annihilate `im(B^T)` and are nonnegative on every effective
cycle, neither class in (9) has a nonnegative representative modulo balancing.
Thus the failure is not a poor choice of invariant-cycle representative.

This obstruction survives every further smooth common refinement.  Indeed,
let `f:X_T->X_W` be any smooth toric refinement and put
`g_L=p_L composed with f`.  If a canonical positive lift existed,

```text
td_2(T) = g_L^*td_2(L)+E,       E effective modulo balancing,             (10)
```

then toric Todd functoriality and the projection formula would give

```text
td_2(W) = p_L^*td_2(L)+f_*E.                            (11)
```

The pushforward `f_*E` is effective, contradicting the first equality in
(9) and its separating weight.  The right side is identical.  Hence adding
more rays to a proposed master cannot repair this canonical upward lift.

The independent graph-correspondence audit in
`GHTE_UNIT_CREPANT_FLIP_TODD_OBSTRUCTION.md` gives the complementary exact
failure `[V(bc)]->-[V(ad)]`.  The actual-volume audit gives the chamber jump
`binomial((-Omega)n+1,3)`, whose linear coefficient is negative.  Therefore
all three canonical transports available from one wall -- actual volume,
graph correspondence, and pullback to the common resolution -- fail on the
same actual primitive hive flip.

## 5. Direct-route decision

A common master fan could still prove GHTE **only** through a new direct theorem
that its Todd cycles are effective in every degree and rank.  Equations (9)--
(11) show that such a theorem cannot be obtained inductively from adjacent
hive fans by canonical toric pullback plus a nonnegative correction.  Iterating
common refinements without that theorem merely replaces GHTE by a rank-growing
family of new GHTE instances and has no bridge to the final deliverable.

The exact exit record is

```text
DEAD: canonical master-refinement transport has no rank-uniform bridge --
on the actual unit hive flip, every smooth common refinement pushes its
putative effective pullback correction to -1/6[V(ae)] or -1/6[V(be)], each
separated from the effective cone by the positive balanced weight (6).
```

This kills the transport, not the abstract possibility that a separately
identified hive-specific master fan has an independently provable effective
Todd class.

The next single falsifiable GHTE action is not another refinement census: take
one full-dimensional side-five hive and audit the first open degree `q=d-1=5`
under the complete-fan checker contract.  A rational
`w>=0, Bw=0, <a,w><0` kills GHTE immediately; a Farkas certificate validates
that one gate only and must not trigger a fixed-rank cascade.

## 6. Replay

```text
python problems_external/ktt_lr_negativity/ghte_master_refinement_transport_audit.py
```

Expected output begins

```text
PASS
payload_sha256=102b0ce9f346f91b9c6a25c23adc6c170d0bfed82da33b21d9ddf6917ac83a3b
```
