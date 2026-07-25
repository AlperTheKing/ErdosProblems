# KTT positivity for partitions of length at most four

## Theorem

Let `lambda`, `mu`, and `nu` be partitions of length at most four, with
`|lambda|+|mu|=|nu|`.  The polynomial which agrees, for every positive integer
`t`, with

```
c(t*nu; t*lambda, t*mu)
```

has no negative coefficient.

This is a computer-assisted proof.  Its only imported structural results are
the hive rule, Buch's integrality statement for size at most four, Ehrhart's
theorem and reciprocity, and the McMullen/Berline--Vergne local formula.

## 1. Reduction to one Ehrhart coefficient

If the unstretched Littlewood--Richardson coefficient is zero, saturation
implies that every positive stretch is zero, so the stretching polynomial is
zero.  Assume henceforth that it is positive.

Pad the three partitions with zeros to length four.  The hive rule identifies
the stretching polynomial with the Ehrhart polynomial of the size-four hive
polytope `Q`.  It has at most three free hive entries, so `dim(Q) <= 3`.
Buch states, immediately after Example 2 in *The saturation conjecture (after
A. Knutson and T. Tao)*, that for an integral border and hive size `n <= 4`,
every corner of the hive polytope is integral.  Thus `Q` is a lattice polytope.

Dimensions at most two are coefficientwise nonnegative by the point and
segment formulas and Pick's theorem.  In dimension three write

```
L_Q(t) = 1 + a1*t + a2*t^2 + a3*t^3.
```

Here `a3` is the lattice volume and `a2` is half the normalized boundary area,
so only `a1` requires proof.

## 2. The fixed normal set

Eliminating the boundary entries from the size-four rhombus inequalities,
in the three interior coordinates `(h_11,h_12,h_21)`, gives the following 15
distinct primitive possible outward facet normals:

```
( 1, 0, 0)  (-1, 1, 0)  (-1, 0, 0)  ( 0,-1, 0)  ( 1,-1, 0)
( 0, 1, 0)  (-1, 0, 1)  ( 1,-1,-1)  (-1, 1,-1)  (-1,-1, 1)
( 0,-1, 1)  ( 0, 0,-1)  ( 1, 0,-1)  ( 0, 1,-1)  ( 0, 0, 1).
```

Only the integral right-hand side changes with the three partitions.  Six of
the 105 unordered normal pairs are parallel, leaving 99 possible edge types.

## 3. Facet balancing

For a lattice 3-polytope `P` supported by these normals, let `Lambda_ij(P)` be
the total relative lattice length of edges incident with facets having normals
`n_i,n_j`.  For a nonparallel pair put

```
u_ij = primitive(n_i cross n_j).
```

Orienting the boundary of facet `i` by its outward normal, an edge shared with
facet `j` has direction `u_ij`.  Every facet is a lattice polygon and its
boundary closes.  Collecting the three closure equations for every facet
defines an integer matrix

```
B : Q^99 -> Q^45,       B*Lambda(P) = 0.
```

Exact rational elimination in the checker gives

```
rank(B)=27,             dim ker(B)=72.                 (1)
```

## 4. The nonnegative local functional

McMullen's local Ehrhart formula says that the coefficient of `t^k` is a sum,
over the `k`-faces, of relative face volume times a weight depending only on
the outer normal cone.  For `k=1` in dimension three, this gives a vector
`alpha in R^99` such that

```
a1(P) = Lambda(P) dot alpha.                            (2)
```

The certificate contains 72 actual integral 3-polytopes `P_1,...,P_72` with
the displayed normal set.  Let `M` be the matrix whose rows are their exact
edge-length vectors, and let `a` contain their exact linear Ehrhart
coefficients.  The independent replay reconstructs the inequalities and all
vertices, counts `L(0),...,L(5)`, reconstructs all genuine facets and edges,
and proves over `Q` that

```
M*B^T = 0,             rank(M)=72.                     (3)
```

Equations (1) and (3) imply

```
rowspan(M) = ker(B).                                    (4)
```

The same certificate contains `mu in Q^99` and the replay proves exactly that

```
mu >= 0 componentwise,          M*mu = a.               (5)
```

For the McMullen vector in (2), the witness identities give `M*alpha=a`.
Now let `P` be any lattice 3-polytope with these possible facet normals.
By balancing and (4), `Lambda(P)=y*M` for some rational row vector `y`.
Consequently

```
a1(P) = Lambda(P) dot alpha
      = y*M*alpha
      = y*a
      = y*M*mu
      = Lambda(P) dot mu
      >= 0,
```

because every edge length and every component of `mu` is nonnegative.  This
proves the theorem.

## 5. Equivalent volume inequality

For a 3-dimensional lattice polytope put

```
c = #(Q intersect Z^3),       i = #(interior(Q) intersect Z^3),
V = normalized volume(Q) = 6*a3.
```

Substituting `t=1,-1` and using Ehrhart reciprocity gives

```
6*a1 = 3*(c+i)-V.
```

Hence the proved sign statement is exactly

```
V <= 3*(c+i).
```

The bound was therefore not established by the earlier census; it follows
from the edge-local certificate above.

## 6. Exact replay

From the repository root run:

```powershell
python problems_external\ktt_lr_negativity\r4_reeve\q2_verify_r4_certificate.py
```

Expected output:

```
PASS
certificate_sha256=c13f8f47dcaa907f4e80616cb88f847d4790113938227ede26c6fe11b6ce0148
witnesses=72 witness_rank=72 balance_rank=27 kernel_dimension=72 min_mu=0
r4_normal_set=PASS
```

The deterministic generator was replayed to a second path and reproduced the
certificate byte for byte.

## 7. A discarded shortcut

The fixed normal matrix is not totally unimodular.  In particular, the hive
with `lambda=mu=(12,8,4,0)` and `nu=(18,14,10,6)` has an integral vertex
`(26,32,38)` whose primitive tangent rays are

```
(0,1,1), (1,0,1), (1,1,0),
```

of determinant two.  Thus the proposed route that excluded every
nonunimodular vertex cone is false.  Smoothness would not have sufficed either;
the proof uses the stronger fixed-normal balancing certificate.

## References used by the proof

- A. S. Buch, *The saturation conjecture (after A. Knutson and T. Tao)*,
  Enseign. Math. 46 (2000), Example 2 and the following paragraph.
- N. Berline and M. Vergne, *Local Euler--Maclaurin formula for polytopes*,
  Moscow Math. J. 7 (2007), 355--386.
- M. H. Ring and A. Schuermann, *Local formulas for Ehrhart coefficients from
  lattice tiles*, Mathematika 66 (2020), 1--31, Definition 1 and Equation (1).
- R. C. King, C. Tollu and F. Toumazet, *The hive model and the polynomial
  nature of stretched Littlewood--Richardson coefficients*, SLC 54A (2006).

