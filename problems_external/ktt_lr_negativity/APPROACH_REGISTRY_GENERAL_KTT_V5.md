# General KTT Proof Workflow — Direct Route Registry V5

Selected: 2026-07-22

Status: DEAD; supersedes V4.  V4 records the exhausted attempt to identify
the negative order polytope with a codegree-three `3 x 8` table polytope.

Language: English for internal plans, prompts, code, checkers, and artifacts.
User-facing discussion may be Turkish.

Outcome: the exact finite sum collapses to

```text
A(a)=(3a/2)(1+H_(2a-1)-H_a)>0
```

for every `a>=3`.  Two independent exact audits are recorded in
`SYMMETRIC_UNIT_TRANSPORT_LINEAR_THEOREM.md` and
`SYMMETRIC_TRANSPORT_LINEAR_REFEREE_AUDIT.md`.  This kills only the registered
family; full KTT remains open.

## Exact target

Prove full KTT in every rank, or produce one exact stretched LR polynomial
with a negative ordinary monomial coefficient and two independent replays.

## DIRECT ROUTE — SYMMETRIC UNIT-COLUMN TRANSPORTATION FAMILY

### 1. Exact final deliverable

For some integer `a>=3`, prove that the full transportation polytope with

```text
row margins    (a,a,a),
column margins (a+1,1,1,...,1),  with 2a-1 unit columns,
```

has a negative Ehrhart coefficient.  Convert it homogeneously to one explicit
LR triple.  A proof that the entire parametric family is Ehrhart positive is a
valid negative route decision but does not prove KTT.

### 2. Current frontier lemma

Let `T_a` denote this `3 x (2a)` transportation polytope and `L_a(n)` its
Ehrhart polynomial.  Determine the exact sign of

```text
A(a)=[n] L_a(n)
```

from one closed finite sum in `a`.  The calibration case `a=4` has exact
linear cancellation ratio

```text
131174147/131215991 = 0.999681106...
```

but positive `A(4)=317/35`, so this is a falsifiable near-boundary family, not
a null census.

### 3. Explicit logical bridge

Put `k=2a-1`.  Project a table to its `k` unit columns.  Inclusion-exclusion
over the three row caps gives

```text
L_a(n)=binom(n+2,2)^k - 3 S_a(n),
```

where

```text
S_a(n) = sum_{0<=y_i<=n, sum(y_i)<=(a-1)n-1} product_i(y_i+1).
```

Equivalently,

```text
S_a(n)=[t^((a-1)n-1)]
       (1-(n+2)t^(n+1)+(n+1)t^(n+2))^k /(1-t)^(2k+1).
```

Expanding the numerator yields one finite binomial sum whose polynomial
linear coefficient is `A(a)`.  Thus the frontier is an exact symbolic sign
problem, not an unbounded sequence of polytope searches.

The table count is also

```text
K_(nA/nB,nw)=c^(nR)_(nA,nS),
```

with

```text
A=(3a,2a,a),                 B=(2a,a),
w=(a+1,1^(2a-1)),
R=(5a,4a,3a,2a-1,2a-2,...,1),
S=(3a,3a,2a-1,2a-2,...,1).
```

This is the audited disconnected-row skew-Kostka construction followed by
the homogeneous skew-Kostka-to-LR bridge.  Therefore `A(a)<0` is literally a
KTT counterexample.

The polytope has dimension `4a-2`, codegree three, and exactly one relative-
interior lattice point in `3T_a`: every unit column is forced to `(1,1,1)`.

### 4. Next falsifiable action

Derive the finite binomial expression over `Q`, validate it against the two
independent `a=3,4` transportation DPs at interpolation and held-out points,
and evaluate the exact sign for a bounded calibration range.  If a negative
value occurs, immediately construct and replay its LR triple.  If calibration
stays positive, continue only by proving an analytic sign or asymptotic theorem
for `A(a)`; do not launch an open-ended integer sweep.

### 5. Exit condition

Success:

```text
A(a)<0 for an explicit a, with exact table, skew-Kostka, and two-engine LR
certificates through the degree and two held-out dilations.
```

Failure:

```text
DEAD: symmetric unit-column transportation family has A(a)>=0 for all a --
<exact finite-sum sign proof>, or no theorem-closing sign bridge survives the
registered calibration.
```

## Retained scope guard

The bounded skew-Kostka gate from V3 continues independently under its fixed
exit.  GHTE remains an open sufficient theorem.  The established theorem is
still only the length-at-most-four case; a positive `A(a)` calculation proves
nothing about full KTT.

## Exit record

Two independent exact derivations give, for every `a>=3`,

```text
A(a)=(3a/2)*(1+H_(2a-1)-H_a)>0.
```

The finite double sum collapses by grouping `i+j=s` and evaluating the inner
reciprocal-binomial sum by a beta integral.  Independent two-dimensional and
cap DPs, interpolation, and held-out dilations verify `a=3,4,5`.  Terms with
`i+j>=a-1` are omitted before polynomial continuation; retaining them as
generalized binomials would introduce spurious terms.

```text
DEAD: symmetric unit-column family has positive linear coefficient for every
a>=3 -- exact harmonic-number sign formula.
```
