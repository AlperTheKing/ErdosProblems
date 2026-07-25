# Symmetric unit-column transportation family: exact linear coefficient

Date: 2026-07-22

## Result and scope

For an integer `a >= 3`, let `T_a` be the full transportation polytope with

```text
row margins    (a,a,a),
column margins (a+1,1^(2a-1)).
```

Write `L_a(n)` for its Ehrhart polynomial and put `H_m=sum_(r=1)^m 1/r`.
The ordinary linear coefficient is

```text
A(a) = [n]L_a(n)
     = (3a/2) (1 + H_(2a-1) - H_a).
```

Consequently

```text
A(a) > 0
```

for every `a >= 3`.  Thus the direct family registered in
`APPROACH_REGISTRY_GENERAL_KTT_V5.md` cannot produce a KTT counterexample by
its linear coefficient.  This theorem concerns only that one parametric
family; it does not prove the KTT conjecture.

## 1. Exact finite binomial formula for the Ehrhart polynomial

Set

```text
k = 2a-1,       m = 2k = 4a-2.
```

Project a table to its `k` unit columns.  With no row cap, every unit column
is a weak composition of `n` into three parts, so the unrestricted count is

```text
U_a(n) = binom(n+2,2)^k.
```

The entries in the large column are nonnegative exactly when each row total
in the unit columns is at most `an`.  Two distinct rows cannot both violate
this cap, because the unit columns have total `(2a-1)n < 2an`.  Symmetry and
disjoint inclusion-exclusion therefore give

```text
L_a(n) = binom(n+2,2)^k - 3 S_a(n),                         (1)
```

where, after replacing a selected row entry `x_l` by `y_l=n-x_l`,

```text
S_a(n) = sum_(0<=y_l<=n, sum y_l <= (a-1)n-1) prod_l(y_l+1).
```

Since

```text
sum_(y=0)^n (y+1)t^y
  = (1-(n+2)t^(n+1)+(n+1)t^(n+2))/(1-t)^2,
```

the cap count is

```text
S_a(n) = [t^((a-1)n-1)]
  (1-(n+2)t^(n+1)+(n+1)t^(n+2))^k/(1-t)^(2k+1).             (2)
```

Expanding the numerator of (2) yields the following finite polynomial sum:

```text
L_a(n) = binom(n+2,2)^k
 - 3 sum_(i,j>=0, i+j<=a-2)
       (-1)^i k!/(i!j!(k-i-j)!) (n+2)^i (n+1)^j
       binom((a-1-i-j)n + 2k-1-i-2j, 2k).                  (3)
```

Here the binomial is its usual polynomial extension in the upper argument.
Formula (3) is exact for every `n >= 0`, with one convention that must be made
before polynomial continuation.  Terms with `i+j >= a-1` have a negative
residual exponent for every `n` and must be omitted at the coefficient-
extraction stage.  For every retained pair the binomial top is nonnegative;
if its residual exponent is negative at a small `n`, the top lies in
`{0,...,2k-1}`, so both the power-series coefficient and the displayed
binomial are exactly zero.  Retaining the omitted terms and then applying a
generalized-binomial convention at negative upper arguments would create
spurious terms.

## 2. Extracting the linear coefficient

For a displayed summand put

```text
alpha = a-1-i-j,
beta  = 2k-1-i-2j.
```

Throughout the summation range, `0 <= beta < 2k`, and the zero of
`binom(x,2k)` at `x=beta` is simple.  Direct differentiation of the falling
factorial gives

```text
[n] binom(alpha*n+beta,2k)
  = alpha (-1)^i / (2k binom(2k-1,i+2j)).                  (4)
```

The binomial factor vanishes at `n=0`, so differentiating `(n+2)^i(n+1)^j`
does not contribute.  Its constant term is `2^i`, and the two signs in (3)
and (4) cancel.  Therefore, with

```text
Q(a) = sum_(i,j>=0, i+j<=a-2)
  k!/(i!j!(k-i-j)!) 2^i (a-1-i-j)
  / binom(2k-1,i+2j),                                      (5)
```

we obtain the requested finite formula

```text
A(a) = 3/(2k) (k^2-Q(a)).                                  (6)
```

## 3. Exact collapse of the finite sum

Group (5) by `s=i+j` and define

```text
J_(k,s) = binom(k,s) sum_(j=0)^s
  binom(s,j) 2^(s-j) / binom(2k-1,s+j).
```

The beta-integral identity

```text
1/binom(2k-1,r)
  = 2k integral_0^1 t^r(1-t)^(2k-1-r) dt
```

gives

```text
J_(k,s)
 = 2k binom(k,s) integral_0^1
     t^s(2-t)^s(1-t)^(2(k-s)-1) dt.
```

Under `u=t(2-t)`, the integral is

```text
(1/2) integral_0^1 u^s(1-u)^(k-s-1) du
  = (1/2) s!(k-s-1)!/k!.
```

Hence the inner sum collapses exactly:

```text
J_(k,s) = k/(k-s).                                         (7)
```

Substituting (7) into (5)-(6), and then writing `r=a-1-s`, yields

```text
A(a)
 = (3/2) (k - sum_(s=0)^(a-2) (a-1-s)/(k-s))
 = (3/2) (2a-1 - sum_(r=1)^(a-1) r/(a+r))
 = (3a/2) (1 + H_(2a-1)-H_a).                              (8)
```

Every term in the harmonic tail is positive, proving `A(a)>0`.  In fact,

```text
A(a) ~ (3a/2)(1+log 2),
```

so the positive margin grows linearly with `a`.

## 4. Independent exact replay

The checker
`symmetric_unit_transport_linear_audit.py` uses three exact routes:

1. the finite binomial polynomial (3);
2. a raw two-dimensional convolution of the first two entries in all unit
   columns, followed by all three row-cap tests;
3. a separate one-variable weighted cap convolution, followed by the disjoint
   inclusion-exclusion formula (1).

For `a=3` (dimension 10) and `a=4` (dimension 14), all three counts agree at
every dilation through `d+2`.  Exact Newton interpolation uses `n=0,...,d`;
the last two dilations are held out and both pass.  The reconstructed linear
coefficients are

```text
A(3) = 261/40,
A(4) = 317/35.
```

The uncollapsed finite sum (5), the grouped identity (7), and the harmonic
formula (8) also agree exactly throughout the bounded calibration range
`3 <= a <= 12`; all ten values are positive.

Replay from the repository root:

```powershell
python problems_external\ktt_lr_negativity\symmetric_unit_transport_linear_audit.py
```

Expected headline output:

```text
PASS
a=3 dimension=10 held_out=[11, 12] A=261/40
a=4 dimension=14 held_out=[15, 16] A=317/35
closed_formula=A(a)=(3a/2)*(1+H_(2a-1)-H_a)>0
payload_sha256=fabd84d1efc1c8b439f2f288d35e8e49245b1cd7624bfddf0b2fdc3623353afb
```

Checker SHA-256:

```text
3F47A87D9DF6B0780236E1AE7C343ECB9FFA68E44345332B739BB2809479E6DF
```

## Route decision

The V5 success condition requires `A(a)<0` for an explicit `a`.  Formula (8)
proves the opposite for every member of the family.  Under the registered
exit condition:

```text
DEAD: symmetric unit-column transportation family has A(a)>0 for all a>=3 --
A(a)=(3a/2)(1+H_(2a-1)-H_a).
```

No LR triple is constructed, because no negative member exists in this
family.  The audited transportation-to-LR bridge remains valid; it is simply
not triggered by this route.
