# C79: independent complement-form audit of C56

## Verdict

The complement-potential inequality isolated from the C75 ablation is exactly
the existing C56 splitless-closed LP under the substitution `u_n=1-t_n`.
It is therefore not a new proof route.  The independent implementation does,
however, reproduce C56 with a smaller model and gives exact rational dual
certificates at additional tight cutoffs.

Let `u_n in [0,1]`, fix `u_2=u_3=0`, and fix `u_e=1` for every structural
splitless nonseed.  For each admissible factorization `ab=n+1`, impose

\[
u_n\le u_a+u_b.                                         \tag{1}
\]

For every seed-2 edge `p -> c=2p-1`, put

\[
q_c\ge u_p-u_c,\qquad q_c\ge0.                          \tag{2}
\]

The finite target is

\[
\sum_{h\text{ hard-shaped}}u_h\le\sum_c q_c.            \tag{3}
\]

With `t=1-u`, (1) is `t_a+t_b-t_n<=1`, (2) is
`t_c-t_p-q_c<=0`, and (3) is precisely C56 `(SCB)`.  The upper bound on `q`
is omitted because minimization makes it redundant; this forces every dual
boundary multiplier to respect its actual objective capacity.

## Exact finite replay

HiGHS was used only to discover multipliers.  The companion verifier
reconstructs every multiplier as `Fraction` and checks signs, stationarity in
every column, and equality of primal and dual objectives over exact rationals.
All multipliers below are integral.

| X | exact max hard minus boundary |
|---:|---:|
| 26 | 0 |
| 54 | 0 |
| 74 | 0 |
| 100 | -1 |
| 186 | 0 |
| 362 | 0 |
| 500 | -6 |
| 1,000 | -3 |
| 2,000 | 0 |
| 5,000 | -21 |
| 10,000 | -42 |
| 20,000 | -145 |
| 50,000 | -510 |
| 100,000 | -1,301 |

These are finite exact theorems only.  C76 supplies an exact determinant-two
minor and non-TDI objective for the larger C75 model, so neither the observed
integral optima nor the integral objective-specific duals can be promoted by a
generic TU/TDI argument.  Constructing the C56/C79 dual for arbitrary `X`
remains the global arithmetic-bank frontier.

## Reproduction

```powershell
python problems/424/compute/wave5/C79_fractional_boundary.py `
  --limits 26 54 74 100 186 362 500 1000 2000 5000 10000 20000 50000 100000 `
  --output problems/424/compute/wave5/C79_fractional_boundary_100k.json

python problems/424/compute/wave5/C79_exact_dual.py `
  --limits 26 54 74 100 186 362 500 1000 2000 5000 10000 20000 50000 100000 `
  --output problems/424/compute/wave5/C79_exact_dual_100k.json
```

```text
3F6B4A97B96C7967F582F7ABAA5C2F11B8F78417AED7A0955050DA01DB006907  C79_fractional_boundary.py
48C4EE3D851F456F9798F0C87467F4419FAA157E37628C06043707321667FDC7  C79_exact_dual.py
1BE7322D8055645339888FC85DF59279ACB373F518F26776E8593A5965B8C081  C79_exact_dual_100k.json
```
