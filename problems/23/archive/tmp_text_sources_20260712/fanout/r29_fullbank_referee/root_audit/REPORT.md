# R29 hub-shore base-transfer referee report

## Verdict

For the all-anchor R29 tuple, `sameFirst` and `commonBad` provide exactly **17,325 distinct available half-keys** to `{0,1,2}`: 17,325 and 0, respectively. At capacity `1/(2K)` per key, reachable capacity is `17325/(2K)`. Against demand 19,953, the base-only cardinal defect is 2,628; these patterns do not absorb the auxiliary scoped defect 28.

The auxiliary `ActiveScoped` count 19,925 is larger by exactly 2,600 `rowCompanion` keys. Thus defect 28 concerns `same-owner union row-companion` after `ScopedReserved`, not the two production base patterns and not complete FullBank.

## Independent hub reconstruction

The archival spec gives 2,943 vertices; hubs `r,cL,cR=0,1,2`; 26 left and 26 right leaves; and 676 rigid rows `(l,cL,r,cR,r')`. Selector, circuit, and cable-seed rows contain no hub. Each hub therefore co-occurs with exactly 54 vertices: two hubs plus 52 leaves.

Of 2,942 distinct second coordinates, 2,888 are free. Two half bits give 5,776 raw `sameFirst` keys per hub. The all-anchor cable scopes one half-zero orientation as reserved at each hub: `3*(5776-1)=17325`. No bad atom meets a hub, so `commonBad`, which requires two distinct actual bad neighbours, is empty.

## Literal keys and capacity

A source is `FreeHalf(sourceX,sourceY,half)`: distinct coordinates, `half in {0,1}`, and `pairCount(sourceX,sourceY)=0`.

- `sameFirst`: `sourceX=owner`.
- `commonBad`: both coordinates are distinct bad neighbours of owner, with a checked nonnegative-loss two-vertex switch. Here there are no candidates.
- Capacity is exactly `1/(2K)` per matched key. Collision matches cancel without a token; HitNeed matches emit a `c5Base` token keyed by the encoded FreeHalf, support `{owner}`, capacity `1/(2K)`.

Reachable cardinality (17,325), rational capacity (`17325/(2K)`), and emitted-token count are different quantities.

## Theorem versus sample; selector dependence

Structural theorem from the row-family spec: every selector alternative has empty hub projection. Hub `pairCount`, raw hub `FreeHalf`, raw `sameFirst=17328`, and `commonBad=0` are invariant over all `680^676` tuples.

Selector choices can change selected union and active graph. Thus `ActiveOwner`, `activeDegree`, `hitNeedUnits`, and `ScopedReserved` can vary. If hubs cease to be active, hub demands disappear. The all-anchor available count 17,325 and demand 19,953 are not asserted universally.

The script reconstructs the all-anchor hub projection and its three specified cable reservations. It does not enumerate the product; no sample is promoted to a theorem.

## Production versus auxiliary

FullBank kinds are `door`, `vertexSlack`, `c5Base`, and `prune`. These FreeHalf transfers are not Door or vertex-slack sources. Auxiliary Lean `Available` is `EligibleOwner and not ScopedReserved`, where `EligibleOwner` is same-owner or row-companion; it has no `commonBad` and is not FullBank. Its 19,925 cannot be attributed to `sameFirst+commonBad`.

## Exact replay

```powershell
python tmp/fanout/r29_fullbank_referee/root_audit/audit_r29_hub_base.py
Get-FileHash -Algorithm SHA256 tmp/fanout/r29_fullbank_referee/root_audit/audit_r29_hub_base.py
Get-FileHash -Algorithm SHA256 tmp/fanout/r29_fullbank_referee/root_audit/REPORT.md
```

Read: `COMMON.md`, active goal, `GOAL_LOOP.md`, archival R19/R20/R22/R23/R28/R29 notes, claimed-number R29 scoped report, and production Lean. No forbidden R29 FullBank/gate/global-min/Lead-B script or JSON was read.
