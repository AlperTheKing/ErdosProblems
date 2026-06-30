# Schur Effective-Shunt Status

This note records the status of the proposed Schur effective-shunt domination
certificate.

Let

```text
H = diag(N - T) + Lstar,
O = {v : T(v) > N},
U = V \ O,
S = H_OO - H_OU H_UU^{-1} H_UO.
```

Since `S` is a symmetric Z-matrix in all exact gates, write

```text
S = L_c + diag(r),
r_o = sum_{o'} S[o,o'].
```

For `R={o:r_o<0}`, let `A=L_c+diag(r^+)`. The EC certificate is

```text
Lambda_R := A_RR - A_RP A_PP^{-1} A_PR >= diag(r^-).
```

## Exact Gate

Fresh run:

```text
python problems/23/writeup/_codex_schur_ec_gate.py
```

Result:

```text
O-cuts = 713
noO = 17968
O_hist = {1:286, 2:280, 3:40, 4:14, 5:1, 6:30, 8:62}
R_hist = {0:712, 1:1}
ec_fail = 0
```

The sole negative-row-shunt case is `MycGrotzsch_N23`, side
`10101101011001000000001`, with `O=[1,2,3,10,22]` and the unique negative
row at vertex `22`.

## Interpretation

The EC certificate is a useful final Schur-side certificate, but after the
positive/negative row-shunt split it is algebraically equivalent to `S >= 0`
when the positive-shunt block is nonsingular. It is therefore not yet the
missing combinatorial proof.

The proof-facing target is the mode-wise capacity inequality

```text
Cap(y) := min_{x_U, x_O=y} x^T H x
       >= sum_{o in O} (T(o)-N) y_o^2
```

for every nonnegative overload potential `y`.

## N23 Diagnostic

On the `MycGrotzsch_N23` witness, the Schur ground state `S^{-1}1`,
normalized to value `1` at the apex `22`, is approximately

```text
[0.239468, 0.305466, 0.239468, 0.235275, 1].
```

Simple gauges such as `1/T`, `1/(T-N)`, and `deg/T` do not match this shape.

The worst generalized mixed-mode margin for `S` against the overload diagonal
is approximately

```text
0.007674
```

in ratio form. Equivalently the worst normalized mode has

```text
y^T S y ~= 0.149573,
sum_o (T(o)-N)y_o^2 ~= 19.490262.
```

The best subset/indicator capacity margin on the same witness is much larger,
about `1.191131` at `{22}`. Thus scalar subset Hall has too much slack to see
the true bottleneck; the remaining proof must be genuinely matrix-capacitary.
