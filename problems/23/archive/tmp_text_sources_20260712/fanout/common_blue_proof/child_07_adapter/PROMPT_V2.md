You are the follow-up adapter child for Lead P. The controlling production file changed after your first audit. Read SHA-256 `71308BE7D0802FBAA04F64282334E88F3A3088B90EFAD78B86E834C10CB63116` of `Gamma/CommonBlueExtendedMatching.lean` and target `MicroMatching`, not the obsolete one-copy `Matching`. Work only in `tmp/fanout/common_blue_proof/child_07_adapter/`; preserve existing artifacts and write new `MicroAdapter.lean`, `MICRO_ADAPTER_REPORT.md`, and `build_v2.log`. Do not edit production/shared files or spawn agents.

Required construction:
1. Define a collision-debit base type obtained from `ActiveCollisionHalf` by forgetting its `half : Fin 2`, retaining owner/other/copy and ActiveOwner proof. Prove an explicit equivalence `ActiveCollisionHalf ≃ CollisionDebit × Fin 2`.
2. Define a free-cell base type obtained from `FreeHalf` by forgetting its `half`, retaining sourceX/sourceY/distinct/free. Prove `FreeHalf ≃ FreeCell × Fin 2`.
3. Given `M : CommonBlueExtendedMatching.MicroMatching G c omega`, conjugate `M.assign` through those equivalences to construct exactly the raw embedding required by `ResidualSourceTokenization.Data.source`:
   `((CollisionDebit × Fin 2) ⊕ (ActiveHitNeed × Fin 25)) ↪ (FreeCell × Fin 2)`.
4. Isolate the genuinely missing component-preservation hypothesis with explicit `vertexComp`, `debitComp`, and `sourceComp`, and prove that this hypothesis plus `unit_pos` constructs a full `ResidualSourceTokenization.Data`. Do not smuggle component preservation out of `MicroAvailable`; audit that it is absent.
5. State the R29 exact gate: MicroDemand 20025, extended reach 20141, and explain why the cardinal scale now passes while component preservation remains semantic.
6. Compile with `lake env lean`, fix all errors, grep forbidden tokens, and `#print axioms` for every load-bearing theorem. Allowed axioms are only `propext`, `Classical.choice`, `Quot.sound`; no `sorry`, `admit`, `native_decide`.

Report exact source hashes, command, rc, theorem names, and the minimal missing hypothesis. No floating theorem evidence.
