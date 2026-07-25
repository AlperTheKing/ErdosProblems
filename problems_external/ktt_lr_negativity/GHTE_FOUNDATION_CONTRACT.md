# Global Hive Todd Effectivity — Exact Foundation Contract

Date: 2026-07-22
Status: definition and reduction theorem; not a proof of GHTE.

## 1. Lattice and fan conventions

Let `M` be a lattice of rank `d`, let `N=Hom(M,Z)`, and let `P` be a
full-dimensional lattice polytope in `M_R`.  Write `Sigma=Sigma_P` for its
complete outer normal fan in `N_R`.

For a cone `sigma in Sigma`, let `F_sigma` be its corresponding face.  Thus

```text
dim(sigma) = q  iff  dim(F_sigma) = d-q.
```

For every incidence `tau < sigma` with dimensions `q-1 < q`, let

```text
u_{sigma/tau}
```

be the primitive generator of the image ray of `sigma` in the quotient
lattice

```text
N / (N intersect span_R(tau)).
```

Choose a `Z`-basis of each quotient only to write coordinates.  Changing that
basis left-multiplies the corresponding balance block by an invertible
integral matrix and does not change its kernel.

## 2. The complete-fan balance matrix

For fixed `q`, define

```text
B_{P,q} : Q^{Sigma(q)}
          -> direct_sum_{tau in Sigma(q-1)}
             (N / N_tau)_Q
```

by

```text
(B_{P,q} w)_tau = sum_{sigma contains tau} w_sigma u_{sigma/tau}.
```

Here `Sigma(q)` denotes the `q`-dimensional cones and
`N_tau=N intersect span_R(tau)`.

Define the nonnegative balanced cone

```text
W_{P,q} = {w >= 0 : B_{P,q} w = 0}.
```

No realizability condition is included in this definition.

## 3. The face-volume vector is balanced

Let

```text
v_{P,q}(sigma) = vol_{M intersect lin(F_sigma)}(F_sigma),
```

where a fundamental parallelepiped of the face lattice has volume one.
Then

```text
v_{P,q} >= 0  and  B_{P,q} v_{P,q} = 0.                (1)
```

To prove (1), fix `tau in Sigma(q-1)`.  The face `F_tau` has dimension
`d-q+1`.  The cones `sigma` of dimension `q` containing `tau` correspond
exactly to the facets `F_sigma` of `F_tau`.  Their primitive outer conormals
in the quotient lattice are `u_{sigma/tau}`.  The lattice Minkowski
equilibrium identity for the polytope `F_tau` is precisely

```text
sum_{sigma contains tau}
  vol(F_sigma) u_{sigma/tau} = 0.
```

This is the `tau` block of (1).

## 4. The BV vector and the Ehrhart pairing

Fix the rational Euclidean complement map used throughout the hive audits.
For `sigma in Sigma(q)`, let

```text
a_{P,q}(sigma) = alpha^BV(sigma)
```

be the constant term of the Berline--Vergne transverse-cone operator, using
the intrinsic quotient lattice.  The local Euler--Maclaurin formula gives

```text
[n^(d-q)] L_P(n) = <a_{P,q}, v_{P,q}>.                 (2)
```

The cone ordering, quotient lattices, and complement map in `a_{P,q}` must be
the same as those used to build `B_{P,q}`.

## 5. Exact Farkas statement

For a finite rational matrix `B` and rational vector `a`, the following are
equivalent:

```text
<a,w> >= 0 for every w >= 0 with B w = 0;              (3)
```

```text
there exists y with a + B^T y >= 0.                    (4)
```

Indeed, the dual cone of `ker(B) intersect Q_+^m` is

```text
Q_+^m + rowspace(B).
```

The sign of `y` is immaterial.  Equations (3)--(4) are the precise meaning of
global Todd effectivity modulo balancing.

## 6. GHTE implies KTT

Assume (4) for `B=B_{P,q}` and `a=a_{P,q}`.  By (1),

```text
<a, v_{P,q}>
 = <a + B^T y, v_{P,q}> >= 0.
```

Equation (2) therefore makes the corresponding Ehrhart coefficient
nonnegative.

For a rational period-one hive polytope, choose `m` so that `mP` is lattice.
Its normal fan is unchanged, its `(d-q)`-face volumes scale by `m^(d-q)`, and

```text
L_{mP}(n) = L_P(mn).
```

Comparing coefficients transfers the same conclusion back to `P`.  Applying
this in every `q` proves all coefficients of every nonzero stretched LR
polynomial nonnegative.

## 7. Scope distinctions

The following statements are different and must be reported separately.

1. A negative simplicial subdivision cell is only a failure of termwise
   subdivision positivity.
2. A negative **actual closed normal cone** refutes pointwise local
   positivity, but not GHTE.
3. A vector `w>=0`, `B w=0`, `<a,w><0` refutes GHTE for that complete fan, but
   not KTT unless `w` is an actual face-volume vector.
4. A hive polytope with `<a,v_{P,q}><0` is an actual KTT counterexample once
   its stretching polynomial is independently certified.

## 8. Required checker contract

Every finite GHTE audit must emit and independently replay:

1. the intrinsic primal and dual lattice bases;
2. the complete face lattice and normal-fan incidences;
3. every primitive quotient vector `u_{sigma/tau}`;
4. the exact matrix `B_{P,q}`;
5. the exact face-volume vector and the check `B v=0`;
6. the exact BV vector in the identical cone ordering;
7. the equality `<a,v>=[n^(d-q)]L_P`; and
8. either a rational `y` proving (4), or a rational negative witness proving
   failure of (3).

Local coarsening data without this complete-fan contract cannot certify GHTE.
