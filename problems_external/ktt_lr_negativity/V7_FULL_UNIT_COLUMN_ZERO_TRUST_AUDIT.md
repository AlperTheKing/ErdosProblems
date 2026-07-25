# Zero-trust audit of the V7 full unit-column theorem

Date: 2026-07-22

## Verdict

**CONFIRMS the theorem, with one local correction to the submitted proof.**

For positive integers `r1,r2,r3`, with `N=r1+r2+r3` and `1<=k<N`, let
`L_(r,k)(n)` count the integer `3 x (k+1)` transportation tables with row
margins `n(r1,r2,r3)` and column margins `n(N-k,1^k)`.  Independently
reconstructing the coefficient extraction gives

```text
[n]L_(r,k)(n)
 = 3k/2 - sum_i F_k(ri) - sum_(i<j) F_k(ri+rj),

F_k(x) = (1/2) sum_(q=1)^(k-x) q/(x+q)  if x<k,
         0                                if x>=k.
```

In fact `[n]L_(r,k)>=3/2`, with equality exactly when `k=1`.  Thus the
ordinary linear coefficient is positive throughout this family.

The strict inequality in equation (24) of
`FULL_UNIT_COLUMN_TRANSPORT_LINEAR_REFEREE.md` is false when its auxiliary
quantity `S` is zero.  For example, `k=1` and rows `(2,5,7)` give `S=0` and
`[n]L=3/2`, not `[n]L>3/2`.  The repaired non-strict argument below proves a
stronger uniform lower bound and does not affect the theorem or route
decision.

This closes only the V7 unit-column transportation mechanism.  It does not
prove general KTT and produces no LR counterexample.

## 1. Model and dimension

Delete the column of sum `(N-k)n`.  Each of the remaining `k` labelled
columns is a weak triple `(x_l,y_l,z_l)` of sum `n`.  The deleted entries are

```text
n*ri - sum_l x_(i,l),
```

so nonnegativity is equivalent to the three aggregate caps
`sum_l x_(i,l)<=n*ri`.  This is a bijection, including at `n=0`.

All margins are positive.  The real table `x_ij=r_i c_j/N` is strictly
positive, so the affine dimension is the full transportation dimension

```text
3(k+1) - (3+(k+1)-1) = 2k.
```

The bipartite incidence matrix is totally unimodular; hence this is a lattice
polytope and `L` is an Ehrhart polynomial of degree `2k`, not a
quasipolynomial.

Without caps the count is `U(n)=binom(n+2,2)^k`, so `[n]U=3k/2`.  Three cap
violations cannot coexist, since their integer aggregate would be at least
`Nn+3>kn`.  Exact inclusion-exclusion therefore stops after pairs.

## 2. One-cap reconstruction

For a cap `x<k`, set `u_l=n-x_l`.  The other two row entries have `u_l+1`
splittings and violation of the cap is `sum_l u_l<=(k-x)n-1`.  Thus its exact
cumulative extractor is

```text
[z^((k-x)n-1)]
 (1-(n+2)z^(n+1)+(n+1)z^(n+2))^k /(1-z)^(2k+1).
```

Retaining every numerator term whose residual exponent is eventually
nonnegative, differentiating its falling-factorial binomial at zero, and
grouping by the total numerator degree gives

```text
[n]E_x
 = (1/(2k)) sum_(s=0)^(k-x-1) (k-x-s) J_(k,s),

J_(k,s)=binom(k,s) sum_(v=0)^s binom(s,v)2^(s-v)
                         /binom(2k-1,s+v)
       = k/(k-s).
```

The last equality follows by writing the reciprocal binomial as a beta
integral and substituting `u=t(2-t)`.  Hence `[n]E_x=F_k(x)`.  If `x>=k`,
the event and `F_k(x)` are both zero.

## 3. Pair term, chambers, and polynomial continuation

For rows one and two put `s=r1+r2` and `b=k-s`.  The event is empty for
`b<=0`.  Otherwise set

```text
H_n(p,t)=h_n(t,1,pt)=sum_(x+y+z=n) p^z t^(x+z).
```

Introducing the two excess slacks gives the exact count

```text
C_12(n)=[p^(bn-2)t^((k-r2)n-1)]
         H_n(p,t)^k/((1-p)(1-pt)).
```

Direct summation gives

```text
H_n(p,t)=((1-p)-t^(n+1)(1-pt)+p^(n+2)t^(n+1)(1-t))
         /((1-p)(1-t)(1-pt)).
```

If `i` and `j` select the second and third numerator summands, respectively,
the residual coefficient is, with its multinomial and sign suppressed,

```text
K(P,Q)=[p^P t^Q](1-p)^(-alpha)(1-pt)^(-gamma)(1-t)^(-delta),

alpha=i+j+1, gamma=k+1-i, delta=k-j,
P=(b-j)n-2-2j,
Q=(k-r2-i-j)n-1-i-j.
```

Terms `j>=b` or `i+j>=k-r2` have a negative residual exponent for every
`n>=0` and are identically absent.  No other term may be discarded merely
because its residual exponent is negative at a small dilation.

The chamber is fixed eventually because

```text
P-Q=(i-r1)n+i-j-1.
```

Thus `i<r1` gives `P<Q`, `i>r1` gives `Q<P`, and `i=r1` is decided by the
constant.  The chamber wall really occurs: `P=Q` when
`i=r1` and `j=r1-1` (when those indices survive).

For `P,Q>=0` an independent direct coefficient formula is

```text
K(P,Q)=sum_(c=0)^min(P,Q)
 binom(P-c+alpha-1,alpha-1)
 binom(c+gamma-1,gamma-1)
 binom(Q-c+delta-1,delta-1).
```

Partial fractions in `p` reproduce equation (14) of the submitted report for
`P<=Q`, including equality.  The `Q<P` formula is exactly the involution
`(P,alpha)<->(Q,delta)`.  This removes any chamber-boundary ambiguity.

For an affine top, every binomial is the polynomial

```text
binom(lambda*n+c,m)=(lambda*n+c)_(falling m)/m!.
```

At a simple root `0<=c<m`, its linear coefficient is

```text
lambda*(-1)^(m-1-c)/(m*binom(m-1,c)).
```

For `c<0` the same falling-factorial polynomial, not the zero-extended
combinatorial binomial, must be differentiated.  The checker evaluates both
rules independently.

There is no small-`n` inference here.  Each retained term agrees with its
fixed-chamber polynomial for every sufficiently large `n`.  Inclusion-
exclusion consequently agrees eventually with a polynomial, while `L` is
already an Ehrhart polynomial.  Equality at all sufficiently large integers
identifies the polynomials and legitimizes evaluating the continued chamber
polynomials at `n=0` solely to extract `[n]`.

## 4. The terminating identity (no unproved Dixon limit)

As an independent check on the singular hypergeometric step, use
`u=n-x` and `v=n-y`.  The per-column kernel is

```text
G_n(p,q)=sum_(0<=u,v<=n; u+v>=n) p^u q^v
 = (q^(n+1)(1-q)-p^(n+1)(1-p)+(q-p)(pq)^(n+1))
   /((1-p)(1-q)(q-p)).
```

Expanding its rectangular cumulative coefficient and combining the two pole
chambers reduces the derivative of a numerator class to

```text
D_(k,i,j)
 = sum_(h=0)^(i+j) (-1)^h binom(i+j,h)
   * binom(2k-i-j-1-h,k-j-1-h)
   /((2k-h)binom(2k-h-1,k-j-1))

 = j!(k-j-1)!/(2*k!)  if i=0,
   0                    if i>0.
```

Out-of-range ordinary binomials in this finite sum are zero.  To verify the
identity, put `m=i+j`, factor its `h=0` term, and use consecutive-term ratios.
The remaining finite sum is

```text
_3F_2(-2k,j+1-k,-m; -k-j,m+1-2k; 1),
```

which is Dixon's series with `a=-2k`, `b=j+1-k`, `c=-m`.  The series stops at
`m<=k-2`, so neither denominator Pochhammer vanishes in the actual finite
sum.  Replace `a` by `-2k+epsilon` and apply Dixon before taking the limit.
Using

```text
Gamma(-d+epsilon) ~ (-1)^d/(d!*epsilon)
```

shows three numerator poles and four denominator poles when `i>0`, hence the
limit is zero.  When `i=0` there are four on each side; cancelling their
residues gives the displayed factorial value.  This proves, rather than
assumes, the terminating singular limit.  In the opposite coefficient
chamber the second pole family has `b=i-k`; the identical pole count gives
zero for every surviving `i>=1`.

After restoring the multinomial factor, all `i>0` classes vanish.  The
`i=0`, `0<=j<b` class contributes

```text
-(b-j)/(2(k-j)).
```

Therefore

```text
[n]C_12
 = -(1/2) sum_(j=0)^(b-1) (b-j)/(k-j)
 = -(1/2) sum_(q=1)^b q/(s+q)
 = -F_k(r1+r2).
```

Together with inclusion-exclusion and the one-cap result, this proves the
claimed all-parameter formula.

## 5. Repaired uniform positivity

Let `h=N-k>=1` and `d(x)=(k-x)_+`.  Since each fraction in `F_k(x)` is at
most one,

```text
F_k(x)<=d(x)/2.
```

For the pair complementary to row `i`,
`d(r_j+r_l)=(r_i-h)_+`.  Hence twice the six-term correction is at most

```text
S=sum_i ((k-ri)_+ + (ri-h)_+).
```

Each summand is at most `k-1`: if `ri<h`, use `ri>=1`; if
`h<=ri<=k`, it equals `k-h`; and if `ri>k`, use
`ri<=N-2=k+h-2`.  Thus `S<=3k-3` and

```text
[n]L_(r,k) >= 3k/2-(3k-3)/2 = 3/2.
```

If `k>1`, either `S=0` and `[n]L=3k/2>3/2`, or `S>0` and at least one
fraction is strictly below one, again giving `[n]L>3/2`.  For `k=1` all caps
are inactive and equality holds for every positive row triple.

## 6. Homogeneous skew-Kostka-to-LR bridge

Set

```text
A=(N,r2+r3,r3), B=(r2+r3,r3), w=(N-k,1^k).
```

These are partitions and `B` is contained in `A`.  The rows of `A/B` occupy
the disjoint column intervals

```text
[r2+r3+1,N], [r3+1,r2+r3], [1,r3].
```

Thus column strictness is vacuous; row multiplicities determine a unique
semistandard filling.  Those multiplicities are exactly the transportation
table, so `L(n)=K_(nA/nB,nw)`.

Define

```text
R=(N+r2+r3,N+r3,N,k,k-1,...,1),
S=(N,N,k,k-1,...,1).
```

Because `N>k`, both are partitions and `S` is contained in `R`.  Also
`|R|=|A|+|S|`.  The top component of `R/S` is a translate of `B`; its lower
components are horizontal rows of lengths `N-k,1,...,1` in mutually disjoint
columns.  Hence

```text
s_(R/S)=s_B h_(N-k) h_1^k=s_B h_w.
```

Hall adjunction now gives

```text
K_(A/B,w)=<s_(A/B),h_w>=<s_A,s_B h_w>
          =<s_A,s_(R/S)>=c^R_(A,S).
```

Scaling first gives tail sums `nN,nk,n(k-1),...,n`; consequently the bridge
partitions are exactly `nR,nS`, not a re-entry into the unscaled family.
Therefore, including the empty case `n=0`,

```text
L_(r,k)(n)=K_(nA/nB,nw)=c^(nR)_(nA,nS).
```

No dimension, zero-part, alphabet-length, size, or partition-order defect was
found.

## 7. Focused executable replay

`v7_full_unit_column_zero_trust_checker.py` is not a bounded census.  It:

1. compares the direct `K(P,Q)` coefficient with both partial-fraction
   chambers and the wall `P=Q`;
2. differentiates generalized binomials with simple and negative tops;
3. checks every surviving numerator term for the minimal wall case
   `k=4,(r1,r2)=(1,1)`, which contains `P<Q`, `P=Q`, and `Q<P` terms;
4. reconstructs the degree-eight polynomial for rows `(1,1,3)`, with two
   held-out dilations;
5. verifies rank/dimension; and
6. independently enumerates transportation tables, skew tableaux, and LR
   tableaux at homogeneous dilations `0,1,2`.

Replay:

```powershell
python problems_external\ktt_lr_negativity\v7_full_unit_column_zero_trust_checker.py
```

Expected key output:

```text
PASS
verdict=CONFIRMS_THEOREM_WITH_STRICT_STEP_REPAIR
pair_linear_caps_1_1_k4=-5/12
full_linear_rows_1_1_3_k4=85/24
chambers=P<Q,P=Q,Q<P
edge_k1_linear=3/2
dimension_k4=8
payload_sha256=82f09b4e291229b436b1dea5fda3286e92eaca288e0178f8b0fcc5980ef017d1
```

Checker SHA-256:

```text
85552D194928CD7A61A7FA723672B895A2893FE143541BD4CA58024D2A98254B
```
