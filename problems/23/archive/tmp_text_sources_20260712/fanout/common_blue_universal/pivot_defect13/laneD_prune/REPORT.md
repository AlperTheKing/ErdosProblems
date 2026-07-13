# Deficient-shore prune provider audit

## Decision

Prune does not pay the 13-slot defect in the current production system. The attributable inventory is empty: zero typed prune source keys, zero legal port incidences, raw `capQ = 0`, Hall-scale `capQ/25 = 0`, and zero spend. Paying 13 Hall slots would require raw `capQ = 325` carried by distinct legally incident tokens. No such graph-to-token provider exists.

This is provider absence, not a theorem that the graph has intrinsically zero capacity under every future prune construction. Aggregate `pruneCapQ` fields and the abstract constructor `CapSource.prune PruneKey` cannot create graph-derived capacity or incidence.

## Independent reconstruction

The replay decodes canonical graph6 `K??E@cyjFgWk` to 12 vertices and 23 edges: 19 blue and 4 bad. The four shortest-row families have sizes `[6,5,8,10]`; choice `[0,4,5,7]` gives rows

```
[6,0,9,2,8]
[6,1,10,3,7]
[7,3,10,5,11]
[8,3,10,5,11]
```

The selected set has 11 vertices. The relevant active component is `[0,1,2,7,10,11]`. Although positive-demand owners are `{7,10,11}`, the exact deficient shore is `{10,11}`: micro-demand 72, existing reachable FreeHalf sources 59, defect 13.

## Finite prune inventory

All 25 Hamming-one shortest-row replacements were reconstructed from the row-family code. Using the extractor's exact active-scoped obligation score as a diagnostic pre-rank, 24 decrease strictly: 21 go `30 -> 0`, while three go `30 -> 22`, `30 -> 16`, and `30 -> 28`; the remaining replacement `(coordinate 2, replacement 7)` stays `30 -> 30`. The complete per-replacement rows and integers are in `result.json`.

These 24 score decreases are rewrite candidates only. They are not legal strict prune steps: production has no `CheckedPruneStep`, checked transfer edge/reachability, strict local-rank field, injective `moveSound` slot transport, component-preservation adapter, or graph-to-ledger constructor. `Ell5DistancePrune` only preserves distance when a subgraph and geodesic are already supplied.

Therefore the legal inventory for the deficient shore is exactly empty under the current executable provider boundary:

| quantity | exact value |
|---|---:|
| legal prune steps | 0 |
| typed keys `CapSource.prune k` | 0 |
| component owners | 0 |
| legal port incidences | 0 |
| raw `capQ` | 0 |
| Hall capacity `capQ/25` | 0 |
| required raw `capQ` | 325 |
| residual defect after prune | 13 |

No-double-spend is vacuous (`0 <= 0`). Relabeling an existing FreeHalf or common-blue source as prune would spend an already enumerated source again and is not licensed by a typed graph-derived constructor.

## Production boundary

`ResidualSourceTokenization` enforces injective source use for debit and need microcopies. `TypedFullBankSources` provides typed labels but no prune provider. `FullBankToLengthSurplusCharge` checks supplied capacity, uniqueness, and spend. `FullBankPortSinks` divides supplied `capQ` by 25 and explicitly records that legal edge-to-token incidence is absent. `CommonBlueExtendedMatching` supplies only the common-blue FreeHalf relation, not a FullBank adapter.

Run from the repository root:

```powershell
$env:PYTHONHASHSEED='0'
python tmp/fanout/common_blue_universal/pivot_defect13/laneD_prune/replay.py
```

