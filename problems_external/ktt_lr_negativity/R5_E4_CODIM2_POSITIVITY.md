# Rank-5 positivity of the fourth Ehrhart coefficient

## Statement

Let `H` be a full-dimensional rank-5 hive polytope in its six standard
interior coordinates, and write

```text
L_H(n) = a_6 n^6 + a_5 n^5 + a_4 n^4 + ... + a_0.
```

If `L_H` is an ordinary polynomial, then

```text
a_4 > 0.
```

For integral partition boundary, ordinary polynomiality is supplied by the
stretched Littlewood--Richardson theorem.  The vertices of `H` need not be
integral: scaling to a lattice polytope and comparing `L_(qH)(n)=L_H(qn)`
extends the local formula unchanged, as proved in
`UNIFORM_CODIM2_POSITIVITY.md`.

## Exact rank-5 atlas

The 30 rank-5 rhombus inequalities reduce to 27 distinct oriented primitive
normals in `Z^6`.  Of their 351 unordered pairs, nine are opposite and 342 are
nonparallel.  Exact Smith-index and Berline--Vergne calculations give

```text
saturation index 1: 339 pairs
saturation index 2:   3 pairs
minimum alpha:       1/9
```

The minimum `1/9` occurs on six index-one pairs.  Each of the three index-two
pairs has local constant `5/18`.  For an index-one pair `u,v`, the checker
computes the inverse normal Gram matrix and evaluates the two inward feasible
rays; this independently verifies the sign in

```text
alpha = 1/4 - (<u,v>/12)(1/<u,u> + 1/<v,v>).
```

For an index-two pair, it constructs the saturated basis
`s=(u+v)/2`, `t=(u-v)/2`, subdivides the feasible cone into two unimodular
cones, and verifies

```text
7/18 + 7/18 - 1/2 = 5/18.
```

Therefore every codimension-two face `F` of a full-dimensional rank-5 hive
satisfies `alpha(T(H,F)) >= 1/9`, and the local formula gives the stronger
rank-5 bound

```text
a_4 >= (1/9) sum_(dim F=4) vol_Z(F) > 0.
```

## Replay

From the repository root, run

```powershell
python problems_external\ktt_lr_negativity\r5_e4_codim2_checker.py
```

The exact checker returns `PASS`, normal-set SHA-256
`4bd294a1e92a805f261b93fd66f9be4997ca4320b7995d01a29e772ef2d7a855`,
27 normals, 342 nonparallel pairs, index histogram `{1:339, 2:3}`, and
minimum `1/9`.

This proves only `a_4` for full-dimensional rank-5 hives.  It does not settle
`a_1`, `a_2`, or `a_3`, and it does not claim the full KTT conjecture.
