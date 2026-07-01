We are working on Erdős Problem #23. The request below concerns only the final
delta=0 proof target after all reductions. Please do not propose scalar Hall
transport, fixed-depth Neumann truncation, terminal degree equalities, or
no-two-hole/single-miss residual-corridor lemmas; all have exact counterexamples
or are known dead ends in our gates.

## Setup

Let `G` be triangle-free. Choose a connected maximum cut `B`, tie-broken to
minimize

```text
Gamma = sum_{f in M} ell(f)^2
```

among connected maximum cuts. Here `M` is the set of bad (monochromatic) edges
and `ell(f)` is the odd-cycle length obtained from a shortest blue path between
the endpoints of `f`.

For each bad edge `f`, let `cyc[f]` be the set of all shortest blue geodesics
between its endpoints, and define the load

```text
T(v) = sum_f ell(f) * Pr_{Q in cyc[f]}[v in Q].
```

The remaining conjecture is implied by the PSD inequality

```text
H := diag(N-T) + Lstar >= 0,
```

where `N=|V(G)|` and

```text
Lstar = sum_f beta'_ell(f)/|cyc[f]| * sum_{Q in cyc[f]} L_Q.
```

`L_Q` is the ordinary cycle Laplacian of the shortest odd cycle `Q plus f`, and
`beta'_ell <= ell/(2+2cos(pi/ell))` is a certified rational lower coefficient.
The local circulant identity gives `N I - K2 >= H`.

Let

```text
O = {v : T(v) > N},    U = V \ O.
```

Assume `H_UU` is nonsingular Stieltjes, and form the Schur complement

```text
S = H_OO - H_OU H_UU^{-1} H_UO.
```

In all exact gates, `S` is a symmetric Z-matrix. Write

```text
c_ij = -S_ij >= 0  (i != j),
rho_i = sum_j S_ij,
S = L_c + diag(rho).
```

Let

```text
a_o = T(o)-N > 0,
A = sum_{o in O} a_o.
```

Also let `h` be the harmonic extension with `h_O=1` and
`H_UU h_U = -H_UO 1`. Then

```text
rho_o = (Hh)_o = -a_o + I_o,
```

where `I_o=(Lstar h)_o` is the Hardy current absorbed at overloaded terminal
`o` from the non-overloaded block.

## Exact empirical target

The strongest current target, exact-verified on the full battery, is:

### Schur Absorption-Hall

For every subset `X subset O`,

```text
a(X) <= A-a(X)  ==>  rho(X) >= 0.
```

Equivalently, every non-strict-majority overload set absorbs at least its own
overload:

```text
a(X) <= A-a(X)  ==>  I(X) >= a(X).
```

Exact gates:

```text
python problems/23/writeup/_schur_absorption_hall_gate.py
```

Local result:

```text
O-cuts = 713
subset checks = 12053
hall_fail = 0
R_not_MAJ = 0
R_hist = {0:712, 1:1}
```

Claude independent result:

```text
708 O-cuts
12043 subset checks
hall_fail = 0
R_hist = {0:707, 1:1}
```

This implies `{rho_o<0}` has size at most one. If a singleton negative row
exists, `S>=0` follows from the direct star rescue

```text
rho_a + sum_{p != a} c_ap*rho_p/(c_ap+rho_p) >= 0,
```

which is exact-verified in the sole current non-diagonally-dominant case
`MycGrotzsch_N23`.

Important guardrail: the Schur statement is false for arbitrary connected
maximum cuts. A hard `h_blowup(3)` side has six negative row sums and `S` not
PSD, but exact enumeration shows it is not `Gamma`-minimal. Gamma-minimality is
essential.

## Request

Give one concrete proof route for Schur Absorption-Hall:

```text
a(X) <= A-a(X)  ==>  rho(X) >= 0.
```

Please express the argument in the graph/geodesic language above, not as a
generic M-matrix fact. Ideally use the harmonic-current form:

```text
rho(X) = -a(X) + I(X),
I(X) = Lstar-current from X to U when h_O=1.
```

The expected mechanism is a Gamma-minimality contradiction: if a non-majority
set `X` has `rho(X)<0`, a harmonic-threshold / coarea switch should be
cut-neutral and Gamma-decreasing. I need the actual finite lemma: what switch is
selected, why it is maximum-cut neutral, and why its square-length replacement
cost is lower.

Please make the proposed lemma exact-testable from the objects
`M, ell, cyc, T, H, S, rho, c_ij`, and state any required sub-quantities
explicitly.
