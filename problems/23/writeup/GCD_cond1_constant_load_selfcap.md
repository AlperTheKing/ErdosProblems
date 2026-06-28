# GCD Cond1: Constant-Load Selfcap Route

Status: **retracted as a broad lemma**. The constant-load selfcap and bridge
targets below are false without an additional saturation/global-overload
hypothesis.

**Correction, 2026-06-28.** GPT-Pro suggested a pinned Wagner construction,
and `problems/23/writeup/_codex_pinned_wagner_counter.py` exact-verifies it:
there is a triangle-free graph with a connected-B maximum cut and a proper
positive K/omega component `C` with

```text
T|_C = 25/2,     |C| = 8,
```

so `lambda <= |C|` fails. The induced cut on `G[C]` has value `8`, while
`MaxCut(G[C])=10`, so the stronger bridge also fails. The pinning edges carry
zero shortest-geodesic traffic, hence they change global maxcut status without
changing `K`, `T`, or `omega` on `C`.

This does **not** falsify the narrower dangerous cond1 case

```text
T|_C = N,     C proper,     O={T>N} nonempty,     omega(C,O)=0.
```

It only kills the broader constant-load shortcut.

Let a gamma-min connected-B maximum cut be fixed. Let `K/omega`
components mean the positive shortest-cycle traffic components, equivalently
the positive `omega` components from the GCD route.

## Retracted Target Lemma

For every proper positive component `C`, if the load is constant on `C`,

```text
T(v) = lambda      for all v in C,
```

then

```text
lambda <= |C|.
```

I called this `CONSTANT-LOAD-SELFCAP`; it is false as stated.

## Why This Is Exactly Useful For Cond1

The grounded-laplacian reduction for

```text
H_QQ = L_omega,QQ + diag(N - T on Q)
```

says that a zero mode exists precisely when some `Q` omega-component has zero
total ground. Such a component has

```text
T(v) = N for every v in C,
omega(C,O) = 0.
```

If `O` is nonempty, this component is proper. A valid saturated replacement
would need to show directly that the special case `lambda=N` cannot be pinned.
The false broad lemma would have given

```text
N <= |C|,
```

contradicting `|C| < N`. Thus this single component lemma proves the `cond1`
positive-definiteness of `H_QQ`.

## Relation To The Induction Bridge

For a component with constant load `lambda`,

```text
Gamma_C := sum_{v in C} T(v) = lambda |C|.
```

Therefore `lambda <= |C|` is the same as

```text
Gamma_C <= |C|^2.
```

One sufficient way to prove this is the stronger bridge. The original form was
stated for gamma-min connected maximum cuts:

```text
the global gamma-min cut restricted to G[C]
is a full gamma-min connected maximum cut of G[C].
```

Then an induction hypothesis / smaller-order SPEC theorem would give
`Gamma_C <= |C|^2`.

The exact evidence suggests an even cleaner version: the restriction bridge
holds for every connected maximum cut, not only the gamma-min member. The
gamma-min hypothesis may therefore be unnecessary for this constant-load
component step.

The bridge is stronger than the selfcap statement. The weaker selfcap
statement is the one actually needed for GCD cond1.

## Exact Diagnostics That Missed The Counterexample

Scripts:

```text
problems/23/writeup/_codex_constant_load_component.py
problems/23/writeup/_codex_constant_load_selfcap.py
problems/23/writeup/_codex_constant_load_selfcap_n11_parallel.py
```

Local results:

```text
census N=7:  const-load comps=24    selfcap_bad=0
census N=8:  const-load comps=88    selfcap_bad=0
census N=9:  const-load comps=448   selfcap_bad=0
census N=10: const-load comps=2406  selfcap_bad=0
census N=11: tested=90842, const-load comps=15205, selfcap_bad=0
```

The glued-island battery also has `selfcap_bad=0` in the local scan, but the
pinned Wagner construction is outside that battery and has `N=26`; it is the
first exact counterexample currently recorded.

The stronger bridge also passes the same local census:

```text
gamma-min maxcuts, N=11:
  tested=90842, const-load comps=15205, bridge_bad=0

all connected maxcuts, N=11:
  tested=90842, const-load comps=15205, allmax_bridge_bad=0
```

## Current Proof Gap

The global maximum-cut property alone does not imply that a component
restriction is a maximum cut of the induced graph, because changing the cut
inside `C` can trade internal edges against boundary B-edges.

The gamma-minimality and constant-load assumptions are the candidate extra
structure. A proof should explain why any internal improvement or lower-Gamma
internal recut would extend to a global maximum cut with smaller Gamma, or else
derive `lambda <= |C|` directly from the positive shortest-cycle traffic
structure.

The statement is not a pure traffic theorem for arbitrary connected-B cuts.
An adversarial scan over all connected-B cuts found a counterexample at

```text
graph H?bFBO{
side = [1,0,1,1,0,1,0,1,0]
C = [0,1,2,4,5,6,7,8]
|C| = 8
lambda = 25/2
```

Thus the maximum-cut / gamma-min hypotheses are load-bearing.

The former sharp target

```text
If a connected maximum cut has a proper positive K/omega component C
with T constant on C, then the restricted cut on G[C] is a maximum cut
of G[C].
```

is false. The remaining possible cond1 induction target must include the
saturation/global-overload assumptions:

```text
SATURATED-PIN-EXCLUSION:
No proper positive K/omega component with T|_C=N, O nonempty, and omega(C,O)=0
can be made globally gamma-min solely by geodesically idle B-pinning.
```

No cond1 closure should be claimed from the broad constant-load bridge.
