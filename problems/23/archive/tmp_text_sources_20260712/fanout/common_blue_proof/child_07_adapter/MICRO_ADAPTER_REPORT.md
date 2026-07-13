# MicroMatching adapter report

## Result

`MicroAdapter.lean` constructs the exact raw embedding required by `ResidualSourceTokenization.Data.source` from a production `CommonBlueExtendedMatching.MicroMatching`:

```text
((CollisionDebit × Fin 2) ⊕ (ActiveHitNeed × Fin 25)) ↪ (FreeCell × Fin 2).
```

`CollisionDebit` retains `owner`, `other`, dependent `copy`, and the `ActiveOwner` proof while forgetting `half`. `FreeCell` retains `sourceX`, `sourceY`, `distinct`, and `free` while forgetting `half`.

The explicit equivalences are `activeCollisionHalfEquiv` and `freeHalfEquiv`. `rawSourceEmbedding` conjugates the micro-matching assignment through their sum/product forms. `dataOfMicroMatching` constructs the complete production `ResidualSourceTokenization.Data`.

## Minimal missing hypothesis

The only missing semantic input is `ComponentPreserving M vertexComp debitComp sourceComp`:

```text
∀ x, sourceComp (rawSourceEmbedding M x).1 =
  Sum.elim (fun d => debitComp d.1)
    (fun s => vertexComp s.1.1) x.
```

Together with `unit_pos : 0 < unit`, this supplies the full `Data`. Production `MicroAvailable` contains only `(EligibleOwner ∨ CommonBlueOwner) ∧ ¬ScopedReserved`; it contains no `vertexComp`, `debitComp`, `sourceComp`, or component equality. Therefore component preservation is not derivable from availability and is kept as an explicit hypothesis.

## R29 exact gate

The exact R29 micro-demand is `20025`; corrected extended reach is `20141`. The kernel theorem `r29_micro_cardinal_gate` proves `20025 ≤ 20141`, leaving cardinal slack `116`. Thus the corrected relation passes the global cardinal scale. Component preservation remains semantic because a global injection/cardinality inequality does not imply that assigned free cells lie in the debit or owner component.

## Checked source hashes

- `problems/23/lean/Erdos23Delta0/Gamma/CommonBlueExtendedMatching.lean`: SHA-256 `71308BE7D0802FBAA04F64282334E88F3A3088B90EFAD78B86E834C10CB63116`
- `problems/23/lean/Erdos23Delta0/ResidualSourceTokenization.lean`: SHA-256 `6509C4F9443BEBF66A0EEA6BE7C6DFA03C0DCD3F72A6575C188B191D0253000E`
- `MicroAdapter.lean`: SHA-256 `CA15E91F7A27DB43D20277461A99AF9CC18794988C69CA428A507060F5665EBC`

The pinned controlling hash matches exactly.

## Build and audit

Command (from `apn-gpt55-workbench/formal-conjectures`):

```powershell
$env:LEAN_PATH='E:/Projects/ErdosProblems/tmp/fanout/common_blue_proof/child_07_adapter/olean;E:/Projects/ErdosProblems/problems/23/lean'; lake env lean E:/Projects/ErdosProblems/tmp/fanout/common_blue_proof/child_07_adapter/MicroAdapter.lean
```

Return code: `0`. Full output is in `build_v2.log`.

Load-bearing declarations checked by `#print axioms`:

- `Child07MicroAdapter.activeCollisionHalfEquiv`: `propext`, `Quot.sound`
- `Child07MicroAdapter.freeHalfEquiv`: `propext`, `Quot.sound`
- `Child07MicroAdapter.rawSourceEmbedding`: `propext`, `Classical.choice`, `Quot.sound`
- `Child07MicroAdapter.dataOfMicroMatching`: `propext`, `Classical.choice`, `Quot.sound`
- `Child07MicroAdapter.r29_micro_cardinal_gate`: `propext`, `Quot.sound`

All are within the allowed axiom set. Exact forbidden-token grep on `MicroAdapter.lean` for the three prohibited proof escape tokens returned no matches.
