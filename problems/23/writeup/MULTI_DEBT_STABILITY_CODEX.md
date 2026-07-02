# Multi-Row Debt Stability Candidate

Status: exact gate alive. This is not a proof.

## Target

Fix a connected-B, Gamma-minimal maximum cut. Let `M` be the bad edges,
`m=|M|`, and

```text
eta = N^2/25 - m.
```

For a positive K-component `C`, define

```text
Tw_C(v) = sum_{g in M_C} p_g(v).
```

For `f in M_C` and `Q in cyc[f]`, set

```text
row_sum(Q) = sum_{v in Q} Tw_C(v),
debt(Q)   = row_sum(Q) - N.
```

The candidate multi-geodesic stability lemma is:

```text
if |cyc[f]| > 1 and debt(Q) > 0, then

    3 * debt(Q) <= 2 * eta.
```

Equivalently:

```text
row_sum(Q) <= N + (2/3) eta.
```

This is stronger than corrected ROWWISE-GERSH for multi-geodesic rows:

```text
row_sum(Q) <= N + eta.
```

It is intended to pair with the separate unique-long-row mechanism
`Banked-UPO`; the combined split target is:

```text
unique rows: prove by Banked-UPO / long-row bank;
multi rows: prove by 3*debt <= 2*eta.
```

## Evidence

Exact script:

```text
problems/23/writeup/_codex_multi_debt_gate.py
```

Mixed battery:

```text
python problems/23/writeup/_codex_multi_debt_gate.py \
  --max-n 10 --max-cuts 4 --two-lane-max 40 --k-lane-max 20
```

Result:

```text
cuts=15570
rows=67945
multi_rows=64750
multi_positive_debt=8
multi_fail=0
corrected_fail=0
min 2*eta-3*debt = 0
```

The tight multi row is:

```text
graph6: I?BD@g]Qo
N=10, m=3, eta=1
f=(7,9)
Q=(7,5,8,6,9)
row_sum=32/3
debt=2/3
2*eta-3*debt=0
```

Broader direct/named battery:

```text
python problems/23/writeup/_codex_multi_debt_gate.py \
  --skip-census --two-lane-max 120 --k-lane-max 80 --max-cuts 8
```

Result:

```text
cuts=77
rows=835
multi_rows=599
multi_positive_debt=0
multi_fail=0
corrected_fail=0
```

Census `N=11` slice:

```text
python problems/23/writeup/_codex_multi_debt_gate.py \
  --skip-direct --skip-named --min-n 11 --max-n 11 --max-cuts 2
```

Result:

```text
cuts=108730
rows=665101
multi_rows=652293
multi_positive_debt=0
multi_fail=0
corrected_fail=0
```

## Diagnostic

For the tight `I?BD@g]Qo` row, Slack-CAGE is not tight on proper subsets.
The bottleneck is the full row `U=V`:

```text
row_sum=32/3
A=N+eta=11
full margin=1/3
min proper Slack-CAGE margin=2
```

So this candidate targets the nonvacuous full-row GERSH obstruction rather
than interior cage inequalities.

## Exact-Test Request

Please exact-test the candidate:

```text
for every connected-B Gamma-minimum maximum cut,
for every positive K-component C,
for every f in M_C with |cyc[f]| > 1,
for every Q in cyc[f],

    3 * (sum_{v in Q} Tw_C(v) - N) <= 2 * (N^2/25 - m)

whenever the left debt is positive.
```

All terms are the standard `_h.py` / row-list objects:

```text
M, cyc from struct_for_side / shortest-row data
p_g(v) = row incidence fraction from cyc[g]
K-component C from support overlap graph of p_g
Tw_C(v) = sum_{g in C} p_g(v)
m = len(M)
eta = Fraction(N*N,25) - m
```

If this fails, return the first exact row profile and ratio
`debt/eta`. If it passes, this becomes a concrete full-row stability lemma
to prove for the multi-geodesic branch.
