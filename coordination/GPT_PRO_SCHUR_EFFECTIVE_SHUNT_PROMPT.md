# GPT-Pro Consult Prompt: Schur Effective-Shunt Proof Target

We are working on Erdős Problem #23, delta=0, after a finite/graphon reduction.
The remaining conjecture-equivalent target is a spectral/ROWSUM inequality.
Please give one concrete proof lemma or certificate class, not a survey.

## Current Schur Certificate

For a connected-B, Gamma-minimal maximum cut in a triangle-free graph, build the
exact rational Hardy matrix

```text
H = diag(N - T) + Lstar,
```

where `T(v)` is the shortest-geodesic load and `Lstar` is the certified
cycle-Hardy Laplacian term with the same rational beta coefficient used in
the exact gates.

Let

```text
O = {v : T(v) > N},
U = V \ O.
```

Assume `H_UU` is strictly positive definite and form the Schur complement

```text
S = H_OO - H_OU H_UU^{-1} H_UO.
```

All exact tests show `S` is a symmetric Z-matrix.  Write

```text
c_ij = -S_ij >= 0  for i != j,
rho_i = sum_j S_ij,
S = L_c + diag(rho).
```

If all `rho_i >= 0`, PSD follows by diagonal dominance.  If exactly one row
sum is negative, say `rho_a < 0`, a star Schur rescue proves PSD if

```text
rho_a + sum_p c_ap*rho_p/(c_ap + rho_p) >= 0,
```

with terms of zero denominator omitted.

## Exact Evidence

Exact Fraction gates:

```text
python problems/23/writeup/_codex_schur_ec_gate.py
python problems/23/writeup/_Rsize_gate.py
```

show:

```text
O-nonempty Schur cuts = 773
R_hist = {0:772, 1:1}
M-matrix failures = 0
S-not-PSD failures = 0
one-terminal scalar failures = 0
```

The only negative-row case is the iterated Mycielskian `MycGrotzsch_N23`,
where the negative row is the apex-like vertex and the star rescue margin is
positive.

Additional inherited max-cut odd-cycle blowup stress:

```text
C5 size vectors entries 1..7, total <=24, bad edge chosen as minimum adjacent product,
plus small C7 sample.
cuts=14092
O-nonempty=3845
Rmax=0
Rhist={0:3845}
Mmat_fail=0
S_notpsd=0
```

So odd-cycle blowups have no negative Schur row at all under the valid max-cut
side.

## Dead Routes To Avoid

Do not propose these:

1. Scalar Hall/subset max-flow for overload capacity.  It is necessary but
   not sufficient for the matrix Schur domination; explicit conductance
   counterexamples pass all indicator cuts while the quadratic form is
   indefinite.
2. Any fixed finite-depth Neumann truncation.  The two-step supersolution
   fails on the N=23 Mycielskian guardrail.
3. A fixed gauge such as `phi=T+1`; exact gate fails on the same N=23 witness.
4. Per-cycle SOS/telescoping that requires `sum_f p_f p_f^T <= N I`; that is
   essentially the original spectral target.
5. Row-side no-two-hole/single-miss geometry.  It is false on hard
   `h_blowup(3)` all-max side; the live row-side route is residual Hall, not
   single-miss.

## Request

Find a proof route for the Schur row-shunt structure:

```text
S is a symmetric M-matrix,
|{i : rho_i < 0}| <= 1,
and if rho_a < 0 then
rho_a + sum_p c_ap*rho_p/(c_ap + rho_p) >= 0.
```

Equivalently, find a graph-theoretic/matrix-capacitary lemma that explains why
two separated negative Schur shunts cannot occur, and why the single negative
shunt is effectively connected strongly enough to the positive shunts.

The lemma must be exact-testable from the existing objects:

```text
M, ell, T, cyc, H, O, U, S, c_ij, rho_i
```

and should be compatible with equality on balanced C5 blowups, where the
relevant null mode is constant and no strict slack should be forced.

Please give a concrete inequality, potential construction, or decomposition
that can be tested exactly before attempting a full proof.
