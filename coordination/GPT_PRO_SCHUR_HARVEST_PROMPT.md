# GPT-Pro Prompt: Schur Harvest Inequality

We are proving the remaining delta=0 step of Erdos Problem #23.  The finite
and algebraic scaffolding is already exact-verified.  The whole proof now
reduces to one per-vertex Schur/Hardy current inequality.

## Setup

Let `G` be triangle-free with a connected `B` maximum cut chosen
`Gamma`-minimal among connected-`B` maximum cuts.  `M` is the set of bad
edges.  For each bad edge `f`, `ell(f)` is the shortest odd-cycle length and
`cyc[f]` is the set of shortest `B`-geodesics closing `f`.

Let `T(v)=sum_f ell(f) p_f(v)` be the load.  Put `N=|V|`,
`O={v:T(v)>N}`, `U=V\\O`, and `a_o=T(o)-N`, `A=sum_{o in O} a_o`.

Build the exact Hardy matrix

```text
H = diag(N-T) + Lstar
```

where `Lstar` is the rational cycle-Hardy Laplacian already accepted by the
exact gates.  Let `h_U` be the harmonic extension with boundary value `h=1`
on `O`, i.e.

```text
H_UU h_U = -H_UO 1_O.
```

Let `S` be the Schur complement of `H` onto `O`, and
`rho_o=sum_{o'} S[o,o']`.  Then

```text
rho_o = -a_o + I_o,
I_o = sum_{u in U} c_ou psi_u,
psi_u = 1-h_u,
c_ou = -H[o,u] >= 0.
```

Also define the direct conductance excess

```text
cU_o = sum_{u in U} c_ou,
e_o  = cU_o - a_o.
```

## Already Exact-Verified

1. Pointwise minority-current target:

```text
a_o <= A-a_o  ==>  25*rho_o >= A-2a_o.
```

This implies the subset Absorption-Hall inequality and hence `H>=0`,
closing delta=0 once proved.

2. Static excess:

```text
a_o <= A-a_o  ==>  5*e_o >= A-2a_o.
```

Full battery, exact rational, zero failures.

3. Broad harvest gate:

```text
a_o <= A-a_o  ==>  25*rho_o >= 4*e_o.
```

Full battery, exact rational, zero failures.  This proves the pointwise target
whenever `A-2a_o <= 4e_o`.

4. High-ratio corner `A-2a_o > 4e_o` appears in exactly one full-battery case:
`MycGrotzsch_N23`, one minority vertex.  The pointwise target still holds
there.  A fixed cloned side of the `2`-blowup violates the target, but CP-SAT
proves that cloned side is not maximum; on an optimal `46`-vertex side the
harvest and target pass.

So the main proof obligation is the harvest inequality:

```text
25*rho_o >= 4*(cU_o-a_o)
```

for every minority overloaded `o`.

In harmonic-defect form this is exactly:

```text
sum_{u in U} c_ou (25*psi_u - 4) >= 21*a_o.
```

Equivalently,

```text
weighted_avg_{c_ou}(psi) >= 4/25 + (21/25)*(a_o/cU_o).
```

## Guardrails / Do Not Propose

- Do not use raw level sets `{phi>t}` without a neutral connected switch:
  exact tests find negative Schur modes on out-of-scope hard-H3 with no
  neutral threshold switch.  Gamma-minimality/minimalized switches are
  load-bearing.
- Do not use scalar Hall or ordinary max-flow; those were refuted.
- Do not use the false companion `rho_o >= e_o/5`; it fails on blowups.
- Do not ignore maxcut/gamma-min scope; cloned blowup sides can fail.

## Request

Give one concrete proof lemma for the harvest inequality:

```text
sum_{u in U} c_ou (25*psi_u - 4) >= 21*a_o
```

using the triangle-free shortest-geodesic structure and `Gamma`-minimality.

The desired answer should specify:

1. the switch or family of switches selected from a harvest violation;
2. why the selected switch is maximum-cut neutral and keeps `B` connected
   after minimalization;
3. why its bad-edge square-length replacement cost is lower, contradicting
   `Gamma`-minimality;
4. an exact-testable finite lemma stated in terms of
   `M, ell, cyc, T, H, h, psi, c_ou`.

Avoid framing only; state the actual finite inequality/switch certificate.
