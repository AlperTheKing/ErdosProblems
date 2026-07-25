# General KTT Proof Workflow — Direct Route Registry V2

Selected: 2026-07-22
Status: ACTIVE; supersedes `APPROACH_REGISTRY_GENERAL_KTT.md`.
Language: English for all internal plans, agent prompts, code, and artifacts.

## Exact target

For every nonzero Littlewood--Richardson triple `(lambda, mu, nu)` in every
rank, prove that

```text
P(n) = c(n nu; n lambda, n mu)
```

has nonnegative coefficients in the ordinary monomial basis.  If false,
produce one independently verified exact counterexample certificate.

## Definitions that must not be conflated

Let `H` be one hive polytope in its intrinsic lattice and let `Sigma_H` be its
**complete normal fan**.

For fixed `q`, let `Sigma_H(q)` be its `q`-dimensional cones.  Fix primitive
quotient-lattice orientations at every incidence.  The Minkowski boundary
matrix

```text
B_{H,q} : Q^{Sigma_H(q)} -> E_{H,q}
```

encodes the balancing equations at all `(q-1)`-dimensional cones.  Define

```text
W_{H,q} = {w in Q^{Sigma_H(q)} : w >= 0 and B_{H,q} w = 0}.
```

This is the cone of **all nonnegative balanced weights**.  It is not, in
general, the cone of weights realizable as face volumes of hive polytopes.
The actual face-volume vector is one distinguished element of `W_{H,q}`.

A flat-rhombus coarsening labels an individual cone or star in `Sigma_H`; it
is not itself a complete fan.  A Farkas certificate cannot be attached to one
local cone without specifying its complete fan and incidence data.

## DIRECT ROUTE A — GLOBAL HIVE TODD EFFECTIVITY

### 1. Exact final deliverable

A rank-uniform proof of full KTT for every rank, intrinsic dimension, and
coefficient.  A fixed-rank or fixed-codimension certificate cascade is not a
deliverable.

### 2. Current frontier lemma

`GLOBAL-HIVE-TODD-EFFECTIVITY (GHTE)`.  For every hive polytope `H` and every
`q`, let `a_{H,q}` be the vector of Berline--Vergne weights on
`Sigma_H(q)`.  Prove that there exists a rational vector `y` such that

```text
a_{H,q} + B_{H,q}^T y >= 0.                            (GHTE)
```

Equivalently, prove

```text
<a_{H,q}, w> >= 0  for every w in W_{H,q}.
```

### 3. Explicit logical bridge

Rational Farkas duality gives the displayed equivalence.  The normalized
face-volume vector of `H` is nonnegative and satisfies the Minkowski
balancing equations, hence lies in `W_{H,q}`.  Its pairing with `a_{H,q}` is
the relevant Ehrhart coefficient by local Euler--Maclaurin.  Polynomiality
and denominator clearing transfer the lattice formula to rational hive PIPs.
Therefore GHTE proves every KTT coefficient nonnegative.

### 4. Next falsifiable action

Before any ear induction, construct and independently verify the exact data
contract for one complete hive normal fan:

1. primitive quotient lattices and oriented incidence numbers;
2. the matrix `B_{H,q}` and a direct check that the actual face-volume vector
   lies in its kernel;
3. the BV vector `a_{H,q}` in the same cone ordering; and
4. exact Farkas primal/dual certificates.

Then formulate a deletion as a map of **complete fans** with explicit chain
maps and lattice maps.  A local planar move is admissible for GHTE only if it
extends to these complete-fan data and gives a rank-independent lift of
balanced weights plus a nonnegative Todd correction.

Small examples are definition and falsification gates only, never the proof.

### 5. Exit condition

Declare

```text
DEAD: complete-fan deletion does not imply GHTE — <exact obstruction>
```

if an exact complete fan has a nonnegative balanced weight with negative Todd
pairing, or if the deletion cannot be defined with compatible intrinsic
lattice and chain maps, or if the required move family grows with rank.

A negative balanced weight refutes GHTE but does **not** refute KTT unless it
is independently shown to be the actual face-volume weight of a hive
polytope.  Preserve this distinction.

## DIRECT ROUTE B — STRONG LOCAL CLOSED-CONE POSITIVITY

### 1. Exact final deliverable

The stronger rank-uniform theorem

```text
alpha^BV(N_F H) >= 0
```

for every face `F` of every hive polytope `H`, in the intrinsic quotient
lattice and the fixed BV complement map.

### 2. Current frontier lemma

`CLOSED-CONE-DELETION`.  Every actual closed hive normal cone admits a
rank-reducing planar deletion for which its BV value equals the smaller cone's
value plus a finite rank-independent family of explicitly nonnegative local
corrections.

### 3. Explicit logical bridge

The Ehrhart coefficient is the sum of these local BV values multiplied by
positive normalized face volumes.  Pointwise closed-cone positivity therefore
implies KTT directly, without a global Farkas shift.

### 4. Next falsifiable action

Give a finite definition of an actual closed normal cone: its primitive tight
rhombus rays, all exact nonnegative slack-closure implications, its intrinsic
quotient lattice, and its BV complement data.  Define one boundary ear/strip
deletion including the induced lattice map.  Derive its exact valuation
identity, or exhibit two cones with the same local combinatorial ear but
incompatible lattice corrections.

### 5. Exit condition

An actual closed hive normal cone with negative exact BV value kills Route B
but leaves Route A open.  A merely negative subdivision cell does not kill
Route B.  An undefined or rank-growing deletion also kills this induction
route.  Do not replace it with a fixed-codimension census.

## Counterexample alternative

A KTT counterexample requires an actual partition triple and an exact
stretching polynomial with a negative coefficient, recomputed by two
independent counting engines through the degree bound plus two held-out
dilations.  A negative local cone or a negative abstract balanced weight is
only a proof-route obstruction unless its face-volume realization is proved.

## Immediate workflow lanes

1. **Foundation lane:** build and verify the complete-fan chain/lattice data
   contract and the GHTE-to-KTT bridge.
2. **Strong local lane:** define one exact closed-cone deletion and derive or
   refute its BV correction identity.
3. **Adversarial lane:** reject every computation lacking the complete-fan or
   closed-cone input contract; search only for exact route obstructions.
4. **Root referee lane:** preserve the distinction among negative cells,
   negative closed cones, negative balanced weights, and actual negative
   Ehrhart coefficients.

## Known completed inputs

See `GENERAL_KTT_PROOF_STATUS.md`.  In particular, side size at most four is
proved; the top four full-dimensional coefficients are rank-uniformly
positive; full-dimensional side five has positive quadratic coefficient; and
the previously audited generic flow, Hilbert, matroid, tableau, and type-A
Todd shortcuts do not establish GHTE.
