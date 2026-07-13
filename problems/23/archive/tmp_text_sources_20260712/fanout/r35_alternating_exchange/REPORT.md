# R35 alternating exchange: exact anchored sterile countermodel

## Verdict

An anchored closed trace does **not** by itself yield an augmentation or a
simultaneous trade lowering `(collisionDefect,rowCode)`.  The obstruction is
an ordinary alternating cycle inside a maximum coherent matching.  Flipping
the cycle preserves matching cardinality, preserves the unmatched set, and,
when every row family is a singleton, preserves the row state and row code.

The countermodel below retains the corrected R34 identity fields

```text
(owner, other, producerAtom, occurrence, copy, half, component)
```

and its repeated trace state retains the matching cursor.  It is the anchored
`3 x 3` double-star model, expressed directly as an alternating exchange
graph.  No endpoint-count argument is used.

## 1. Anchored row state

Use core vertices

```text
L = {l0,l1,l2},  R = {r0,r1,r2},  cL, v, cR
```

and four vertices `z0,...,z3`.  For each `0 <= i,j < 3`, introduce a bad
atom `Aij` with the singleton selected row

```text
Qij = (li,cL,v,cR,rj).
```

Give each `zk` a private singleton five-vertex row on four fresh private
vertices.  These four atoms and their 16 private vertices bring the totals to
13 atoms and 29 vertices.  All 13 endpoint pairs are distinct, every row
starts and ends at its own atom endpoints, and all selected rows are distinct.
Thus `RowEndpointAnchoring`, `BadEndpointPairsDistinct`, and the conclusion of
`selectedRow_injective` all hold literally.

Every row family is a singleton.  Hence the row-choice type has one element,
called `omega`; every simultaneous row change has `newState = omega` and

```text
rowCode(newState) = rowCode(omega).
```

Declare `v` active in one component with canonical label `kappa`.  The four
private rows may support an abstract active cable; its details do not enter
the matching calculation.

## 2. Full occurrence-level obligations

For an ordered pair `(v,x)`, let `Occ(x)` be the database-ordered list of
selected atoms whose rows contain both coordinates.  Explicitly,

```text
Occ(v) = Occ(cL) = Occ(cR)
       = [A00,A01,A02,A10,A11,A12,A20,A21,A22],
Occ(li) = [Ai0,Ai1,Ai2],
Occ(rj) = [A0j,A1j,A2j].
```

For every `x` in

```text
C_v = {v,cL,cR,l0,l1,l2,r0,r1,r2},
```

every `0 <= k < |Occ(x)|-1`, and every `h in {0,1}`, create the obligation

```text
d(x,k,h) =
  (owner=v,
   other=x,
   producerAtom=Occ(x)[k+1],
   occurrence=k+1,
   copy=k,
   half=h,
   component=kappa).
```

This is exactly the positive-occurrence convention of
`CollisionDefectGraphAdapter.IsActiveObligation`: `occurrence = copy+1`, and
the producer is the atom at that occurrence.  No occurrences, copies, halves,
or components are identified.

The exact demand is

```text
3 * 8 * 2 + 6 * 2 * 2 = 72.
```

The first term is for `v,cL,cR`; the second is for the six leaves.

## 3. Exact coherent source graph

Take 38 distinct unreserved P1 source halves and the 24 P3 source halves on
the 12 ordered same-side leaf bases

```text
(li,li') with i != i', and (rj,rj') with j != j'.
```

There are exactly

```text
38 + 12 * 2 = 62
```

source keys.  Make every one of the 72 obligations eligible for every source
key.  Thus the exchange incidence graph is `K_{72,62}`.  All obligations have
component `kappa`, so every injection is
`BaseKeyComponentCoherent`, including when both halves of one base are used.

Consequently every coherent partial matching has size at most 62, while an
injection of size 62 exists.  Therefore

```text
collisionDefect(omega) = 72 - 62 = 10.
```

This equality is the honest minimum in `CheckedCollisionDefectTrade.Data`,
not merely the unmatched count of one chosen witness.

## 4. Matching-cursor-faithful sterile trace

Choose nine distinct obligations

```text
q_t = d(v,t,0)  for 0 <= t < 8,
q_8 = d(v,0,1).
```

In particular, `q_0` and `q_8` have the same owner, other coordinate, copy,
occurrence, producer, and component, but remain distinct because their halves
are different.  Choose nine distinct P1 keys `s_0,...,s_8`.  Extend

```text
M(q_t) = s_t
```

to a coherent size-62 matching, leaving ten obligations unmatched.  Let `r`
be one unmatched obligation outside `{q_0,...,q_8}`.

The alternating exchange graph has obligation-to-source arcs for eligible
nonmatching pairs and source-to-obligation arcs given by `M^{-1}`.  It contains
the lollipop trace

```text
r -> s0 -> q0 -> s1 -> q1 -> ... -> s8 -> q8 -> s0 -> q0.
```

The first arc enters the saturated core.  The suffix

```text
q0 -> s1 -> q1 -> ... -> q8 -> s0 -> q0
```

is a closed alternating cycle.  Its initial and final corrected cursors are
identical:

```text
(matching=M, cursor=obligation q0).
```

Every intermediate obligation carries its full occurrence/copy/half/component
identity, and every source cursor carries its full base and half identity.
Thus the repetition is not created by projecting away any R34 state field.

There is no augmenting terminal: all 62 sources are matched.  Flipping the
closed cycle gives

```text
M'(q_t) = s_(t+1 mod 9)
```

and leaves all other assignments fixed.  Hence `|M'|=|M|=62`, the same ten
obligations remain unmatched, source realization is unchanged, and component
coherence is unchanged.  Flipping the entry prefix `r -> s0 -> q0` merely
moves the unmatched obligation from `r` to `q0`; it also keeps defect 10.

## 5. Why neither checked trade exists

A `CheckedCollisionDefectTrade` would require a new matching with fewer than
the old exact unmatched count 10.  This is impossible because there are only
62 source keys for 72 obligations.

A `CheckedCollisionLexTrade.Trade` would require both nonincreasing unmatched
count and

```text
rowCode(newState) < rowCode(omega).
```

But the singleton row families make `newState = omega`, so strict row-code
descent is impossible.  The alternating rotation is therefore neither kind
of checked trade, although it is a genuine closed exchange trace.

The exact objective before and after every cycle rotation is

```text
(collisionDefect,rowCode) = (10,rowCode(omega)).
```

## 6. Scope of the obstruction

This is an exact countermodel to the proposed implication from

```text
anchored sterile closed trace
  => augmentation or lexicographically improving simultaneous trade.
```

It is not a counterexample to the final real-graph feasibility theorem.  The
P4/P5/common-blue relations and maximum-cut geometry were supplied abstractly;
a concrete graph can force additional sources or detour rows.  Therefore the
missing theorem must use such real graph geometry.  Anchoring, complete
cursor identity, finite termination, and alternating-cycle structure alone
cannot exclude a neutral sink cycle.

The strongest sound conclusion from a sterile repeated corrected cursor is
only: there is a cardinality-preserving coherent matching rotation.  Strict
descent requires a separately checked augmenting endpoint, a genuinely
different row tuple with explicit lower rank, or a graph-derived source that
breaks saturation.
