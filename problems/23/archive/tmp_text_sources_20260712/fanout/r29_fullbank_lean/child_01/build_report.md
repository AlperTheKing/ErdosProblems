# Kernel build report

## ChainProbe.lean

Command (cwd `E:\Projects\ErdosProblems\formal-conjectures`):

```powershell
$env:LEAN_PATH='E:\Projects\ErdosProblems\tmp\claude_lean_o_base_v1'
lake env lean --root='E:\Projects\ErdosProblems' --o='E:\Projects\ErdosProblems\tmp\fanout\r29_fullbank_lean\child_01\ChainProbe.olean' 'E:\Projects\ErdosProblems\tmp\fanout\r29_fullbank_lean\child_01\ChainProbe.lean'
```

- rc: `0`
- case-insensitive grep `error`: `0`
- grep `\bsorry\b|\badmit\b|native_decide|sorryAx` over source+log: `0`
- source SHA256: `BA7F84688ABC4CF8C9F496B401E4E8337E2DF3B09603176A3A5AAD873521B7DB`
- olean SHA256: `06DE4694D4D3D04A9F1D9AFEE960B531BA93CD48364094BF43C952B5E9C01CC1`
- log SHA256: `1D1A1D784813D99BF33BCC04E52492F62AC17534AF9FF637B81B7EB28D7DA941`

Exact `#print axioms` output summary:

- `CheckedC5BaseTransfer.TerminalData.check_eq_true_iff`: `[propext, Quot.sound]`
- `CheckedRowCompanionBaseTransfer.TerminalData.checked_of_check_eq_true`: `[propext, Quot.sound]`
- `CanonicalCollisionHall.collisionMatching_nonempty_iff_hall`: `[propext, Classical.choice, Quot.sound]`
- `Ell5ActiveComponentBankHall.certificate_of_activeComponent_mixedDoorBankHall`: `[propext, Classical.choice, Quot.sound]`
- `TypedOwnDoorHalfLayer.halfLayerRouted_of_checkedEdgeDoorSources`: `[propext, Classical.choice, Quot.sound]`
- `FullBankGlobalPackage.fullBankGlobalPackage_sound`: `[propext, Classical.choice, Quot.sound]`
- `FullBankGlobalPackage.gammaUpper_from_fullBankGlobalPackage`: `[propext, Classical.choice, Quot.sound]`
- `FullBankGlobalPackage.gammaUpper_from_fullBankPackage_via_chargeCertV2`: `[propext, Classical.choice, Quot.sound]`

Full output: `E:\Projects\ErdosProblems\tmp\fanout\r29_fullbank_lean\child_01\ChainProbe.build.log`.

## MissingSymbolProbe.lean (intentional negative probe)

Command (same cwd/environment):

```powershell
lake env lean --root='E:\Projects\ErdosProblems' --o='E:\Projects\ErdosProblems\tmp\fanout\r29_fullbank_lean\child_01\MissingSymbolProbe.olean' 'E:\Projects\ErdosProblems\tmp\fanout\r29_fullbank_lean\child_01\MissingSymbolProbe.lean'
```

- rc: `1` (expected)
- grep `error`: `4`
- forbidden-token grep: `0`
- source SHA256: `69B4FA69A298328EE5811DBF00CBD6ECF7922FF178411EB0D6A4D9AE6225CC2E`
- log SHA256: `64A1E50AF879E801D731D0F4AE0FE48867A4678851959CF419113366059AFCFC`
- exact unknown identifiers: `CheckedTransferMatching`, `CheckedOutsideAttachmentBaseTerminal`, `checkedTransferMatching_to_activeFullBank`, `checkedMatching_withOutsideAttachment_sound`.

## AggregateLedgerNoIncidenceCounterexample.lean

Command (cwd `E:\Projects\ErdosProblems\formal-conjectures`):

```powershell
$env:LEAN_PATH='E:\Projects\ErdosProblems\tmp\claude_lean_o_base_v1'
lake env lean --root='E:\Projects\ErdosProblems\problems\23\lean' --o='E:\Projects\ErdosProblems\tmp\fanout\r29_fullbank_lean\child_01\AggregateLedgerNoIncidenceCounterexample.olean' 'E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\AggregateLedgerNoIncidenceCounterexample.lean'
```

- rc: `0`
- grep `error`: `0`
- forbidden-token grep: `0`
- production source SHA256: `624C56995234F4EF5D68804013CE69D66962CFB2A3230DE7C8D601DB6870089F`
- olean SHA256: `03E604E57725F4E5D5CCDDF7C48E59ED61797ECB37B911A41398206CFEDFF3AB`
- log SHA256: `1FB2DB499C28B5743EEB2BDB5378CC28E6CD5354BE1482101B75FC3CE20A495F`
- `#print axioms checkedAggregatePackage_and_noHalfLayerRouting`: `[propext, Classical.choice, Quot.sound]`.
