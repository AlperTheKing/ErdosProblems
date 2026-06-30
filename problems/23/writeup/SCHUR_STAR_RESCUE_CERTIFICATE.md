# Schur Star-Rescue Certificate

Status: exact-testable proof target for the Schur/Open-Capacity route.

Let

```text
H = diag(N-T) + Lstar
O = {v : T(v) > N}
U = V \ O
S = H_OO - H_OU H_UU^{-1} H_UO
```

on a gamma-minimal connected-B maximum cut, with the same certified rational
cycle coefficients used in `_hardy_gate.py`.

Assume `H_UU` is strictly positive definite.  Then `H >= 0` is equivalent to
`S >= 0`.

## O-Network Form

Write

```text
c_ij = -S_ij                         for i != j,
rho_i = sum_j S_ij.
```

The tested Schur complements have

```text
c_ij >= 0,
```

so

```text
S = L_c + diag(rho),
```

where `L_c` is the graph Laplacian on `O` with conductances `c_ij`.

If all `rho_i >= 0`, then `S` is a symmetric weakly diagonally dominant
M-matrix, hence `S >= 0`.

## One-Negative Star Rescue

Suppose exactly one row sum is negative, say `rho_a < 0`, and all other
`rho_p >= 0`.

Discard all conductances among `O \ {a}` and keep only the star edges
from `a` to `p`.  The discarded conductances form a PSD Laplacian, so it is
enough to prove PSD for the star-plus-killing matrix

```text
S_star = sum_p c_ap (e_a-e_p)(e_a-e_p)^T + rho_a e_a e_a^T
         + sum_p rho_p e_p e_p^T.
```

Eliminating each positive leaf `p` gives the one-dimensional Schur
condition

```text
rho_a + sum_p c_ap*rho_p/(c_ap+rho_p) >= 0.      (STAR)
```

Terms with `c_ap=0` or `rho_p=0` contribute `0`.

Therefore the following finite structural statement implies `S >= 0`:

```text
S_ij <= 0 for i != j,
|{i : rho_i < 0}| <= 1,
and if rho_a < 0 then STAR(a) holds.
```

## Local Exact Gate

Local Codex gate:

```text
census N<=10
Grotzsch
Myc(Grotzsch) N=23
glued C5 chains q=2..15
odd C5 blowups to N<=27
glued island
120 random N=11/12 graphs
```

Result:

```text
O-nonempty cases = 713
row-sum negative count histogram = {0: 712, 1: 1}
STAR failures = 0
```

The only non-diagonal-dominant local case is the Myc(Grotzsch) `N=23`
guardrail with `O=[1,2,3,10,22]`; the negative row is the apex vertex `22`.
There

```text
sum_p c_ap*rho_p/(c_ap+rho_p) ~= 3.2272994593
and
-rho_a ~= 3.2010780475.
```

So the one-star rescue has positive margin.

## Remaining Proof Work

This note does not prove the graph-theoretic content.  It isolates it:

1. Prove `H_UU` is strictly positive definite when `O` is nonempty.
2. Prove `S` is an M-matrix.
3. Prove the row-sum structure and `STAR(a)` inequality above.

The last two items are the current Open-Capacity target.
