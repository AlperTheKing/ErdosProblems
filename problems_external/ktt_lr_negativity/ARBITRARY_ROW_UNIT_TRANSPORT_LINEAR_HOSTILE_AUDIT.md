# Hostile audit: arbitrary-row unit-column transportation linear coefficient

Date: 2026-07-22

## Verdict

The proposed formula is correct.  Let `k>=1`, let
`r=(r1,r2,r3)` be positive integers, and put `N=r1+r2+r3>k`.
For the full `3 x (k+1)` transportation polytope with margins

```text
rows:    (r1,r2,r3),
columns: (N-k,1^k),
```

write `L_r,k(n)` for its Ehrhart polynomial.  Define

```text
F_k(x) = (1/2) sum_(t=1)^(k-x) t/(x+t)   if x<k,
         0                                if x>=k.
```

Then

```text
[n]L_r,k(n)
 = 3k/2 - sum_i F_k(ri) - sum_(i<j) F_k(ri+rj).             (1)
```

Moreover,

```text
[n]L_r,k(n) >= 3/2 > 0.                                    (2)
```

Thus no member of this entire arbitrary-row family can give a KTT
counterexample through its linear coefficient.  This is a theorem about this
transportation family, not a proof of general KTT.

## 1. Projection and cap invariance

Project a table at dilation `n` to its `k` unit columns.  Each projected
column is a weak composition of `n` into three parts.  If `Si` is the
aggregate in row `i`, the deleted large-column entry is forced to be

```text
n*ri-Si.
```

Hence the projected constraints are exactly `Si<=n*ri`.  Since always
`Si<=kn`, replacing any `ri>=k` by `k` preserves the complete projected
lattice-point set at every dilation.  The large-column margin changes by the
same amount as its forced row entries, so this is a dilation-compatible
lattice bijection, not merely equality at `n=1`.

## 2. Inclusion-exclusion

Without row caps there are

```text
U_k(n)=binom(n+2,2)^k
```

configurations, and `[n]U_k=3k/2`.  Let `A_i(n)` count configurations with
`Si>n*ri`, and let `A_ij(n)` count those with both indicated violations.
The triple intersection is empty: it would imply

```text
S1+S2+S3 > n(r1+r2+r3)=nN>nk.
```

Therefore

```text
L_r,k=U_k-sum_i A_i+sum_(i<j) A_ij.                         (3)
```

The required local coefficient calculation is the following exact lemma.

## 3. One-cap/two-cap coefficient lemma

For positive integers `x,y`, using any two specified rows,

```text
[n] #{S1>xn}              =  F_k(x),
[n] #{S1>xn and S2>yn}    = -F_k(x+y).                      (4)
```

The right sides are zero when the corresponding cap or cap sum is at least
`k`, exactly when the half-open violation is empty.

### 3.1 One cap

Put `u_j=n-x_j` in each unit column.  For fixed `u_j`, the other two entries
have `u_j+1` choices, and `S1>xn` becomes

```text
sum_j u_j <= (k-x)n-1.
```

The exact coefficient extractor is therefore

```text
[z^((k-x)n-1)]
 (1-(n+2)z^(n+1)+(n+1)z^(n+2))^k /(1-z)^(2k+1).            (5)
```

Expand the numerator, discard before polynomial continuation precisely the
terms whose residual exponent is negative for every `n>=0`, and differentiate
the resulting falling-factorial binomials at `n=0`.  Grouping the two
numerator indices by their sum `s` gives

```text
[n]A_x = (1/2) sum_(s=0)^(k-x-1) (k-x-s)/(k-s)
        = (1/2) sum_(t=1)^(k-x) t/(x+t)
        = F_k(x).                                           (6)
```

The collapse uses

```text
binom(k,s) sum_(j=0)^s binom(s,j)2^(s-j)/binom(2k-1,s+j)
 = k/(k-s),                                                 (7)
```

obtained by a beta integral and the substitution `u=t(2-t)`.  This also
guards against the generalized-binomial small-`n` error identified in the
earlier symmetric audit.

### 3.2 Two caps

For a unit-column triple `(a,b,c)`, put

```text
u=n-a=b+c,    v=n-b=a+c.
```

Then `0<=u,v<=n`, `u+v>=n`, and the transformation is bijective.  If
`b0=k-x-y>0`, the two violations are

```text
sum u <= (k-x)n-1,
sum v <= (k-y)n-1.
```

The per-column bivariate kernel is

```text
H_n(p,q)=sum_(0<=u,v<=n; u+v>=n) p^u q^v
 = {q^(n+1)(1-q)-p^(n+1)(1-p)+(q-p)(pq)^(n+1)}
   /{(1-p)(1-q)(q-p)}.                                     (8)
```

Thus the pair count is the rectangular cumulative coefficient of `H_n^k` at
the two displayed bounds.  Expand the three numerator terms in (8), split the
`q-p` pole in either coefficient chamber, and differentiate the affine
binomials at zero.  Combining the two chambers reduces the derivative to the
following finite identity.  With out-of-range binomials interpreted as zero,

```text
D_(k,i,j)
 = sum_(h=0)^(i+j) (-1)^h binom(i+j,h)
   * binom(2k-i-j-1-h,k-j-1-h)
   /{(2k-h) binom(2k-h-1,k-j-1)}

 = { j!(k-j-1)!/(2k!)   if i=0,
     0                   if i>0. }                          (9)
```

Identity (9) is a terminating Chu--Vandermonde identity.  A direct proof
inserts

```text
1/{(2k-h)binom(2k-h-1,k-j-1)}
 = integral_0^1 z^(k-j-1)(1-z)^(k+j-h) dz,
```

takes the `(i+j)`-th finite difference inside the integral, and applies the
beta integral.  For `i>0` the difference has zero integral; for `i=0` it is
`B(j+1,k-j)/2`, which is the nonzero value in (9).

All `i>0` numerator classes in (8) consequently cancel.  The surviving
`i=0`, `0<=j<b0` classes give

```text
[n]A_(x,y)
 = -(1/2) sum_(j=0)^(b0-1) (b0-j)/(k-j)
 = -(1/2) sum_(t=1)^b0 t/(x+y+t)
 = -F_k(x+y).                                              (10)
```

This proves (4).  Substitution into (3) proves formula (1), including its
minus sign on the pair corrections.

## 4. Uniform strict positivity

For every positive integer `x`,

```text
F_k(x) <= (k-x)_+/2,                                       (11)
```

because every summand `t/(x+t)` is less than one.  Put
`delta=N-k>=1`.  The deficit belonging to the pair complementary to row `i`
is

```text
(k-rj-rl)_+ = (ri-delta)_+.
```

Twice the six-term correction in (1) is therefore at most

```text
S=sum_i ((k-ri)_+ + (ri-delta)_+).                          (12)
```

Each summand in (12) is at most `k-1`:

- if `ri<delta`, only `(k-ri)_+` remains and `ri>=1`;
- if `delta<=ri<=k`, the sum is `k-delta<=k-1`;
- if `ri>k`, then `ri<=N-2=k+delta-2`, so it is at most `k-2`.

Consequently `S<=3k-3`, and (1) gives

```text
[n]L_r,k >= 3k/2-(3k-3)/2 = 3/2.
```

This proves (2) for every allowed parameter, with no asymptotic or finite
search step.

## 5. Independent exact replay

`arbitrary_row_unit_transport_linear_audit.py` does not use (5), (8), or (9)
to count.  It directly convolves the triangular kernel
`{(a,b):a,b>=0,a+b<=n}` over the `k` labelled unit columns, applies the three
row caps, and reconstructs the degree-`2k` polynomial by exact Newton
interpolation.  Dilations `2k+1` and `2k+2` are held out.

The bounded hostile calibration covers every unordered capped positive row
triple with `N>k` for `1<=k<=7`, as well as all one-cap and two-cap terms in
that range:

```text
full_row_cases=185
single_cap_checks=21
pair_cap_checks=22
held_out_full_checks=370
vandermonde_checks_through_k12=364
minimum_linear=3/2 rows=(1,1,1) k=1
```

Explicit asymmetric cases include

```text
rows=(1,2,5), k=7:  [n]L=2407/420
rows=(1,4,4), k=7:  [n]L=1927/280
rows=(2,2,4), k=7:  [n]L=691/105
rows=(2,3,3), k=7:  [n]L=719/105
```

The checker also compares uncapped rows `(1,k,k+4)` with `(1,k,k)` at every
interpolation and held-out dilation for each `1<=k<=7`; all counts agree.

Replay:

```powershell
python problems_external\ktt_lr_negativity\arbitrary_row_unit_transport_linear_audit.py
```

Expected payload SHA-256:

```text
cd2314207b507e7f32d25b4d34c17ccc1a2370403da3cc14036217356ee8dc85
```

Checker SHA-256:

```text
D2F4233225D3F70C166B06A3D1F8B9862F51EFE2F6DEA82BACAD5BEAE28688A8
```

## 6. Zero-trust audit of the homogeneous LR bridge

Put

```text
A=(N,r2+r3,r3),                 B=(r2+r3,r3),
w=(N-k,1^k),
R=(N+r2+r3,N+r3,N,k,k-1,...,1),
S=(N,N,k,k-1,...,1).                                     (13)
```

All five displayed sequences are partitions.  The only potentially relevant
junction is `N>k`, which is an assumption.  Their sizes satisfy

```text
|A|-|B|=|w|=N,
|R|=|A|+|S|.                                               (14)
```

The three rows of `A/B` occupy the column intervals

```text
[r2+r3+1,N],   [r3+1,r2+r3],   [1,r3].                    (15)
```

They are pairwise disjoint and have lengths `r1,r2,r3`.  Hence there are no
column comparisons in a semistandard tableau of this shape.  Sorting each row
is a bijection between such tableaux of content `w` and nonnegative matrices
with row margins `r` and column margins `w`.  Scaling (15) by `n` gives the
same bijection for every dilation:

```text
L_r,k(n)=K_(nA/nB,nw).                                    (16)
```

For completeness, apply the general skew-Kostka bridge with `lambda=A`,
`beta=B`, and `W=|w|=N`.  The tail sums of `w` are

```text
N,k,k-1,...,1.
```

The bridge therefore produces exactly the `R,S` in (13).  Its skew diagram
`R/S` consists of a translate of `B` and isolated horizontal strips of
lengths `N-k,1,...,1`, in disjoint row and column sets.  Thus

```text
s_(R/S)=s_B h_(N-k) h_1^k.
```

Taking the `s_A` coefficient and using the Hall inner product and iterated
Pieri rule proves

```text
K_(A/B,w)=c^R_(A,S).                                      (17)
```

Every entry, width, and tail sum in this construction is linear in the input.
Replacing `(A,B,w)` by `(nA,nB,nw)` therefore replaces `(R,S)` by `(nR,nS)`.
Combining (16)-(17) gives the exact all-dilation identity

```text
L_r,k(n)=K_(nA/nB,nw)=c^(nR)_(nA,nS)   for every n>=0.     (18)
```

At `n=0`, all partitions and the content normalize to empty.  Both sides of
(18) equal one: the unique empty tableau and `c^0_(0,0)=1`.  Thus there is no
hidden positive-dilation exception.

`arbitrary_row_transport_lr_bridge_audit.py` independently checks partition
order, (14), interval disjointness, and the general bridge construction on
1,000 parameter tuples, with 5,000 homogeneity checks including `n=0`.  It
also compares a raw transportation DP with the exact LR hive engine:

```text
rows=(1,1,1), k=2: n=1 -> 6,    n=2 -> 21
rows=(1,1,2), k=3: n=1 -> 12,   n=2 -> 72
rows=(1,2,3), k=5: n=1 -> 60,   n=2 -> 1185
```

All six counts agree.  Replay:

```powershell
python problems_external\ktt_lr_negativity\arbitrary_row_transport_lr_bridge_audit.py
```

Bridge payload SHA-256:

```text
510aafb6878dd2db0f77ee04895a4eae4c4b9e3bdc360ce5df1bdd203d4fa443
```

Bridge checker SHA-256:

```text
25ED776A09D197B027D580BA4E8F6626E9810C092FC4B562289C9A6346D7A82D
```

## 7. Scope conclusion

The arbitrary-row formula survives both symbolic and exact hostile checks,
and the elementary deficit bound proves strict positivity uniformly.  This
closes the all-parameter linear-coefficient endpoint for column margins
`(N-k,1^k)`.  It says nothing about higher ordinary coefficients or other
column-margin patterns, so general KTT remains open.
