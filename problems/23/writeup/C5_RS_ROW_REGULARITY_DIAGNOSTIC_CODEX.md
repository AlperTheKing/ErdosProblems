# C5-RS Row-Regularity Diagnostic

Status: exact diagnostic after Claude's 2026-07-01 row-regularity lead, updated with the stronger C5-LIFT-PMS candidate.

## C5-RS Reparametrization

For a row `Q=(q0,...,q4)` in an all-length-5 K-component, put

```text
s_i = Tw_C(q_i),
tau = 5m/N,
eta = N^2/25 - m,
A = {i : s_i > tau}.
```

Define the inactive deficit

```text
d(Q) = sum_{i notin A} (tau - s_i).
```

Then

```text
sum_i max(0, s_i - tau)
  = sum_i s_i - 5 tau + d(Q)
  = row_sum(Q) - N + (25 eta / N) + d(Q).
```

Therefore C5-RS

```text
sum_i max(0, s_i - tau) <= (1 + 25/N) eta
```

is exactly equivalent to

```text
row_sum(Q) + d(Q) <= N + eta.          (C5-RS')
```

This is the same as the uniform-width net-DW expression
`sum_i max(s_i,tau) <= N+eta`.

## Sharper Exact-Tested Candidate: C5-LIFT-PMS

The diagnostic also tests the stronger inequality

```text
row_sum(Q) + d(Q) <= N + (2/3) eta.      (C5-LIFT-PMS)
```

Equivalently,

```text
sum_i max(s_i,tau) <= N + (2/3) eta.
```

This keeps the correct threshold `tau=5m/N`. It is not the false threshold-shift statement `sum_i(s_i-N/5)_+ <= eta`; Claude exact-falsified that `HL` statement. `C5-LIFT-PMS` is strictly stronger than C5-RS when `eta>0`, and it is tight on the sparse `N=10, m=3` equality atom:

```text
N=10, m=3, eta=1, tau=3/2,
s=[2,34/15,32/15,34/15,2],
row_sum=32/3, inactive_deficit=0,
row_sum + d(Q) - N = 2/3 = (2/3) eta.
```

## Immediate Active-All-Five Case

If all five coordinates are active, then `d(Q)=0`, and C5-RS reduces to the corrected rowwise GERSH bound

```text
row_sum(Q) <= N + eta.
```

If the row is non-overloaded (`row_sum(Q)<=N`), active-all-five is automatic:

```text
sum_i max(0,s_i-tau) = row_sum(Q)-5tau <= N-5tau = 25eta/N,
```

so the C5-RS margin is at least `eta`.

For C5-LIFT-PMS, active-all-five reduces to the sharper row-sum stability

```text
row_sum(Q) <= N + (2/3) eta.
```

## Exact Diagnostic Script

```text
python problems/23/writeup/_codex_c5rs_inspect.py --min-n 8 --max-n 10
python problems/23/writeup/_codex_c5rs_inspect.py --skip-named --min-n 11 --max-n 11
python problems/23/writeup/_codex_c5rs_inspect.py --skip-census
```

The script computes exact Fraction data:

```text
s_i, tau, eta, C5-RS margin, C5-LIFT-PMS margin, row_sum,
inactive_deficit, active set, component size, |cyc[f]|, and p_f(q_i).
```

## Local Results

Named cases plus census `N=8..10`:

```text
rows=80320, over_rows=36, fails=0, lift_fails=0, floor_viol=0.
```

Worst overloaded row:

```text
N=10, m=3, eta=1, tau=3/2,
s=[2,34/15,32/15,34/15,2],
row_sum=32/3, inactive_deficit=0,
C5-RS margin=1/3,
C5-LIFT-PMS margin=0.
```

Census `N=11`:

```text
rows=1045374, over_rows=0, fails=0, lift_fails=0, floor_viol=0.
```

Worst C5-RS row:

```text
N=11, m=4, eta=21/25, tau=20/11,
s=[2,5/2,2,5/2,2],
row_sum=11, inactive_deficit=0,
C5-RS margin=21/25,
C5-LIFT-PMS margin=14/25.
```

Named-only battery:

```text
rows=1436, over_rows=0, fails=0, lift_fails=0, floor_viol=0,
min C5-LIFT-PMS margin=19577/17325.
```

## Proof Split Suggested By The Data

1. Active-all-five non-overloaded rows are algebraic for C5-RS: C5-RS follows from `row_sum<=N`.

2. Overloaded rows in the exact battery are active-all-five and empirically C5-hom; they need the `overload => C5-model` bridge or another row-sum stability argument. C5-LIFT-PMS asks for the sharper active-all-five stability `row_sum<=N+(2/3)eta`, tight at the sparse atom.

3. Active-proper rows have nonzero inactive deficit. C5-RS is exactly the claim that this deficit plus any row overload is paid by `eta`:

```text
(row_sum(Q)-N) + d(Q) <= eta.
```

The sharper candidate says the same debt is paid by only two thirds of the deficit bank:

```text
(row_sum(Q)-N) + d(Q) <= (2/3) eta.
```

4. The self-geodesic floor `p_f(q_i)>=1/|cyc[f]|` is exact and always holds in the diagnostic, but by itself is too weak as an abstract inequality. It must be combined with shortest-geodesic/max-cut structure.

5. If `C5-LIFT-PMS` is globally true, it simultaneously proves C5-RS and recovers the sparse atom equality that originally motivated the seven-cut PMS route, while avoiding the false `N/5` threshold shift.
