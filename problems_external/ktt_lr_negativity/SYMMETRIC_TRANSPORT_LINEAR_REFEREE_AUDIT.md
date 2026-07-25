# Hostile audit of the symmetric unit-column transportation family

## Verdict

The proposed family cannot contain a negative linear Ehrhart coefficient.
For every integer `a >= 3`, its exact linear coefficient is

```text
A(a) = (3a/2) (1 + H_(2a-1) - H_a) > 0.
```

Consequently this direct counterexample route is **DEAD**.  This conclusion is
strictly family-specific: it neither proves KTT nor proves Ehrhart positivity
for arbitrary transportation polytopes.

## 1. Exact count and disjoint inclusion-exclusion

Put

```text
k = 2a-1,       D = 2k = 4a-2.
```

After projecting away the column of margin `(a+1)n`, each of the `k` remaining
columns is a weak composition of `n` into three parts.  The projected row sums
must each be at most `an`.  Two rows cannot violate their bounds
simultaneously: two violations would have total at least `2an+2`, whereas all
unit columns together have total `(2a-1)n < 2an+2`.  Thus

```text
L_a(n) = binom(n+2,2)^k - 3 S_a(n).
```

For one specified bad row, write `y_l=n-x_l` in unit column `l`.  The other two
entries can then be chosen in `y_l+1` ways, and the bad-row inequality becomes

```text
sum_l y_l <= (a-1)n-1.
```

Therefore

```text
S_a(n) = [t^((a-1)n-1)]
         (1-(n+2)t^(n+1)+(n+1)t^(n+2))^k / (1-t)^(D+1).
```

## 2. The finite binomial formula and the small-n trap

Let `i` count selections of `-(n+2)t^(n+1)` and let `j` count selections of
`(n+1)t^(n+2)` in the numerator.  The remaining denominator degree is

```text
q = (a-1-i-j)n - 1-i-2j.
```

If `i+j >= a-1`, then `q<0` for every `n>=0`, so these terms must be omitted.
For `i+j <= a-2`, expansion gives the exact finite formula

```text
S_a(n) = sum_{i,j>=0; i+j<=a-2}
  (-1)^i k!/[i!j!(k-i-j)!] (n+2)^i (n+1)^j
  * binom((a-1-i-j)n + D-1-i-2j, D).                 (1)
```

Formula (1) is valid even at small `n`; it is not merely an eventual identity.
Indeed, for every retained pair its binomial top is nonnegative.  When `q<0`,
that top lies in `{0,...,D-1}`, so both the power-series coefficient and the
falling-factorial polynomial are exactly zero.

There is nevertheless a genuine convention hazard: if the omitted
`i+j>=a-1` terms are retained and their binomials are interpreted as
generalized polynomial binomials after the top becomes negative, one obtains
spurious nonzero terms.  They are absent at the coefficient-extraction stage
and must remain absent.

## 3. Extracting the linear coefficient

For a retained pair set

```text
r = a-1-i-j,       c = D-1-i-2j.
```

Since `0<=c<D`, the constant term of `binom(rn+c,D)` is zero.  Its linear term
is

```text
[n] binom(rn+c,D)
  = r (-1)^(D-1-c) / (D binom(D-1,c))
  = r (-1)^i / (D binom(D-1,i+2j)).
```

The sign cancels the numerator sign in (1), while derivatives of
`(n+2)^i(n+1)^j` contribute nothing because the binomial factor has zero
constant term.  Hence

```text
[n]S_a(n) = sum_{i+j<=a-2}
  k!/[i!j!(k-i-j)!] 2^i (a-1-i-j)
  / (D binom(D-1,i+2j)).                              (2)
```

Every summand in (2) is positive, but the required comparison with the total
term is not immediate from this form.

## 4. Collapse of the double sum

Use

```text
1/(D binom(D-1,l))
  = integral_0^1 x^l (1-x)^(D-1-l) dx.
```

For fixed `m=i+j`, the sum over `i,j` in (2) contains

```text
p = 2x/(1-x),       q = x^2/(1-x)^2,
p+q = (1-x)^(-2)-1.
```

Writing `t=1-x`, then `u=t^2`, gives

```text
[n]S_a(n)
 = (1/2) sum_{m=0}^{a-2}
     binom(k,m)(a-1-m) B(k-m,m+1)
 = (1/2) sum_{m=0}^{a-2} (a-1-m)/(k-m)
 = (1/2) sum_{r=1}^{a-1} r/(a+r).                    (3)
```

The unrestricted-column term has linear coefficient `3k/2`.  Combining it
with (3),

```text
A(a)
 = 3k/2 - (3/2) sum_{r=1}^{a-1} r/(a+r)
 = (3a/2) (1 + H_(2a-1)-H_a).
```

This is strictly positive.  In fact `A(a)>3a/2`, and

```text
A(a) = (3/2)(1+log 2)a - 9/8 + O(1/a).
```

## 5. Independent exact replay

The checker
[`symmetric_transport_linear_referee.py`](symmetric_transport_linear_referee.py)
uses four exact paths:

1. a direct two-dimensional DP over all projected unit columns for `n=0..4`;
2. an independent one-dimensional weighted bad-row DP;
3. the finite binomial sum (1), checked at every interpolation and held-out
   point; and
4. exact Newton interpolation, compared with (2), (3), and the harmonic
   formula.

It gives:

| `a` | degree | exact `A(a)` | direct counts `L(0),...,L(4)` |
|---:|---:|---:|---|
| 3 | 10 | `261/40` | `1, 210, 6978, 91756, 706146` |
| 4 | 14 | `317/35` | `1, 1890, 254187, 9303295, 161119755` |
| 5 | 18 | `3895/336` | `1, 17178, 9287646, 943763230, 36738144180` |

For each case, interpolation used `degree+1` values and passed the two unused
dilations `degree+1` and `degree+2`.

```text
checker SHA-256:
9EC77D0F04B3E506E8482CBFE0A00FCBF37D0883F5E14DA63A586596B545774F

payload SHA-256:
b4f28c6e7d76f38e1ea4c6a736bc0eb144706bba842e476956b1546f634fa838

PASS
```

## Scope conclusion

The calibration value `A(4)=317/35` is correct, but its near cancellation does
not persist toward negativity.  The exact formula proves that the whole
symmetric unit-column family has positive linear coefficient.  No LR replay is
needed because the registered success condition `A(a)<0` never occurs.
