# GPT-Pro Consult Prompt — Erdős #23 Delta-Zero Crux

I am working on Erdős Problem #23. The finite-N Step-1 certificate is already finished; do not redo it. The remaining graphon/finite blow-up delta-zero conjecture has been rigorously reduced to one inequality.

## Objects

Let `G` be triangle-free on `N` vertices with a fixed maximum cut. Let `B` be the bipartite cut-edge graph and `M` the bad edges. Each bad edge `f=(a,b)` closes an odd cycle of length

```text
ell(f) = d_B(a,b)+1 >= 5.
```

For each bad edge `f`, define `p_f(v)` as the fraction of shortest `a-b` paths in `B` passing through `v`. Then

```text
sum_v p_f(v) = ell(f)
P[v,f] = p_f(v)
K = P P^T
T(v) = sum_w K[v,w] = sum_f ell(f) p_f(v)
```

Let

```text
O = {v : T(v) > N}
Q = V \ O
u(q) = N - T(q) >= 0 for q in Q.
```

The whole proof is now reduced to:

```text
(k2) For every o in O,

T(o)-N <= (1/N) sum_{q in Q} K[o,q] u(q)
          + (1/N^2) sum_{q,q2 in Q} K[o,q] K[q,q2] u(q2).
```

This is exactly the overloaded-vertex part of an explicit Collatz-Wielandt supersolution. All other parts are already proven algebraically:

```text
phi(o)=1 for o in O
phi(q)=1-u(q)/N-(K_QQ u)(q)/N^2 for q in Q
```

On Q, `phi(q)>=0` and `N phi(q)-(K phi)(q)=(K_QQ^2 u)(q)/N^2>=0` are proven. On O, `K phi<=N phi` is exactly `(k2)`. Thus proving `(k2)` proves `rho(K)<=N`, hence `Gamma<=N^2`, hence Erdős #23.

## Verified state

`(k2)` has 0 exact rational violations on the full connected triangle-free census through `N<=11` (756 overloaded cases at N=11), named stress graphs, and overloaded blow-ups to `N=22`. The tightest N=11 exact margin is `5584/9801` on graph6 `J???E?pNu\?`.

## What failed today

1. `k=1` is false. The one-hop inequality

```text
T(o)-N <= (1/N) sum_q K[o,q]u(q)
```

fails on named graphs; two-hop is genuinely needed.

2. A length-5-only simplification is false. There are overloaded witnesses with bad-edge length 7, e.g. `J???CBoBz{?`; however they have huge k2 margin, so long edges are not automatically hard.

3. Edgewise decomposition is false. Let

```text
psi(q)=N u(q)+(K_QQ u)(q)
H_f=sum_{q in Q} p_f(q) psi(q).
```

The tempting bound `H_f >= N^2(ell(f)-4)` fails exactly, e.g. graph `I?BD@g]Qo`, edge `(7,9)`, margin `-221/125`.

4. Stronger delta decomposition is false. Since

```text
sum_f p_f(o) H_f - N^2(T(o)-N)
= sum_f p_f(o)(H_f-N^2(ell(f)-4)) + N^2(N-4S(o)),
S(o)=sum_f p_f(o),
```

I tested the stronger clean form

```text
sum_f p_f(o)(H_f-N^2(ell(f)-4)) >= N^2 max(0, 4S(o)-N),
```

and it fails on graph `J??CA?{{?]?`, overloaded vertex `8`, with `S=2`, `T=14`, margin `-246`. So the positive baseline `N^2(N-4S)` is essential in low-incidence/long-edge overloads.

## Two model witnesses

### Tight high-incidence length-5 witness

Graph `J???E?pNu\?`, N=11:

```text
bad edges: (0,10),(1,10),(8,10), all ell=5
O={7,9,10}
T(7)=35/3, T(9)=T(10)=15
For o=9 or 10:
deficit = 4
one-hop = 380/99 = 3.838...
two-hop = 7168/9801 = 0.731...
margin = 5584/9801.
```

Here one-hop almost covers the deficit; two-hop repairs the small gap.

### Low-incidence long-edge witness

Graph `J??CA?{{?]?`, N=11:

```text
bad edges: (6,10),(7,10), both ell=7
O={8,9,10}
T(o)=14 for all o in O
S(o)=2
deficit=3
one-hop=32/11
two-hop=128/121
margin=117/121.
```

Here overload is length-driven, not multiplicity-driven; the baseline `N^2(N-4S)` dominates after subtracting edge baselines.

## Request

Give one concrete new lemma/proof route for `(k2)`, not a survey. It must use triangle-freeness/max-cut geometry, not just generic nonnegative matrices; random synthetic nonnegative `P` matrices fail `(k2)`.

Helpful directions might include:

- a two-hop corridor-capacity proof for `u` returning to each overloaded `o`;
- a decomposition that treats the two regimes `S(o)<=N/4` and `S(o)>N/4`;
- a layer-by-layer inequality along bad-edge intervals that keeps the necessary edge interactions;
- an SOS/Dirichlet/maximum-principle proof for the explicit `phi` supersolution.

Avoid re-proposing: ordinary Hall/min-cut over fixed corridors, bounded-edge support reductions, per-edge lower bounds, or subset/Crofton cut-metric certificates; all have exact counterexamples.
