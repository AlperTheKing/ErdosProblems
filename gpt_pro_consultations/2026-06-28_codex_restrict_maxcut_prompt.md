# GPT-Pro consult (Codex) — gamma-minimum maxcut restriction lemma for K-closed islands

We are working on Erdős Problem #23. The whole remaining conjecture has been reduced to one scalar inequality, but this consult is for one Schur-condition sublemma.

## Setup

Let `G` be triangle-free on `N` vertices. Choose a maximum cut `sigma` such that:

1. the cut-edge graph `B` is connected;
2. among such maximum cuts, the value
   `Gamma = sum_{bad edge f} ell(f)^2`
   is minimum.

Here a bad edge is a monochromatic edge in the cut. For a bad edge `f=(a,b)`, `ell(f)=d_B(a,b)+1 >= 5`, and `p_f(v)` is the fraction of shortest `a-b` paths in `B` through `v`. Let `K=PP^T`, `T(v)=sum_w K[v,w]`, and `O={v:T(v)>N}`.

A full K-component is a connected component of the graph on vertices with edge `vw` if `K[v,w]>0`. Equivalently, bad-edge geodesic supports do not straddle full K-components.

Schur condition (1) reduces to excluding a critical full K-component `C` contained in `Q={T<=N}` when `O` is nonempty. Such a critical component would have:

`T(v)=N` for every `v in C`, hence
`Gamma_C := sum_{f:supp(p_f) subset C} ell(f)^2 = sum_{v in C} T(v) = N|C|`.

Since `O` is nonempty, `C` is proper, so `|C|<N`. If we could apply the conjecture to the induced island `G[C]`, we would get `Gamma_C <= |C|^2`, contradiction.

The clean induction route therefore needs:

> RESTRICT-MAXCUT, critical-filtered form:
> If `C` is a critical full K-component disjoint from `O`, then the inherited cut `sigma|C` is a maximum cut of `G[C]`.

Even a slightly weaker conclusion enough to apply the smaller-order theorem to `Gamma_C` would work.

## What is known / ruled out

The unfiltered statement is false:

- There are O-empty examples where a proper full K-component has inherited cut smaller than `MaxCut(G[C])`.
- There are examples where the component meets O and inherited cut is not max.

So do not prove the unrestricted statement.

The filtered statement is vacuous on the ordinary exact gate:

- full census N<=11: no bad-carrying K-component disjoint from O with O nonempty;
- named/blow-ups/Mycielskians: none.

But adversarial glued islands do realize filtered noncritical components:

- `C5 island + Myc(C7)` with one bridge has O nonempty and a bad-carrying K-island `C=C5`;
- inherited cut on C is max (`4=MaxCut(C5)`);
- `Gamma_C=25=|C|^2`, but it is noncritical (`T=5` on C while ambient `N=20`).

A false route:

- Full ZMU was proposed: if a cut edge has zero geodesic traffic `mu(e)=0`, then one endpoint has `T=0`. This is false on the glued island bridge: `mu=0` but endpoint loads are `5` and `15/2`.

A weaker possible route:

- SAT-ZMU appears true in exact tests: if `mu(e)=0`, no endpoint has exactly `T=N`.
- Since every B-boundary edge of a full K-component has `mu=0`, SAT-ZMU would directly exclude a critical component boundary. But SAT-ZMU also needs proof.

## Useful elementary inequality

For any subset `X⊂C`, global maxcut/CD gives

`delta_M^C(X) - delta_B^C(X) <= delta_B(X, V\\C)`,

because no bad edge straddles a full K-component. Thus the inherited cut on `C` can fail to be maximum only if the internal improvement is paid for by B-boundary edges.

Gamma-minimality among maximum cuts is the likely extra lever. If flipping some `X⊂C` preserves total cut size (equality in the inequality above), gamma-minimality should rule out a lower-Gamma alternative. The hard case is strict inequality or critical saturation forcing equality somehow.

## Question

Give a rigorous proof of one of these, or a precise counterexample mechanism:

1. Critical RESTRICT-MAXCUT:
   If `C` is a critical full K-component (`T=N` on C) disjoint from O and O is nonempty, then `sigma|C` is a maximum cut of `G[C]`.

2. SAT-ZMU:
   If a B-edge `e` has zero geodesic traffic `mu(e)=0`, then neither endpoint has `T=N`.
   This would also exclude a critical component, since every B-boundary edge of a full K-component has `mu=0`.

3. Direct critical-island contradiction:
   Use triangle-free + maximum cut + gamma-minimality to show no proper full K-component can have `T=N` on every vertex when O is nonempty.

Please give one concrete proof mechanism. Avoid proposing the unrestricted restriction lemma, full ZMU, per-vertex underload charging, fixed finite Neumann truncation, fixed-coefficient SOS, or ordinary subset Hall; all are refuted.
