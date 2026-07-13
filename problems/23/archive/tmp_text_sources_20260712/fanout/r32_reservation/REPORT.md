# R32 micro-reservation ledger

## Implemented surface

`CheckedMicroReservationLedger.lean` defines:

- `PhysicalHalfKey`: the ordered `(sourceX, sourceY, half)` identity, with
  `ofFreeHalf_injective` proving that only proof fields are erased;
- `SourceFamily`: P1, P2, P3, P4, P5, and common-blue audit tags;
- exact rational keyed spends `rawFreeSpendAtKey` and
  `tokenizedSpendAtKey`;
- `PhysicalHalfExclusive`, checking their sum is at most one per canonical
  key;
- typed bank terms using production `TypedLedgerToken` values;
- the exact term law
  `priorSpend + localReserve + newSpend <= term.capQ`;
- source-key and typed-term deduplication;
- ordered-base-key component coherence for the two half bits;
- Boolean reflection through `check_eq_true_iff` and conservative semantic
  export through `sound_of_check_eq_true`;
- residual-capacity lemmas and a coherent base-component labeling;
- `GraphExistenceHypothesis` and `sound_of_graph_existence`, which require a
  caller-supplied graph realization and checked-ledger existence.

Source-family tags create no legality or capacity.  The module proves no row
choice, matching, graph realization, main theorem, or graph-level existence
statement.

## Verification

Lean version: 4.27.0.

Production build:

```text
lake env lean -R .. -o <owned olean> \
  ../problems/23/lean/Erdos23Delta0/Gamma/CheckedMicroReservationLedger.lean
```

Result: exit code 0.  Independent import probe: exit code 0.

The ten imported declaration probes use only:

```text
propext
Classical.choice
Quot.sound
```

`ofFreeHalf_injective` uses only `propext` and `Quot.sound`.

Exact forbidden-token scan for `sorry`, `admit`, and `native_decide`: zero
hits.  Target-only `git diff --check`: pass.

## Hashes

```text
D5DEA65048E11E247244FB60408674074077031DC1FB6459C27B67E2EB83AD38  CheckedMicroReservationLedger.lean
A1232CFE8C68BE4381FFB7689BC68E86A8E2F8CCE9DCC56FB4BBEC9F622C63BF  build_04.log
1BA433098BE526F5B01C302D21B345FC28B63D6BDD67629FFCB558CC109D02BB  axiom_probe_04.log
262F2D266A850857FD441B3E1F766EAD05D875DFB27C8B5E6E7DD66F1F8F9C9C  CheckedMicroReservationLedger.olean
```
