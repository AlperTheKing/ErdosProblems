# Rank-5 gate for the local Ehrhart-certificate method

## Status

This note proves that fractional hive vertices do **not** obstruct a fixed
normal-cone local formula.  It also reduces rank-5 positivity to four finite
face-local problems.  It does not yet prove those four positivity statements.

The relevant external inputs are:

1. hive lattice points count Littlewood--Richardson coefficients;
2. stretched Littlewood--Richardson coefficients are polynomials; and
3. McMullen local formulas express lattice Ehrhart coefficients as weighted
   sums of normalized face volumes, with weights depending only on normal
   cones.

Primary references for (2) and (3) include Derksen--Weyman, *On the
Littlewood--Richardson polynomials*, and Ring--Schuermann,
[*Local Formulas for Ehrhart Coefficients from Lattice Tiles*](https://arxiv.org/abs/1709.10390).
Berline--Vergne's affine-cone construction is in
[*Local Euler--Maclaurin formula for polytopes*](https://arxiv.org/abs/math/0507256).

## Exact rank-5 normal atlas

The size-5 hive has ambient dimension

```
D = (5-1)(5-2)/2 = 6.
```

There are 30 nonconstant rhombus inequalities and 27 distinct primitive
oriented normals.  Three normals occur twice.  Exact enumeration over all
`C(27,6) = 296010` six-subsets gives

```
abs(det) : count
       0 : 185914
       1 :  80088
       2 :  25794
       3 :   2010
       4 :   1940
       5 :     12
       6 :    234
       7 :     18
```

The standalone integer-arithmetic replay is `r5_local_gate.py`.  Retaining
the three duplicate rows instead gives the older 30-row nonzero histogram

```
1:146656, 2:40320, 3:2892, 4:2502, 5:18, 6:252, 7:18,
```

which independently cross-checks the construction.

Fractional vertices occur already in the full-dimensional cell.  For example,

```
lambda = (16,12,8,5,3)
mu     = (12,11,6,5)
nu     = (20,19,18,12,9)
```

has a certified vertex

```
(36, 93/2, 53, 54, 121/2, 133/2).
```

It satisfies all 30 inequalities exactly and its seven tight rows have rank
6.  The rational point

```
(71/2, 47, 105/2, 54, 62, 135/2)
```

has minimum slack `1/2`, proving full dimension.  Existing independent
stretched counts give a degree-6 polynomial.  Thus this is a genuinely
full-dimensional rational period-collapse example, not a lower-dimensional
artifact.

## PIP scaling lemma

Let `M` be a lattice, let `P` be a nonempty rational polytope in `M_R`, and
write

```
d   = dim(P),
W   = lin(P-P),
M_W = M intersect W.
```

For a `k`-face `F`, put `W_F = lin(F-F)` and
`M_F = M intersect W_F`.  Normalize Lebesgue measure on `W_F` so that a
fundamental parallelepiped of `M_F` has volume one; denote the resulting
volume by `vol_Z(F)`.

Use intrinsic normal cones in `W*`:

```
N_F^W(P) = {phi in W* : phi is maximized on P along F}.
```

Equivalently, use the transverse cone in `W/W_F`.  Fix any rational
complement map on `W`, for example the one induced by a rational Euclidean
inner product, and let `alpha` be its McMullen/Todd local formula.

**Lemma.**  Suppose

```
L_P(n) = #(nP intersect M) = sum_{k=0}^d e_k(P) n^k
```

is a polynomial.  Then, for every `k`, the same lattice local formula extends
to `P`:

```
e_k(P) = sum_{F face of P, dim(F)=k}
           alpha(N_F^W(P)) vol_Z(F).
```

**Proof.**  Choose a positive integer `q` for which every vertex of `qP` is
in `M`, choose a vertex `v0` of `qP`, and set

```
R = qP - v0.
```

Then `R` is a `d`-dimensional lattice polytope in the intrinsic lattice
`M_W`.  Translation by `v0` is integral, so for every nonnegative integer
`n`,

```
#(nR intersect M_W)
  = #(nqP intersect M)
  = L_P(qn).
```

Scaling and translation preserve the face poset, all spaces `W_F`, all
intrinsic normal cones, and the fixed complement map.  They also give

```
vol_Z(qF) = q^k vol_Z(F)   when dim(F)=k.
```

Apply the lattice local formula to `R`.  Comparing the coefficient of `n^k`
on both sides gives

```
q^k e_k(P)
  = sum_{dim(F)=k} alpha(N_F^W(P)) q^k vol_Z(F).
```

Division by `q^k` proves the claim.  The result is therefore independent of
the chosen denominator and translation.  QED.

The affine offsets in a direct rational Berline--Vergne decomposition can
produce periodic local terms.  The lemma shows that for a period-one rational
polytope those terms cancel globally and the ordinary cone-only lattice
weights still recover every polynomial coefficient.

## Consequence for the existing rank-4 certificate

Every nonempty hive polytope is a rational period-one Ehrhart polytope because
its dilate counts are the stretched Littlewood--Richardson polynomial.
Therefore the existing rank-4 nonnegative edge functional applies to `qH`,
where `qH` is lattice, and the scaling lemma transfers it back to `H`.

Consequently the separate vertex-integrality condition stated in
`r4_reeve/R4_EDGE_POSITIVITY_CERTIFICATE.md` is unnecessary.  Subject to the
independent replay of that certificate and the standard hive/polynomiality
inputs, it proves coefficientwise positivity for all hives of rank at most 4.

## Which rank-5 coefficients remain

For a full-dimensional rank-5 hive write

```
L_H(n) = e_0 + e_1 n + ... + e_6 n^6.
```

The universally protected coefficients are

```
e_0 = 1,
e_6 = vol_Z(H) > 0,
e_5 = (1/2) sum_facets vol_Z(facet) > 0.
```

The only possible negative coefficients are therefore

```
e_1, e_2, e_3, e_4.
```

The local formula pairs them with faces and intrinsic normal cones as follows:

```
coefficient  face dimension  normal-cone dimension
e_1          1 (edges)       5
e_2          2               4
e_3          3               3
e_4          4 (ridges)      2
```

Thus rank 5 requires four local effectivity certificates; the single rank-4
edge certificate has no one-equation analogue that closes all four at once.

## Cheapest finite exact rank-5 test

The first test should be `e_4`, because every pointed two-dimensional normal
cone has exactly two extreme rays.  Of the `C(27,2)=351` normal pairs, nine are
opposite, leaving 342 possible ridge types.

For facet normal `n_i`, the primitive conormal of its ridge with facet `j` is
the primitive class of `n_j` in the quotient dual lattice

```
Z^6 / Z n_i.
```

It is represented integrally by

```
primitive(n_i wedge n_j).
```

Minkowski boundary closure inside every five-dimensional facet gives a
universal integer balance matrix

```
B_4 : Q^342 -> Q^(27*15).
```

The exact replay `r5_ridge_balance_gate.py` gives

```
rank(B_4) = 120,
dim ker(B_4) = 342 - 120 = 222.
```

The rank also has a short certificate.  Each facet block has rank at most 5,
and summing the 27 blocks gives 15 independent wedge-coordinate row
dependencies, so `rank(B_4) <= 27*5-15 = 120`.  Elimination modulo `1000003`
has rank 120, which supplies the matching exact lower bound over `Q`.

A direct rank-4-style certificate for `e_4` is now finite and explicit:

1. construct 222 actual lattice six-polytopes with the 27 normals whose
   normalized ridge-volume vectors form a basis of `ker(B_4)`;
2. compute each `e_4` exactly;
3. solve exactly for a componentwise nonnegative vector `mu_4 in Q^342` with
   `Lambda(P) dot mu_4 = e_4(P)` on the 222 basis witnesses; and
4. ship the witnesses, rank proof, and nonnegative vector to an independent
   checker.

Success proves `e_4 >= 0` for every full-dimensional rank-5 hive, including
the half-integral ones, by the PIP scaling lemma.  Exact infeasibility on a
spanning witness set gives a Farkas certificate that this nonnegative
ridge-weight route cannot work.  No partition census is involved.

## Uniform reduction of KTT

Fix the standard rational Euclidean complement map on each hive coordinate
lattice and restrict it to the actual affine direction space of each hive.
The following single statement is sufficient for the full KTT conjecture.

**Uniform Hive Todd Effectivity (UHTE).**  For every rank `r`, every nonempty
rank-`r` hive polytope `H` of actual dimension `d`, and every face `F` with

```
1 <= dim(F) <= d-2,
```

the associated local Todd weight is nonnegative:

```
alpha(N_F^{lin(H-H)}(H)) >= 0.
```

**Reduction theorem.**  UHTE implies coefficientwise nonnegativity of every
stretched Littlewood--Richardson polynomial.

Indeed, polynomiality and the PIP scaling lemma express every intermediate
coefficient as a sum of nonnegative Todd weights times positive normalized
face volumes.  The constant, leading, and second-leading coefficients are
already nonnegative by the formulas above.  Empty hive cells give the zero
stretching polynomial and are harmless.

For fixed `r`, UHTE is finite: the rhombus normal set is fixed, global equality
spaces are cut out by subsets of that set, and every intrinsic face normal
cone is generated by restrictions of those normals.  A weaker sufficient
version may replace the standard Berline--Vergne weights by any coherent
McMullen local formula that is nonnegative on precisely these realized cones.
