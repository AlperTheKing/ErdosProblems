# R29 FullBank prune/slot-transport audit

## Verdict

**UNDEFINED.** The complete production FullBank absorption question cannot be evaluated for the prune class. Production defines abstract prune labels and checks supplied token capacities, uniqueness, and no-double-spend, but it does not implement a graph-derived prune-step predicate, local rank, injective affected-slot transport, prune reachability relation, or real-graph provider.

This lane therefore does **not** prove that prune capacity is mathematically zero and does **not** promote the surviving 28-unit auxiliary defect to a FullBank falsifier.

## Exact R29 result

The replay reconstructs the deterministic cage rather than trusting copied totals:

| Quantity | Exact value |
|---|---:|
| vertices / edges | 2,943 / 8,422 |
| blue / bad edges | 7,039 / 1,383 |
| MaxCut / Gamma | 7,039 / 34,575 |
| row-family path-count histogram | 707 x 1, 676 x 680 |
| verified all-anchor replacements | 676 |
| hub owners | `{0,1,2}` |
| demand per owner | 6,651 each |
| total hub-shore demand | 19,953 |
| distinct implemented auxiliary base `FreeHalf` sources | 19,925 |
| auxiliary defect | 28 |

The 19,925-source union is already deduplicated: 17,325 are same-first only, 2,600 row-companion only, and 0 have both reasons.

## Prune enumeration and accounting

Every operationally instantiated production prune source reachable from the hub shore was enumerated. The set is empty because there is no executable production predicate/provider with which a row rewrite can qualify:

| Incremental class | Raw | Overlap with prior union | New distinct capacity | Residual defect |
|---|---:|---:|---:|---:|
| implemented prune/slot transport | 0 | 0 | 0 | 28 |

Injectivity and no-double-spend hold only vacuously for this empty enumerable set. The exact attributable incremental capacity is 0 units. This is not an upper bound on a future implementation.

R29 has 676 selector families with 680 shortest rows each, so alternative rows exist. They are not legal prune steps without the required strict local-rank test and injective `move`/`moveSound` map on affected half-slot keys.

## Implemented boundary

- [`GOAL_LOOP.md`](../../../../GOAL_LOOP.md) line 16 requires prune to have injective slot transport and local rank decrease.
- [`WALL_ATTACK_R19_GPTPRO56.md`](../../../../problems/23/writeup/WALL_ATTACK_R19_GPTPRO56.md) lines 19-25 specify the missing `CheckedPruneStep`; lines 36-40 identify the slot map as open.
- [`WALL_ATTACK_R20_GPTPRO56.md`](../../../../problems/23/writeup/WALL_ATTACK_R20_GPTPRO56.md) lines 39-50 keeps prune as a residual stage requiring an injective slot map and local rank.
- [`TypedFullBankSources.lean`](../../../../problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean) lines 24-29 provides only an abstract `PruneKey` constructor; line 14 says the adapter is separate and absent.
- [`FullBankToLengthSurplusCharge.lean`](../../../../problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean) lines 188-205 consumes supplied prune spend, uniqueness, and no-double-spend; it does not derive tokens from graph data.
- [`FullBankPortSinks.lean`](../../../../problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean) line 80 explicitly says legal edge-to-token incidence is absent.
- [`Ell5/ConcreteCage/Bank.lean`](../../../../problems/23/lean/Erdos23Delta0/Ell5/ConcreteCage/Bank.lean) lines 21-44 defines abstract local bank terms and support containment, not prune generation.
- [`Ell5DistancePrune.lean`](../../../../problems/23/lean/Erdos23Delta0/Ell5DistancePrune.lean) line 8 proves only distance preservation under a supplied subgraph/geodesic.
- [`Ell5FullBankInterface.lean`](../../../../problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean) lines 4-9 names `Ell5FullBankRelaxedCover_exists` as remaining open work.
- [`AggregateLedgerNoIncidenceCounterexample.lean`](../../../../problems/23/lean/Erdos23Delta0/AggregateLedgerNoIncidenceCounterexample.lean) lines 6-15 and 152-157 prove that aggregate package checking alone cannot create missing routing incidence.

Repository-wide tracked-source search returned no match for `CheckedPruneStep`, `localRankDecrease`, `moveSound`, `slotTransport`, or `pruneTransport`. The exact unproved provider is a real-graph `CheckedPruneStep`/`CheckedTransferMatching` constructor carrying old/new shortest rows, same-cut bad set, strict local rank decrease, an injective sound slot move, and component preservation, ultimately supplying `Ell5FullBankRelaxedCover_exists` / `Ell5FullBankRelaxedCover_globalPackage_exists`.

## Replay commands

From `E:\Projects\ErdosProblems`:

```powershell
python tmp/fanout/r29_fullbank_gate/lane07_prune/audit_prune.py
python tmp/fanout/r29_fullbank_gate/lane07_prune/verify_audit.py
Get-FileHash -Algorithm SHA256 tmp/fanout/r29_fullbank_gate/lane07_prune/audit_prune.py,tmp/fanout/r29_fullbank_gate/lane07_prune/audit.json,tmp/fanout/r29_fullbank_gate/lane07_prune/verify_audit.py,tmp/fanout/r29_fullbank_gate/lane07_prune/verification.json,tmp/fanout/r29_fullbank_gate/lane07_prune/REPORT.md
```

Machine-readable values, source line captures, source SHA256 values, and exact search commands are in `audit.json`. Final artifact hashes are in `HASHES.sha256`.
