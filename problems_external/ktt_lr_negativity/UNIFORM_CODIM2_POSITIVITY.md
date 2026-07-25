# Rank-uniform positivity of the codimension-two Ehrhart coefficient

## Theorem

Let `H` be a full-dimensional rank-`r` hive polytope in the standard lattice
of interior hive coordinates, and put

```text
d = (r-1)(r-2)/2,
L_H(n) = sum_{k=0}^d a_k n^k.
```

Assume that `L_H` is an ordinary polynomial.  This is automatic for a hive
with integral partition boundary because it is the corresponding stretched
Littlewood--Richardson coefficient.  If `d >= 2`, then

```text
a_(d-2) > 0.
```

More precisely, for the Berline--Vergne scalar-product complement map,

```text
a_(d-2) >= (1/12) sum_F vol_Z(F),
```

where the sum is over the codimension-two faces of `H`.  Thus the third
leading monomial coefficient of every full-dimensional hive Ehrhart
polynomial is positive, uniformly in the rank.

This is only a codimension-two theorem.  It does not prove the lower
coefficients, and it does not automatically cover a hive that is
lower-dimensional in the standard interior-coordinate space.

## 1. Rational polytopes with polynomial lattice count

The local formula can be used even when `H` has rational vertices.  The
following scaling observation removes the lattice-polytope hypothesis.

Let `P` be a rational full-dimensional polytope whose lattice-point enumerator
is the polynomial `L_P(n)=sum a_k n^k`.  Choose a positive integer `q` such
that `qP` is a lattice polytope.  Then

```text
L_(qP)(n) = L_P(qn),
```

so the coefficient of `n^k` on the left is `q^k a_k`.  Apply the
McMullen--Berline--Vergne formula to `qP`:

```text
q^k a_k
  = sum_{dim F=k} alpha(T(P,F)) vol_Z(qF)
  = q^k sum_{dim F=k} alpha(T(P,F)) vol_Z(F).
```

Scaling preserves the face lattice and every transverse feasible cone, while
relative lattice volume on a `k`-face scales by `q^k`.  Division by `q^k`
therefore gives the same local formula for `P`.  No vertex-integrality lemma
is needed.

For `k=d-2`, the transverse feasible cones are two-dimensional.

## 2. The only possible facet normals

Fix the boundary of a rank-`r` hive and use its interior values as coordinates.
After the boundary constants are moved to the right, a rhombus inequality has
a primitive outward row

```text
u in {0,1,-1}^d
```

with at most four nonzero entries.  Every facet of `H` is supported by one of
these inequalities; deleting duplicate or redundant inequalities does not
introduce a new normal.

A codimension-two face of a full-dimensional polytope is contained in exactly
two facets.  Hence its two-dimensional normal cone has two nonparallel
primitive extreme normals `u,v` of the preceding form.  Extra tight rhombus
rows, if present, lie inside their positive span and do not change the
transverse cone.

Let

```text
q = [sat(Zu+Zv) : Zu+Zv].
```

By Smith normal form, `q` is the gcd of the two-by-two minors of the matrix
with rows `u,v`.  Every such minor is `0`, `1`, `-1`, `2`, or `-2`; because
`u,v` are independent, at least one is nonzero.  Consequently

```text
q in {1,2}.
```

The two cases below exhaust every hive ridge in every rank.

## 3. Saturation index one

Put

```text
A = <u,u>,  B = <v,v>,  C = <u,v>.
```

When `q=1`, `u,v` are a lattice basis of the saturated normal plane.  In the
dual quotient-lattice coordinates, the two inward feasible rays are
`(-1,0)` and `(0,-1)`.  Their Gram matrix is the inverse of

```text
[[A,C],[C,B]],
```

whose off-diagonal entry is `-C/(AB-C^2)`.  The constant term of the
Berline--Vergne function of a two-dimensional unimodular feasible cone is

```text
1/4 + (1/12)( <x,y>/<x,x> + <x,y>/<y,y> ).
```

Substitution therefore gives

```text
alpha(u,v) = 1/4 - (C/12)(1/A + 1/B).                 (1)
```

This also fixes the sign: the plus sign belongs to the **feasible rays**;
conversion from outward normals introduces the minus sign in (1).

If `C <= 0`, (1) is at least `1/4`.  If `C > 0`, the entries being
`0,1,-1` imply

```text
C <= |supp(u) intersect supp(v)| <= min(A,B).
```

Assume `A <= B`.  Then

```text
C(1/A+1/B) <= A(1/A+1/B) = 1+A/B <= 2,
```

and hence

```text
alpha(u,v) >= 1/12.                                   (2)
```

## 4. Saturation index two

Suppose `q=2`.  Regard each coordinate as a column `(u_i,v_i)` in
`{0,1,-1}^2`.  All determinants of two columns are even.  An axis column and
any independent column would have determinant `1` or `-1`, so no axis column
can occur.  Since the two rows are independent, the nonzero columns use both
diagonal directions.  Thus `u` and `v` have the same support and

```text
s = (u+v)/2,  t = (u-v)/2
```

are integral nonzero vectors with disjoint supports.  A coordinate from each
support gives a two-by-two minor `1` or `-1`, so `s,t` form a saturated normal
basis.  Write

```text
A = <s,s> > 0,  B = <t,t> > 0.
```

They are orthogonal.  In coordinates dual to `s,t`, the feasible inequalities
are

```text
x+y <= 0,  x-y <= 0.
```

The extreme primitive rays are `(-1,1)` and `(-1,-1)`.  Subdivide their
index-two cone by the primitive ray `(-1,0)`.  The quotient metric is
`diag(1/A,1/B)`.  Applying the preceding unimodular formula to the two pieces
and subtracting the common ray contribution `1/2` gives

```text
alpha(u,v)
  = alpha((-1,1),(-1,0)) + alpha((-1,0),(-1,-1)) - 1/2
  = (A+2B)/(6(A+B))
  >= 1/6.                                              (3)
```

This is an exact valuation computation in the saturated quotient lattice;
using the ambient determinant `2` without saturation would give the wrong
local lattice.

## 5. Summing over ridges

Equations (2) and (3) show that every codimension-two transverse feasible
cone of a hive has Berline--Vergne constant at least `1/12`.  The local formula
now yields

```text
a_(d-2)
  = sum_F alpha(T(H,F)) vol_Z(F)
  >= (1/12) sum_F vol_Z(F) > 0.
```

Every relative face volume in the last sum is positive.  This proves the
theorem.

For rank `3`, the ambient hive dimension is `1`, so no codimension-two
coefficient or nonparallel normal pair exists; this is a not-applicable case,
not a zero minimum.  For rank `4`, the theorem directly gives positivity of
the linear coefficient.  For rank `5`, it gives positivity of `a_4`; the
rank-5 atlas sharpens the uniform local lower bound from `1/12` to `1/9`.

## 6. Exact finite audit

`uniform_codim2_gate_canonical.py` reconstructs all primitive rhombus rows in ranks
`3` through `20`, checks that every nonparallel pair has saturation index one
or two, and evaluates every local constant with exact rational arithmetic.
The computation is a consistency audit of the rank-uniform argument, not a
finite substitute for it.  Its required terminal summary is

```text
r=3 normals=2 codim2=not_applicable
...
PASS ... proof_bound=1/12 observed_min=1/9
```

The separate `r5_e4_codim2_checker.py` reconstructs the rank-5 atlas from
scratch and verifies the exact rank-5 minimum.
