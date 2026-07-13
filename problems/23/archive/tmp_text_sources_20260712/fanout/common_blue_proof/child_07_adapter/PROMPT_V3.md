You are the reservation-semantics follow-up for Lead P. Work only in `tmp/fanout/common_blue_proof/child_07_adapter/`; preserve prior artifacts and write V3-named files. Do not edit production/shared files or spawn agents.

Controlling facts:
- `MicroAdapter.lean` already compiles the raw `MicroMatching` embedding and keeps `ComponentPreserving` explicit.
- Common-blue terminal use reserves its two blue source-owner edges. The posted R29 14-pair/28-half assignment is not ledger-safe merely from `TerminalData.Valid`.
- Exact mailbox gate: honest union old-source deduction makes that assignment net `28-1=27`; a conservative edge-exclusive selection over the full pool nets only `+2`. Do not assume reservation idempotence.
- Reservation-free Pattern 5 has an exact R29 28-key repair, but universal all-row Pattern 5 is false (R31). Treat Pattern 5 only as a supplied matching/provider interface.

Tasks:
1. In `ReservationAwareAdapter.lean`, define an abstract finite reservation ledger for a supplied micro assignment. Separate base terminal cells from half keys. Record each used base terminal's reserved edge set, the old FreeHalf keys deducted by the union of those edges, injectivity of assigned half keys, assignment-image disjointness from deductions, and a conservative pairwise-disjoint/exclusive reservation variant. Do not prove or postulate idempotence.
2. Prove graph-free cardinal lemmas showing usable net capacity is assigned-new keys minus the union of deducted old keys, and that a matching ignoring deduction is insufficient. A tiny exact countermodel is acceptable. Compile without `sorry`, `admit`, `native_decide`; print axioms.
3. Separately define a generic reservation-free supplied micro matching and prove its assignment conjugates through `ActiveCollisionHalf ≃ CollisionDebit × Fin 2` and `FreeHalf ≃ FreeCell × Fin 2` to the exact `ResidualSourceTokenization.Data.source` type. Construct `Data` only with an explicit `ComponentPreserving` hypothesis and positive unit.
4. Identify a typed Pattern-5 c5Base interface: an injective base-key map into `TypedFullBankSources.CapSource.c5Base`, component identity, and no reservation deductions. Do not assert a graph-derived provider or universal Pattern-5 matching.
5. Replay or cite exact commands for `_claude_r29_commonblue_gate.py` and `_claude_r29_pattern5_gate.py`; distinguish the posted-family `+27` recount from the full-pool exclusive `+2`. Write `RESERVATION_ADAPTER_REPORT.md`, `build_v3.log`, hashes, and exact remaining obligations.

Allowed axioms only `propext`, `Classical.choice`, `Quot.sound`.
