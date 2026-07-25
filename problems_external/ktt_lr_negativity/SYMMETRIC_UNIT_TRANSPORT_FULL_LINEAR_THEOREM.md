# Full symmetric unit-column transportation family: exact linear coefficient

Date: 2026-07-22

## Result and exact scope

For integers `a>=1` and `1<=k<=3a-1`, let `T_(a,k)` be the full
`3 x (k+1)` transportation polytope with

```text
row margins    (a,a,a),
column margins (3a-k,1^k).
```

Write `L_(a,k)(n)` for its Ehrhart polynomial.  Its ordinary linear
coefficient is strictly positive throughout this entire two-parameter family.
In the only nontrivial double-cap range, put

```text
b=k-2a,                 1<=b<=a-1.
```

Then the exact formulas are

```text
[n]C1(a,k;n) =  (1/2) sum_(r=1)^(a+b) r/(a+r),
[n]C2(a,k;n) = -(1/2) sum_(r=1)^b     r/(2a+r),              (1)
```

and hence

```text
[n]L_(a,k)(n)
 = (3/2) [a-b + a(H_k-H_a) + 2a(H_k-H_(2a))] > 0.           (2)
```

The positivity is immediate: `a-b=3a-k>=1` and both harmonic tails are
nonnegative.  In particular,

```text
[n]L_(a,k)(n) >= (3/2)(3a-k) > 0.                            (3)
```

This proves that the complete symmetric unit-column family registered in
`APPROACH_REGISTRY_GENERAL_KTT_V6.md` cannot furnish a negative linear
coefficient.  It does **not** prove KTT outside this family.

## 1. Inclusion-exclusion and the one-cap term

Project away the column of margin `(3a-k)n`.  Each of the remaining `k`
columns is a weak composition `(x_l,y_l,z_l)` of `n`, and the projected row
sums must be at most `an`.  Let `U`, `C1`, and `C2` respectively denote the
unrestricted count, the count in which one specified row exceeds `an`, and
the count in which two specified rows exceed `an`.  Since `k<3a`, three row
sums cannot all exceed their caps.  Therefore

```text
L_(a,k)(n)=U(n)-3C1(a,k;n)+3C2(a,k;n),
U(n)=binom(n+2,2)^k,
[n]U(n)=3k/2.                                                (4)
```

For `C1`, reverse the selected entry by `u_l=n-x_l`.  The other two entries
can then be chosen in `u_l+1` ways, and with `h=k-a` the bad-row condition is

```text
sum_l u_l <= hn-1.
```

Exactly as in the V5 calculation, expansion of

```text
[t^(hn-1)]
 (1-(n+2)t^(n+1)+(n+1)t^(n+2))^k/(1-t)^(2k+1)
```

followed by one beta integral gives

```text
[n]C1(a,k;n)
 = (1/2) sum_(s=0)^(h-1) (h-s)/(k-s)
 = (1/2) sum_(r=1)^h r/(a+r).                               (5)
```

If `k<=a`, all three caps are automatic.  If `a<k<=2a`, pair intersections
are empty, so (4)-(5) already give

```text
[n]L_(a,k)(n)=(3a/2)(1+H_k-H_a)>0.                          (6)
```

It remains to derive `C2` when `2a<k<3a`.

## 2. Exact bivariate generating function for `C2`

For two specified violating rows put

```text
u_l=n-x_l=y_l+z_l,       v_l=n-y_l=x_l+z_l.
```

Both violations are equivalent to

```text
sum_l u_l <= (k-a)n-1,  sum_l v_l <= (k-a)n-1.
```

For one column the bivariate enumerator is

```text
sum p^u q^v = h_n(p,q,pq).
```

Set `q=pt`, `h=k-a`, and `b=k-2a`.  Since

```text
h_n(p,pt,p^2t) = p^n h_n(t,1,pt),
```

cumulative coefficient extraction gives the exact identity

```text
C2(a,k;n)
 = [p^(bn-2) t^(hn-1)] h_n(t,1,pt)^k/((1-p)(1-pt)).         (7)
```

The needed complete homogeneous polynomial has the three-term numerator

```text
h_n(t,1,pt)
 = ((1-p)-t^(n+1)(1-pt)+p^(n+2)t^(n+1)(1-t))
   /((1-t)(1-pt)(1-p)).                                    (8)
```

Let `i` count copies of the middle summand in (8), and `j` copies of the last
summand.  Terms with `j>=b` or `i+j>=h` have a negative residual exponent for
every `n` and are absent.  For all remaining pairs, the eventual polynomial
term is

```text
(-1)^i k!/[i!j!(k-i-j)!] Phi_(i,j)(n),

Phi_(i,j)(n)
 = [p^P t^Q]
   1/((1-p)^(i+j+1)(1-t)^(k-j)(1-pt)^(k-i+1)),              (9)

P=(b-j)n-2-2j,
Q=(h-i-j)n-1-i-j.
```

Equality for all sufficiently large `n` is enough here: both sides of (7)
are polynomial functions of `n`, so their polynomial continuations agree.

## 3. The bivariate cone lemma

The load-bearing calculation is

```text
[n]Phi_(i,j)(n) =
  -(b-j)/(2(k-j) binom(k,j)),   if i=0,
   0,                            if i>=1.                    (10)
```

Here is an exact derivation.  For positive `A,B,C` and `P<=Q`, direct
Vandermonde convolution gives the chamber polynomial

```text
[p^P t^Q](1-p)^(-A)(1-t)^(-B)(1-pt)^(-C)
 = sum_(m=0)^(B-1) (-1)^m
     binom(Q+B-1-m,B-1-m)
     binom(C+m-1,m)
     binom(P+A+C-1,A+C+m-1).                                (11)
```

For `i<a`, (9) lies in this chamber for large `n`.  Differentiate (11) at
`n=0`.  The last binomial has a simple zero.  After `r=k-j-1-m`, the remaining
finite sum is

```text
S_(i,j)=sum_(r=0)^(i+j) (-1)^r binom(i+j,r)
  binom(2k-i-j-1-r,k-j-1-r)
  /((2k-r) binom(2k-r-1,k-j-1)).                            (12)
```

Factoring its `r=0` term turns (12) into

```text
R_0 * _3F_2(
  -2k, j+1-k, -i-j;
  -k-j, i+j+1-2k; 1),                                      (13)

R_0=(2k-i-j-1)!(k+j)!/((k-i)!(2k)!).
```

This is exactly Dixon's terminating sum: its lower parameters are
`1-2k-(j+1-k)=-k-j` and `1-2k-(-i-j)=i+j+1-2k`.  Apply Dixon's gamma quotient
with a generic parameter in place of `-2k` and take the pole-free terminating
limit.  Since `i+j<k`, no denominator in the finite sum vanishes, and the
limit is

```text
S_(i,j) = 0,                                      i>=1,
S_(0,j) = j!(k-j-1)!/(2k!)
          = 1/(2(k-j)binom(k,j)).                           (14)
```

Thus (10) follows in the `P<=Q` chamber.  If `i>=a`, then `Q<P` eventually;
for `i=a` this is already forced by

```text
Q-P=1+j-a<0,
```

because `j<=b-1<=a-2`.  Interchanging the two coefficient variables in
(11), deleting its initial zero ranges, gives two terminating sums.  They are
again Dixon sums, with parameter lists

```text
(-2k, j+1-k, -i-j; -k-j, i+j+1-2k)
```

and

```text
(-2k, i-k, -i-j; 1-k-i, i+j+1-2k).
```

The same pole-free limiting evaluation is zero for every `i>=1`.  This proves
(10) in the opposite chamber as well.  No interpolation or asymptotic
approximation enters the cone lemma.

Multiplying (10) by the multinomial factor in (9) leaves only `i=0`:

```text
[n]C2(a,k;n)
 = -sum_(j=0)^(b-1) (b-j)/(2(k-j))
 = -(1/2) sum_(r=1)^b r/(2a+r).                             (15)
```

This is the requested closed double-cap formula.

## 4. Positivity and asymptotics

Substitution of (5) and (15) into (4) gives

```text
[n]L_(a,k)(n)
 = (3/2) [k
   - sum_(r=1)^(a+b) r/(a+r)
   - sum_(r=1)^b r/(2a+r)]
 = (3/2) [a-b+a(H_k-H_a)+2a(H_k-H_(2a))].                  (16)
```

Every summand in the final expression is nonnegative and `a-b>=1`, proving
the sign uniformly.  If `k/a -> rho` with `2<rho<3`, then

```text
[n]L_(a,k)(n)
 = (3a/2)(3-rho+log(rho)+2log(rho/2))+O(1),                 (17)
```

whose displayed leading constant is positive.  The exact lower bound (3) is
stronger than any asymptotic sign claim near a fixed finite parameter.

## 5. Exact replay

The checker `symmetric_unit_transport_full_audit.py` uses independent raw
two-dimensional convolution for all dilations `0,...,2k+2`, exact Newton
interpolation only through `2k`, and the final two dilations as heldouts.  It
also evaluates the numerator expansion (7)-(9) independently and replays both
finite chamber identities over all 66 open pairs with `2<=a<=12`.

| `(a,k)` | degree | `[n]C1` | `[n]C2` | `[n]L` | heldouts |
|---:|---:|---:|---:|---:|---:|
| `(2,5)` | 10 | `43/60` | `-1/10` | `101/20` | `11,12` |
| `(3,7)` | 14 | `241/280` | `-1/14` | `2157/280` | `15,16` |
| `(3,8)` | 16 | `657/560` | `-11/56` | `4419/560` | `17,18` |

The heldout `L` values are

```text
(2,5): n=11 -> 763437753;          n=12 -> 1647393046
(3,7): n=15 -> 461631388202848;    n=16 -> 1055733509225079
(3,8): n=17 -> 130446487442150037; n=18 -> 302870652007962475
```

Replay from the repository root:

```powershell
python problems_external/ktt_lr_negativity/symmetric_unit_transport_full_audit.py
```

Expected payload SHA-256:

```text
2cf9b20044eff0c0e3b487d7688120ce9f5d998ab6c373f57aadd69390991d37
```

## Route decision

The registered family has no negative linear coefficient.  Under the V6 exit
condition:

```text
DEAD: full symmetric unit-column family has nonnegative linear coefficient --
[n]L=(3/2)(a-b+a(H_k-H_a)+2a(H_k-H_(2a)))>0.
```

The audited homogeneous transportation-to-skew-Kostka-to-LR bridge remains
valid, but it is not triggered because this family contains no negative
linear coefficient.
