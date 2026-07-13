# R45 M1: Checked sink-neutral attachment class

## Scope

Created the M1 production interface only.  The module is specialized to
`CollisionDefectGraphAdapter.defectData`; it does not assume or prove the
missing exposure/augmentation theorem.

## Source

- `problems/23/lean/Erdos23Delta0/Gamma/CheckedSinkNeutralAttachmentClass.lean`
- SHA256: `D861DCBCA028831C41D5FF105F33411684C9432744F3D31E7DFD13149197125A`

## Production definitions

- `AttachmentDefectData`
- `CollisionTracePayload`
- `CollisionTraceState`
- `CheckedMatchedSourceStep`
- `CheckedBaseConflictStep`
- `CheckedTwoEdgeDetour`
- `CheckedNeutralAttachmentStep`
- `SinkNeutralAttachmentClassData`
- `CheckedSinkNeutralAttachmentClass`
- `CheckedSinkNeutralAttachmentClass.Augmentation`

The trace payload contains a real row tuple, exact optimal coherent matching,
globally minimum defect proof, least unmatched root, and same-component
alternating cursor.  The neutral relation is exactly the archived union of
matched-source, base-conflict, and equal-defect live-detour edges.

## Checkers and principal soundness theorems

- `checkMatchedSourceStep_eq_true_iff`
- `checkBaseConflictStep_eq_true_iff`
- `checkTwoEdgeDetour_eq_true_iff`
- `checkNeutralAttachmentStep_eq_true_iff`
- `SinkNeutralAttachmentClassData.check_eq_true_iff`
- `SinkNeutralAttachmentClassData.sound_of_check_eq_true`
- `SinkNeutralAttachmentClassData.edge_preserves_defect`
- `SinkNeutralAttachmentClassData.neutral_successor_mem`
- `CheckedSinkNeutralAttachmentClass.defect_pos`
- `CheckedSinkNeutralAttachmentClass.edge_iff_neutral`
- `CheckedSinkNeutralAttachmentClass.stronglyConnected`
- `CheckedSinkNeutralAttachmentClass.sink_closed`

## Independent builds

Lean version:

```text
Lean 4.27.0, commit db93fe1608548721853390a10cd40580fe7d22ae
```

Command shape, run twice into distinct output roots:

```powershell
$env:LEAN_PATH='E:\Projects\ErdosProblems\tmp\claude_lean_o_base_v1'
lake env lean --root=E:\Projects\ErdosProblems \
  --o=<fresh-output> \
  E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\Gamma\CheckedSinkNeutralAttachmentClass.lean
```

Both runs returned `rc=0`.  Their `.olean` files are byte-identical:

```text
2BBF813BD5C298B19078E0913AAA9038AB0CDF66409488BE73297AAF7EE1B611
```

Build logs are byte-identical:

- `logs/build.log`
- `logs/replay_build.log`
- SHA256: `F87D853DCCE05DA7A86C44524FCCAE0C7E330CA832CD5DB89A84426B01FF3A45`

All printed theorem dependencies are subsets of:

```text
propext
Classical.choice
Quot.sound
```

The source and both logs contain no `sorry`, `admit`, `native_decide`,
`sorryAx`, compiler error, or compiler warning.

## Explicit non-result

No theorem in this module constructs an augmentation, proves positive
exposure, or excludes a positive-defect sink class.  The type
`CheckedSinkNeutralAttachmentClass.Augmentation` is only the downstream target
shape.
