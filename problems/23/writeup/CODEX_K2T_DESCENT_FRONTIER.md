# K2T Descent Frontier

> RETRACTED 2026-07-01: this route targets the false statement
> `K2*T <= N*T` / `R[v]>=0` on gamma-min cuts.  The two-lane `L=12`
> construction has a unique gamma-min connected maximum cut with
> `rho(K2)>N` and `R[v]<0` on nine vertices while `Gamma<=N^2`.
> Do not use this file as an active proof target.  The live target is
> `LOAD-PSC-5`, recorded in `LOAD_PSC_CAPACITY_TARGET_CODEX.md`.

This note records the current proof-facing target after the ROWSUM/SPEC and
fixed-coefficient harvest routes were ruled out by exact gates.

## Verified Reduction

For a connected-`B` maximum cut, let `M` be the bad edges, `cyc[f]` the
shortest `B`-geodesics closing `f`, and `ell[f]` the corresponding odd-cycle
length.  Let

```text
K2[v,w] = sum_f Pr_{Q in cyc[f]}[v,w in Q]
T[v]    = sum_f ell[f] Pr_{Q in cyc[f]}[v in Q].
```

The exact gate

```text
python problems/23/writeup/_k2t.py
```

reported:

```text
gamma-min cuts tested: 18814
K2*T <= N*T VIOLATIONS: 0
```

The reduction chain is:

```text
K2*T <= N*T on support(T)
=> rho(K2) <= N                 (Collatz-Wielandt)
=> rho(K) <= N                  (K <= K2 by Jensen)
=> Gamma = 1^T K 1 <= N^2.
```

Vertices with `T[v]=0` have zero row and column in `K2`, so the
Collatz-Wielandt step applies on the positive support of `T` without a
reducibility hole.

Thus the single remaining theorem can be stated as:

```text
gamma-min cut => R[v] := N*T[v] - (K2*T)[v] >= 0 for all v.
```

Equivalently, prove the contrapositive:

```text
R[v] < 0
=> there exists a neutral connected switch S containing v
   with Gamma(after flipping S) < Gamma(before).
```

## Exact Construction Gate

The current selected switch family is the length-bundle half-switch:

For a vertex `v`, a length `L`, and an orientation, collect all rows
`Q in cyc[f]` with `ell[f]=L` and `v in Q`.  The switch is the union of either
all terminal prefixes ending at `v`, or all terminal suffixes starting at `v`.

Exact gate:

```text
python problems/23/writeup/_construction_gate.py
```

The lighter gate

```text
python problems/23/writeup/_codex_k2t_switch_probe.py --min-n 5 --max-n 9
```

reported:

```text
negative-residual vertices: 21
covered by neutral B-connected Gamma descent: 21
NO-SWITCH: 0
```

The full construction proof should therefore target:

```text
R[v] < 0
=> some length-bundle half-switch S(v,L,orientation)
   is neutral, B-connected after flip, and Gamma-decreasing.
```

## Candidate Selection Lemma

Use the terminal overload coarea identity only as a guide, not as a raw
selector.  For row atoms
`a=(f,Q)` with mass `mu_a=1/|cyc[f]|`, define for each length and orientation
the terminal-bundle overload

```text
Omega_{L,eps}(v)
  = sum_x omega_{L,eps}^v(x) * (T[x]-N)
    - (m_L(v)/2) * (T[v]-N).
```

Then

```text
-(R[v]) = sum_L (Omega_{L,-}(v) + Omega_{L,+}(v)).
```

So if `R[v]<0`, at least one terminal bundle has positive `Omega`.
The proof should select a peak bundle, for example maximizing

```text
Omega_{L,eps}(v) / (L*m_L(v)).
```

Guardrail: the raw peak terminal-overload selector is already false in the
exact gates.  The working selector is a **completed seed+moat switch**:

```text
R[v] < 0
=> there exists a length-bundle half-switch seed A through v
   and a set S = A or S = A union {z}
   such that S is neutral, B-connected after flip, terminal-shadow valid,
   and Psi(S)>0.
```

Existing exact gate evidence is recorded in
`MOAT_SELECTOR_PROOF_TARGET.md`:

```text
negative: 193
covered: 193
added histogram: {0: 165, 1: 28}
fail: 0
```

When the moat vertex `z` is needed, observed profiles are:

```text
(boundary_delta(A), boundary_delta({z}), boundary_delta(S), e_B(z,A), e_M(z,A))
= (4,0,0,2,0) or (2,0,0,1,0).
```

Thus the selector theorem to prove is not "peak bundle works"; it is:

1. `R[v]<0` produces a length-bundle seed `A` with positive square surplus
   after completion.
2. If `A` is not already neutral and connected, a single cut-neutral moat
   vertex `z` internalizes the seed's excess `B`-boundary without adding old
   bad adjacency to the seed.
3. The completed switch `S` is terminal-shadow valid and has `Psi(S)>0`.

## Gamma Drop Once Hall Is Known

For a completed neutral terminal-shadow switch `S`, write

```text
C = delta_M(S)
E = delta_B(S)
Wit(f) = exits e in E used by terminal rows of f
lambda(e) = min{ell[f] : e in Wit(f)}.
```

If the witness graph `C--E` has an SDR saturating `E`, and one matched witness
is strict, then

```text
Psi(S) = sum_{f in C} ell[f]^2 - sum_{e in E} lambda(e)^2 > 0.
```

The verified switch identity gives

```text
Gamma(after flipping S) <= Gamma(before) - Psi(S).
```

So the remaining Hall theorem is:

```text
Terminal-Shadow SDR:
Every neutral terminal-shadow switch arising as a peak length-bundle switch
has a matching from exits E to crossing bad edges C through Wit.
```

The strongest current proof routes are:

1. **Biconvex interval Hall.**
   Prove a no-reentry lens ordering of crossing bad edges and exits, then show
   any Hall-critical subset can be chosen as an interval whose prefix hull
   contradicts max-cut.

2. **Selected-switch star-door fan.**
   For the blue-closed bad-subset hull of the selected peak switch, prove the
   one-hub door-set trichotomy: every extra bad edge opens either no extra
   exit, one extra exit, or all extra exits, and full-door edges cover missing
   singleton exits.

The attached "no-two-hole residual corridor" lemma is best treated as a
component-local sublemma for route 1: two missed exits in one residual
co-witness component should force either a shorter-row lens or a negative
stage-0 rare exchange.  It is not currently the primary global statement,
because the selected peak-switch hypothesis is the essential scope.
