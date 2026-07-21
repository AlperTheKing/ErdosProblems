# Frozen reference CNF for the fixed `K_19-C_19` cell

Status: **FROZEN INDEPENDENT SPECIFICATION**.  This document was derived from
`N19_MECHANISM.md` before inspecting any CNF generator.  It specifies a
baseline formula, its exact semantics, and adversarial calibration cases.  No
solver run is reported here.

The scope is only orientations of `K_19-C_19` with every outdegree equal to
8 and with the proved `3`-by-`3` unreachable-incidence ledger.  SAT would
produce a literal SSNC counterexample after independent replay.  Checked
UNSAT would exclude only this fixed connected missing-cycle cell.

## 1. Fixed graph and literal convention

Let

```text
V = Z/19Z = {0,...,18}.
```

For distinct vertices `v,u`, define

```text
missing(v,u) iff (u-v) mod 19 is 1 or 18,
present(v,u) iff not missing(v,u).
```

Thus the missing unordered pairs are exactly `{i,i+1 mod 19}`.  In
particular, `{18,0}` is missing.  There are `171-19=152` present unordered
pairs, and every vertex has 16 present neighbours.

For each present pair `{i,j}` with `i<j`, introduce one Boolean orientation
variable

```text
a[i,j] = true iff i -> j.
```

Define the **signed arc literal** `X(v,u)` by

```text
X(v,u) = a[v,u]      if present(v,u) and v<u,
X(v,u) = not a[u,v]  if present(v,u) and u<v,
X(v,u) = FALSE       if v=u or missing(v,u).
```

Consequently, on a present pair, `X(u,v)=not X(v,u)`.  On a loop or a
missing pair, however, **both directions are constant false**.  In
particular, it is incorrect to represent the reverse direction of a missing
edge by negating a literal: that would make one forbidden direction true.

The one-variable convention enforces exactly one direction on every present
edge without additional clauses and enforces no loops or digons by
construction.  An implementation using two ordered variables instead is
equivalent only if it emits, for each present unordered pair,

```text
(x[v,u] or x[u,v])
(not x[v,u] or not x[u,v])
```

and emits unit-negative clauses for both directions of every loop and fixed
missing pair.  The two conventions must not be mixed.

## 2. CNF macros, including signed and constant literals

A clause below is a disjunction.  Negating a signed literal reverses its
sign: if `L=not a[i,j]`, then `not L=a[i,j]`.  `FALSE` and `TRUE` are
constants, not variable identifiers.  Constant-fold clauses as follows:

- a clause containing `TRUE` is a tautology and is dropped;
- occurrences of `FALSE` are removed;
- an empty clause is contradiction; and
- a one-literal clause is a unit clause.

### 2.1 AND equivalence

For an output variable `p` and literals `L1,L2`, the exact equivalence

```text
p iff (L1 and L2)
```

is the conjunction of all three clauses

```text
(not p or L1)
(not p or L2)
(p or not L1 or not L2).
```

If either input is structural `FALSE`, the simplified result is the unit
clause `(not p)`.  Omitting only the third clause permits a real path to be
hidden by setting `p=false`; omitting either of the first two clauses permits
a path witness to be invented.

### 2.2 OR equivalence

For an output variable `r` and inputs `p[0],...,p[m-1]`, the exact
equivalence

```text
r iff OR_i p[i]
```

is

```text
(not p[i] or r)                 for every i,
(not r or p[0] or ... or p[m-1]).
```

For an empty input list, the last clause becomes the unit `(not r)`.  The
short clauses prevent a genuine witness from being ignored; the long clause
prevents `r` from becoming true without a witness.

### 2.3 Unreachable equivalence

For off-diagonal `(v,u)`, with `L=X(v,u)` and `r=reach[v,u]`, the exact
equivalence

```text
z[v,u] iff (not L and not r)
```

is

```text
(not z[v,u] or not L)
(not z[v,u] or not r)
(z[v,u] or L or r).
```

When `(v,u)` is a fixed missing direction, `L=FALSE`, so these simplify to

```text
(not z[v,u] or not r)
(z[v,u] or r),
```

namely `z[v,u] iff not r`.  A missing neighbour is therefore a legitimate
unreachable target when it has no two-step witness; it must not be omitted
from the ledger.

The diagonal is exceptional and is defined by the unit clause

```text
(not z[v,v]).
```

Do not apply the off-diagonal equivalence to `v=u`.  In an oriented graph a
two-step return `v -> w -> v` would be a digon, so `reach[v,v]=false`; the
generic formula would consequently force the incorrect value `z[v,v]=true`.

### 2.4 Reference cardinality clauses

For literals `L={L1,...,Lm}`, define the deliberately simple, non-optimized
reference encoding

```text
AtMost(k,L):  for every S subset L with |S|=k+1,
              emit OR_{ell in S} (not ell).

AtLeast(k,L): for every S subset L with |S|=m-k+1,
              emit OR_{ell in S} ell.

Exactly(k,L): AtMost(k,L) and AtLeast(k,L).
```

These definitions apply to signed literals.  A sequential counter, totalizer,
or cardinality network may replace them in production only if separately
calibrated against this truth table.  Auxiliary variables from different
rows or columns must not be accidentally shared.

## 3. Complete baseline variable and clause specification

The full-array baseline is intentionally redundant and easy to audit.
Optimized implementations may omit variables already forced false, but must
be projection-equivalent to this formula.

### 3.1 Orientation and symmetry variables

Create the 152 variables `a[i,j]` described in Section 1.  No variable exists
for a loop or fixed missing edge.  Add the safe symmetry unit

```text
X(0,2),
```

which, under the canonical convention, is simply `(a[0,2])`.

### 3.2 Literal two-step witnesses

For every ordered triple `(v,w,u) in V^3`, create `p[v,w,u]` and encode

```text
p[v,w,u] iff (X(v,w) and X(w,u))
```

using the three AND clauses in Section 2.1.  If either step is a loop or fixed
missing direction, emit the simplified unit `(not p[v,w,u])`.  Keeping all
`19^3=6859` variables is the reference choice.  Omitting structurally false
ones is safe only if every reachability OR treats each omitted witness as
constant false.

The index order is semantic and load-bearing:

```text
source v -> intermediate w -> target u.
```

It is not `v -> u -> w`, `u -> w -> v`, a common-out-neighbour test, or a
common-in-neighbour test.

### 3.3 Literal two-step reachability

For every ordered pair `(v,u) in V^2`, create `reach[v,u]` and encode

```text
reach[v,u] iff OR_{w in V} p[v,w,u]
```

using all 19 short implications and the one 19-input reverse clause from
Section 2.2.  `reach[v,u]` records a literal two-step walk even when `u` is
also a direct out-neighbour of `v`.  Direct-neighbour exclusion belongs in
`z`, not in this OR gate.

For `v=u`, all witnesses are false: `w=v` gives a loop, while `w!=v` would
require both directions of one present edge or includes a missing direction.
The gate therefore forces `reach[v,v]=false`.

### 3.4 Literal unreachability

Create `z[v,u]` for every ordered pair.  For `v!=u`, encode

```text
z[v,u] iff (not X(v,u) and not reach[v,u])
```

with the three clauses in Section 2.3.  For `v=u`, emit only
`(not z[v,v])`.

Thus `z[v,u]` means exactly that `u` is neither the source itself, nor a
direct out-neighbour, nor reachable by a directed two-step walk from `v`.

### 3.5 Exact outdegree 8

For every source `v`, let

```text
Out(v) = [X(v,u) : u in V and present(v,u)].
```

This list has 16 signed literals.  Emit

```text
Exactly(8, Out(v)).
```

With the reference subset encoding, this means one all-negative clause and
one all-positive clause for every 9-subset of `Out(v)`.  It is essential to
count `X(v,u)`, not the underlying unsigned variable ID: whenever `u<v`, the
outgoing literal is negative.

Because every vertex has 16 present neighbours and each present pair has one
direction, exact outdegree 8 also implies exact indegree 8.

### 3.6 Exact unreachable row and column ledgers

For every source `v`, emit

```text
Exactly(3, [z[v,u] : u in V, u!=v]).
```

For every target `u`, independently emit

```text
Exactly(3, [z[v,u] : v in V, v!=u]).
```

Each list has 18 variables.  Under the reference subset encoding, exact 3
means:

- one all-negative clause for every 4-subset; and
- one all-positive clause for every 16-subset.

The row constraint fixes three unreachable targets for every source.  The
column constraint fixes three unreachable roots for every target.  These are
different axes and neither family may be replaced by a duplicate or transpose
of the other.

The column equalities are sound for this sharp cell: the fixed-target packing
bound gives each column at most three, while the 19 row equalities give 57
total incidences, forcing every one of 19 columns to equal three.

## 4. Soundness and completeness for the frozen cell

The gate clauses make every auxiliary value unique once the 152 orientation
variables are fixed:

1. `p[v,w,u]` is true exactly for a directed walk `v -> w -> u`;
2. `reach[v,u]` is true exactly when at least one such walk exists; and
3. off the diagonal, `z[v,u]` is true exactly when `u` is outside
   `{v} union N+(v) union N++(v)`.

Each source has eight direct out-neighbours.  Among the remaining ten
off-diagonal vertices, exactly three have `z=true`; the other seven are
literal new second out-neighbours.  Hence any satisfying assignment has

```text
|N+(v)|   = 8,
|N++(v)|  = 7
```

for every vertex.  After independent replay, its orientation would refute
SSNC.

Conversely, any orientation in the fixed `K_19-C_19`, degree-8 sharp cell
with the proved three-by-three incidence equality extends uniquely to values
of `p`, `reach`, and `z` satisfying the baseline formula.  Therefore the
baseline neither invents nor loses a witness in this registered cell.

The target-triangle and singleton-difference consequences from
`N19_MECHANISM.md` are deliberately absent.  They may later be added as
redundant propagation only after a separate clause audit; baseline
correctness and certificate replay must not depend on them.

## 5. Why the single `0 -> 2` symmetry pin is safe

The dihedral group of the labelled missing cycle preserves the fixed graph
and all degree, path, reachability, and ledger predicates.  If a satisfying
orientation already contains `0 -> 2`, no relabelling is needed.  Otherwise
it contains `2 -> 0`.  The reflection

```text
f(i) = 2-i mod 19
```

preserves every missing cycle edge and swaps vertices 0 and 2.  It maps the
arc `2 -> 0` to `0 -> 2`.  Thus every dihedral orbit of solutions has a
representative satisfying the unit `X(0,2)`.

This proof licenses only the signed literal `X(0,2)`, not an unsigned variable
chosen by position.  It does not license a fixed root triple, additional arc
pins, or global arc reversal.  Any further symmetry restriction requires its
own orbit proof or complete branching over the omitted orbits.

## 6. One-way and indexing failure catalogue

### Orientation layer

1. Using `a[min,max]` with positive sign in both directions creates a digon
   semantically; the larger endpoint must use the negative literal.
2. Treating the reverse of a missing edge as the negation of `FALSE` creates
   a forbidden arc.  Both missing directions are `FALSE`.
3. Testing only ordinary integer difference 1 misses the wrap edge `{18,0}`;
   the missing predicate is modulo 19.
4. With two ordered variables, only at-most-one permits an extra missing
   present edge, while only at-least-one permits a digon.  Both clauses are
   required.
5. Summing raw canonical variables instead of signed outgoing literals gives
   incorrect degrees for every larger-labelled endpoint.
6. Encoding only `AtMost(8)` or only `AtLeast(8)` changes the sharp regular
   cell.

### Two-step AND layer

1. Omitting `(p or not L1 or not L2)` lets a real two-step path disappear.
2. Omitting either `(not p or L1)` or `(not p or L2)` lets a false path be
   invented.
3. Negating a variable ID instead of the signed literal reverses one of the
   clauses whenever a step runs from a larger to a smaller label.
4. Swapping `w` and `u`, reversing `v` and `u`, or using
   `X(v,w) and X(u,w)` tests a different graph relation.
5. Dropping a constant-false input clause without also forcing `p=false`
   leaves witnesses through loops or missing edges unconstrained.

### Reachability OR layer

1. Keeping only `p -> reach` permits unsupported `reach=true` values.
2. Keeping only `reach -> OR p` permits genuine paths with `reach=false`.
3. Using `p[u,w,v]`, `p[v,u,w]`, or an OR over the wrong free index silently
   transposes or changes the relation.
4. An empty witness list is `FALSE`, not a tautology.
5. Adding the direct arc to the OR, or replacing literal reachability by an
   already filtered new-second-neighbour predicate, violates the frozen
   auxiliary semantics.

### Unreachable layer

1. `not (X and reach)` and `(not X or not reach)` are not
   `(not X and not reach)`.
2. Keeping only `z -> (not X and not reach)` allows actual unreachable pairs
   to be omitted; keeping only the reverse implication allows arbitrary
   false unreachable witnesses.
3. Using `X(u,v)` or `reach[u,v]` computes unreachability in the reverse
   direction.
4. Excluding fixed missing neighbours from the `z` domain is wrong: they may
   or may not have a two-step witness.
5. Applying the off-diagonal formula on `z[v,v]` forces the diagonal true;
   the diagonal must instead be unit false.
6. Defining `z` as merely `not reach` incorrectly counts a direct
   out-neighbour that lacks a two-step walk.

### Ledger and symmetry layers

1. Row sums range over targets `u`; column sums range over sources `v`.
   Accidentally emitting the row family twice removes the target capacity.
2. Including `z[v,v]`, counting `reach` instead of `z`, or using only one
   side of exact 3 changes the incidence mechanism.
3. Reusing cardinality auxiliary variables between different rows or columns
   couples unrelated constraints.
4. Pinning raw `a[0,2]` is safe only because its declared meaning is
   `0 -> 2`; the invariant statement is the signed unit `X(0,2)`.
5. A fixed root triple or multiple convenient arcs are not consequences of
   the dihedral action.  Global reversal is not an approved symmetry.

## 7. Tiny pinned calibration suite

These are proposed unit tests, not solver results.  Each gate test uses only
the named gate clauses plus unit assumptions.  To test a forced value, add
the opposite unit and require UNSAT; add the expected unit and require SAT.

### 7.1 Literal/static tests

| ID | Pins or query | Required result | Detects |
|---|---|---|---|
| O1 | `a[0,2]=1` | `X(0,2)=1`, `X(2,0)=0` | reversed sign loss |
| O2 | `a[0,2]=0` | `X(0,2)=0`, `X(2,0)=1` | reversed sign loss |
| O3 | query `{0,1}` and `{18,0}` | all four directions are constant false | missing edge made orientable; wrap bug |
| O4 | query `(v,v)` for several `v` | `X(v,v)=FALSE` and no orientation variable | loop bug |

For a signed-cardinality check, instantiate `Exactly(2,[a,not b,c,not d])`.
The assignment `(a,b,c,d)=(1,1,0,0)` has exactly two true literals and must
be accepted; changing only `d` to 1 leaves one true literal and must be
rejected.  This catches counters that strip literal signs.

### 7.2 AND/path tests

| ID | Pins | Required result | Detects |
|---|---|---|---|
| P1 | `a[0,2]=1`, `a[2,4]=1` | `p[0,2,4]=1` | missing AND reverse clause |
| P2 | `a[2,4]=0`, `a[0,2]=0` | `p[4,2,0]=1` | two negative signed steps; index reversal |
| P3 | `a[0,2]=1`, `a[2,4]=0` | `p[0,2,4]=0` | invented path; missing forward clause |
| P4 | any value of `X(1,3)` | `p[0,1,3]=0` because `X(0,1)=FALSE` | missing-edge constant handling |
| P5 | any value of `X(0,2)` | `p[18,0,2]=0` because `X(18,0)=FALSE` | wrap-edge constant handling |

### 7.3 OR/reach tests

Use a standalone three-input OR gate as the smallest truth-table harness.

| ID | Input pins | Required result | Detects |
|---|---|---|---|
| R1 | `(p0,p1,p2)=(0,1,0)` | `reach=1` | omitted `p -> reach` |
| R2 | `(p0,p1,p2)=(0,0,0)` | `reach=0` | omitted long reverse clause |

For an index test, instantiate two separate gates, give the `reach[0,4]`
gate the true input `p[0,2,4]`, and pin every input of `reach[4,0]` false.
The forced pair is `(reach[0,4],reach[4,0])=(1,0)`.  Any equality or swap
between them exposes a reversed source-target index.

### 7.4 Unreachable truth table

For an off-diagonal gate with direct literal `L`, all three rows below are
required:

| ID | `(L,reach)` | Required `z` |
|---|---:|---:|
| Z1 | `(1,0)` | `0` |
| Z2 | `(0,1)` | `0` |
| Z3 | `(0,0)` | `1` |

Additionally:

- for missing `{0,1}`, `reach[0,1]=0` must force `z[0,1]=1`, while
  `reach[0,1]=1` must force `z[0,1]=0`; and
- `reach[v,v]=0` must coexist with the separately forced `z[v,v]=0`.

The second check distinguishes the diagonal override from an incorrectly
uniform unreachable gate.

### 7.5 Row-versus-column ledger tests

Use a standalone `5 by 5` Boolean incidence matrix with diagonal fixed zero.
The following row supports each have size three:

```text
R0={1,2,3}
R1={0,2,3}
R2={0,1,3}
R3={0,1,2}
R4={0,1,2}
```

Their column sums are `(4,4,4,3,0)`.  Therefore this assignment must satisfy
the row-exact-3 block and fail the column-exact-3 block.  Its transpose must
fail rows and satisfy columns.  The circulant supports

```text
Rv={v+1,v+2,v+3 mod 5}
```

have zero diagonal and all row and column sums equal to three, so they must
satisfy both blocks.  Together these three fixtures catch omitted, duplicated,
or transposed ledger families.

### 7.6 Symmetry relabelling test

Given any complete orientation assignment with `X(2,0)=true`, relabel every
vertex, arc, and auxiliary index by `f(i)=2-i mod 19`.  A static checker must
confirm:

1. all and only the same 19 cycle pairs remain missing;
2. the transformed assignment has `X(0,2)=true`;
3. every transformed `p`, `reach`, and `z` value is the relabelled original
   value; and
4. all row and column sums are preserved.

This test validates the single symmetry unit without asserting that any
additional canonicalization is safe.

## 8. Frozen audit checklist

With the full arrays and the subset-cardinality encoding above, apply the
stated structural reductions to the `p` and `z` gates but retain all 19 `p`
inputs in every `reach` gate.  The resulting reference fingerprint is:

| Family | Variables | Clauses |
|---|---:|---:|
| orientation | 152 | 0 structural clauses |
| `p` | 6,859 | 16,587 |
| `reach` | 361 | 7,220 |
| `z` | 361 | 1,007 |
| degree exactly 8 | 0 auxiliary | 434,720 |
| row/column exactly 3 | 0 auxiliary | 122,094 |
| symmetry | 0 | 1 |
| **total** | **7,733** | **581,629** |

For the `p` count, 4,864 triples have two structurally present steps and use
three clauses; the other 1,995 triples simplify to a unit-negative clause.
For `z`, 304 present off-diagonal directions use three clauses, 38 missing
directions use two after folding, and 19 diagonals use one unit each.  An
optimized cardinality encoder will intentionally have different totals, but
the full reference build should match this table exactly.

Before a production solve, an implementation audit should establish all of
the following against this document:

- exactly 152 orientation variables, with the literal map sampled in both
  signs;
- both directions of all 19 missing pairs, including `{18,0}`, are constant
  false;
- every nonconstant `p` has all three AND directions, with signed inputs, and
  every structurally false `p` is unit negative;
- every `reach` has every short implication and its complete reverse OR;
- every present off-diagonal `z` has all three clauses, every missing
  direction has the exact two-clause reduction, and every diagonal `z` is
  unit false;
- 19 exact-degree-8 constraints over 16 signed literals each;
- 19 source-row and 19 target-column exact-3 constraints over 18 `z`
  variables each;
- the only symmetry clause is the signed unit `X(0,2)`; and
- every calibration in Section 7 has the stated SAT/UNSAT truth-table result.

Generator agreement with this frozen specification is necessary before any
solve.  It is not itself evidence of SAT, UNSAT, or an SSNC result.
