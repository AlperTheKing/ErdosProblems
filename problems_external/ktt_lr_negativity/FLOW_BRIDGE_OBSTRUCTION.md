# Hive-flow / Lidskii bridge: exact obstruction

## Verdict

The Buergisser--Ikenmeyer hive-flow model is a lattice isomorphism of the
**ambient linear spaces**, but it does not identify a hive polytope with an
ordinary network-flow polytope.  In fact, a verified full-dimensional size-four
hive polytope is not lattice-affinely equivalent to any ordinary network-flow
polytope, and one of its tangent cones is not lattice-equivalent to any ordinary
network-flow cone.  Therefore the Baldoni--Vergne--Lidskii formula cannot be
transferred to all hives by this route.

This is an obstruction to the proposed bridge, not a counterexample to KTT.

## 1. What the hive-flow isomorphism actually says

Let `H` be hive vertex labels with the top label fixed to zero, and let `Z` be
the closed throughput functions on the edges of the triangular grid.  In
Section 2.2 of Buergisser--Ikenmeyer, the coboundary map

```
partial : H -> Z,  h |-> (h(k+) - h(k-))_k
```

is a real linear isomorphism and restricts to a lattice isomorphism
`H_Z -> Z_Z`.  Via throughput coordinates, `Z_Z` is the lattice of flow
classes `F(G)_Z` on their bidirected honeycomb graph.  Thus the lattice is
tracked exactly.

The inequalities are not lost under this map.  A flow class is a **hive flow**
only when every rhombus slack satisfies

```
sigma_rho(f) >= 0.
```

These are additional linear inequalities on flow classes; they are not the
coordinate nonnegativity constraints of an ordinary flow polytope.  Indeed,
Buergisser--Ikenmeyer Observation 3.3 exhibits complete path flows with
negative rhombus contribution, and Example 4.5 gives a turnpath with slack
`-4`.

For boundary data `(lambda,mu,nu)`, their bounded-flow polytope `B` adds box
constraints only on boundary throughputs.  The capacity-achieving polytope `P`
sets **every** such boundary throughput equal to its capacity.  Consequently,
`P` is precisely the fixed-boundary hive polytope in flow-class coordinates,
but it still carries all the rhombus inequalities.  Stretching the boundary by
`t` dilates this same polytope and the ambient lattice is unchanged.

The residual graph does not repair this.  `R_f` depends on the chosen hive flow
`f` and its flat rhombi.  The paper constructs an integral linear map

```
pi : F(R_f) -> F(G),
```

but never an integral bijection.  The Rerouting Theorem replaces a feasible
direction by a nonnegative residual flow having the same flatspace boundary
weights; its stated corollary preserves overall throughput, not the direction
itself.  Hence this is an optimization device, not a lattice equivalence of
tangent cones and not an Ehrhart-preserving parametrization.

Primary source: [Buergisser--Ikenmeyer, arXiv:1204.2484](https://arxiv.org/pdf/1204.2484),
especially Sections 2.2--2.3 and 4.1--4.3.

## 2. A lattice obstruction for every ordinary network-flow model

### Lemma (simple network-flow vertices are smooth)

Let

```
Q = {x in R^E : A x = b,  x >= 0}
```

be an ordinary integral network-flow polytope, where `A` is a node--arc
incidence matrix.  More generally one may impose integral upper capacities
`x <= u`.  Relative to its intrinsic flow lattice, every simple vertex of `Q`
has a unimodular tangent cone.

### Proof

Delete coordinates fixed throughout `Q`, and work componentwise, so `Q` is
full-dimensional in `Ax=b`.  Choose a spanning forest `T`, delete one incidence
row in each component, and write the other arcs as `N`.  The square matrix
`A_T` is unimodular.  Projection to the non-tree coordinates identifies the
difference lattice `ker(A) intersect Z^E` with `Z^N`, since

```
x_T = -A_T^{-1} A_N x_N.
```

The resulting coordinate matrix

```
C = [ -A_T^{-1} A_N ]
    [       I_N        ]
```

is totally unimodular: `A_T^{-1}A_N` is the standard network matrix, and
adjoining identity rows preserves total unimodularity.  Thus in intrinsic
coordinates the facets of `Q` have normals among the rows of `C` (or among the
rows of `C` and `-C` when upper capacities are present).

At a simple `d`-dimensional vertex, choose the `d` independent primitive facet
normals.  They form a nonsingular `d` by `d` submatrix of this totally
unimodular matrix, so its determinant is `+1` or `-1`.  It is therefore a basis
of the dual lattice, and the primitive tangent rays form a basis of the primal
lattice.  The tangent cone is unimodular.  QED.

The same proof applies directly to a pointed simplicial ordinary network-flow
cone.

## 3. Explicit hive refuter

Consider the size-four hive with

```
lambda = mu = (12,8,4,0),
nu = (18,14,10,6).
```

In the three internal hive coordinates (whose intrinsic lattice is `Z^3`), the
polytope is full-dimensional.  At

```
v = (26,32,38)
```

the primitive tangent rays are exactly

```
r1 = (0,1,1),  r2 = (1,0,1),  r3 = (1,1,0).
```

There are three rays, so the vertex is simple, but

```
abs(det[r1 r2 r3]) = 2.
```

Thus the cone has lattice multiplicity two.  Equivalently, the integral tangent
point `(1,1,1) = (r1+r2+r3)/2` lies in the cone but not in the semigroup freely
generated by its primitive rays.  By the lemma, neither this tangent cone nor
the hive polytope can be lattice-affinely equivalent to an ordinary network-flow
cone/polytope.

Independent replay:

```
python problems_external/ktt_lr_negativity/r4_reeve/audit_zero_trust_det2.py
```

The checker enumerates the 11 vertices and 50 lattice points, verifies `v`,
derives the three extreme rays from the tight rhombus rows, and returns
`primitive_ray_det=2`.

## 4. Lidskii positivity has a second scope obstruction

Even ordinary flow polytopes are not all Ehrhart-positive.  The
Baldoni--Vergne--Lidskii formula applies to acyclic directed graphs with a
nonnegative netflow vector, but its binomial summands are not coefficientwise
positive for arbitrary graphs.  A standard sufficient hypothesis is that every
non-sink vertex has indegree at most one; see Corollary 2.1.5 of
[Fu Liu's survey](https://arxiv.org/pdf/1711.09962).  The same survey records
non-Ehrhart-positive order polytopes that are unimodularly equivalent to planar
flow polytopes.  Hence even a hypothetical ordinary-flow representation would
still need a separate graph-structure theorem placing it in a positive Lidskii
subfamily.

The exact Lidskii hypotheses and formulas are in
[Meszaros--Morales, arXiv:1710.00701](https://arxiv.org/pdf/1710.00701), Theorem
1.1.

## Consequence for the all-rank proof

The direct route

```
hive-flow lattice isomorphism -> ordinary flow polytope -> Lidskii positivity
```

is dead.  A residual-flow extended formulation or a projection is not enough:
projection can create the index-two cone above, but it does not preserve the
intrinsic lattice-point count or Ehrhart polynomial.  Reviving a flow route
would require a new, rank-uniform **lattice-point bijection with singleton
fibres** (or a positive fibrewise generating-function identity) that also
incorporates every rhombus inequality.  Buergisser--Ikenmeyer's rerouting map
does not have this property.
