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

## 2026-07-04 EQ-ODL1 Farkas / full-cone gate update

- Full unrestricted Rung-1 cone sizing probe: `tmp/eq_odl1_full_cone_size_v1.json`.
  - All 15 generators with shifted monomials including constant terms at current caps.
  - `variable_count = 1,755,182`, `target_terms = 17,575`, `target_negative_terms = 4,169`.
  - This exceeds Claude's `~150k` threshold, so no full-cone Clarabel solve was launched.

- Restricted support `F1,F2,F3,F4,B0_eta25_25` infeasibility now has exact rational Farkas replay.
  - Certificate: `tmp/eq_odl1_clarabel_F1_F2_F3_F4_B0_sum_t180_farkas_cert_v1.json`.
  - Checker: `problems/23/writeup/_codex_eq_odl1_farkas_cert_check.py`.
  - Checker output: `tmp/eq_odl1_farkas_cert_check_F1_F2_F3_F4_B0_v1.json`.
  - Verdict: `ok=true`, `variables=11157`, `constraints=47655`, `min_ATy=1663/83370000`, and exact `b^T y < 0`.

- The strict conic-stationarity replay remains false after independent rounding of both Clarabel dual blocks. The exact artifact uses the correct finite-LP Farkas gate `y >= 0`, `A^T y >= 0`, `b^T y < 0`.

## 2026-07-04 EQ-ODL1 Rung-2 chart stats

- Seed-ray digit verifier: `problems/23/writeup/_codex_eq_odl1_seed_ray_verify.py`.
  - Output: `tmp/eq_odl1_seed_ray_verify_v1.json`.
  - Exact identities verified: `I_EQ-N`, `D_EQ`, `eta25=25`, `P_EQ1(t)`, and nonnegative shifted `t=1+u` coefficients.

- Chart/triviality scaffold: `problems/23/writeup/_codex_eq_odl1_rung2_charts.py`.
  - Output: `tmp/eq_odl1_rung2_chart_triviality_v1.json`.
  - `300` dominance-band chart labels checked.
  - `0/300` close by `P_k` Bernstein coefficients alone.

- Band-only LP pass: `problems/23/writeup/_codex_eq_odl1_rung2_band_lp.py`.
  - Output: `tmp/eq_odl1_rung2_band_lp_all_v1.json`.
  - `20` height-chart/band cases, all HiGHS infeasible, no timeouts.
  - Therefore `0/300` dominance-band labels close at band-only stage.

- Full dominance LP size probe: `tmp/eq_odl1_rung2_full_dominance_size_v1.json`.
  - Degree-9 Bernstein multiplier count on the 10-variable simplex: `48620`.
  - Degree-10 band multiplier count: `92378`.
  - Direct full dominance LP size per chart label: `1,502,358` variables.
  - All 300 materialized directly: `450,707,400` variables.

### Rung-2 reduced-support full dominance smoke (Codex)
- Added `problems/23/writeup/_codex_eq_odl1_rung2_support_lp.py`.
- Model: degree-2 homogenized generators/deltas, degree-9 generator and delta multipliers, degree-10 band multiplier, degree-11 Bernstein residual.
- Support mode `negative`: inverse-select columns that directly repair negative degree-11 Bernstein target slots.
- Smoke chart `(k=0, dominant=B0_eta25_25, band=near_2s_minus_1)`:
  - target negative Bernstein slots: 2086
  - variables: 43128
  - constraints: 167960
  - sparse nnz: 1545048
  - HiGHS sum-objective status: feasible/optimal within 60s
  - float nonzeros: 2687
  - exact replay: not yet certified; high-denominator attempts still leave tiny negative residuals (`-8/562741619` at max_den=1e8; `-344/24197889639` at max_den=1e10)
- Margin objective on same support timed out at 120s; zero objective timed out at 60s.
- Artifact: `tmp/eq_odl1_rung2_support_lp_smoke_k0_B0_near_highden_v1.json`.

### Rung-2 reduced-support cached k=0 hard-dominant sweep
- Script now caches prepared chart data per height chart.
- Command artifact: `tmp/eq_odl1_rung2_support_lp_k0_hard3_bands_v1.json`.
- Scope: `k=0`, dominants `B0_eta25_25`, `G6_A2_9T`, `G7_B2_4T`, both bands, negative-support inverse-selected columns, sum objective, 60s per LP.
- Result: 6 rows; 3 floating-feasible; 3 timeouts; 0 exact replays.
- Near band rows feasible for all three dominants. Infinity band rows timed out for all three dominants at 60s.
- Representative sizes: 42.6k-47.2k variables, 167,960 constraints, 1.07M-1.55M nonzeros.

### Rung-2 infinity-band solver-method comparison
- Row: `k=0`, dominant `B0_eta25_25`, band `inf_1_minus_2s`, negative-support selected columns.
- Size: 42,631 variables; 167,960 constraints; 1,540,078 nonzeros.
- `method=highs`, sum objective, 240s LP cap: timeout.
- `method=highs-ds`, sum objective, 240s LP cap: timeout.
- `method=highs-ipm`, sum objective, 240s LP cap: timeout.
- Artifacts:
  - `tmp/eq_odl1_rung2_support_lp_k0_B0_inf_t240_v1.json`
  - `tmp/eq_odl1_rung2_support_lp_k0_B0_inf_highsds_t240_v1.json`
  - `tmp/eq_odl1_rung2_support_lp_k0_B0_inf_highsipm_t240_v1.json`

### Rung-2 exact reconstruction attempt for first feasible chart
- Added `problems/23/writeup/_codex_eq_odl1_rung2_basis_replay.py` for highspy basis extraction and exact-core probe.
- Added `problems/23/writeup/_codex_eq_odl1_rung2_scipy_core_probe.py` for SciPy active-core diagnostics.
- Target chart: `k=0`, dominant `B0_eta25_25`, band `near_2s_minus_1`, negative-support reduced LP.
- Highspy direct solve/basis extraction attempts:
  - simplex, presolve off: stopped after exceeding practical window before result.
  - simplex, presolve on: stopped after exceeding practical window before result.
  - ipm, presolve on, 64 threads: stopped after exceeding practical window before result.
- SciPy core diagnostics on same row:
  - LP success; objective `3727.7482899220886`; positive columns `2687`.
  - tight rows at residual tolerance `1e-8`: `162614`, not square.
  - nonzero inequality dual rows at `1e-9`: `3238`, not square against 2687 positive columns.
  - Active-core exact replay was therefore not attempted; basis selection remains unresolved.
- Artifacts:
  - `tmp/eq_odl1_rung2_scipy_core_probe_k0_B0_near_v1.json`
  - `tmp/eq_odl1_rung2_scipy_core_probe_k0_B0_near_dual_v1.json`

### Rung-2 SciPy active-core QR diagnostics
- Target chart: `k=0`, dominant `B0_eta25_25`, band `near_2s_minus_1`.
- Dual-active rows at `dual_tol=1e-9`: 3,238.
- QR row-selection on dual-active submatrix:
  - `x_tol=1e-9`: positive cols 2,687; rank 2,676; no square independent core.
  - `x_tol=1e-7`: positive cols 2,686; rank 2,675; no square independent core.
  - `x_tol=1e-5`: positive cols 2,586; rank 2,576; no square independent core.
- Conclusion: the SciPy feasible solution is structurally degenerate; simple positive-support/dual-row basis replay is not enough.
- Artifacts:
  - `tmp/eq_odl1_rung2_scipy_core_probe_k0_B0_near_qr_v1.json`
  - `tmp/eq_odl1_rung2_scipy_core_probe_k0_B0_near_qr_xtol1e7_v1.json`
  - `tmp/eq_odl1_rung2_scipy_core_probe_k0_B0_near_qr_xtol1e5_v1.json`

### Rung-2 infinity-band reduced-form probes per Claude 10:30Z
Target row: `k=0`, dominant `B0_eta25_25`, band `inf_1_minus_2s`.
Implemented support flags in `_codex_eq_odl1_rung2_support_lp.py`:
- `--no-deltas`: omit dominance delta families.
- `--leading-s0-only`: keep only degree-2 Bernstein generator coefficients with simplex `s` exponent 0, used as the leading homogeneous face model.

Results:
- `--no-deltas --leading-s0-only`: 9,031 vars, 135,274 nnz, HiGHS infeasible (not timeout). Artifact `tmp/eq_odl1_rung2_support_lp_k0_B0_inf_leads0_nodelta_v1.json`.
- `--no-deltas` full generators: 20,455 vars, 390,094 nnz, 60s timeout. Artifact `tmp/eq_odl1_rung2_support_lp_k0_B0_inf_nodelta_fullgen_v1.json`.
- `--leading-s0-only` with deltas restored: 13,567 vars, 329,674 nnz, HiGHS infeasible (not timeout). Artifact `tmp/eq_odl1_rung2_support_lp_k0_B0_inf_leads0_withdelta_v1.json`.

Interpretation: the strict s=0 Bernstein-face encoding of "leading homogeneous generator multipliers" is numerically infeasible on the test row, even with deltas. This may indicate a spec deviation or that the leading-homogeneous encoding should not be the raw Bernstein face-support filter.

### Rung-2 numeric-map driver smoke
- Added `problems/23/writeup/_codex_eq_odl1_rung2_support_map.py`.
- Multiprocessing pool with `workers=2` is blocked by Windows sandbox (`WinError 5` creating multiprocessing Pipe).
- Serial smoke command artifact: `tmp/eq_odl1_rung2_support_numeric_map_smoke_2charts_v2.json`.
- Scope: charts `0,5`, dominants `B0_eta25_25,G6_A2_9T`, both bands, negative support, sum objective, 20s cap.
- Result: 8 rows; feasible_numeric 3; timeouts 5; infeasible 0; other_failure 0.
- This validates the map format; full parallel map needs subprocess-style parallelism or unsandboxed multiprocessing approval.

### Rung-2 exact replay: perturbation objective opens square core
- Added deterministic objective modes to `_codex_eq_odl1_rung2_scipy_core_probe.py`: `lex-small`, `lex-large`, `family`.
- Target chart: `k=0`, dominant `B0_eta25_25`, band `near_2s_minus_1`.
- `lex-small` result:
  - LP success.
  - positive columns: 2,686.
  - dual-active rows: 3,239.
  - QR row-selection from dual-active rows: rank 2,686.
  - selected square core exists in floating arithmetic.
  - artifact: `tmp/eq_odl1_rung2_scipy_core_probe_k0_B0_near_lexsmall_qrskip_v1.json`.
- Exact solve attempt on the 2,686 x 2,686 selected rational core was launched and stopped after a bounded attempt; SymPy dense LU is too slow for this size.
- Remaining blocker is efficient exact solve/export of the selected sparse rational core, not basis degeneracy.
