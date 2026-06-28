We are working on Erdős Problem #23. Please give one concrete proof mechanism, not a survey.

Context and definitions:

Fix a triangle-free graph `G` on `N` vertices and a connected maximum cut. Let `B` be the cut-edge graph and `M` the monochromatic "bad" edges. Each bad edge `f=ab` has odd-cycle length

```text
ell(f) = d_B(a,b)+1 >= 5.
```

Let `p_f(v)` be the fraction of shortest `a-b` paths in `B` passing through `v`, and define

```text
T(v) = sum_f ell(f) p_f(v).
```

Let the K-support graph join two vertices if they lie together on some shortest bad-edge geodesic; K-components are its components. Let

```text
O = {v : T(v) > N}.
```

The global conjecture has been rigorously reduced to a spectral/ROWSUM inequality. One remaining condition, cond(1), is reduced to the following saturation-qualified lemma:

SAT-ZMU-CONN:
In a gamma-minimal connected-B maximum cut, if `O` is nonempty, `uv` is a B-edge with zero geodesic traffic `mu(uv)=0`, and `T(u)=N`, then the K-component of `u` intersects `O`.

It is convenient to split it into:

A-alltie:
If `mu(uv)=0` and `T(u)=N`, then `T(v)=0`.

C-alltie:
If `O` is nonempty, `T(z)=0`, `zv in B`, and `T(v)=N`, then the K-component of `v` intersects `O`.

Both are exact-verified on the finite gate; what is missing is proof. The C-alltie case is the live target.

Important false routes already killed:

1. O-K-SUPPORT is false globally: it is not true that every positive K-component meets O when O is nonempty.
2. O-K-CONNECTED is false globally.
3. DISCONNECTED-K-SELFCAP `T(v)<=|C|` is false.
4. ONE-BAD-EDGE-ISLAND is false.

Counterexample family to those false routes:
Take `m` copies of C5 sharing a common vertex `0`, plus a disjoint C5, plus one cut bridge. With the natural max cut, for `m=7` we get `N=34`, `T(0)=35>N`, and a separate low-load C5 K-component disjoint from O. This is harmless for cond(1) because the disjoint component is low-load, not saturated/critical.

So do NOT prove any statement forbidding all disconnected positive K-support. The proof must use saturation `T=N` or criticality.

Proposed route to analyze:

Zero-moat prefix switch.

Assume for contradiction:

```text
O != empty,
T(z)=0,
zv in B,
T(v)=N,
and Kcomp(v) is disjoint from O.
```

For a vertex set `S`, flip the cut on `S`. Let

```text
Delta_beta(S) = |delta_B(S)| - |delta_M(S)|.
```

Maxcut gives `Delta_beta(S)>=0`. If `Delta_beta(S)=0` and the new cut-edge graph `B^S` is connected, gamma-minimality gives `Gamma^S >= Gamma`, where

```text
Gamma = sum_{f in M} ell(f)^2.
```

For a bad edge `f=ab` in the positive K-component of `v`, choose a shortest B-geodesic

```text
P=(x_0=a,...,x_{ell(f)-1}=b)
```

through `v=x_i`. A prefix switch on `{x_0,...,x_i}` or `{x_i,...,x_{ell-1}}` rotates the bad edge around the shortest odd cycle: the old bad edge `f` becomes cut, and the exposed path edge becomes bad with the same length `ell(f)`. Therefore the principal square contribution to `Gamma` cancels exactly.

Since `T(z)=0`, no bad geodesic uses the zero-load B-component containing `z`. The idea is to include a connected zero-load moat `Z` containing `z`, disjoint from Kcomp(v), and set

```text
S = prefix union Z.
```

The moat can remove the gate edge `zv` from the new bad-boundary cost and may convert positive cut-loss into a cut-tight switch.

Question:

Can you prove C-alltie by establishing the following zero-moat prefix-switch lemma, or give a sharper replacement?

Lemma target:
Under the contradiction assumptions above, there exists a bad edge `f` in Kcomp(v), a shortest geodesic occurrence through `v`, one of its two oriented prefixes `A`, and a connected zero-load moat `Z` containing `z`, such that for `S=A union Z`:

```text
Delta_beta(S)=0,
B^S is connected,
Gamma^S < Gamma.
```

This would contradict gamma-minimality.

Please focus on a rigorous mechanism for the cut-tightness and strict Gamma descent. A plausible path is a coarea/averaging argument over all shortest-geodesic prefixes through `v`, using `T(v)=N` saturation and `Kcomp(v) cap O = empty` to show one zero-moat prefix is cut-tight and Gamma-decreasing.

Please avoid:
- raw positive-support connectedness;
- `T(v)<=|C|` self-cap;
- one-bad-edge island;
- finite enumeration.

I need one concrete lemma/proof step that can be exact-tested by Claude's rational verifier.
