# KTT Stretched-LR Negativity Hunt — Approach Registry

> **Current general-KTT workflow (2026-07-22):**
> `APPROACH_REGISTRY_GENERAL_KTT_V3.md` is the active direct-proof registry.
> It supersedes the older `DIRECT ROUTE FULL POSITIVITY` sections below.

Selected: 2026-07-21 (user-directed 64-agent / ~8-hour swarm campaign)
Status: ACTIVE

## Exact target

For partitions lam, mu, nu with |lam|+|mu|=|nu|, let c(nu; lam, mu) be the
Littlewood-Richardson coefficient (coefficient of s_nu in s_lam * s_mu), and
let P(n) = c(n*nu; n*lam, n*mu). Derksen-Weyman: P is a polynomial in n.
King-Tollu-Toumazet (2004) conjectured all coefficients of P (in the monomial
basis n^k) are nonnegative.

TARGET (= FrontierMath open-problem statement): exhibit one triple
(lam, mu, nu) such that P has at least one strictly negative coefficient.

## DIRECT ROUTE

### 1. Exact final deliverable

One triple + the exact interpolated polynomial P over Q + the full sample
table c(n*nu; n*lam, n*mu) for n = 0..D+2 computed EXACTLY by two independent
engines + verification at two extra points beyond the assumed degree bound.
This is a finite, machine-checkable certificate; FrontierMath has an external
verifier. A NO_HIT sweep proves nothing and is recorded as such.

### 2. Current frontier lemma / finite certificate

`KTT-CE`: a single negative coefficient in one exactly-interpolated stretched
LR polynomial. Degree bound: with r = len(nu), deg P <= (r-1)(r-2)/2 (hive
polytope dimension). Sample n = 0..D, interpolate exactly, then MANDATORY
check at n = D+1, D+2 (mismatch = DEGREE_ANOMALY, never a hit).

### 3. Explicit logical bridge

Knutson-Tao hive theorem: c(nu; lam, mu) = #integer hives with boundary given
by partial sums of lam, mu, nu (triangle side r). Stretching dilates the hive
polytope, so P is its Ehrhart polynomial (a genuine polynomial by
Derksen-Weyman), and any exact interpolation certified at D+2 points equals P.
A negative coefficient in P refutes the KTT positivity conjecture outright.
Known dead zones (engine validators, not hunt targets): c=1 => P==1 (KTW /
Fulton), c=2 => P=n+1 (Ikenmeyer; Sherman). Hunt bias: thin-but-high-
dimensional hive polytopes (small P(n) values, dimension >= 6), i.e. c in
[3,12], r in {5,6,7}, |nu| <= 60 — Ehrhart negativity lives in spiky
low-volume polytopes (Reeve-type phenomenon).

### 4. Next falsifiable action

Launch workflow `ktt-lr-negativity-hunt`: 2 independent exact engines
(C++ hive DFS counter with abort-cap; independent LR-rule tableau counter) +
cross-calibration gate (300 random triples r<=5 + c=1/c=2 stretched
validators; any disagreement aborts) + 4 waves x 14 family hunters
(adaptive: dead-family registry passed between waves) + adversarial
verification of every candidate hit by fresh agents recomputing all samples
with both engines and re-interpolating independently. ~64 agents, ~8h wall.
Artifacts under problems_external/ktt_lr_negativity/{engine,runs}/.

### 5. Exit condition

Stop on first CONFIRMED hit (then package HIT_CERTIFICATE.md + notify user;
submission decisions are the user's). Otherwise stop at wave-4 end or ~8h:
record NO_HIT with the dead-family registry and per-wave triple counts.
No restricted-family failure is evidence for the conjecture; no claim is made
from heuristic absence. Kill any engine lane on calibration disagreement.

## Novelty gate snapshot (2026-07-21)

- No published counterexample or claim found (web sweep 2026-07-21; FrontierMath
  lists the problem as open, "Major advance" tier, added Feb 2026).
- Polynomiality: Derksen-Weyman; short proof arXiv:2211.06810.
- c=2 theorem: Ikenmeyer (combinatorial), Sherman (arXiv:1505.06551 geometric).
- KTT source: King-Tollu-Toumazet, "Stretched Littlewood-Richardson and
  Kostka coefficients" (2004).

## DIRECT ROUTE R4 POSITIVITY

### 1. Exact final deliverable

A theorem, with a finite independently checkable certificate, that for every
triple of partitions `lambda, mu, nu` of length at most four, every coefficient
of the stretched Littlewood-Richardson polynomial
`c(t*nu; t*lambda, t*mu)` is nonnegative.

### 2. Current frontier lemma / finite certificate

For the 15 primitive facet normals of a size-four hive, let `B` be the
facet-boundary closure map on the 99 nonparallel normal pairs.  The frontier
certificate consists of `rank(B)=27`, 72 genuine integral 3-polytopes whose
edge-length vectors have rank 72 and lie in `ker(B)`, and a rational vector
`mu >= 0` satisfying `M*mu=a1` on those 72 witnesses.  The generated artifact
is `r4_reeve/q2_basis_witness_certificate.json`; the independent standard-
library replay currently returns `PASS`, SHA-256
`c13f8f47dcaa907f4e80616cb88f847d4790113938227ede26c6fe11b6ce0148`.

### 3. Explicit logical bridge

Buch states that every corner of a size-`n` hive polytope with integral border
is integral for `n <= 4`; hence the size-four hive is a lattice polytope.
Dimensions at most two are Ehrhart-positive by the segment formula and Pick's
theorem.  In dimension three, McMullen's edge-local formula makes `a1` a linear
functional of the 99 edge-length coordinates.  Every such length vector is in
`ker(B)` by polygonal closure on each facet.  Since the 72 witness rows span
`ker(B)` and `M*mu=a1` with `mu >= 0`, every size-four hive has
`a1=Lambda*mu >= 0`; the leading, quadratic, and constant coefficients are
automatically positive.  Equivalently, `V <= 3(c+i)`.

### 4. Next falsifiable action

Run `python r4_reeve/q2_make_basis_certificate.py` only when regenerating a
fresh non-overwriting artifact, then run the independent checker
`python r4_reeve/q2_verify_basis_certificate.py`.  Audit the theorem draft
against Buch's exact size convention and a primary statement of McMullen's
formula; have an adversarial referee try to invalidate the closure orientation,
rank calculation, witness provenance, or the passage from basis rows to all
hive polytopes.

### 5. Exit condition

Kill this route if Buch's `n <= 4` does not match the three-variable hive used
here, if independent replay fails, if `rank(B) != 27`, if the witness rank is
less than 72, if any witness is nonlattice or has a wrong Ehrhart coefficient,
if any component of `mu` is negative, or if McMullen locality does not use the
same 99 edge-type coordinates.  A census or an unverified fitted vector is not
a substitute.  The separate smooth/unimodular-cone shortcut is DEAD because
smooth lattice 3-polytopes with negative Ehrhart coefficients are known.

## DIRECT ROUTE FULL POSITIVITY

### 1. Exact final deliverable

A rank-uniform proof of the full King--Tollu--Toumazet coefficientwise
positivity conjecture for all partition lengths.  A finite cascade of fixed-rank
certificates is not a deliverable.

### 2. Current frontier lemma / finite certificate

`UNIFORM-HIVE-LOCALITY`: on every homogenized integer hive cone, every
potentially negative monomial Ehrhart coefficient has a nonnegative face-local
representative built from finitely many rank-independent rhombus stencils.

### 3. Explicit logical bridge

Apply local Euler--Maclaurin to the homogenized hive cone.  If each relevant
coefficient is the sum of the `UNIFORM-HIVE-LOCALITY` stencil weights against
nonnegative relative face measures, then every monomial coefficient of every
stretched Littlewood--Richardson polynomial is nonnegative in every rank.

### 4. Next falsifiable action

At `r=5` (`d=6`), compute the exact local terms for every coefficient that can
be negative, including all boundary residue classes, and test whether one
rank-independent finite rhombus-stencil rule represents them consistently.

### 5. Exit condition

Declare `DEAD: no uniform bridge` on the first inconsistent local assignment,
essential periodic boundary dependence, or rule requiring a rank-only lookup.
Do not continue to an `r=6` certificate cascade after any such failure.

## DIRECT ROUTE FULL POSITIVITY -- TABLEAU DECOMPOSITION

### 1. Exact final deliverable

A rank-uniform proof of the full King--Tollu--Toumazet coefficientwise
positivity conjecture for all partition lengths.  A finite cascade of fixed-rank
certificates is not a deliverable.

### 2. Current frontier lemma / finite certificate

`UNIFORM-TABLEAU-DECOMPOSITION`: every fixed-content Littlewood--Richardson
tableau family admits a rank-uniform disjoint decomposition into products of
order-map families on ideals or filters of the skew shape, with the stretch
parameter `n` occurring only in nonnegative markings.

### 3. Explicit logical bridge

Jochemko--Menon Proposition 2.1 and Theorem 1.3 give nonnegative multivariate
polynomials for the resulting marked order-map families.  Nonnegative sums,
products, and substitution of markings by `n` times nonnegative slacks preserve
monomial coefficientwise positivity, hence so does every stretched
Littlewood--Richardson polynomial.

### 4. Next falsifiable action

For the `r=5` half-integral hive family
`lambda=(2,2,1)`, `mu=(k,3,2,1)`,
`nu=(k+1,4,3,2,1)`, test whether its content-and-lattice-word fiber admits the
stated disjoint order-map decomposition with an `n`-independent poset.

### 5. Exit condition

Declare `DEAD: no tableau bridge` if enforcing fixed content requires diagonal
coefficient extraction, signed inclusion--exclusion, or an `n`-dependent poset.
Do not continue to a fixed-rank certificate cascade after any such failure.
