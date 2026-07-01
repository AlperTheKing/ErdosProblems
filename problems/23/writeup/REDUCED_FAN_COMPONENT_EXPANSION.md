# Componentwise Reduced Fan Expansion Candidate

This is a sharper candidate replacement for the NL leaf-descent target in
`NO_NAKED_LEAF_RFC_TARGET.md`.

## Setup

Use the same blue-closed prefix hull data:

```text
C = delta_M(S)
E = delta_B(S)
X subset C
Y = Wit(X)
U0 = union Pref_S(f,e), f in X, e in Wit(f)
U = cl_B^S(U0)
B+ = delta_B(U) \ Y
M+ = delta_M(U) \ X
```

For `g in M+`, orient `g` from its endpoint in `U` to its endpoint outside
`U`, and define `D_U(g)` as the set of extra doors `e in B+` through which a
shortest row of `g` exits `U` as a clean initial segment.

Let `Z subset B+` be nonempty and **reduced**:

```text
for every g in H=N(Z),     |D_U(g) cap Z| >= 2.
```

Choose one clean initial segment `Q_U(g,e)` for each incidence
`g in H`, `e in D_U(g) cap Z`, and build the chosen fan graph

```text
F_Z = union Q_U(g,e).
```

For a connected fan component `K`, let

```text
Z_K = doors of Z whose inner endpoints lie in K,
H_K = rows g in H with at least one chosen Z-door in K.
```

## Candidate Lemma: CRFE

For every reduced `Z` and every nonempty connected fan component `K`,

```text
|H_K| >= |Z_K|.
```

Equivalently, no reduced component has positive Euler surplus
`|Z_K|>|H_K|`.

This implies RFC immediately.  Since each row `g` starts all its chosen
segments at the same `U`-endpoint, all chosen `Z`-doors of one `g` lie in one
fan component.  Thus the `H_K` partition `H` and the `Z_K` partition `Z`, so
summing gives

```text
|H| >= |Z|.
```

Hence a reduced deficient `Z` cannot exist.

## Sharper Candidate: Componentwise SDR

The cardinal CRFE may be provable through an explicit matching.  For a fan
component `K`, form the bipartite graph

```text
left  = Z_K,
right = H_K,
e -- g  iff  e in D_U(g).
```

The stronger candidate is:

```text
for every reduced Z and every fan component K,
the graph (Z_K,H_K) has a matching saturating Z_K.
```

This immediately implies `|H_K| >= |Z_K|`.  It is also closer to the geometry:
each extra door is assigned to one row that actually opens it, rather than
only counted against the total number of rows in the component.

The pure counting consequence is machine-checked in
`problems/23/lean/ResidualHallScratch.lean`:

```text
component_expansion_of_injection
deficient_set_contradicts_componentwise_sdr
```

## Exact Probe

The exploratory gate

```text
python problems/23/writeup/_nl_leaf_broad_probe.py --h-inherited 3 --h3-hard --max-cross 15
```

enumerates all reduced `Z`, not just deficient ones, using the same chosen-row
fan convention as `_nl_leaf_gate.py`.

Current output:

```text
switches: 155
XU: 1776
all reduced Z: 29087
fan components: 29087
min |H_K|-|Z_K|: 0
zero-margin components: 126
positive-Euler Z: 0
positive-Euler components: 0
NL failures: 0
```

The stronger SDR gate

```text
python problems/23/writeup/_crfe_matching_probe.py --h-inherited 3 --h3-hard --max-cross 15
```

currently gives:

```text
switches: 155
XU: 1776
all reduced Z: 29087
fan components: 29087
min |H_K|-|Z_K|: 0
component matching failures: 0
```

A separate full-census stress through `N=11` produced no reduced components
before the duplicated H-battery phase:

```text
census N=11: switches=32 XU=0 reduced=0 components=0 fail=0
```

The initial hard-H3/Hblow2-only battery had strict margin one, but inherited
H3 supplies zero-margin components.  Thus the correct candidate is
nonnegative component expansion, not strict expansion.

A first zero-margin example is:

```text
H3-inherited, N=27, side 111111111111111000000000000
X={(15,24)}
Z={(9,25),(10,25),(11,25),(12,25),(13,25),(14,25)}
H={(15,25),(16,25),(17,25),(18,25),(19,25),(20,25)}
margin |H|-|Z| = 0
```

## Proof Shape To Try

The reduced condition gives every row in a fan component at least two chosen
doors.  A bare hypergraph with this condition can still violate CRFE (one row
with three doors), so the proof must use shortest-row geometry and blue
closure.

The likely local invariant is a balanced version of no-naked-leaf:

```text
Every terminal-side door branch of a multidoor row is paid by at least one
row whose chosen doors stay in that branch, except for equality atoms where
the boundary-vertex fan is already perfectly balanced.
```

The proof target is now an injection from component doors to component rows,
not to non-root rows.  Equality atoms such as inherited-H3 boundary fans must
be allowed.

The SDR candidate makes this injection literal.  A proof can aim for Hall on
the component door-row incidence graph.  If a component SDR Hall failure exists,
its witness is a smaller and more structured object than a positive-Euler
component: a door subset `Y subset Z_K` with fewer opening rows than doors.

This still needs a proof of the same Case-2 splice:

```text
selected prefix crosses a leaf branch as a middle interval
=> shortest-path exchange produces a private trapped row in the branch.
```

The advantage is that the counting conclusion is now componentwise and does
not require assuming Hall deficiency.
