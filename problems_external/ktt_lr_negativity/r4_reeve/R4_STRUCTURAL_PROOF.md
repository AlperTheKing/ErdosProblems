# Structural proof of KTT positivity in rank at most four

## Theorem

For every triple of partitions of length at most four, every monomial
coefficient of the stretched Littlewood--Richardson polynomial is
nonnegative.

This proof uses only polynomiality, the hive model, the local Ehrhart formula,
and the four-point shape of a rhombus row.  It does not require vertex
integrality or the 72-witness edge-balance certificate.

## Proof

If the unstretched Littlewood--Richardson coefficient is zero, saturation
implies that every positive stretch is zero, so the stretched polynomial is
identically zero.  Suppose henceforth that the hive polytope `H` is nonempty.

For rank at most four, the standard interior-coordinate space has dimension
at most three.  Let `delta=dim(H)`.  The stretched coefficient is the ordinary
polynomial lattice count of the rational polytope `H`.

For any rational polytope with polynomial lattice count, choose `q` such that
`qH` is a lattice polytope.  Since

```text
L_(qH)(n)=L_H(qn),
```

the coefficient of degree `k` for `qH` is `q^k` times that for `H`.
Consequently the usual lattice formulas imply coefficientwise positivity in
dimensions zero, one, and two: a point gives `1`, a segment gives lattice
length times `n` plus `1`, and a lattice polygon gives normalized area times
`n^2`, half the boundary lattice length times `n`, plus `1`.

It remains to treat `delta=3`, which can occur only in rank four.  Write

```text
L_H(n)=a_3 n^3+a_2 n^2+a_1 n+a_0.
```

The leading coefficient `a_3` is normalized volume and is positive.  The
coefficient `a_2` is half the normalized boundary area and is positive, by
the same scaling argument.  Nonemptiness and scaling to `qH` give `a_0=1`.

For `a_1`, use the codimension-two local formula.  Every primitive rank-four
rhombus normal has entries in `{0,1,-1}`.  Every edge is a ridge and hence is
contained in exactly two facets; its transverse feasible cone is therefore
determined by two nonparallel rhombus normals.  The rank-uniform theorem in
`UNIFORM_CODIM2_POSITIVITY.md` proves that the Berline--Vergne constant of
each such feasible cone is at least `1/12`.  Thus

```text
a_1
  = sum_edges(E) alpha(T(H,E)) length_Z(E)
  >= (1/12) sum_edges(E) length_Z(E)
  > 0.
```

The formula remains valid for rational `H`: apply it to `qH`, observe that
edge lengths and `a_1` both scale by `q`, and divide by `q`.

All four coefficients are therefore positive for a nonempty
three-dimensional rank-four hive.  Together with the lower-dimensional and
zero cases, this proves the theorem.

## Independent rank-four local audit

The rank-four normal atlas has 15 primitive normals and 99 nonparallel pairs.
Exact saturated-lattice evaluation gives

```text
saturation index 1: 96 pairs
saturation index 2:  3 pairs
minimum alpha:      1/9
```

Each index-two pair has alpha `5/18`.  Thus the atlas sharpens `1/12` to
`1/9`, although the sharper number is not needed for the proof.

## Why nonsimple vertices do not obstruct the proof

The verified vertex with primitive tangent rays

```text
(0,1,1), (1,0,1), (1,1,0)
```

has tangent determinant two and six tight rhombus inequalities.  This does
not affect the argument.  The coefficient `a_1` is local on edges, not
vertices.  In every three-dimensional convex polytope, each edge is a ridge
and lies in exactly two facets.  Additional rhombus rows tight along an edge
are redundant or lie inside its two-dimensional normal cone; the two extreme
facet normals still give precisely the feasible cone evaluated above.

The normal-versus-feasible sign is also fixed explicitly: in a saturated
normal basis with Gram matrix `[[A,C],[C,B]]`, the two inward feasible rays
have inverse Gram matrix with off-diagonal entry `-C/(AB-C^2)`.  Hence

```text
alpha = 1/4 - (C/12)(1/A+1/B),
```

not the same expression with a plus sign on the outward-normal inner product.
