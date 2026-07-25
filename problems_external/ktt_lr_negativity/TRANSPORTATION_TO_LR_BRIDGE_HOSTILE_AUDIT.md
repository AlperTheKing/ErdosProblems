# Hostile Audit: the Codegree-Three `3 x 8` Transportation-to-LR Bridge

Date: 2026-07-22  
Verdict on the bridge: **CONFIRMED**.  
Verdict on the invariant-matching gate `L_T(1)=255`: **EMPTY, exactly**.  
Scope: this report proves the displayed homogeneous reduction and the exact
obstruction to the V4 finite gate.  It neither proves nor refutes general KTT.

## 1. Explicit transportation-to-skew-Kostka construction

Let the positive row margins be

```text
r=(r1,r2,r3),  each ri >= 3,  N=r1+r2+r3,
```

and fix the eight column margins

```text
w=(N-7,1,1,1,1,1,1,1).
```

Since `N>=9`, all eight parts of `w` are positive.  Define

```text
A=(N,r2+r3,r3),
B=(r2+r3,r3).
```

Both are partitions and `B` is contained in `A`.  The three rows of `A/B`
are exactly

```text
row 1: columns r2+r3+1,...,N       (length r1),
row 2: columns r3+1,...,r2+r3      (length r2),
row 3: columns 1,...,r3            (length r3).
```

Their column intervals are pairwise disjoint.  Therefore a semistandard
tableau of shape `nA/nB` and content `nw` has no vertical comparison between
different rows.  Once the multiplicities of the eight letters in each row
are specified, weak row increase forces a unique filling.  These
multiplicities are precisely a nonnegative `3 x 8` integer table with row
margins `nr` and column margins `nw`.  Hence, for every `n>=1`,

```text
L_T(n)=K_(nA/nB,nw).                                      (1)
```

For `n=0`, both sides are one by the usual empty-object convention.

## 2. Explicit final LR triple

For the bridge in `KOSTKA_TO_LR_HOMOGENEOUS_BRIDGE.md`, the inner partition
`B` has length `s=2`; its omitted third part is zero.  The tail sums of `w`
are

```text
T1=N, T2=7, T3=6, T4=5, T5=4, T6=3, T7=2, T8=1, T9=0.
```

Consequently the two bridge partitions are

```text
R=(N+r2+r3,N+r3,N,7,6,5,4,3,2,1),
S=(N,N,7,6,5,4,3,2,1).
```

They are partitions because `N>=9`.  Also `S` is contained in `R`, and the
size convention is exact:

```text
|A| = N+r2+2r3,
|S| = 2N+28,
|R| = 3N+r2+2r3+28 = |A|+|S|.
```

The cells of `R/S` are a translate of `B` in the first two rows, followed by
eight single rows of lengths `N-7,1,1,1,1,1,1,1`.  These nine components use
disjoint row and column sets, so

```text
s_(R/S)=s_B h_(N-7) h_1^7.
```

Hall adjunction and Pieri give

```text
K_(A/B,w)=c^R_(A,S).
```

Every displayed part and every tail sum scales linearly.  Combining this with
(1) gives the full counting-function identity

```text
L_T(n)=K_(nA/nB,nw)=c^(nR)_(nA,nS)       for every n>=0.   (2)
```

Thus the final KTT triple, in the convention `c^(nu)_(lambda,mu)`, is

```text
lambda=A,  mu=S,  nu=R.
```

There is no hidden dominance or nonvanishing condition: (2) and the existence
of an integer transportation table imply the base LR coefficient is nonzero.

## 3. Dilation, zero rows, alphabet length, translation, period, dimension

- **Dilation.**  One must first fix `w=(N-7,1^7)` and then scale it to
  `nw=(n(N-7),n,n,n,n,n,n,n)`.  Re-entering the family formula after replacing
  `N` by `nN` would instead produce `(nN-7,1^7)` and would be wrong.  The V4
  logical bridge uses the correct fixed-margin dilation, but this convention
  should be stated explicitly.
- **Zero rows.**  The route assumes `ri>=3`, so no transportation row is zero.
  The only omitted zero is the padded third part of `B`; this is why `s=2`,
  even though `A/B` has three nonempty rows.
- **Alphabet length.**  It is exactly eight for every `n>=1`; equal unit
  weights still correspond to seven distinct letters/transportation columns.
  At `n=0`, all parts disappear and (2) is checked separately as `1=1`.
- **Translation.**  The top component of `R/S` is a horizontal translate of
  `B`.  Translation does not change its skew Schur function, and its columns
  are disjoint from those of all eight lower rows.
- **Period.**  A transportation polytope has a totally unimodular constraint
  matrix, so integral margins give a lattice polytope and an Ehrhart
  polynomial, not a quasipolynomial.  Identity (2) transfers that exact
  polynomial.
- **Dimension.**  The real table `x_ij=r_i w_j/N` is strictly positive, so the
  polytope has full affine dimension `(3-1)(8-1)=14`.

None of these points breaks the bridge.

## 4. Independent codegree-three proof

Relative-interior lattice points of `nT` are positive integer tables.  After
subtracting one from each of the 24 entries, their new margins are

```text
row i: n ri-8,
large column: n(N-7)-3,
each of the seven unit columns: n-3.
```

For `n=1,2`, a unit column cannot contain three positive integers, so there is
no relative-interior lattice point.  For `n=3`, all seven shifted unit-column
margins are zero.  The shifted table is therefore supported only on the large
column, whose entries are forced to be

```text
3r1-8, 3r2-8, 3r3-8.
```

They are nonnegative because every `ri>=3`, and their sum is
`3N-24=3(N-7)-3`, the shifted large-column margin.  Thus `3T` has exactly one
relative-interior lattice point.  The codegree is exactly three.

## 5. Exact obstruction: the `L_T(1)=255` gate has no survivor

At dilation one, each of the seven labeled unit columns chooses one of the
three rows.  If `xi` unit columns choose row `i`, the large-column entry is
forced to be `ri-xi`; hence the assignment is feasible exactly when
`xi<=ri`.  Therefore

```text
L_T(1)=#{f:{1,...,7}->{1,2,3}: |f^(-1)(i)|<=ri for all i}.
```

This is monotone in each `ri`.  Under `ri>=3`, its minimum occurs at
`r=(3,3,3)`.  The only occupancy types are permutations of `(3,3,1)` and
`(3,2,2)`, so

```text
min L_T(1)
 = 3 * 7!/(3!3!1!) + 3 * 7!/(3!2!2!)
 = 420+630
 = 1050.
```

In particular,

```text
L_T(1)>=1050>255
```

for every member of the V4 family.  The proposed invariant-matching gate is
therefore empty without enumeration.  Under V4's stated exit condition this
route must be recorded as

```text
DEAD: codegree-three 3x8 transfer invariant gate exhausted --
L_T(1)>=1050, so no margin pattern has L_T(1)=255.
```

This obstruction kills only the `L_T(1)=255` finite route.  It does not show
that every `3 x 8` transportation Ehrhart polynomial is positive, and it does
not invalidate the homogeneous reduction (2).

## 6. Executable replay

The focused checker verifies all displayed partition, cell-set, size,
dilation, dimension, and codegree identities; independently counts tables by
a two-row dynamic program; proves the `1050` lower bound; and checks one
explicit final LR coefficient against the separate hive engine:

```text
python problems_external/ktt_lr_negativity/transportation_lr_bridge_audit.py
```

Expected output:

```text
status: PASS
dimension: 14
codegree: 3
interior_points_at_codegree: 1
minimum_base_count: 1050
base_count_255_survivors: 0
explicit_lr_replays: 1
replay_records_sha256:
e38a892ddf3a7fef243c96dda167f2a60abab00b848bbb8145762cd5133811b6
```

Checker SHA-256:

```text
DA210DFF3D840A4F433A9FF56786EDC02CA1A915B7600E387B41F3210A83265F
```
