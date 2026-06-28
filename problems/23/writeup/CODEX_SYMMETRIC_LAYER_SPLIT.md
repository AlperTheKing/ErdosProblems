# Symmetric Layer-Split Certificate for ROWSUM-O

Status: candidate for selected/tie-broken gamma-min cuts.  The integer form
is not tie-invariant over all gamma-min cuts.  The fractional shell-crossing
form repairs the first N<=10 tie-cut issue but fails on a later N=11
gamma-min tie cut; do not use SPLIT as an all-cut invariant until this is
reconciled.

## Statement

Fix a gamma-min connected-B maximum cut and a bad edge `f=(a,b)`.
Let

```text
L = ell(f) = d_B(a,b)+1 = 2m+1
```

and let `I_i(f)` be the shortest-geodesic layer:

```text
I_i(f) = {v : v lies on a shortest a-b B-geodesic and d_B(a,v)=i}.
```

Define

```text
A_i(f) = sum_{v in I_i(f)} p_f(v) S(v),
S(v) = sum_g p_g(v).
```

The candidate certificate says that for every bad edge `f` there is an
integer `t` with `1 <= t <= m` such that

```text
OUT_t(f) = sum_{i<t} A_i(f) + sum_{i>=L-t} A_i(f) <= 2t N / L
```

and

```text
CEN_t(f) = sum_{t<=i<L-t} A_i(f) <= (L-2t) N / L.
```

Adding the two inequalities gives `sum_i A_i(f) <= N`, which is exactly
`ROWSUM-O` for `f`.

## Fractional Form

For a tie-invariant version, the fractional shell-crossing variant is the
right relaxation, but current evidence shows it still depends on the chosen
gamma-min cut.
Let

```text
B_t = OUT_t(f) - 2tN/L,
R = ROWSUM(f) - N.
```

An integer split is `R <= B_t <= 0` for some integer `t`.  A fractional split
allows convex averaging between shell splits: find weights `lambda_t >= 0`,
`sum_t lambda_t=1`, such that

```text
sum_t lambda_t OUT_t(f) <= sum_t lambda_t 2tN/L,
sum_t lambda_t CEN_t(f) <= sum_t lambda_t (L-2t)N/L.
```

Adding these two averaged inequalities gives `ROWSUM(f)<=N`.

In the one-dimensional `B_t` notation, this asks that

```text
sum_t lambda_t B_t in [R,0].
```

Equivalently, the scalar interval `[min_t B_t, max_t B_t]` intersects
`[R,0]`.  This formulation is a certificate, not an assumption of ROWSUM:
the lower endpoint condition is exactly the averaged center inequality.

For diagnostics it is convenient to check

```text
min_t B_t <= 0,
max_t B_t >= R,
R <= 0.
```

but a proof should establish the two averaged inequalities directly.

## `{1,2}` Fractional Form

All current gates are consistent with support only on `t=1,2`.  Write

```text
E = A_0 + A_{L-1},
U = A_1 + A_{L-2},
C = A_2 + ... + A_{L-3}.
```

Then

```text
B_1 = E - 2N/L,
B_2 = E + U - 4N/L,
R = E + U + C - N.
```

The `{1,2}` fractional certificate is

```text
conv{B_1,B_2} intersects [R,0].
```

Equivalently:

If `U >= 2N/L`, then `B_1 <= B_2`, so it is enough and necessary that

```text
E <= 2N/L,
C <= (L-4)N/L.
```

If `U <= 2N/L`, then `B_2 <= B_1`, so it is enough and necessary that

```text
E+U <= 4N/L,
U+C <= (L-2)N/L.
```

Thus the proof can be reduced to a three-block shell statement:
endpoints `E`, first-neighbor shells `U`, and deep center `C`.

An even cleaner equivalent form uses the capped first-neighbor buffer

```text
T0 = 2N/L,
H = min(U,T0).
```

The two cases above are exactly equivalent to the two inequalities

```text
E + H <= 2T0 = 4N/L,
C + H <= N - T0 = (L-2)N/L.
```

So the `t=1,2` fractional proof target is:

> The first-neighbor shell `U` can be used as a capped buffer of size `H`;
> the endpoint block plus `H` fits in two shell budgets, and the deep center
> plus `H` fits in the complementary `(L-2)` shell budgets.

This formulation is the current cleanest proof sub-target.

## Why This Is The Right Shape

The pathwise strengthening is false: a shortest `B`-geodesic can have
`sum_{v in P} S(v) > N`.  The first exact witness is

```text
g6 = I?BD@g]Qo, N=10, f=(7,9), path (7,5,8,6,9)
pathload = 32/3 > 10, but ROWSUM(f)=689/75 < 10.
```

Thus the proof must use the `p_f` averaging over the shortest-geodesic
bundle.  Arbitrary prefixes and arbitrary intervals are also false.  The
surviving shape is symmetric: pair endpoint shells with the complementary
center interval.

## Exact Evidence

Probe:

```text
problems/23/writeup/_codex_layer_split_probe.py
```

Local commands:

```text
python problems/23/writeup/_codex_layer_split_probe.py -n 11 --workers 61
python problems/23/writeup/_codex_layer_split_probe.py --witnesses
```

Results:

```text
N<=11 census: graphs=71797 rows=97972 fail_rows=0.
First valid split histogram:
  (L,t)=(5,1): 96879 rows
  (5,2): 1 row
  (7,1): 1068 rows
  (9,1): 23 rows
  (11,1): 1 row

The only census row needing t>1 is:
  g6=J?AEB?cu?}?, N=11, f=(0,5), L=5, t=2.
  Layer contributions:
    (3/2, 8/3, 4/3, 3, 4/3)
  t=1 fails only on the center block, while t=2 succeeds.

Named witnesses incl. J???E?pNu\?[2] and C5[4], C7[3], C9[2], C11[2]:
fail_rows=0.
```

Tie-cut audit:

```text
Integer split is not invariant over all gamma-min cuts.
All-gamma-min-cuts probe through N<=10:
  script: _codex_layer_split_allcuts.py
  first integer failure:
    g6=G?bF`w, side=11111000, f=(0,4), L=5.
    A=(3/2, 2, 1, 2, 1), ROWSUM=15/2<N=8.
    t=1 fails center; t=2 fails outer by 1/10.

Fractional repair:
  script: _codex_layer_fractional_split_allcuts.py
  N<=10 all gamma-min connected-B cuts:
    graphs=6553, cuts=18278, first_frac_fail=None.

The restricted `{1,2}` fractional form also passes this all-cut gate:

```text
python _codex_layer_fractional_split_allcuts.py -n 10 --workers 61 --support12
  graphs=6553, cuts=18278, first_frac_fail=None.
```

Selected-cut case/slack probe:

```text
python _codex_split_case_probe.py -n 11 --workers 61
  rows=97972, hi(U>=T0)=28, lo(U<=T0)=97962.
  Worst gaps for all four case inequalities are 0, attained only by C5.
```

N=11 all-cut caveat:

```text
g6=J?AAFAwe_}?, side=11111010000, N=11.
This is a connected-B max cut and gamma-min cut with M={(1,6),(5,10),(7,10)}
and Gamma=75.

For f=(1,6), L=5:
  A=(1,2,19/7,71/35,47/35), ROWSUM=318/35<11.
  R=-67/35, B_1=-72/35, B_2=-17/7.
Since L=5 there are no other split points, so fractional SPLIT fails on this
tie cut although ROWSUM holds.

This was sent to Claude for independent reconciliation on 2026-06-28.
```

Odd-cycle quotient stress:

```text
Script: problems/23/writeup/_codex_split_bigblowup.py

Named nonuniform C7 cases:
  (3,423,173,7,176,7,423), bad=2: pass.
  (5,715,303,12,304,12,715), bad=0 and bad=6: pass.

Random quotient sweeps, 100000 samples each, C5/C7/C9/C11/C13, N up to 4000:
  split_fails=0 for all five lengths.

Targeted obstruction-shaped C7 sweep:
  samples=200000, quotient_rows=314842, split_fails=0.
  first-valid split histogram: t=1 for 291326 rows, t=2 for 23516 rows.
  Worst best split had outer_gap=0 exactly:
    parts=(7,307,243,11,213,11,307), bad=0, t=1.
```

The restricted `{1,2}` quotient stress also passes:

```text
C5/C7/C9/C11/C13, 100000 samples each, N<=4000: split_fails=0.
Targeted C7 obstruction family, 314842 quotient rows: split_fails=0.
```

The certificate is sharp on odd-cycle blow-ups and on small tight cases.

## Sweep Form

Let

```text
D_t = OUT_t(f) - 2t N / L.
```

The center gap is

```text
CEN_t(f) - (L-2t)N/L = ROWSUM(f) - N - D_t.
```

So the certificate is equivalent to finding a shell `t` with

```text
ROWSUM(f)-N <= D_t <= 0.
```

A proof should therefore be a one-dimensional symmetric shell crossing
argument, not a pathwise or one-sided prefix argument.
