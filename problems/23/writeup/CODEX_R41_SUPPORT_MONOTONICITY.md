# R41 support-monotonicity lemma

## Setup

Fix one cut and one selected shortest-row tuple `omega`. Replace one selected
row

```text
Q  = (..., x, m, y, ...)
```

by the two-edge detour

```text
Q' = (..., x, v, y, ...).
```

All row edges except `xm,my` versus `xv,vy` agree. A genuine attachment
detour assumes `xv` and `vy` are blue active edges before the replacement, so
neither belongs to `selectedSupport(omega)`.

Let `u` be the number of old edges among `{xm,my}` whose only selected-row
occurrence is `Q`. Then `u` is in `{0,1,2}` and

```text
|selectedSupport(omega')| = |selectedSupport(omega)| + 2 - u.    (1)
```

Indeed, the two active edges are genuinely new support edges; the only support
edges that can disappear are `xm,my`, and each disappears exactly when no
other selected row contains it.

## Induced-row bridge

A shortest four-edge blue geodesic is induced. If two of its vertices are
joined by a blue edge, they must be consecutive; otherwise that edge shortcuts
the geodesic to length at most three.

Consequently, for a blue edge `ab`,

```text
pairCount_omega(a,b) >= 2
```

implies that after replacing one selected row containing `ab`, another
selected row still contributes the actual edge `ab` to selected support.
Thus:

```text
pairCount_omega(m,x) >= 2  -> xm does not disappear,
pairCount_omega(m,y) >= 2  -> my does not disappear.              (2)
```

## Consequences

From (1), selected-support cardinality never decreases along an attachment
detour.

If the R38 multiplicity-saturation conditions

```text
pairCount_omega(m,x) >= 2,
pairCount_omega(m,y) >= 2
```

hold, then `u=0` by (2), and support cardinality increases by exactly two.
Such a transition cannot lie on a directed cycle of row tuples.

More generally, every directed neutral cycle has constant support cardinality
on every transition. Hence every transition on it has `u=2`, so both old
middle edges are unique selected-row occurrences. The target tuple therefore
frees the ordered pairs `(m,x),(x,m),(m,y),(y,m)`, while covering the analogous
pairs through the new middle `v`.

Therefore the strict multiplicity-saturated neutral square rotor proposed in
R38 is not graph-realizable. Any remaining zero-exposure rotor must instead be
a fully unsaturated source-swap rotor in which every newly freed physical half
is immediately matched or component-blocked in its target state.

## Exact gate

The bounded real gate in `tmp/fanout/r41_rotor_realization/` enumerates a
33-vertex maximum-cut cage with nine complete row families and all 144 row
tuples. It checks 32 saturated swaps and finds zero support-persistence
failures. Manifest SHA-256:

```text
1A8A538DDDBB6F61CDBCE18CB7D1B787620EEAB56E68035B497A89EB95FDD7CE
```

The remaining proof target is the source-swap case, not the saturated rotor.
