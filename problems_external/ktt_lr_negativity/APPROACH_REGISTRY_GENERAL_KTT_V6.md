# General KTT Proof Workflow — Direct Route Registry V6

Selected: 2026-07-22

Status: DEAD; superseded by V7.  The full V6 family has strictly positive
linear coefficient by the exact double-cap formula recorded below.

Language: English for internal plans, prompts, code, checkers, and artifacts.
User-facing discussion may be Turkish.

## Exact target

Prove full KTT in every rank, or produce one exact stretched LR polynomial
with a negative ordinary monomial coefficient and two independent replays.

## DIRECT ROUTE — FULL SYMMETRIC UNIT-COLUMN TRANSPORTATION FAMILY

### 1. Exact final deliverable

For integers `a>=1` and `1<=k<=3a-1`, let `T_(a,k)` be the full
`3 x (k+1)` transportation polytope with

```text
row margins    (a,a,a),
column margins (3a-k,1^k).
```

Find an explicit pair with a negative linear Ehrhart coefficient and transfer
it homogeneously to LR, or prove that the linear coefficient is nonnegative
throughout this entire two-parameter family.

### 2. Current frontier lemma

Let `C_1(a,k;n)` count unit-column configurations for which one specified row
sum exceeds `an`, and let `C_2(a,k;n)` count configurations for which two
specified row sums exceed `an`.  Since `k<3a`, three rows cannot all exceed the
cap.  Prove the exact sign of

```text
[n]L_(a,k)(n) = 3k/2 - 3[n]C_1(a,k;n) + 3[n]C_2(a,k;n).       (1)
```

The first correction is already closed.  For `a<=k<=2a`, pair intersections
are empty and

```text
[n]L_(a,k)(n)=(3a/2)*(1+H_k-H_a)>0.
```

For `k<=a`, every row cap is automatic and
`L_(a,k)(n)=binom(n+2,2)^k`.  Thus the only open parameter region is

```text
2a < k < 3a,
```

and the load-bearing frontier is one exact bivariate coefficient formula for
`[n]C_2` there.

### 3. Explicit logical bridge

Projection to the `k` unit columns identifies `L_(a,k)(n)` with the number of
`k` weak three-part compositions of `n` whose aggregate row sums are at most
`an`.  Inclusion-exclusion gives (1), so a closed formula for the double-cap
term decides the linear sign for the full family.

The same count is a stretched skew Kostka number and then one LR coefficient:

```text
A=(3a,2a,a),                 B=(2a,a),
w=(3a-k,1^k),
R=(5a,4a,3a,k,k-1,...,1),
S=(3a,3a,k,k-1,...,1),
L_(a,k)(n)=K_(nA/nB,nw)=c^(nR)_(nA,nS).
```

All maps are dilation-compatible lattice bijections.  Therefore a negative
value in (1) is literally a KTT counterexample.

### 4. Next falsifiable action

Derive `[n]C_2` from the exact bivariate unit-column generating function,
validate it on the minimal open cases `(a,k)=(2,5),(3,7),(3,8)` by raw DP,
Newton interpolation, and held-out dilations, and test a bounded calibration
range.  If no negative pair occurs, continue only with an analytic sign or
asymptotic theorem for the bivariate formula.  Do not launch an open-ended
two-parameter sweep.

### 5. Exit condition

Success:

```text
one (a,k) with [n]L_(a,k)<0, followed by exact table, skew-Kostka, and
two-engine LR certificates through the degree and two held-out dilations.
```

Failure:

```text
DEAD: full symmetric unit-column family has nonnegative linear coefficient --
<exact bivariate sign proof>, or the registered bivariate sign bridge fails
and no theorem-closing continuation remains.
```

## Scope guard

This is one parametric theorem problem, not a sequence of growing searches.
The bounded skew-Kostka gate from V3 remains independent.  GHTE remains an
open sufficient theorem.  Full KTT remains open unless an actual LR
certificate is produced.

## Resolution

Put `b=k-2a` in the only open chamber `2a<k<3a`.  Exact bivariate
coefficient extraction gives

```text
[n]C_2(a,k;n) = -(1/2) sum_(q=1)^b q/(2a+q),

[n]L_(a,k)(n)
 = (3/2) [a-b+a(H_k-H_a)+2a(H_k-H_(2a))]
 >= (3/2)(3a-k)>0.
```

The direct DP/interpolation checker and an independent partial-fraction
checker both pass, including two held-out dilations.  See
`SYMMETRIC_UNIT_TRANSPORT_FULL_LINEAR_THEOREM.md` and
`FULL_UNIT_COLUMN_TRANSPORT_LINEAR_REFEREE.md`.  Therefore the V6 exit is

```text
DEAD: the full symmetric unit-column family has positive linear coefficient.
```
