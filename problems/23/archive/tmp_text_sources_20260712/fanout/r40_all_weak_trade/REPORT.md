# R40 all-weak attachment trade audit

## Verdict

The proposed implication is **not proved or refuted** by the stated reduction.
The reduction has one rigorous conclusion: at each universally weak owner,
one entire attachment class is singleton-tight.  The next claimed step,
from tight singleton flips and endpoint anchoring to a `RowChoice` trade in
the original cut, is invalid without an additional incidence theorem.

No real counterexample to the full implication was found.  Conversely, no
proof may identify a tight cut flip with a row replacement: the former changes
the bad-edge keys and hence changes the row database.  This report records the
exact boundary and the completed falsifier searches rather than asserting the
missing theorem.

## 1. Exact zero-class lemma

Fix an active owner `v`.  Let `A` be its active off-support blue neighbours
and `S` its selected-support blue neighbours.  Triangle-freeness makes
`N_B(v)` independent in the full graph.  Put

```text
a(z) = sigma({z}) = d_B(z) - d_M(z).
```

Maximum-cutness gives `a(z) >= 0`, integrally.  For distinct
`x,y in N_B(v)`, independence gives

```text
sigma({x,y}) = a(x) + a(y).                                (1)
```

Assume every attachment probe `(x,y) in A x S` is weak-free, so its
pair count is zero and its sigma is zero or one.  If neither `A` nor `S`
were entirely zero, choose `x in A` and `y in S` with `a(x),a(y) >= 1`.
Equation (1) would give `sigma({x,y}) >= 2`, a contradiction.  Therefore

```text
(forall x in A, a(x)=0) or (forall y in S, a(y)=0).         (2)
```

This proof uses the whole probe rectangle.  It is stronger than pooling and
does not assign the weak free halves any terminal or bank capacity.

## 2. Why tight flips do not yet give a row trade

Let `z` satisfy `a(z)=0`.  Flipping `z` preserves the maximum-cut value.
For an incident old bad atom `zw` with selected anchored row

```text
(z,p1,p2,p3,w),
```

the flip makes `zw` blue and `zp1` bad.  Direct edge-status inspection shows
that

```text
(z,w,p3,p2,p1)
```

is a length-four blue row for the **new atom `zp1` in the flipped cut**.
It is not an alternative row for the old atom `zw` in the original cut.

Endpoint anchoring proves only that distinct selected rows have distinct
ordered endpoint pairs.  It does not say that the map

```text
incident bad atom zw |-> first selected blue edge zp1
```

is injective, surjective, or compatible with the fixed bad-atom keys.
Although tightness gives `d_M(z)=d_B(z)`, cardinality equality alone supplies
none of those properties.  Thus the exact output of (2) is a family of
maximum-cut carrier rotations, not a simultaneous `RowChoice` replacement.

The N20 model exhibits this distinction at `z=5`:

```text
sigma({5})=0,
old bad carrier 56,
new bad carrier after flipping 5: 57,
Gamma before = Gamma after = 100.
```

This is the neutral C5 rotation from R38.  It cannot be consumed by
`CheckedCollisionDefectTrade`, whose graph, cut, bad list, and row families
are fixed.

## 3. Exact N20 active-path audit

At the displayed N20 state the active component is the path

```text
0 - 7 - 10 - 15 - 1.
```

The complete row family for bad atom `01` is

```text
(0,2,3,4,1), (0,7,10,15,1).
```

Replacing the first row by the second makes every old active edge support;
vertices `2,3,4` leave the selected union, so the recomputed active scope is
empty.  Thus N20 is a positive model for the proposed conclusion.

It does **not** satisfy the universal-weak hypothesis.  Its complete probe
table `(owner,active,support;sigma)` is

```text
(0,7,2;6)   (1,15,4;4)
(7,0,5;1)   (7,0,8;3)   (7,10,5;2)  (7,10,8;4)
(10,7,12;6) (10,15,12;4)
(15,1,17;3) (15,10,17;4).
```

Every pair count is zero, but only `(7,0,5)` is weak.  Hence N20 neither
proves the all-weak implication nor refutes it.

## 4. Exact falsifier searches

`search_singleton_counterexample.py` exhaustively inspected the canonical
connected all-length-five systems through order 12.  A singleton complete
row database would refute the alternative-row conclusion immediately, but
every such system with a valid canonical cut had empty active scope:

```text
orders 5..10:     687 singleton systems, all inactive
order 11:       4,016 singleton systems, all inactive
order 12:      33,720 singleton systems, all inactive
```

`search_allweak_counterexample.py` then used the literal full rectangle
`A x S` at every active vertex on every lexicographically first state:

```text
orders 5..11: 70,690 inactive; 18 active, all with a nonweak probe
order 12:    921,266 inactive; 644 active, all with a nonweak probe
```

A separate deterministic seed-40 scan of 100,000 complete row tuples in the
real N24 cage found 43,953 inactive states and 56,047 active states with a
nonweak probe; it found no universally weak state.  These are bounded
falsifier results, not a proof of impossibility.

Replay:

```powershell
python tmp/fanout/r40_all_weak_trade/search_singleton_counterexample.py --n-min 11 --n-max 11 --workers 60 --chunk-size 128 --output tmp/fanout/r40_all_weak_trade/witness_n11.json
python tmp/fanout/r40_all_weak_trade/search_singleton_counterexample.py --n-min 12 --n-max 12 --workers 60 --chunk-size 128 --output tmp/fanout/r40_all_weak_trade/witness_n12.json
python tmp/fanout/r40_all_weak_trade/search_allweak_counterexample.py --n-min 12 --n-max 12 --workers 60 --chunk-size 128 --output tmp/fanout/r40_all_weak_trade/allweak_n12.json
```

The order-11 and order-12 all-weak manifests have SHA-256 respectively
`9DB2E4D1DC0A0F0C836A1FB18B665A07C23FA4E2B21A369EC8BBAC465CFF08FA`
and
`FA6F48FF253444DE8E595835E93D4E72DFE089E75368B685252B680D74E84989`.

## 5. Exact remaining lemma

To prove the requested implication one still needs a fixed-cut theorem:

```text
zero attachment class + complete anchored rows + no attachment detour
  => a simultaneous replacement of the original bad atoms
     lowers collisionDefect or empties the original active scope.
```

Neither `a(z)=0`, incidence-count equality, nor endpoint anchoring supplies a
map from recut carriers back to the original bad-atom keys.  That map is the
frontier; treating it as automatic would repeat the R38 neutral-carrier error.
