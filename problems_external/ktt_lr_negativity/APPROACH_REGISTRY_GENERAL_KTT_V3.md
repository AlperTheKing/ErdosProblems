# General KTT Proof Workflow — Direct Route Registry V3

Selected: 2026-07-22
Status: ACTIVE; supersedes V1 and V2.
Language: English for every internal plan, agent prompt, code path, checker,
and research artifact. User-facing discussion may be Turkish.

## Exact target

For every nonzero Littlewood--Richardson triple in every rank, prove that the
ordinary monomial coefficients of

```text
P(n) = c(n nu; n lambda, n mu)
```

are nonnegative. If the assertion is false, produce one partition triple and
an exact stretching-polynomial certificate independently replayed by two
counting engines.

## DIRECT ROUTE — GLOBAL HIVE TODD EFFECTIVITY

### 1. Exact final deliverable

A rank-uniform proof of full KTT for every rank, intrinsic dimension, and
coefficient. A fixed-rank certificate cascade or a finite negative census is
not a deliverable.

### 2. Current frontier lemma

`GLOBAL-HIVE-TODD-EFFECTIVITY (GHTE)`. For every nonempty hive polytope `H`,
work in its saturated intrinsic tangent lattice. For every `q`, let
`Sigma_H(q)` be the `q`-cones of its complete normal fan, let `B_{H,q}` be the
primitive quotient-lattice balancing matrix, and let `a_{H,q}` be the matching
Berline--Vergne vector. Prove

```text
there exists y in Q^rows(B) with
a_{H,q} + B_{H,q}^T y >= 0.                           (GHTE)
```

Equivalently, prove that the Todd pairing is nonnegative on every
nonnegative balanced weight of the complete fan.

### 3. Explicit logical bridge

The normalized face-volume vector `v_{H,q}` is nonnegative and satisfies
`B_{H,q} v_{H,q}=0` by lattice Minkowski equilibrium in every face. Rational
Farkas duality turns GHTE into

```text
<a_{H,q}, w> >= 0 for all w >= 0 with B_{H,q}w=0.
```

Local Euler--Maclaurin identifies `<a_{H,q},v_{H,q}>` with the coefficient of
`n^(dim(H)-q)` in the Ehrhart polynomial. Denominator clearing transfers the
lattice statement to rational period-one hive polytopes. Thus GHTE in every
`q` implies full KTT.

The exact definitions and checker contract are in
`GHTE_FOUNDATION_CONTRACT.md`. They must be verified in the saturated
intrinsic lattice before this bridge is used.

### 4. Completed falsifiable action and route decision

The two definition gates and the exact primitive hive wall have now been
replayed. Refinement descent is valid, but all three canonical upward moves
on that wall are obstructed: actual-volume propagation, graph correspondence,
and pullback to every smooth common refinement. The artifacts are listed in
the DEAD routes below.

The single authorized non-cascading GHTE falsification gate used the smooth
full-dimensional side-five hive

```text
lambda=(16,13,10,4,1), mu=(13,9,4,1,0),
nu=(27,22,13,5,4).
```

It returned `PASS` in every `q=0,...,6`, independently.  At `q=5`, the exact
primitive matrix has shape `136 x 48` and rank `46`; the independent effective
Todd representative is

```text
td_5=(11/6)[V(0,1,2,3,4)]+(59/20)[V(0,1,2,3,5)].
```

The exact linear coefficient is `287/60`.  The root and zero-trust artifacts
are `ghte_r5_full_dim_smooth_audit.py`,
`GHTE_R5_FULL_DIM_SMOOTH_ZERO_TRUST_AUDIT.md`, and
`ghte_r5_full_dim_smooth_zero_trust_audit.py`.  This is one finite validation
fact only.  It supplies no rank-uniform bridge and does not authorize another
fan or codimension cascade.

A future GHTE proof route requires a new hive-specific rank-uniform
effectivity theorem which does not lift certificates by any of the three
obstructed wall maps. Merely constructing larger common refinements is not an
authorized next step.  The wall-transport implementation is therefore closed
under the exit record

```text
DEAD: complete-fan transport has no rank-uniform bridge -- actual-volume,
graph, common-refinement pullback, and actual star-subdivision pullback each
have an exact negative correction separated from the effective cone.
```

This does not assert that GHTE is false.  It means GHTE is retained only as an
open sufficient theorem statement, not as an active attack lacking a new
rank-uniform falsifiable mechanism.

### 5. Exit condition

Declare

```text
DEAD: GHTE is false — <exact complete-fan balanced witness>
```

if some complete hive normal fan admits `w>=0`, `Bw=0`, and `<a,w><0`.
This kills GHTE but does not refute KTT unless `w` is the actual face-volume
vector of a hive polytope.

Declare

```text
DEAD: complete-fan transport has no rank-uniform bridge — <exact obstruction>
```

if every candidate complete-fan move requires rank-growing data or fails an
exact chain/lattice identity. Do not continue with an unbounded cascade of
fixed ranks or codimensions. A new direct route then requires a new registry.

## COUNTEREXAMPLE ALTERNATIVE

The falsifiable theorem-level alternative remains a genuine KTT
counterexample: an actual partition triple whose exact stretching polynomial
has a negative monomial coefficient. It must be recomputed by two independent
counting engines through the degree bound and at two held-out dilations. A
negative subdivision cell, closed cone, or abstract balanced weight is not a
KTT counterexample.

### Dilation-compatible skew-Kostka gate

`KOSTKA_TO_LR_HOMOGENEOUS_BRIDGE.md` proves an exact homogeneous embedding

```text
K_(n lambda / n beta, n w) = c^(n R)_(n lambda,n S)
```

for explicitly constructed partitions `R,S`. Therefore one negative
coefficient in a stretched skew-Kostka polynomial would be a literal KTT
counterexample. One bounded exact gate is authorized by that document. It
must stop at its stated exit condition; it may not become an unbounded census
cascade. The public 2026 `kostka` code is treated only as an untrusted candidate
engine until its degree/interpolation path passes the `P(0)=1` and held-out
checks.

The exact no-pruning census for side five and `|nu|=27..30` is queued after
the prior hive-engine jobs. Together with the completed `|nu|<=26` census it
tests the full side-five weight range in the FrontierMath statement. Its
null result, if any, will remain a finite result and not evidence for general
KTT.

## DEAD ROUTE — CANONICAL LOCAL EAR/STRIP DELETION

The V2 `CLOSED-CONE-DELETION` route is dead in its canonical planar form.

For the actual side-four hive

```text
lambda=mu=(3,2,1,0), nu=(5,4,2,1),
```

the closed edge cone generated by adjacent strip normals has Gram matrix
`((2,1),(1,2))` and BV value `1/6`. The literal deletion has correction
`-1/3`; even the natural one-dimensional fibre normalization gives `-1/12`.
The induced integral strip map also fails to preserve the BV orthogonal
complement.

Independently, the same labelled boundary rhombus `A(1,1)` occurs in two
actual closed side-four cones with primitive quotient multiplicities two and
one. Hence a planar ear label does not determine the saturated lattice
correction. Boundary-strip restriction also exposes `r-2` variable interface
coordinates, so it does not land in one fixed-boundary smaller hive.

Replayable artifacts:

```text
CLOSED_CONE_EAR_DELETION_OBSTRUCTION.md
closed_cone_ear_deletion_obstruction.py
closed_cone_strip_lattice_map.py
CLOSED_CONE_BOUNDARY_DELETION_AUDIT.md
closed_cone_boundary_ear_pair.py
```

These facts kill the canonical local deletion proof, not pointwise closed-
cone positivity, GHTE, or KTT. A different local route would need a new exact
frontier lemma carrying the full saturated closed-cone and variable-interface
data.

## DEAD ROUTE — CANONICAL COMMON/MASTER-REFINEMENT TRANSPORT

The canonical coarsest common refinement of the exact primitive side-four
`2<->2` hive flip is the smooth star subdivision with ray
`e=a+d=b+c`. In codimension two its Todd class is effective, but the two
canonical upward pullbacks satisfy

```text
td_2(W)-p_L^*td_2(L) = -1/6[V(ae)],
td_2(W)-p_R^*td_2(R) = -1/6[V(be)].
```

An exact strictly positive balanced weight pairs to `-1/6` with both
corrections, so neither is effective modulo balancing. The same contradiction
persists after any further smooth common refinement by Todd pushforward and
the projection formula. Thus iterated common refinement cannot transport
GHTE certificates upward by canonical pullback plus a nonnegative correction.

Replayable artifacts:

```text
GHTE_MASTER_REFINEMENT_TRANSPORT_AUDIT.md
ghte_master_refinement_transport_audit.py
GHTE_UNIT_CREPANT_FLIP_TODD_OBSTRUCTION.md
ghte_unit_crepant_flip_todd_audit.py
```

This does not refute GHTE: the audited common fan is itself effective. A
master-fan route would now require a new direct rank-uniform theorem proving
effectivity of the master independently of every adjacent fan. Without such
a theorem, iterating rank-growing refinements has no bridge to the final
deliverable and is stopped by the DIRECT-PROOF GUARD.

The obstruction is not confined to facet-preserving `2<->2` flips.  An actual
side-four facet-birth wall has the primitive saturated-link circuit

```text
a+b=c
```

and the refined fan is the star subdivision along `c`.  Its complete Todd
pullback corrections are

```text
t_q(refined)-pi^*t_q(coarse)=(0,-[D_c]/2,-(5/6)[V(cu)],0).
```

Strictly positive balanced weights separate both nonzero corrections from the
effective cone.  Both endpoint fans satisfy GHTE independently, so this again
kills canonical upward transport rather than GHTE itself.  It also proves that
a rank-uniform wall theorem cannot assume every actual support wall is a unit
`2<->2` circuit.  Replayable artifacts are
`HIVE_WALL_CIRCUIT_CLASSIFICATION.md`,
`verify_smallest_actual_hive_wall.py`,
`GHTE_ACTUAL_STAR_SUBDIVISION_TODD_OBSTRUCTION.md`, and
`ghte_actual_star_subdivision_todd_audit.py`.

## Scope guard

The currently established theorem remains length at most four. The full KTT
conjecture is not proved. Known fixed-rank and top-coefficient results are
inputs and validation gates only; they are not the rank-uniform bridge.
