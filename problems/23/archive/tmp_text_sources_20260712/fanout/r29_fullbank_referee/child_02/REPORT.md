# R29 hub-shore ActiveScoped demand audit

## Verdict

The hub-shore `ActiveScoped` demand is **constant, equal to 19,953, over all `680^676` selector tuples**. This is a symbolic conclusion, not an inference from the sample gate.

## Minimum symbolic reconstruction and proof

Only four selector effects can change demand owned by a hub `h`: a change to some `pairCount(h,y)` (collision halves), to `pairCount(h,h)` (selected load), to an active edge incident with `h` (active degree), or to `ActiveOwner(h)`.

The archival R29 construction rules out all four. Selector rows lie wholly in the two lock/selector regions: no selector row contains a hub and no selector row-path edge is incident with a hub. Vertices controlling hub-incident active edges are selected by rigid families. The fixed circuit/cable keeps both endpoints of a rigid hub atom in the same off-support component for every selector tuple. Hence every hub stays an `ActiveOwner`, and every selector coordinate change has

```text
delta pairCount(h,y) = 0 (all y), delta selectedLoad(h) = 0,
delta activeDegree(h) = 0, delta ActiveOwner(h) = 0.
```

The fixed hub-local census is 6,650 collision halves and one residual HitNeed at each hub 0, 1, 2. Thus for every tuple `omega`,

```text
|{d : Demand omega // demandOwner d in {0,1,2}}|
  = sum_h (6650 + 1) = 3 * 6651 = 19953.
```

This proves demand constancy only. It does not assert that the `Available` source neighborhood is constant, nor that every selector tuple fails Hall.

## Definition audit

`ActiveOwner` is stronger than membership in `activeGraph`: one active connected component must contain the owner and both endpoints of some selected bad atom. Reachability is reflexive. The fixed cable/circuit is therefore essential.

`ActiveCollisionHalf` filters `CollisionHalf` by `ActiveOwner(d.owner)`. `ActiveHitNeed` is syntactically unfiltered, but an off-active vertex has `activeDegree = 0`, so truncated subtraction gives zero HitNeed. At a hub, `hitNeedUnits = activeDegree - (N - 5*pairCount(h,h))`.

`ScopedReserved` and `Available` affect only the source shore, not `Demand` cardinality.

`MinimumDemandCollisionHall` uses `canonicalChoice`, minimizing unscoped `obligationScore = 2*collisionUnits + 2*|activeEdges|`. It has no `ActiveOwner` filter and no HitNeed demand. It must not be conflated with `MinimumActiveScopedHall`, which uses `scopedCanonicalChoice` and scoped `Demand`. Both Lean bridges are conditional finite-minimum arguments; neither proves its exchange/provider hypothesis.

## Exact sample gate

Run `python tmp/fanout/r29_fullbank_referee/child_02/gate.py`. It uses integers only and checks all-anchor, two uniform non-anchor extremes, alternating extremes, and one-coordinate extreme. These are **samples only**. The universal result is the zero-delta proof above, not enumeration.

## Artifact hashes

- `gate.py`: `83bc5347cdf6fff93896182ba1112bf74ea03bc88674786941f8e5bbcbf636e6`
- `gate.out`: `2d7bb003ea50e66471f09cf1bda6de2fc2d8bb2f1947500daadd4a1255abb035`
- `REPORT.md` before this hash appendix: `6805a08d63e6491abdc249ca26aaf699b1eb3216a713e00c0d15aeb0c121d13e`
- gate JSON payload SHA256 (printed by the script): `111d750254498f05c4a7526beeef64b731ec0a2e030c3d99ecd662ad96641887`
