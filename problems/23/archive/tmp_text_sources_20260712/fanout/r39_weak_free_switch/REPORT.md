# Weak-free multi-pair switch audit

## Verdict

The aggregate upgrade is false, even for a canonical real cage.  Maximum-cut
switching gives an exact interaction-corrected identity, but it cannot upgrade
pair surpluses in `{0,1}` to two units per common-blue terminal.

## Exact identities

Give every graph edge the signed weight

```text
w(e) = +1 for a blue edge, -1 for a bad edge.
```

Then `sigma(S) = sum_e w(e) 1[e crosses S]`.  For arbitrary vertex sets
`A,B`, edgewise inspection gives the signed uncrossing identity

```text
sigma(A) + sigma(B)
  = sigma(A union B) + sigma(A intersect B)
    + 2 w(E(A minus B, B minus A)).                         (U)
```

There is no useful submodular sign in `(U)`: the last term counts blue edges
minus bad edges.

For an arbitrary finite family `P_1,...,P_k`, put

```text
r_e = #{i : e crosses P_i}.
```

Switching every `P_i` has final switch set `P_1 triangle ... triangle P_k`.
Since an edge crosses that symmetric difference iff `r_e` is odd,

```text
sigma(P_1 triangle ... triangle P_k)
  = sum_i sigma(P_i) - 2 sum_e w(e) floor(r_e/2).            (S)
```

If the `P_i` are pairwise disjoint, their symmetric difference is their union
and an edge can cross at most two of them.  Thus `(S)` becomes

```text
sigma(union_i P_i)
  = sum_i sigma(P_i)
    - 2 sum_{i<j} (B(P_i,P_j) - M(P_i,P_j)).                (D)
```

Maximum-cut maximality says only that the left side of `(S)` or `(D)` is
nonnegative.  The signed interaction has no forced direction.

There is also a sharper local diagnosis.  Set

```text
a(z) = sigma({z}) = dB({z}) - dM({z}).
```

If `P={x,y}` is an attachment pair, both vertices are blue neighbours of one
owner.  They are on the same shore, and triangle-freeness makes `xy` absent.
Consequently

```text
sigma({x,y}) = a(x) + a(y).                                 (L)
```

All `a(z)` are nonnegative integers in a maximum cut.  Hence a weak-free pair
of surplus zero has endpoint slacks `(0,0)`, and one of surplus one has
endpoint slacks `(0,1)` up to order.  Nothing in max-cut maximality supplies
the missing two-unit lower bound.

## Canonical real cage

Take two disjoint copies of the exact 20-vertex R36 cage and add one blue
bridge from vertex `3` of the first copy to vertex `22` (base vertex `2`) of
the second.  The bridge endpoints avoid the weak pairs.  Use the displayed
R36 rows in each copy and order rows lexicographically.

The resulting graph has 40 vertices and 49 edges.  It is triangle-free.  Its
eight displayed edge-disjoint 5-cycles force at least eight uncut edges in
every cut, so every cut has size at most `49-8=41`; the displayed cut has
exactly the eight bad edges and attains 41.  The blue graph is connected.

The complete shortest-row databases are unchanged because the copy graph is
a tree with one bridge: a simple path leaving a copy cannot return to it.
Their family sizes are `(2,1,1,1,2,1,1,1)`.  In each two-row family the
displayed row is lexicographically first, so the selected tuple is the
natural mixed-radix rank-zero canonical choice.

For copy indices zero and one, respectively, the attachment data are

```text
(owner,x,y) = (7,0,5), (27,20,25).
```

Each owner lies in an active component containing both endpoints of its
selected bad atom.  The owner-to-`x` edge is active, the owner-to-`y` edge is
selected support, `pairCount(x,y)=0`, both free halves are unreserved, and

```text
(dB,dM,sigma) = (3,2,1)
```

for each pair.  There are no edges between the two pairs, so their signed
interaction is zero.  Formula `(D)` therefore gives

```text
sigma({0,5,20,25}) = 1+1 = 2 < 4 = 2 times terminal_count.
```

Indeed every nonempty subfamily `J` has `sigma(union_{i in J} P_i)=|J|`, so
all max-cut switch inequalities hold while the aggregate upgrade fails by
exactly `|J|` units.  Chaining `k` copies by the same kind of bridge gives the
same failure for every `k>=1`.

## Consequence

No multi-pair max-cut switch or uncrossing argument can replace the production
guard `sigma(P)>=2` by `sigma(P)>=0`.  Any valid repair must contribute a new
graph hypothesis that excludes this tree-joined family, or must retain the
weak-free outcome as a nonterminal branch and pay it through a separately
typed, injective source mechanism.  Aggregate raw surplus alone is
insufficient.

Replay with integer and finite-set arithmetic only:

```powershell
python tmp/fanout/r39_weak_free_switch/check_cage.py
```
