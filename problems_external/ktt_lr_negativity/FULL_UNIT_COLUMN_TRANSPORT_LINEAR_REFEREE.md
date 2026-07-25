# Independent referee audit: the full three-row unit-column family

Date: 2026-07-22

## Verdict

Let `r1,r2,r3,k` be positive integers, put `R=r1+r2+r3`, and assume
`R>k`.  Consider the transportation polytope with

```text
row margins    (r1,r2,r3),
column margins (R-k,1^k).
```

If `L(n)` is its Ehrhart polynomial, then its ordinary linear coefficient is

```text
[n]L(n) = 3k/2
           - sum_i F_k(ri)
           - sum_{i<j} F_k(ri+rj),                         (1)

F_k(x) = (1/2) sum_{q=1}^{k-x} q/(x+q)   if x<k,
         0                                if x>=k.          (2)
```

Formula (1) is strictly positive.  In particular, for the symmetric V6
family `r1=r2=r3=a`, `2a<k<3a`, and `b=k-2a`,

```text
[n]C_2(a,k;n)
  = -(1/2) sum_{q=1}^{b} q/(2a+q),                         (3)

[n]L_(a,k)(n)
  = (3a/2)(1+H_k-H_a)
    -(3/2) sum_{q=1}^{b} q/(2a+q)
  > 3(a-b)/2
  > 0.                                                     (4)
```

Thus V6 cannot yield a negative linear coefficient.  This is a theorem about
one family of three-row transportation polytopes.  It does not establish any
other Ehrhart coefficient and does not prove full KTT.

## 1. Projected unit-column model

Project away the column of margin `(R-k)n`.  The remaining `k` labelled
columns are weak triples

```text
(x_l,y_l,z_l),   x_l+y_l+z_l=n,
```

and their aggregate row sums must not exceed `r1*n,r2*n,r3*n`.  With no row
caps there are

```text
U(n)=binom(n+2,2)^k,
[n]U(n)=3k/2.                                             (5)
```

Let `E_i` be the event that row `i` exceeds its cap.  All three events cannot
occur together, since

```text
sum_i Xi = k*n < R*n+3 <= sum_i (ri*n+1).
```

Consequently exact inclusion-exclusion stops after pairs:

```text
L(n)=U(n)-sum_i |E_i(n)|+sum_{i<j}|E_i(n) intersect E_j(n)|. (6)
```

## 2. One-cap term

For a cap `x<k`, reverse the selected row entry in every unit column.  If
`u_l=n-x_l`, the other two entries can be split in `u_l+1` ways and the strict
violation is

```text
sum_l u_l <= (k-x)n-1.
```

Expanding the exact bounded-composition numerator and differentiating its
finite binomial formula gives

```text
[n]|E_i(n)|
 = (1/(2k)) sum_{s=0}^{k-x-1} (k-x-s) J_(k,s),             (7)

J_(k,s)
 = binom(k,s) sum_{v=0}^s binom(s,v)2^(s-v)
                     /binom(2k-1,s+v)
 = k/(k-s).                                                (8)
```

The last identity follows from the beta integral followed by
`u=t(2-t)`.  Substituting `q=k-x-s` in (7) gives exactly `F_k(x)` in (2).
If `x>=k`, the event is empty and both sides are zero.

## 3. Exact bivariate coefficient for a pair violation

It suffices to treat rows one and two.  Put

```text
s=r1+r2,          b=k-s>0.
```

If `b<=0`, the two strict violations are impossible.  For one unit column
define

```text
H_n(p,t)=h_n(t,1,pt)
        =sum_(x+y+z=n) p^z t^(x+z).
```

Write `Z=sum z_l` and `V=sum(x_l+z_l)=kn-Y`.  Multiplication by
`1/((1-p)(1-pt))` introduces two nonnegative slacks.  The coefficient

```text
C_12(n)
 = [p^(bn-2) t^((k-r2)n-1)]
     H_n(p,t)^k / ((1-p)(1-pt))                            (9)
```

is exactly the pair intersection.  Indeed, for a monomial `p^Z t^V`, the
`pt`-slack is `(k-r2)n-1-V=Y-r2*n-1`, and the remaining `p`-slack is
`V-Z-r1*n-1=X-r1*n-1`.  Thus both are nonnegative exactly when both rows
strictly violate their caps.

This is also the point at which an attractive but false shortcut must be
excluded.  Mapping a unit triple to

```text
(n-x,n-y,x+y)
```

produces a column of sum `2n`, but its image additionally satisfies
`u<=n`, `v<=n`, and `u+v>=n`.  It is therefore not an unrestricted
transportation column.  No unrestricted `3 x (k+1)` table interpretation is
used here.

## 4. Rational numerator and the two coefficient chambers

Partial fractions for the complete homogeneous polynomial give the exact
identity

```text
H_n(p,t)
 = ((1-p)-t^(n+1)(1-pt)+p^(n+2)t^(n+1)(1-t))
   /((1-p)(1-t)(1-pt)).                                   (10)
```

In the `k`th power of the numerator, let `i` count copies of the middle
summand and `j` copies of the last summand.  After cancellation against the
denominator, the corresponding term is

```text
(-1)^i binom(k;i,j,k-i-j) K(P,Q),                          (11)

K(P,Q)=[p^P t^Q]
 (1-p)^(-alpha)(1-pt)^(-gamma)(1-t)^(-delta),              (12)

alpha=i+j+1,     gamma=k+1-i,     delta=k-j,
P=(b-j)n-2-2j,
Q=(k-r2-i-j)n-1-i-j.                                      (13)
```

Terms with `j>=b` or `i+j>=k-r2` have a permanently negative residual
exponent and are absent before polynomial continuation.

For `P<=Q`, partial fraction in `p` at the poles `p=1` and `p=1/t` gives

```text
K(P,Q)
 = sum_(m=0)^(alpha-1) (-1)^m binom(gamma+m-1,m)
     binom(P+alpha-m-1,alpha-m-1)
     binom(Q+gamma+delta-1,gamma+delta+m-1)

 + (-1)^alpha sum_(m=0)^(gamma-1) binom(alpha+m-1,m)
     binom(P+gamma-m-1,gamma-m-1)
     binom(Q-P+delta+m-1,delta+alpha+m-1).                 (14)
```

For `Q<P`, the exact formula is obtained by interchanging
`(P,alpha)` with `(Q,delta)`.  These formulas fix the chamber and eliminate
any ambiguity about generalized binomials.

Differentiate (14) after substituting (13).  At every simple zero use

```text
[n] binom(lambda*n+c,m)
 = lambda*(-1)^(m-1-c)/(m*binom(m-1,c)),   0<=c<m.         (15)
```

At negative `c`, use the falling-factorial polynomial convention and its
logarithmic derivative.  The terminating sums reduce to Dixon's identity

```text
_3F_2(a,b,c;1+a-b,1+a-c;1),                               (16)
```

with `a=-2k`.  In the `P<=Q` chamber the parameters are

```text
b=j+1-k,       c=-i-j.                                    (17)
```

In the opposite chamber the two pole families give (17) and

```text
b=i-k,         c=-i-j,                                    (18)
```

respectively.  Taking the terminating singular limit in Dixon's formula
gives zero for every `i>=1`.  For `i=0`, necessarily `P<Q`; the two pole
families contribute, after the multinomial in (11),

```text
(s-j-1)/(2(k-j)),       -(k-2j-1)/(2(k-j)).                (19)
```

Their sum is `-(b-j)/(2(k-j))`.  Therefore

```text
[n]C_12(n)
 = -sum_(j=0)^(b-1) (b-j)/(2(k-j))
 = -(1/2) sum_(q=1)^b q/(s+q)
 = -F_k(s).                                                (20)
```

This also proves that the linear pair correction depends only on `r1+r2`,
not on the split between the two caps.

## 5. Positivity of the final formula

Equations (5)--(8) and (20) inserted into (6) prove formula (1).  It remains
to prove its sign without an asymptotic estimate.

Put `h=R-k>0` and `d(x)=max(k-x,0)`.  Every summand that occurs in (2) is
strictly less than one, so the non-strict bound valid in all cases is

```text
F_k(x)<=d(x)/2.                                            (21)
```

Also

```text
d(ri+rj)=max(r_l-h,0),    {i,j,l}={1,2,3}.                 (22)
```

Hence twice the elementary upper bound for all six correction terms is

```text
S=sum_i ((k-ri)_+ + (ri-h)_+).                            (23)
```

For every positive integral `ri`, the corresponding summand in (23) is at
most `k-1`:

* if `ri<h`, it is `(k-ri)_+<=k-1`;
* if `h<=ri<=k`, it is `k-h<=k-1`;
* if `ri>k` and `ri>=h`, it is `ri-h< R-h=k`, because the other two row
  margins are positive.

Thus `S<=3k-3`.  By (21), the total correction in (1) is at most `S/2`, hence

```text
[n]L(n)>=3k/2-S/2>=3/2>0.                                 (24)
```

## 6. Independent exact replay

The checker
`v6_full_symmetric_transport_referee.py` uses only Python integers and exact
fractions.  It performs all of the following independently:

1. direct reversed one-row and two-row dynamic programs;
2. direct projected-table dynamic programs with all three caps;
3. exact degree-`2k` Newton interpolation;
4. two held-out dilations for every case;
5. the rational numerator term decomposition;
6. both partial-fraction chambers with explicit generalized-binomial
   derivatives; and
7. the closed formulas (1)--(4).

The mandatory symmetric cases give

| `(a,k)` | `[n]C_2` | `[n]L` |
|---:|---:|---:|
| `(2,5)` | `-1/10` | `101/20` |
| `(3,7)` | `-1/14` | `2157/280` |
| `(3,8)` | `-11/56` | `4419/560` |

Two different splits with the same pair sum agree exactly:

```text
[n]C_(1,3;k=7)=[n]C_(2,2;k=7)=-101/210.
```

Five asymmetric full polynomials were independently reconstructed:

| rows | `k` | exact linear coefficient |
|---|---:|---:|
| `(2,3,3)` | 7 | `719/105` |
| `(1,4,4)` | 7 | `1927/280` |
| `(2,2,4)` | 7 | `691/105` |
| `(1,3,5)` | 8 | `3833/560` |
| `(2,4,5)` | 9 | `1921/210` |

All ten held-out values pass.  The checker also compares the direct eventual
coefficient of every surviving numerator term with the appropriate exact
partial-fraction chamber for `(a,k)=(2,5),(3,8),(4,11)`.

Replay from the repository root:

```powershell
python problems_external\ktt_lr_negativity\v6_full_symmetric_transport_referee.py
```

Expected final line:

```text
PASS
```

## Route decision

The entire registered V6 symmetric family, and in fact its arbitrary-row
extension above, has strictly positive ordinary linear Ehrhart coefficient.
Accordingly:

```text
DEAD: full three-row unit-column transportation family has positive linear
coefficient -- exact one-cap/pair-cap formula (1) and bound (24).
```

No LR counterexample is produced.  The homogeneous transportation-to-LR
bridge remains valid but is not triggered.
