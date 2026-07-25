# GHTE reduction and the uniform endpoint cases

Date: 2026-07-22
Status: proved reduction and elementary GHTE cases; not a proof of full KTT.

## Theorem 1 — intrinsic complete-fan reduction

Let `P=H(lambda,mu,nu)` come from a nonzero Littlewood--Richardson
triple, and let `d=dim(P)`. Thus `P` contains an integral hive at stretch one;
choose one and call it `p0`. Put

```text
V = span_R(P-P),
M = Z^I intersect V,
Q = P-p0 subset M_R,
N = Hom(M,Z).
```

Then `M` is the saturated intrinsic tangent lattice, `Q` is full-dimensional
in `M_R`, and

```text
#(nP intersect Z^I) = #(nQ intersect M)                (1)
```

for every nonnegative integer `n`. Indeed, translation by the lattice vector
`n p0` identifies the two sets.

Let `m` clear the vertex denominators of `Q`. The lattice polytope `mQ` has
the same complete normal fan `Sigma` as `Q`, and

```text
L_{mQ}(n) = L_Q(mn).                                  (2)
```

For `0<=q<=d`, index the `q`-dimensional cones of `Sigma` by `sigma`. At every
incidence `tau<sigma` of dimensions `q-1<q`, use the primitive image ray
`u_{sigma/tau}` in the saturated quotient lattice `N/N_tau`. Define

```text
(B_q w)_tau = sum_{sigma>tau} w_sigma u_{sigma/tau}.
```

Let `v_q^(m)(sigma)` be the normalized `(d-q)`-volume of the face of the
**lattice polytope `mQ`** dual to `sigma`. Lattice Minkowski equilibrium
inside the face dual to `tau` gives

```text
v_q^(m) >= 0,
B_q v_q^(m) = 0.                                      (3)
```

Fix the rational Euclidean complement map and let `a_q(sigma)` be the
constant Berline--Vergne normal-cone coefficient in the same intrinsic
quotient lattice. Local Euler--Maclaurin gives

```text
[n^(d-q)] L_{mQ}(n) = <a_q,v_q^(m)>.                  (4)
```

Equivalently, if `v_q(Q)` denotes the rational normalized face-volume vector
before denominator clearing, then
`v_q^(m)=m^(d-q) v_q(Q)`.

Suppose GHTE holds for this complete fan:

```text
there is y with a_q+B_q^T y >= 0.                     (5)
```

Pairing (5) with (3) and using (4) proves the coefficient in (4)
nonnegative. Equation (2) says that this coefficient equals `m^(d-q)` times
the corresponding coefficient of `L_Q`. It follows from (1) that the
coefficient of the stretched LR polynomial is nonnegative.

Therefore GHTE for every complete intrinsic hive normal fan and every `q`
implies the full King--Tollu--Toumazet conjecture.

The converse is not asserted: GHTE tests all nonnegative balanced weights,
whereas KTT uses only the actual face-volume vector.

## Theorem 2 — exact rational Farkas equivalence

For every rational matrix `B` and rational vector `a`, the following are
equivalent:

```text
<a,w> >= 0 for every w>=0 with Bw=0;                  (6)

there exists rational y with a+B^T y>=0.              (7)
```

Proof. Let `C=ker(B) intersect R_+^s`. The dual cone is

```text
C^* = R_+^s + rowspace(B).
```

Thus (6) says exactly that `a=z+B^T y` for some `z>=0`; changing the sign of
`y` gives (7). Since `a` and `B` are rational, a nonempty rational polyhedron
of solutions has a rational point. This proves the equivalence.

## Proposition 3 — GHTE at q=0, q=1, and q=d

GHTE holds for these three values on every complete normal fan of every
lattice polytope.

### q=0

There is one zero cone, its BV value is one, and `B_0` has no target. Hence
`a_0=(1)` is already nonnegative.

### q=1

Every primitive ray has constant BV value `1/2`. Hence
`a_1=(1/2,...,1/2)` is coordinatewise positive and `y=0` is a GHTE
certificate. This is the uniform positivity of the second-leading Ehrhart
coefficient.

### q=d

At every codimension-one cone `tau`, exactly two maximal cones meet and their
primitive quotient rays are opposite. Therefore `B_d w=0` forces the weights
on adjacent maximal cones to be equal. The adjacency graph of maximal cones
in a complete polytopal fan is connected, so

```text
ker(B_d) intersect R_+ = {c*1 : c>=0}.                (8)
```

Every vertex has normalized zero-volume one. The constant-term case of local
Euler--Maclaurin, or `L_P(0)=1`, gives

```text
sum_{sigma in Sigma(d)} a_d(sigma) = 1.               (9)
```

Equations (8)--(9) imply `<a_d,w>=c>=0` for every nonnegative balanced
weight. Theorem 2 supplies a rational Farkas certificate. More explicitly,
choose one maximal cone as root and a nonnegative vector `b` with total sum
one supported at the root. Then `b-a_d` has coordinate sum zero. The image of
the transpose of a connected oriented graph incidence matrix is precisely
the sum-zero subspace, so a spanning-tree solve gives `y` with
`a_d+B_d^T y=b>=0`.

This is the uniform constant-term case.

## Remaining frontier

For `d>=3`, the unresolved GHTE range is

```text
2 <= q <= d-1.
```

The endpoint proposition does not prove a new KTT range beyond the standard
leading, second-leading, and constant coefficients. Its purpose is to fix
the complete-fan conventions and remove the trivial degrees from the active
frontier.

Primary background:

- Berline--Vergne, *Local Euler--Maclaurin formula for polytopes*,
  arXiv:math/0507256.
- Fulton--Sturmfels, *Intersection Theory on Toric Varieties*,
  arXiv:alg-geom/9403002 (complete-fan Minkowski weights).
