# Exact q <= 50 equality-face certificate

## Scope

This certificate covers the finite primitive integer equality rays

`a in Z_{\ge 0}^{11}`, `5 <= sum(a) <= 50`,
`gcd(a_0,...,a_10)=1`, and
`min_S q_S(a)=(sum(a))^2/25`,

modulo the dihedral group `D22` and positive integer scaling.  It does not
claim a classification of all real equality rays and it does not solve an SDP.

## Collector completeness in the stated finite scope

Positive `ARCBOUND` implies that the support contains an induced `C5`.
Gamma_11 has 33 induced `C5`s in three `D22` orbits.  The collector therefore
searches vectors positive on one fixed representative from each orbit.  Its
exact branch upper bound cannot discard a completion with
`min_S q_S(a) >= q^2/25`; every surviving leaf is tested against all 56 cuts.
The output is then reduced to primitive rays, canonicalized under `D22`, and
deduplicated.

Only totals divisible by five need be searched because equality makes
`q^2/25` an integer.  The exact run through `q=50` found 439 primitive orbit
representatives:

| q | new orbits | cumulative | nodes | pruned | leaves |
|---:|---:|---:|---:|---:|---:|
| 5 | 3 | 3 | 30 | 0 | 3 |
| 10 | 6 | 9 | 2,517 | 1,720 | 23 |
| 15 | 13 | 22 | 40,579 | 32,884 | 62 |
| 20 | 18 | 40 | 409,847 | 351,546 | 120 |
| 25 | 36 | 76 | 2,346,786 | 2,076,264 | 197 |
| 30 | 33 | 109 | 11,228,038 | 10,109,383 | 293 |
| 35 | 69 | 178 | 38,379,088 | 35,063,068 | 408 |
| 40 | 66 | 244 | 122,221,131 | 112,773,314 | 542 |
| 45 | 99 | 343 | 324,736,850 | 302,160,115 | 695 |
| 50 | 96 | 439 | 810,857,593 | 759,315,043 | 867 |

## Symbolic plateau and face

An independent symbolic enumeration found ten complete induced `C5`-blowup
partitions up to `D22` and the `D10` automorphisms of the five classes.
Enumerating all primitive balanced class-weight grids through total 50 gives
exactly the same 439 canonical rays.  Their support sizes are
`{5: 3, 6: 94, 7: 342}`.

For an equality ray `a`,

`sum_S nu_S(a) * (q^2/25-q_S(a)) = 0`.

Every summand is nonnegative, so a multiplier value is zero for every
non-tight cut.  With nonnegative multiplier coefficients, every multiplier
monomial supported in `supp(a)` is forced to zero.  In parity block `p`, the
Gram kernel vector is represented, up to a common positive square-root
factor, by the integer vector

`v_beta(a)=prod_i a_i^((beta_i-p_i)/2)`.

The cumulative exact face dimensions are:

| q max | rays | forced nu | F2 kernel rank | Gram H rank | Gram face dim |
|---:|---:|---:|---:|---:|---:|
| 5 | 3 | 1,147 | 74 | 1,471 | 7,176 |
| 10 | 9 | 2,051 | 302 | 4,921 | 3,726 |
| 15 | 22 | 2,085 | 399 | 6,092 | 2,555 |
| 20 | 40 | 2,085 | 402 | 6,129 | 2,518 |
| 25 | 76 | 2,085 | 402 | 6,129 | 2,518 |
| 30 | 109 | 2,085 | 402 | 6,129 | 2,518 |
| 35 | 178 | 2,085 | 402 | 6,129 | 2,518 |
| 40 | 244 | 2,085 | 402 | 6,129 | 2,518 |
| 45 | 343 | 2,085 | 402 | 6,129 | 2,518 |
| 50 | 439 | 2,085 | 402 | 6,129 | 2,518 |

Thus the q<=50 face has 526 live multiplier orbit variables and 2,518 Gram
face variables, for 3,044 linear variables before the 56 normalization and
392 coefficient-matching equations.  The face already stabilizes at q<=20.

## Replay

From `E:\Projects\ErdosProblems`:

```powershell
clang++ -O3 -march=native -std=c++17 problems/23/round10/CODEX_R10_c5_FACE_EQUALITY.cpp -o problems/23/round10/CODEX_R10_c5_FACE_EQUALITY.exe
problems/23/round10/CODEX_R10_c5_FACE_EQUALITY.exe 5 50 32 problems/23/round10/CODEX_R10_c5_FACE_EQUALITY_q5_q50.log
python problems/23/round10/CODEX_R10_c5_FACE_EQUALITY.py
python problems/23/round10/CODEX_R10_c5_FACE_EQUALITY_GATE.py
```

The independent gate reparses and exactly checks all 439 rays, validates the
ten complete blowup partitions, replays the incremental F1 and F2 ranks modulo
the independent prime 1,000,003, compares the q=5 layer with the original C5
face, checks all sparse coefficient maps, verifies that all 6,129 exported
Gram rows are genuine weighted equality-kernel equations, and exhibits a
nonzero 6,129-row minor modulo 1,000,003.  It reports
`FINITE_EXACT_GATE_PASS`.

## SHA-256

```text
2038893123CD7C21F728FCD84207DB0C6153A6C879770021964140AAB2A1BE8F  CODEX_R10_c5_FACE_EQUALITY.cpp
9C5DF59D46299CD66916D1EA6BD515CDEF9A0DD97A00CCA106662A9096713163  CODEX_R10_c5_FACE_EQUALITY.exe
13ADE6807DDEA2B2BB6B831F4D4FD85595FA55CBBBC24AFFE27FD3F2B0C79233  CODEX_R10_c5_FACE_EQUALITY_q5_q50.log
8C81549E56E8071AE4C3C18304AEB9B2A34FA8A260B56D8B12CB18FF43795B89  CODEX_R10_c5_FACE_EQUALITY.py
08DC9A3A4A8B5931B67B128CB7FD393EA126BA233CDC208A3675CB650C4FDA0F  CODEX_R10_c5_FACE_EQUALITY_data.npz
735F03D7F7EF3ADBB834CEAA8256F367D5E724147298E8507D2DB9C69E2256D7  CODEX_R10_c5_FACE_EQUALITY_summary.json
D2FE93E8EBB53CED1F5A4590CA059746EC2ECE79983CF12D2424AB3E9D2F6D7D  CODEX_R10_c5_FACE_EQUALITY_REPORT.md
7D659750A1032F90B65211E9CEB0730DB6F742F4A437C92CC1AC477B1609C2F8  CODEX_R10_c5_FACE_EQUALITY_GATE.py
3A692081CCC4B1B10659AF1BDB8442013029F092C350B85BA6B0DB9574331F6C  CODEX_R10_c5_FACE_EQUALITY_GATE.log
```
