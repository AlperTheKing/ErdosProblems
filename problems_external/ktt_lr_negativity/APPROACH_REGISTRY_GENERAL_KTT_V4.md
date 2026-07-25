# General KTT Proof Workflow — Direct Route Registry V4

Selected: 2026-07-22

Status: DEAD; superseded by V5.  V3 remains the audit record for the open GHTE
statement and the dead canonical Todd-transport implementations.

Language: English for internal plans, prompts, code, checkers, and research
artifacts.  User-facing discussion may be Turkish.

## Exact target

For every nonzero Littlewood--Richardson triple in every rank, prove that every
ordinary monomial coefficient of

```text
P(n)=c(n nu; n lambda,n mu)
```

is nonnegative.  If false, produce one partition triple with an exact negative
coefficient, reconstructed by two independent counting engines through the
degree bound and at two held-out dilations.

## DIRECT ROUTE — CODEGREE-THREE TRANSPORTATION TRANSFER

### 1. Exact final deliverable

An actual KTT counterexample obtained from a full transportation polytope with
a negative Ehrhart coefficient, followed by the exact homogeneous chain

```text
transportation tables -> stretched skew Kostka -> stretched LR.
```

This route is authorized because every arrow preserves the complete counting
function at every dilation, not merely one value, a face, or a projection.

### 2. Current frontier lemma or finite certificate

Decide the following finite certificate problem.  Let `r=(r1,r2,r3)` with
each `ri>=3`, put `N=sum(r)`, and let

```text
c=(N-7,1,1,1,1,1,1,1).
```

For the full `3 x 8` transportation polytope `T(r,c)`, determine exactly
whether some margin pattern has a negative ordinary Ehrhart coefficient.  The
first gate is the invariant-matching subfamily `L_T(1)=255`, because the known
negative order polytope `O(P_(7,7))` has dimension 14, codegree three, one
interior lattice point in `3O`, and `L_O(1)=255`.

This is finite up to row permutation and the truncation `ri -> min(ri,7)` for
the `L(1)=255` gate: the seven unit columns carry only seven units at dilation
one.  Exact polynomials are then reconstructed only for surviving margins.

### 3. Explicit logical bridge

The polytope has dimension `(3-1)(8-1)=14`.  At dilation three, subtract one
from every table entry.  The seven unit-column margins become zero, so the
large column is forced entry by entry; hence `3T` has exactly one relative-
interior lattice point.  No relative-interior lattice point exists at
dilations one or two, so the codegree is three.

For arbitrary positive row and column margins, place three horizontal strips
of lengths `r1,r2,r3` in pairwise disjoint column intervals of a skew Young
diagram.  Sorting each tableau row identifies its multiplicities with a
nonnegative `3 x 8` table having those margins.  Scaling the two boundary
partitions and the content by `n` gives exactly the tables with margins
`(nr,nc)`.  Thus the equality is homogeneous in every dilation.

`KOSTKA_TO_LR_HOMOGENEOUS_BRIDGE.md` then converts that stretched skew Kostka
number into one stretched LR coefficient.  Therefore a negative coefficient
found here is literally a KTT counterexample.

### 4. Next falsifiable action

Enumerate the finite invariant-matching row-margin gate over exact integers;
for every survivor, compute the degree-14 Ehrhart polynomial by dynamic
programming, verify two held-out dilations, and compare it with `O(P_(7,7))`.
If no survivor exists or all survivors are Ehrhart positive, record the exact
obstruction and stop this family.  Do not expand to an unbounded transportation
census without a new theorem-closing invariant.

### 5. Exit condition

Success:

```text
one negative transportation Ehrhart coefficient + explicit skew shape/content
+ explicit LR partitions + two independent exact counting replays.
```

Failure:

```text
DEAD: codegree-three 3x8 transfer family exhausted -- <exact finite result>;
no theorem-closing bridge authorizes a larger margin cascade.
```

## Retained alternatives and scope guard

The bounded skew-Kostka gate authorized in V3 remains active and must stop at
its existing finite exit condition.  GHTE remains a sufficient open theorem,
not an active transport attack.  The negative order-polytope transfer report
excludes only its analyzed skew/flagged and two-row routes; it does not exclude
the full `3 x 8` transportation family tested here.

The currently established theorem remains length at most four.  Full KTT is
open unless the success certificate above is produced.

## Exit record

The exact gate is empty.  Every allowed margin has

```text
L_T(1) >= 1050 > 255=L_O(1).
```

An independent exact DP also reconstructed the degree-14 polynomials for all
35 capped representatives and found no negative coefficient, with held-out
dilations 15 and 16 matching.  Projection to the seven unit columns proves
that replacing every `ri>7` by `7` preserves the count at every dilation, so
the 35 representatives cover the entire registered margin family.  This fact
is not used as evidence for general KTT.

```text
DEAD: codegree-three 3x8 order-polytope transfer exhausted -- the base-count
invariant already excludes every margin in the registered family.
```
