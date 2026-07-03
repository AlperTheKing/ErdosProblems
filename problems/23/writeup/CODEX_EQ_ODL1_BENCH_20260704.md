# CODEX EQ-ODL1 Bench — 2026-07-04

## Target

Latest Claude handoff `2026-07-04T00:55Z` retires old sharp `c=2/3` CERT-2 and replaces it with EQ-ODL1:

```text
P_EQ1 = D_EQ * (eta25 - 25*(I_EQ - N)) >= 0
```

Domain: seven-cut inequalities plus CERT-1 bank/grouped generators. Exact arithmetic only.

## Exact falsifier scout

Script:

```text
problems/23/writeup/_codex_eq_odl1_chart_falsifier.py
```

The script evaluates `P_EQ1` by direct exact `Fraction` row-overlap and exact integer `D_EQ` clearing. It enforces:

```text
F1..F7 >= 0
eta25-25 >= 0
UV-T >= 0
UZ-T >= 0
XY-T >= 0
VZ-XY >= 0
VZ-T >= 0
A^2-9T >= 0
B^2-4T >= 0
```

Runs:

```text
python -B problems/23/writeup/_codex_eq_odl1_chart_falsifier.py --bound 2 --random-bound 60 --random-samples 2000 --summary tmp/eq_odl1_chart_falsifier_bound2_rand2k_v1.json
python -B problems/23/writeup/_codex_eq_odl1_chart_falsifier.py --bound 3 --random-bound 100 --random-samples 10000 --summary tmp/eq_odl1_chart_falsifier_bound3_rand10k_v1.json
python -B problems/23/writeup/_codex_eq_odl1_chart_falsifier.py --bound 4 --random-samples 0 --summary tmp/eq_odl1_chart_falsifier_bound4_v1.json
```

Results:

```text
bound2 + random: PASS, no hit
bound3 + random: PASS, no hit
bound4 exhaustive: PASS, no hit
```

Bound4 checked `19,531,250` chart-normalized integer points. Among generator-feasible points, best `P_EQ1` was `375` at the all-ones seed in every chart.

Main artifact:

```text
tmp/eq_odl1_chart_falsifier_bound4_v1.json
```

## Shifted-cone LP scout

Script:

```text
problems/23/writeup/_codex_eq_odl1_shifted_lp.py
```

Generator caps implemented:

```text
F1..F4 multiplier degree <= 10
F5..F7 multiplier degree <= 9
B0_eta25_25 multiplier degree <= 9
CERT-1 grouped generators multiplier degree <= 9
```

Negative-target support model size:

```text
variables = 37,882
constraints = 47,655
target terms = 17,575
target negative terms = 4,169
```

Timed HiGHS runs:

```text
python -B problems/23/writeup/_codex_eq_odl1_shifted_lp.py --support negative --objective sum --max-den 1000,1000000 --time-limit 60 --summary tmp/eq_odl1_shifted_lp_negative_t60_v1.json
python -B problems/23/writeup/_codex_eq_odl1_shifted_lp.py --support negative --objective zero --max-den 1000,1000000 --time-limit 60 --summary tmp/eq_odl1_shifted_lp_negative_zero_t60_v1.json
```

Results:

```text
objective=sum: HiGHS time limit reached, no exact certificate.
objective=zero: HiGHS time limit reached, no exact certificate.
```

Interpretation: no infeasibility claim. The first Rung-1 model builds correctly but needs decomposition, solver tuning, or a smaller certificate support strategy.

## Support-reduction diagnostics

Added scripts:

```text
problems/23/writeup/_codex_eq_odl1_support_diagnose.py
problems/23/writeup/_codex_eq_odl1_reduced_lp.py
```

Support diagnostic:

```text
python -B problems/23/writeup/_codex_eq_odl1_support_diagnose.py --greedy-limit 5000 --summary tmp/eq_odl1_support_diagnose_v2.json
```

Result:

```text
candidate_columns = 37,882
target_negative_terms = 4,169
greedy_columns = 669
greedy_uncovered_terms = 0
```

This shows negative-row coverage can be achieved by a much smaller column set, but coverage alone is not a certificate.

Reduced LP runs:

```text
greedy 669 columns: infeasible, vars=669, constraints=17,579
F5 only: infeasible, vars=3,257, constraints=24,633
F5 + B0_eta25_25: infeasible, vars=6,514, constraints=47,655
F5,F6,F7: infeasible, vars=9,771, constraints=24,905
CERT-1 block: infeasible, vars=20,211, constraints=47,655
CERT-1 block + F5: infeasible, vars=23,468, constraints=47,655
CERT-1 block + F5,F6,F7: stopped after no verdict; reported vars=29,982, constraints=47,655
```

Artifacts:

```text
tmp/eq_odl1_support_diagnose_v2.json
tmp/eq_odl1_reduced_lp_greedy669_zero_t120_v1.json
tmp/eq_odl1_reduced_lp_F5_zero_t120_v1.json
tmp/eq_odl1_reduced_lp_F5_B0_zero_t120_v1.json
tmp/eq_odl1_reduced_lp_F5_F6_F7_zero_t120_v1.json
tmp/eq_odl1_reduced_lp_CERT1block_zero_t120_v1.json
tmp/eq_odl1_reduced_lp_CERT1block_F5_zero_t120_v1.json
```

Interpretation: the certificate is not carried by a single dominant negative-row family or by CERT-1 geometry alone. The next useful move is a smarter mixed support or a chart/KKT split, not simply increasing the same monolithic LP timeout.

## Claude 03:35Z follow-up: linear+B0 and Clarabel

New Claude guidance at `2026-07-04T03:35Z` asked for:

```text
1. Long Clarabel-preferred EQ-ODL1 run.
2. Support reduction by dropping quadratic multiplier columns first, keeping linear F_j deg 10 + B0 deg 9.
```

Added script:

```text
problems/23/writeup/_codex_eq_odl1_clarabel_lp.py
```

Runs:

```text
python -B problems/23/writeup/_codex_eq_odl1_reduced_lp.py --mode generators --generators F1,F2,F3,F4,B0_eta25_25 --objective zero --time-limit 180 --summary tmp/eq_odl1_reduced_lp_F1_F2_F3_F4_B0_zero_t180_v1.json
```

Result:

```text
HiGHS: infeasible, vars=11,157, constraints=47,655
```

Clarabel smoke on the same support:

```text
python -B problems/23/writeup/_codex_eq_odl1_clarabel_lp.py --mode generators --generators F1,F2,F3,F4,B0_eta25_25 --objective sum --time-limit 120 --max-iter 500 --threads 64 --summary tmp/eq_odl1_clarabel_F1_F2_F3_F4_B0_sum_t120_v1.json
```

Result:

```text
Clarabel: PrimalInfeasible, iterations=14, solve_time=59.5625857s
```

Full negative-support Clarabel run:

```text
python -B problems/23/writeup/_codex_eq_odl1_clarabel_lp.py --mode negative --objective sum --time-limit 600 --max-iter 1000 --threads 64 --summary tmp/eq_odl1_clarabel_negative_sum_t600_v1.json
```

Result:

```text
Clarabel: MaxTime, iterations=36, solve_time=623.4103564s
variables=37,882, constraints=47,655, conic rows=85,537, nnz(A)=730,781
```

Additional mixed support:

```text
F1,F2,F3,F4 + CERT-1 block (no F5-F7): stopped after no verdict, vars=28,111, constraints=47,655
```

Interpretation: dropping quadratic columns first is infeasible. Full Rung-1 remains open; Clarabel made progress but did not reach a certificate under 600s. The next technical route is likely either a better mixed support including selected quadratic columns, a warm-start/reweighted Clarabel run, or Rung-2 chart/KKT splitting.

## Seven-cut plus B0 split

Tested the complementary split that keeps all seven cut generators plus the scalar bank, but omits grouped CERT-1 generators.

HiGHS:

```text
python -B problems/23/writeup/_codex_eq_odl1_reduced_lp.py --mode generators --generators F1,F2,F3,F4,F5,F6,F7,B0_eta25_25 --objective zero --time-limit 180 --summary tmp/eq_odl1_reduced_lp_F1_F2_F3_F4_F5_F6_F7_B0_zero_t180_v1.json
```

Result:

```text
HiGHS: time limit, vars=20,928, constraints=47,655
```

Clarabel:

```text
python -B problems/23/writeup/_codex_eq_odl1_clarabel_lp.py --mode generators --generators F1,F2,F3,F4,F5,F6,F7,B0_eta25_25 --objective sum --time-limit 300 --max-iter 1000 --threads 64 --summary tmp/eq_odl1_clarabel_F1_F2_F3_F4_F5_F6_F7_B0_sum_t300_v1.json
```

Result:

```text
Clarabel: MaxTime, iterations=35, solve_time=315.5726256s
vars=20,928, constraints=47,655, conic rows=68,583, nnz(A)=396,384
```

Interpretation: all-seven-cuts plus B0 is neither quickly feasible nor quickly infeasible. Compared with full negative support, the residual behavior still looks hard, so the missing certificate likely needs either selected grouped generators plus selected quadratic columns, or the Rung-2 chart/KKT split.

## Top-k mixed-support selector

Added script:

```text
problems/23/writeup/_codex_eq_odl1_select_support.py
```

The selector ranks columns by exact negative-target monomial repair weight and emits a `greedy` support JSON compatible with `_codex_eq_odl1_reduced_lp.py`.

Runs:

```text
top 200 per generator: selected=2,800, HiGHS infeasible, constraints=18,065
top 500 per generator: selected=7,000, HiGHS infeasible, constraints=19,273
top 1000 per generator: selected=13,669, HiGHS infeasible, constraints=22,546
```

Artifacts:

```text
tmp/eq_odl1_support_top200_allgens_v1.json
tmp/eq_odl1_reduced_lp_top200_allgens_zero_t180_v1.json
tmp/eq_odl1_support_top500_allgens_v1.json
tmp/eq_odl1_reduced_lp_top500_allgens_zero_t180_v1.json
tmp/eq_odl1_support_top1000_allgens_v1.json
tmp/eq_odl1_reduced_lp_top1000_allgens_zero_t240_v1.json
```

Interpretation: score-ranked negative-target repair columns are not sufficient even at 13,669 columns. The missing columns are likely structurally low-score but needed to control positive spillover constraints. Do not continue this support line by merely increasing `top-k`; use a dual/constraint-driven support refinement or move to chart/KKT splitting.

## Full negative-support Clarabel feasibility run

Claude `2026-07-04T05:30Z` approved a long Clarabel run on full Rung-1 negative support. I ran the feasibility-oriented objective-zero variant:

```text
python -B problems/23/writeup/_codex_eq_odl1_clarabel_lp.py --mode negative --objective zero --time-limit 3600 --max-iter 5000 --threads 64 --summary tmp/eq_odl1_clarabel_negative_zero_t3600_v1.json
```

Result:

```text
Clarabel: PrimalInfeasible
iterations=26
solve_time=405.1274344s
variables=37,882
constraints=47,655
conic rows=85,537
```

Interpretation: this is strong numerical evidence that the negative-repair support cone is infeasible, unlike the previous objective=sum run that hit MaxTime. It is not an exact certificate. To make this finite LP infeasibility audit-grade, the next step would be extracting/rationalizing a Farkas dual ray for the selected finite LP, or accepting this as the computational abort signal and moving to the Rung-2 chart/KKT split once specified.
