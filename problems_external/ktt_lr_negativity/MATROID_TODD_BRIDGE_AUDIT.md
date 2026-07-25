# Matroidal / secondary-fan Todd bridge audit

Date: 2026-07-22

## Verdict

No known graphic, cographic, regular-matroid, Bergman-fan, nested-set, or
secondary-fan theorem supplies the missing rank-uniform Todd positivity for
hive polytopes.  There are three independent scope obstructions.

1. The tight-rhombus row configuration is not even binary.  A genuine
   size-four hive face carries a `U_{2,4}` restriction, so the proposed
   graphic/cographic/regular identification is false as a statement about
   tight rows.
2. Matroid combinatorics omits the lattice indices and scalar-product data on
   which the Berline--Vergne local functional depends.  The determinant-two
   size-four hive cone already exhibits this missing arithmetic.
3. Even the much more special braid/permutohedral and matroid-polytope
   settings do not have a general effective Todd or Ehrhart-positivity
   theorem: permutohedral Todd effectivity fails in high dimension, and
   connected matroid base polytopes can have negative Ehrhart coefficients.

These are obstructions to the proposed *proof bridge*, not counterexamples to
KTT.  Pointwise nonnegativity of every **closed** hive normal cone remains a
hive-specific possible theorem.  Nothing matroidal found here proves it.

## 1. Exact non-binary tight-row obstruction

Four primitive normals in the size-four hive atlas are

```text
v1 = (-1,-1, 1)
v2 = (-1, 0, 0)
v3 = (-1, 1,-1)
v4 = ( 0,-1, 1).
```

They satisfy

```text
v1 = v2 + v4,       v3 = v2 - v4.
```

Their rank is two and every pair has rank two.  Hence their vector-matroid
restriction is `U_{2,4}`.  A two-dimensional vector space over `F_2` has only
three nonzero projective points, so `U_{2,4}` is not binary.  Graphic,
cographic and regular matroids are binary; therefore the complete hive-normal
matroid is none of these.

This is not merely an incompatible abstract subset.  The integral boundary

```text
lambda = (3,2,1,0)
mu     = (3,2,1,0)
nu     = (5,4,2,1)
```

defines a full-dimensional size-four hive.  It has the edge

```text
[(7,8,10), (7,9,11)]
```

on which exactly original rows `(2,7,9,10,11)` are tight.  Their distinct
normal directions are precisely `v1,v2,v3,v4` (row `v2` occurs twice).  Thus
the flat-rhombus coarsening itself has the displayed non-binary tight-row
matroid.

Exact replays:

```text
python hive_matroid_obstruction.py
python hive_matroid_face_search.py
```

The first script checks atlas membership, all six pair ranks, both displayed
relations, and the `U_{2,4}` conclusion.  The second exhaustively finds and
then exactly verifies the full-dimensional hive and its edge; it uses no
floating point.

There is an important limitation: in this edge cone some tight normals are
redundant as cone rays.  Thus this witness refutes a graphic/cographic theorem
about the complete tight-row coarsening, but does not prove that the matroid of
the *extreme rays of every closed normal cone* is non-binary.  Any proposed
extreme-ray theorem still needs a separate rank-uniform proof and the
arithmetic compatibility in the next section.

## 2. Matroid data do not determine the hive Todd weight

For

```text
lambda = mu = (12,8,4,0),
nu = (18,14,10,6),
```

the hive vertex `(26,32,38)` has primitive tangent rays

```text
(0,1,1), (1,0,1), (1,1,0)
```

of determinant two.  Their abstract vector matroid is the free matroid
`U_{3,3}`, exactly the same matroid as the unimodular coordinate orthant.
Nevertheless one cone has intrinsic lattice index two and the other index
one.  Berline--Vergne's local Euler--Maclaurin functional uses the rational
cone in its lattice together with the chosen complement/scalar product, not
only its independence matroid.

Consequently a Bergman/nested-set or secondary-fan correspondence at the
level of face posets, oriented matroids, or regular subdivisions cannot carry
the required Todd statement.  One would need an explicit lattice fan map
preserving the complement map and every local BV class.  No such map is
present: the determinant-two cone already rules out a unimodular fan
identification with the standard nested-set cones.

The same distinction explains the secondary-fan gap.  Gale/secondary theory
can encode which tight subsets occur while right-hand sides vary.  The normal
cone of an individual hive lives in the intrinsic hive dual lattice, and its
BV value retains arithmetic that a combinatorial regular subdivision forgets.

## 3. No generic matroid or braid-fan Todd-effectivity theorem

The strongest nearby primary results have the wrong conclusion.

* Feichtner--Sturmfels construct Bergman and nested-set fans from matroids and
  explain their relation, but do not identify hive normal fans with those
  fans or prove Todd effectivity:
  <https://arxiv.org/abs/math/0411260>.
* Castillo--Liu compute the Todd class of the permutohedral variety and prove
  that it is **not effective for dimension at least 24**.  They do prove the
  linear Ehrhart coefficient of every lattice generalized permutohedron is
  positive, but not all coefficients and not pointwise Todd positivity:
  <https://arxiv.org/abs/1909.09127>.
* Ferroni constructs connected matroids of every rank at least three whose
  base polytopes are not Ehrhart positive; these are also generalized
  permutohedra:
  <https://arxiv.org/abs/2105.04465>.
* The 2026 matroidal Hirzebruch--Riemann--Roch package constructs a Todd class
  for matroid building sets, but its theorem is a class identity/HRR formula,
  not effectivity or coefficientwise positivity:
  <https://arxiv.org/abs/2606.22650>.

Therefore even an exact proof that a hive fan is matroidal or a braid-fan
coarsening would not, by itself, prove KTT.

## 4. Exact surviving lemma

The matroid/secondary shortcut is dead.  The surviving direct route is the
hive-specific statement already isolated by the balancing audit.

For every rank, every codimension `q`, and every 2-connected
primitive-interior **closed flat-rhombus coarsening** `Sigma`, let `a_q` be the
vector of BV/Todd weights and let

```text
partial_q : Q^{Sigma(q)} -> E_q
```

be the Minkowski boundary map.  Prove

```text
a_q + partial_q^T y >= 0
```

for some rational `y`, uniformly in the rank and coarsening.  Equivalently,

```text
<a_q,w> >= 0
```

for every nonnegative balanced realizable face weight `w`.

Horn factorization handles separating boundary cases.  What is missing is a
rank-uniform generator or deletion theorem for the nonnegative balanced cone
of 2-connected primitive-interior hive coarsenings.  It must use forced
flat-rhombus closure and the intrinsic lattice; generic matroid, Bergman,
secondary-fan, or cocircuit balancing cannot supply it.

Continuing through fixed codimensions would not prove this lemma and would be
an unbounded certificate cascade.
