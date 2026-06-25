# GPT Pro Answer: K=3,T=2 Frontier Reroot Compression

Received via user on 2026-06-20.

## Main Claim

If `T=2` means the global minimum nonedge-codegree is attained at `2`, then
the valid `q=13,K=3,T=2` frontier need not be attacked with the existing
eight-label `K=3` coordinates.

Choose a nonedge `uv` with exactly two common neighbours and reroot at `uv`.
Then `K=2`, `C=N(u)∩N(v)`, and

```
q = 30 - d(u) - d(v) <= 14
```

because `d(u),d(v) >= 8`.  Equality `q=14` occurs exactly when both endpoint
degrees are `8`, so if the full `q=14,K=2,T=2,(A,B)=(6,6)` branch is closed
for the current edge window, all surviving exact-two roots have `6 <= q <= 13`.

This reroot is finite and preserves `G`, `e(G)`, `beta(G)`, and global
codegree constraints.  It does not use terminal-touch equalities.

## Audit Prerequisites

Before excluding `q=14`, the old `q=14,T=2` certificate must be checked for:

1. edge window through `e<=143`, not only the previous cap;
2. independence from the `K=3,T=2` frontier;
3. no use of `terminal_closure` or terminal-touch degree equalities;
4. no circular use of anti-tightness derived from the same `q=14` closure.

If this audit fails, include `q=14` in the new `K=2` four-label search and
disable anti-tightness until `q=14` is independently closed.

## Four-Label Profile Theorem

With `K=2`, labels are

```
E = empty
S1 = {1}
S2 = {2}
D = {1,2}
```

Counts `(c0,c1,c2,c3)` satisfy:

```
c0+c1+c2+c3 = q
c1+c3 >= 6
c2+c3 >= 6
c1>0 => c2>=2
c2>0 => c1>=2
```

Up to exchanging the two colours, only six support families occur:

```
{D}
{S1,S2}
{S1,S2,D}
{E,D}
{E,S1,S2}
{E,S1,S2,D}
```

Allowed `R` edge blocks are:

```
E-E, E-S1, E-S2, E-D, S1-S2
```

The answer gave the following profile counts for `q=6..13`:

```
raw profiles:          231
colour-swap orbits:    161
profile-side instances 297
```

Including `q=14` adds:

```
raw profiles           145
colour-swap orbits      90
profile-side instances  90
```

for at most `387` integrated profile-side instances.

## Static Paired Cuts

For every `W subset R`, define `boundary_R(W)`.

Paired opposite-root cut:

```
M + U + 2 eR - 2 boundary_R(W) >= 70
```

Paired same-root cut:

```
2p + U + M + 2 eR - 2 boundary_R(W) >= 74
```

These are P-template-free, static, linear, and independent of H14 or terminal
closure.

When `c0=0`, `R` is bipartite and taking `W` as one shore gives:

```
M + U >= 70
2p + U + M >= 74
```

## Recommended Experiment

1. Audit `q14/T2` closure against cap143.
2. Add the paired cut families before state construction.
3. Run a P-free skeleton master on the `K=2` four-label profile-side instances.
4. Pass only survivors to the exact A/B state-count quotient.

## Weakest Steps Listed By GPT Pro

1. The reroot reduction requires `T=2` to mean an attained global minimum
   nonedge-codegree.  If `T` is only a lower bound, exact-codegree-two
   existence must be established separately; otherwise the graph is in a
   `T>=3` branch.
2. Excluding `q=14` requires a valid `q14/T2` certificate through edge count
   `143`, independent of anti-tightness and rejected terminal equalities.
3. The profile counts and support-family classification should be checked by
   a generator before being used in proof manifests.
4. The paired cuts are proved and safe, but their computational impact remains
   to be measured.
