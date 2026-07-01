# Schur Jacobi-6 Harvest Target (Falsified By Larger Blowups)

This was a finite-depth replacement target for the remaining Schur harvest
inequality.  It survives the small census-style battery but fails on larger
canonical C5 blowups, so it is not a valid proof target.  The definitions and
data are kept as a negative datum.

For a gamma-minimal connected-B maximum cut, build

```text
H = diag(N-T) + Lstar
```

as in `_hardy_gate.py`.  Let

```text
O = {v : T(v) > N},       U = V \ O.
```

For `u != v`, write

```text
c_uv = max(0, -H[u,v]).
```

For `u in U`, define

```text
d_u = N - T(u),
D_u = d_u + sum_{w in U, w != u} c_uw + sum_{p in O} c_up.
```

Define Jacobi lower iterates on `U` by

```text
phi^(0)_u = 0,
phi^(k+1)_u =
  (d_u + sum_{w in U, w != u} c_uw phi^(k)_w) / D_u.
```

Since `H_UU` is a Stieltjes M-matrix in the accepted Schur gates, these
iterates are monotone lower bounds for

```text
psi = H_UU^{-1} (N-T)_U.
```

For `o in O`, put

```text
a_o = T(o)-N,
A = sum_{p in O} (T(p)-N),
cU_o = sum_{u in U} c_ou,
e_o = cU_o - a_o,
I6_o = sum_{u in U} c_ou phi^(6)_u.
```

## Falsified Target

For every minority overloaded vertex

```text
a_o <= A - a_o,
```

The attempted target was

```text
25 * (I6_o - a_o) >= 4 * e_o.        (J6-HARVEST)
```

Because `phi^(6) <= psi`, this would have implied the full harvest inequality

```text
25 * rho_o >= 4 * e_o.
```

Together with the static conductance-excess inequality and the recorded
high-ratio guardrail, it would have been enough for the pointwise
minority-current lemma, and hence for the quantitative Absorption-Hall Schur
certificate.

## Current Exact Evidence

Local gate:

```text
python problems/23/writeup/_schur_local_bound_probe.py
```

on 713 O-cuts reported:

```text
Jacobi-5 failures: 496
Jacobi-6 failures: 0
minimum Jacobi-6 margin: approximately 0.137797329
attained at blow(5,4,5,4,5)
```

The purely local star-O harvest bound fails on four small census-8 cuts, and
the one-step full-star bound is much too weak.  The sixth diffusion step is the
first finite-depth certificate surviving this small battery.

Scope check:

```text
hard-H3 non-gamma-min side:
  Jacobi-6 failures: 9 overloaded vertices
  minimum Jacobi-6 margin: approximately -61.4228
```

So J6-HARVEST is not a generic property of the Schur network.  Any proof must
use the gamma-minimal connected-B maximum-cut hypothesis, just as the full Schur
effective-shunt certificate does.

## Larger Blowup Falsification

Direct tests on canonical C5 blowups with side pattern `1,0,1,0,0` and sizes
`[k+1,k,k+1,k,k+1]` show that fixed depth 6 is not blowup-stable:

```text
[5,4,5,4,5],  N=23: min J6 margin  +0.137797329
[6,5,6,5,6],  N=28: min J6 margin  -8.906112387
[7,6,7,6,7],  N=33: min J6 margin -18.456713677
[8,7,8,7,8],  N=38: min J6 margin -28.344313152
[13,12,13,12,13], N=63: min J6 margin -80.299185090
```

Thus any surviving harvest proof must use the full harmonic inverse, or a
diffusion certificate whose depth or form scales with the blowup, not a fixed
six-step Jacobi truncation.
