# K2T Lmax Witness-Hall Draft

Status: proof skeleton for the remaining switch-existence lemma.

## Global Target

For a connected-`B` maximum cut, define

```text
R[v] = N*T[v] - (K2*T)[v].
```

The needed contrapositive is:

```text
R[v] < 0
=> there is a neutral B-connected switch S containing v with Gamma(S) < Gamma.
```

The exact-gated canonical form is now:

```text
R[v] < 0
=> an Lmax terminal half-bundle through v has strict witness-Hall surplus.
```

Here

```text
Lmax(v) = max { ell[f] : some Q in cyc[f] contains v }.
```

For each orientation of each `Lmax` row through `v`, define `S` as the union of
the terminal prefixes or the union of the terminal suffixes.

## Terminal Witness Graph

For such an `S`, define:

```text
F(S) = delta_M(S)   # old bad edges crossing S
E(S) = delta_B(S)   # old cut edges crossing S
```

For `f in F(S)` and `e in E(S)`, put `f ~ e` if some shortest row of `f`,
oriented from the endpoint of `f` inside `S`, has `S` as a terminal prefix and
exits through `e`.

Let

```text
lambda_S(e) = min { ell[f] : f ~ e }.
```

A strict witness matching is a perfect matching between `F(S)` and `E(S)` such
that at least one matched pair satisfies

```text
ell[f] > lambda_S(e).
```

This implies

```text
sum_{f in F(S)} ell[f]^2 > sum_{e in E(S)} lambda_S(e)^2,
```

hence `terminal_shadow_psi(S)>0`, hence `Gamma` drops by the exact replacement
identity after the neutral switch.

## Gated Facts

Local battery:

```text
census N<=10 + H?AFBo][2,3,4] + random N11/12 probes
```

Full-battery confirmation by Claude:

```text
census N<=10 + H?AFBo][4] N=36 + random 200
negative sites: 84
Lmax witness-Hall covered: 84
fail: 0
```

Additional local diagnostics:

```text
all Lmax half-bundles through R[v]<0 sites:
  checked: 336
  neutral: 336
  terminal-shadow valid: 336

selected witness graph components:
  checked: 84
  components with #F < #E: 0
  observed components are balanced (#F=#E).
```

## Proof Kernel 1: Component Boundary Identity

Let `C` be a connected component of the terminal witness graph. Define:

```text
Y_C = F(S) vertices in C
X_C = E(S) vertices in C
U_C = union of all terminal prefixes, inside S, of all rows of f in Y_C
```

Exact-gated identity:

```text
delta_M(U_C) = Y_C,
delta_B(U_C) = X_C.
```

This passed:

```text
components checked: 84
failures: 0
```

Expected proof: shortest-geodesic uncrossing. If a boundary edge of `U_C`
landed outside `X_C`, then its row-exit relation would connect `C` to another
witness component. If a crossing bad edge outside `Y_C` entered `U_C`, one of
its terminal rows would share an exit/prefix with `C`, again connecting the
components.

Consequences:

```text
max-cut => |X_C| >= |Y_C| for every component C.
```

Together with neutrality of `S`, this gives component balance:

```text
|X_C| = |Y_C| for every component C.
```

Then the witness graph has a perfect matching componentwise.

## Proof Kernel 2: Lmax Legality And Strictness

The remaining non-formalized implication is:

```text
R[v] < 0
=> every Lmax terminal half-bundle through v is neutral and terminal-shadow valid,
   and at least one such half-bundle has strict witness surplus.
```

The broad statement without `R[v]<0` is false. First counterexample:

```text
graph6 ECpo, N=6, side 111000, vertex 0:
Lmax suffix has delta_B-delta_M = 1 and is not terminal-shadow valid.
```

So the residual hypothesis is essential.

Working contrapositive to prove:

```text
If all Lmax terminal half-bundles through v have no strict surplus
or fail terminal legality, then R[v] >= 0.
```

The exact probes show no simple equality between `-R[v]` and Lmax `Psi`, but
`sum Psi` is always positive when `R[v]<0` in the tested family. Ratios
`sumPsi/(-R[v])` observed:

```text
24, 48, 96.
```

Thus the proof should use positivity/strictness, not an exact scalar identity.

## Current Finish Line

It is enough to prove:

1. Component boundary identity for terminal witness components.
2. `R[v]<0` forces Lmax terminal legality and strict surplus on one side.

Then:

```text
R[v]<0
=> strict witness perfect matching
=> terminal_shadow_psi(S)>0
=> DeltaGamma(S) = -terminal_shadow_psi(S) < 0
```

contradicting `Gamma`-minimality. Therefore `R[v]>=0` for all `v`, giving
`K2T<=NT`, then `rho(K2)<=N`, then the Erdős #23 bound through the already
proved reduction chain.
