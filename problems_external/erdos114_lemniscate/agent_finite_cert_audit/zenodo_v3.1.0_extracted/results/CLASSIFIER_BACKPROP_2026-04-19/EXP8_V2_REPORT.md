# EXP8_v2 — Hypercube Leg-4 M_L Kink Test (three-null)

**Date:** 2026-04-19  
**Preregistration:** `TRACK_A_PREREGISTRATION.json` (FROZEN)  
**Wall time:** 2164.3 s  
**Verdict:** **LEG4_FAIL**

## Hypothesis

Delta(eps)/sqrt(n) on the Huang-signed hypercube exhibits a kink at eps = M_L = 0.4804530 that is absent on three geometry-killed nulls (ER_Gnp, sign_randomized_cube, degree_shuffle).

## C1 — Strength ratio (cube / null) ≥ 3 at n ≥ 11

| null | n | cube Δslope | null Δslope | ratio | passes 3× |
|---|---|---|---|---|---|
| ER_Gnp | 11 | 0.1028 | 0.3499 | 0.2939 | NO |
| ER_Gnp | 12 | 0.1035 | 0.3271 | 0.3165 | NO |
| ER_Gnp | 13 | 0.1062 | 0.3133 | 0.3391 | NO |
| sign_randomized_cube | 11 | 0.1028 | 0.5559 | 0.185 | NO |
| sign_randomized_cube | 12 | 0.1035 | 0.5503 | 0.1881 | NO |
| sign_randomized_cube | 13 | 0.1062 | 0.57 | 0.1864 | NO |
| degree_shuffle | 11 | 0.1028 | 0.3302 | 0.3115 | NO |
| degree_shuffle | 12 | 0.1035 | 0.3106 | 0.3334 | NO |
| degree_shuffle | 13 | 0.1062 | 0.2953 | 0.3597 | NO |

**C1 overall:** FAIL

## C2 — Scaling

Cube Δslope by n: n=10:0.101, n=11:0.1028, n=12:0.1035, n=13:0.1062
Cube strictly increasing: **True**

| null | slopes n=10..13 | Spearman ρ | |ρ| ≤ 0.3 |
|---|---|---|---|
| ER_Gnp | 0.3785, 0.3499, 0.3271, 0.3133 | -1 | NO |
| sign_randomized_cube | 0.5397, 0.5559, 0.5503, 0.57 | 0.8 | NO |
| degree_shuffle | 0.3421, 0.3302, 0.3106, 0.2953 | -1 | NO |

**C2 overall:** FAIL

## C3 — Model selection (evaluated at n = 13)

Cube ΔBIC = 485.1 (threshold ≥ 10): **PASS**

| null | ΔBIC at n=13 | ≤ 2 |
|---|---|---|
| ER_Gnp | 445.8 | NO |
| sign_randomized_cube | 496.6 | NO |
| degree_shuffle | 447 | NO |

At least one null ≤ 2: **NO**

**C3 overall:** FAIL

## Verdict

- C1: FAIL
- C2: FAIL
- C3: FAIL

**LEG 4 VERDICT: LEG4_FAIL**