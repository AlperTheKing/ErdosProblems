# Exact obstruction to the canonical closed-cone ear deletion

## Verdict

The canonical endpoint deletion of an adjacent boundary strip does not give
the lattice/complement map or the nonnegative BV correction required by
`CLOSED-CONE-DELETION`.

The obstruction occurs in an actual side-four hive normal cone with only two
tight rhombi.  The planar deletion has an integral map on the height and dual
lattices, but this map is incompatible with the Euclidean complement used by
the Berline--Vergne valuation.  Its exact Todd correction is negative.  Thus
the failure is already present in the smallest connected strip and is not a
large-rank or nonsimplicial phenomenon.

This kills this canonical ear/strip induction.  It does **not** exhibit a
negative closed hive cone, a negative Ehrhart coefficient, or a KTT
counterexample.

## 1. Actual closed-cone input contract

Consider the side-four hive

```text
lambda = mu = (3,2,1,0),
nu = (5,4,2,1).
```

Its intrinsic height lattice is

```text
M_4 = Z{h_(1,1), h_(1,2), h_(2,1)} = Z^3.
```

The hive is full-dimensional.  The segment

```text
F = [(7,8,10),(8,9,11)]
```

is an edge, and the complete exact tight-row set on `F` is

```text
B(0,2), B(1,2).
```

There are no other tight rows, so this is an actual closed normal cone, not a
nonclosed simplicial cell.  Its primitive normal rays in `N_4=Hom(M_4,Z)` are

```text
u = (1,-1,0),
v = (0,-1,1).
```

The rhombi are consecutive members of the same `B` strip and their supports
meet in the single coordinate `h_(1,2)`.  Hence either endpoint is a planar
ear.  The normal plane is saturated: the gcd of its two-by-two minors is one.
Its Gram matrix for the fixed Euclidean complement is

```text
G = ((2,1),(1,2)).                                    (1)
```

Deleting either tight row leaves an actual facet of the same hive, so both
the two-dimensional cone and each proposed one-ray deletion are realized
closed cones.

Exact replay:

```text
python problems_external/ktt_lr_negativity/closed_cone_ear_deletion_obstruction.py
```

## 2. The literal rank-reducing strip map

Delete the left boundary strip and reindex `(x,y)` as `(x-1,y)`.  The unique
side-three interior coordinate `h'_(1,1)` is old `h_(2,1)`.  The induced map
on dual lattices is therefore

```text
pi : N_4 -> N_3 = Z,
pi(a,b,c) = c.
```

It has the expected combinatorial action

```text
pi(u)=0,
pi(v)=1,
```

where `v=B(1,2)` becomes the primitive side-three row `B(0,2)`.

This integral map does not preserve the BV complement.  Orthogonal projection
from the saturated plane `Z u + Z v` to the retained ray `Z u` sends

```text
v |-> (<u,v>/<u,u>) u = u/2,                          (2)
```

which is not integral.  Equivalently, the squared norm in the Euclidean
orthogonal quotient is

```text
||[v]||^2 in span(u,v)/span(u)
  = <v,v> - <u,v>^2/<u,u>
  = 2 - 1/2
  = 3/2,                                              (3)
```

whereas the primitive side-three dual ray has standard squared norm one.
Thus the integral planar strip map and the orthogonal quotient map required
by the fixed BV construction are different maps.  No induced lattice
isometry carries the old complement data to the smaller cone.

Exact replay of (2)--(3):

```text
python problems_external/ktt_lr_negativity/closed_cone_strip_lattice_map.py
```

## 3. Exact negative Todd correction

For a saturated pair of primitive outward normals `u,v`, put

```text
A=<u,u>, B=<v,v>, C=<u,v>.
```

The two-dimensional BV constant is

```text
alpha(u,v) = 1/4 - (C/12)(1/A+1/B).
```

Substituting (1) gives

```text
alpha(cone(u,v)) = 1/4 - (1/12)(1/2+1/2) = 1/6.       (4)
```

Every primitive one-dimensional cone has BV constant `1/2`.  Therefore the
literal additive correction required by

```text
alpha(old cone) = alpha(deleted cone) + correction
```

is

```text
correction = 1/6 - 1/2 = -1/3.                        (5)
```

Even if one repairs the dimensional mismatch by inserting the natural
one-dimensional Todd factor `1/2`, the correction remains negative:

```text
1/6 - (1/2)(1/2) = -1/12.                             (6)
```

So the problem is not just that the original registry used an additive
identity across different dimensions.  The fibre-normalized local identity
also has the wrong sign on this actual connected ear.

## 4. Why normal-cone subdivision does not repair the deletion

Berline--Vergne Definition 23 and Corollary 24 say that the dual normal-cone
functional is a simple valuation under a subdivision **inside one fixed
rational Euclidean lattice**.  That result explains zero correction for a
stellar subdivision of the same normal cone.  It does not apply to the strip
map above: the dimension, intrinsic lattice, and Euclidean quotient metric
all change, as (2)--(3) show.

Primary source:

<https://nicole.berline.perso.math.cnrs.fr/Berline-Vergne-Local%20Euler%20Maclaurin.pdf>.

## 5. Consequence for the general workflow

The candidate move fails both load-bearing requirements:

1. it does not induce a map compatible with the intrinsic lattice and fixed
   BV complement; and
2. its exact correction is negative on the smallest local connected
   generator.

Hence endpoint deletion of a boundary rhombus strip cannot prove strong
local closed-cone positivity by induction.  Repeating it in larger ranks or
codimensions cannot change (2), (5), or (6).

Route B could only be revived by specifying a genuinely different
rank-reducing move whose intrinsic lattice map and BV correction are both
explicit.  Merely changing the complement map would prove a different local
positivity statement and would require a new global Euler--Maclaurin bridge.
Route A, based on complete normal fans and globally balanced weights, is not
refuted by this local obstruction.

