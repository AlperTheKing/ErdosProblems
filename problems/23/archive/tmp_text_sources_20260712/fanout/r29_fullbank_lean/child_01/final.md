# Final audit: CheckedTransferMatching to FullBankGlobalPackage

## Exact finding

There is no production Lean declaration named `CheckedTransferMatching`. The intentional negative kernel probe also finds no `CheckedOutsideAttachmentBaseTerminal`, `checkedTransferMatching_to_activeFullBank`, or `checkedMatching_withOutsideAttachment_sound`. Those names are prose-only designs: `E:\Projects\ErdosProblems\problems\23\writeup\WALL_ATTACK_R19_GPTPRO56.md:29-34` and `E:\Projects\ErdosProblems\problems\23\writeup\WALL_ATTACK_R23_GPTPRO56.md:29-34`.

The exact implemented auxiliary transfer relation is narrower:

- Implemented definitions: `CollisionHalf` at `E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\Gamma\MinimumDemandCollisionHall.lean:56`, `FreeHalf` at `:66`, `Reserved` at `:77`, `SameOwner` at `:84`, `RowCompanion` at `:92`, and `Eligible` at `:100`. `Eligible` is definitionally only `SameOwner ∨ RowCompanion` (`:103`).
- Implemented definition and compiled theorem: `CollisionMatching` at the same file `:120`, `CollisionHallCondition` at `:128`, and `collisionMatching_nonempty_iff_hall` at `:136`.
- The R29 `ActiveScoped` relation is likewise only same-owner or row-companion: `EligibleOwner` at `E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\Gamma\ActiveScopedMinimumExchange.lean:136`; its `Matching`, `HallCondition`, and compiled Hall equivalence are at `:154`, `:160`, and `:167`. Thus the supplied R29 defect is not a defect for a production full-bank relation—no such relation is compiled.

Every source pattern/class presently represented is recorded in `source_patterns.csv`:

1. `sameFirst`: implemented as `SameOwner` and included in `Eligible`.
2. `rowCompanion`: implemented and included in `Eligible`.
3. corrected common-blue terminal: `TerminalData.Valid` at `E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\Gamma\CheckedC5BaseTransfer.lean:36`, with compiled `check_eq_true_iff` at `:54`; it is standalone and not included in `Eligible`.
4. checked row-companion terminal: `RawValid` at `E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\Gamma\CheckedRowCompanionBaseTransfer.lean:71`, `CheckedRowCompanionBaseTerminal` at `:108`, and compiled `checked_of_check_eq_true` at `:126`; the global matching layer remains separate by the file's explicit statement at `:12-13`.
5. `outsideAttachment`: prose-only, absent from production.
6. checked prune reachability: prose-only, absent from production matching. `prune` exists only as a bank capacity constructor.
7. FullBank capacity classes: implemented `CapKind = door | vertexSlack | c5Base | prune` at `E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\Gamma\FullBankToLengthSurplusCharge.lean:26`; typed `CapSource` has the same four constructors at `E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\Gamma\TypedFullBankSources.lean:24`.

## Actual theorem-chain components and breaks

The first independently compiled bank constructor is conditional on a provider Hall hypothesis. `ActiveComponentBankHall` is defined at `E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\Ell5ActiveComponentBankHall.lean:53`; `certificate_of_activeComponent_mixedDoorBankHall` at `:109` consumes it as `hHall` at `:126` and returns `FullBankRelaxedCoverCert` at `:130`. The target type is defined at `E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\Ell5FullBankInterface.lean:27`; its compiled algebraic consumer `bankedCutDomination_of_cert` is at `:43`.

There are two missing edges before final soundness:

- No compiled theorem maps `CollisionMatching` or the prose `CheckedTransferMatching` to `ActiveComponentBankHall`/`FullBankRelaxedCoverCert`.
- No compiled theorem maps `FullBankRelaxedCoverCert` to `FullBankGlobalPackage`.

The final ledger is a separate implemented interface: `FullBankGlobalPackage` at `E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\Gamma\FullBankToLengthSurplusCharge.lean:134` and `FullBankGlobalPackage.Checked` at `:177`. `Checked` is a provider record: it asks for local demand/cap bounds, kind-spend identities, nonnegative spend, no double spend, no cross-component spend, source uniqueness, reserve identities, row counts, and superadditivity (`:177-227`).

Once `P.Checked` is supplied, the remainder is kernel-proved. The local/global lemmas occur at `:229`, `:235`, `:242`, `:250`, `:256`, `:262`, and `:272`; `fullBankGlobalPackage_sound` at `:288` proves `lengthSurplusGD rows ≤ 25 * etaQ G c`; `gammaUpper_from_fullBankGlobalPackage` at `:311` applies `GammaAggregation.gammaUpper_from_lengthSurplus`, defined at `E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\GammaAggregation.lean:50`, to conclude `gammaOfGD G c rows ≤ G.n^2`.

The optional typed-charge bridge is also conditional bookkeeping: `chargeCertProviderOfFullBankLedger` at `E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\Gamma\FullBankChargeCertProvider.lean:54`, compiled checker theorem at `:64`, and final charge route at `:83`; that final route additionally takes the named `hGersh` provider at `:86`.

Typed door incidence is separate from the global package. `OwnEdgeDoorSourceData.Checked` is at `E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\Gamma\TypedFullBankSources.lean:109`; `DoorWallAdapter` is a named provider structure at `E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\Gamma\TypedOwnDoorHalfLayer.lean:35`; the compiled conditional constructor `halfLayerRouted_of_checkedEdgeDoorSources` is at `:61`. `FullBankPortSinks.lean` explicitly says its token subtypes/capacities do not provide legal incidence or Hall at `E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\Gamma\FullBankPortSinks.lean:80-81`.

## Smallest missing real graph-derived theorem

At the final interface, the smallest missing theorem is:

```text
(real graph/cut/complete-row hypotheses)
  -> exists P : FullBankGlobalPackage G c rows, P.Checked
```

No production declaration currently fixes that provider's formal signature. Internally it must supply the absent all-pattern transfer/typed-incidence exporter, no-double-spend proof, component ownership, and reserve identities. Merely proving a narrow ActiveScoped matching is insufficient.

## Impossibility and circularity warning

It is impossible to derive the needed wall incidence from `FullBankGlobalPackage.Checked` alone. The compiled exact countermodel `checkedAggregatePackage_and_noHalfLayerRouting` at `E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\AggregateLedgerNoIncidenceCounterexample.lean:154` gives a checked aggregate package together with failure of `HalfLayerRouted`; the source explains the missing incidence at `:8-16`.

Therefore:

- R29 does not refute FullBank: ActiveScoped omits common-blue, outside-attachment, typed Door, vertexSlack, c5Base exporter, and prune classes.
- R29 also cannot be declared absorbed in Lean: outside-attachment and `CheckedTransferMatching` are absent.
- A provider that simply assumes `demand_le_rhs`, no-double-spend, reserve identities, or port incidence would be circular. Those fields must be derived from the real graph and checked traces before invoking `fullBankGlobalPackage_sound`.

## Machine-readable artifacts and kernel evidence

- `dependency_graph.json`: 42 nodes, 35 typed edges; edge statuses distinguish kernel-proved, provider-required, and missing.
- `nodes.csv`, `edges.csv`, `source_patterns.csv`.
- `build_report.md` contains exact commands, rc values, greps, `#print axioms`, and SHA256 values.
- Green `ChainProbe.lean`: rc `0`, zero error/forbidden-token grep; SHA256 `BA7F84688ABC4CF8C9F496B401E4E8337E2DF3B09603176A3A5AAD873521B7DB`.
- Intentional negative `MissingSymbolProbe.lean`: rc `1`, exactly four unknown identifiers; SHA256 `69B4FA69A298328EE5811DBF00CBD6ECF7922FF178411EB0D6A4D9AE6225CC2E`.
- Production countermodel rebuild: rc `0`, zero error/forbidden-token grep; olean SHA256 `03E604E57725F4E5D5CCDDF7C48E59ED61797ECB37B911A41398206CFEDFF3AB`.
- All green probed declarations use axioms within `{propext, Classical.choice, Quot.sound}`; no `sorry`, `admit`, `native_decide`, or `sorryAx` occurred.
