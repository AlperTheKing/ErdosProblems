# Reservation-aware adapter V3

`ReservationAwareAdapter.lean` compiles without `sorry`, `admit`, or `native_decide`. `build_v3.log` shows all printed declarations use only `propext`, `Classical.choice`, and `Quot.sound` (or a subset).

## Result

`ReservationLedger` separates base terminal cells from half keys. It records `baseOf`, per-base `reservedEdges`, the union-induced old `FreeHalf` deductions, injective assignment, and assignment-image disjointness from deductions. `Exclusive` adds conservative pairwise-disjoint edge reservations and edge-deduction sets. No reservation idempotence is assumed or proved.

`usableNetCapacity_eq` proves net capacity equals assigned-new cardinality minus the union-cardinality of deducted old keys. `tinyIgnoringDeduction` has one injectively assigned half and one distinct deducted half; `tiny_net_zero` proves net zero, so a raw matching count is insufficient.

`conjugatedAssignment` transports a supplied raw embedding through `ActiveCollisionHalf ≃ CollisionDebit × Fin 2` and `FreeHalf ≃ FreeCell × Fin 2`. `dataOfSupplied` has exactly the `ResidualSourceTokenization.Data.source` type and requires explicit `ComponentPreserving` and `unit_pos`.

`Pattern5C5BaseProvider` is only a typed interface: injective base-key map into `TypedFullBankSources.CapSource.c5Base`, component identity, and empty reservation deductions. It asserts neither a graph-derived provider nor a universal all-row Pattern-5 matching (false at R31).

## Gate replay

Exact commands:

```powershell
python E:\Projects\ErdosProblems\problems\23\writeup\_claude_r29_commonblue_gate.py
python E:\Projects\ErdosProblems\problems\23\writeup\_claude_r29_pattern5_gate.py
```

Logs: `commonblue_gate_v3.log`, `pattern5_gate_v3.log`. The posted 14-pair/28-half family has honest-union net `28-1=27`. Separately, the common-blue script's conservative edge-exclusive full-pool selection gains 4 halves, deducts 2, and nets only `+2`. The Pattern-5 all-anchor instance pays 28/28; this does not supply a universal provider.

Build command, from `apn-gpt55-workbench/formal-conjectures`:

```powershell
$env:LEAN_PATH='E:/Projects/ErdosProblems/tmp/fanout/common_blue_proof/child_07_adapter/olean;E:/Projects/ErdosProblems/problems/23/lean'
lake env lean E:/Projects/ErdosProblems/tmp/fanout/common_blue_proof/child_07_adapter/ReservationAwareAdapter.lean
```

## Exact remaining obligations

1. Construct the graph-derived common-blue reservation ledger and prove assignment/deduction disjointness.
2. Prove required net capacity after union deduction; `TerminalData.Valid` and raw matching do not imply it.
3. If exclusivity is used, construct a selection exceeding the replayed `+2` net.
4. Supply `ComponentPreserving` and a positive unit for the chosen reservation-free matching.
5. Supply a case-specific Pattern-5 provider; do not infer a universal all-row provider.

SHA-256 values and exact paths are in `HASHES_V3.txt`.
