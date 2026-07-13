# R33 checked collision-defect trade

## Production file

`problems/23/lean/Erdos23Delta0/Gamma/CheckedCollisionDefectTrade.lean`

The module imports `Erdos23Delta0.Gamma.Pattern5StaticOwnership` and reuses
`Pattern5StaticOwnership.BaseKeyComponentCoherent` on canonical
`SourceBase x Fin 2` half keys. It constructs no row state, source relation,
graph realization, row change, checked trade, or canonical feasible tuple.

## Exact declarations

All declarations are in
`Erdos23Delta0.Gamma.CheckedCollisionDefectTrade`.

- `Data`: state-indexed finite collision obligations, component labels, and
  the caller-supplied graph relation `sourceRealized`.
- `CoherentPartialMatching`: a matched obligation finset with subset proof,
  an injective source-half assignment, source-realization proofs, and
  base-key component coherence.
- `CoherentPartialMatching.unmatched`
- `CoherentPartialMatching.unmatchedCount`
- `CoherentPartialMatching.unmatchedCount_eq_card_sub_matched`
- `CoherentPartialMatching.empty`
- `CoherentPartialMatching.unmatched_empty`
- `CoherentPartialMatching.unmatchedCount_empty`
- `Data.collisionDefect`: the minimum unmatched count over coherent,
  graph-realized partial matchings in one supplied state.
- `Data.collisionDefect_le_unmatchedCount`
- `Data.exists_matching_realizing_collisionDefect`
- `Data.collisionDefect_eq_zero_iff_exists_total`
- `Data.collisionDefect_le_obligationCard`
- `CheckedCollisionDefectTrade`: explicit old/new state realization, a typed
  simultaneous row-change witness and realization, an old exact-defect
  matching, and a new coherent matching with fewer unmatched obligations.
- `defect_lt`
- `old_defect_eq_demand_sub_matched`

The audited fixed-state bridge has the exact type:

```lean
theorem Data.collisionDefect_eq_zero_iff_exists_total
    (D : Data State Obligation SourceBase Comp) (state : State) :
    D.collisionDefect state = 0 ↔
      ∃ M : CoherentPartialMatching D state,
        M.matched = D.obligations state
```

Thus totality still carries `M.source_realized` and
`M.base_component_coherent`; the theorem does not infer graph existence.

## Lean verification

Toolchain command, run from
`E:\Projects\ErdosProblems\formal-conjectures`:

```powershell
lake env lean --version
```

Result:

```text
Lean (version 4.27.0, x86_64-w64-windows-gnu, commit db93fe1608548721853390a10cd40580fe7d22ae, Release)
```

Final production build command from the same directory:

```powershell
$env:LEAN_PATH='E:\Projects\ErdosProblems\tmp\fanout\r32_static_ownership\olean;E:\Projects\ErdosProblems\problems\23\lean'
lake env lean -R .. -o ..\tmp\fanout\r33_trade_lean\olean\Erdos23Delta0\Gamma\CheckedCollisionDefectTrade.olean ..\problems\23\lean\Erdos23Delta0\Gamma\CheckedCollisionDefectTrade.lean *> ..\tmp\fanout\r33_trade_lean\production_build_final.log
```

Result: exit code 0; `production_build_final.log` is empty.

The scratch `olean` tree is an isolated hardlink closure of the existing
Lean-4.27 R32 cache plus the newly built module. Final import/axiom probe:

```powershell
$env:LEAN_PATH='E:\Projects\ErdosProblems\tmp\fanout\r33_trade_lean\olean;E:\Projects\ErdosProblems\problems\23\lean'
lake env lean -R .. -o ..\tmp\fanout\r33_trade_lean\olean\ImportAxiomProbe.olean ..\tmp\fanout\r33_trade_lean\ImportAxiomProbe.lean *> ..\tmp\fanout\r33_trade_lean\import_axiom_probe_final.log
```

Result: exit code 0. The probe imports the compiled production module,
checks the public signatures, and prints axioms for eight load-bearing
theorems, including `collisionDefect_eq_zero_iff_exists_total`.

Finite 1-to-0 instantiation probe:

```powershell
lake env lean -R .. -o ..\tmp\fanout\r33_trade_lean\olean\TradeInstantiationProbe.olean ..\tmp\fanout\r33_trade_lean\TradeInstantiationProbe.lean *> ..\tmp\fanout\r33_trade_lean\trade_instantiation_probe_final.log
```

Result: exit code 0. It proves an old defect of one, obtains new defect zero
from a total coherent matching through the audited bridge, constructs a
typed checked trade, and proves `tiny_defect_lt`.

Every theorem printed by the two probes reports only:

```text
propext
Classical.choice
Quot.sound
```

Forbidden-token and whitespace checks:

```powershell
$targets=@(
  'problems/23/lean/Erdos23Delta0/Gamma/CheckedCollisionDefectTrade.lean',
  'tmp/fanout/r33_trade_lean/ImportAxiomProbe.lean',
  'tmp/fanout/r33_trade_lean/TradeInstantiationProbe.lean'
)
rg -n "\b(sorry|admit|native_decide)\b|sorryAx" $targets
$targets | Select-String -Pattern '[ \t]+$'
```

Results: no forbidden-token matches (`rg` exit 1), zero trailing-whitespace
matches, and all three files end in a newline.

## SHA-256

```text
7467DC4E3B37BF8BC782DD2DEC1615F5171BFD07D8C3709A4D5F61CBD19C785A  problems/23/lean/Erdos23Delta0/Gamma/CheckedCollisionDefectTrade.lean
545D189D899F96A16F422F7E2804933221A20A1DD72BC6702BB4BC165F374876  tmp/fanout/r33_trade_lean/ImportAxiomProbe.lean
1912287208F3648A6E8E20E62390257170EEBAED385DA49838699E37CBF5800D  tmp/fanout/r33_trade_lean/TradeInstantiationProbe.lean
E7F76905A58929F204603255D37CB16B4A8909FF514A3B1D15F7F883449EC1DF  tmp/fanout/r33_trade_lean/olean/Erdos23Delta0/Gamma/CheckedCollisionDefectTrade.olean
A6BB99321405D19AB6798486D4E231BE39A76F4AB1B27671D99D0E77476790E8  tmp/fanout/r33_trade_lean/olean/ImportAxiomProbe.olean
AF9243560848A47BA579575E0D1C4C535AEDE35D99A94D5265D7E1AD9DF98F88  tmp/fanout/r33_trade_lean/olean/TradeInstantiationProbe.olean
0941B5879F540530B18DB47F82DFD2B36D9D2CAC15CCC133DD171AB27BD380BC  tmp/fanout/r33_trade_lean/lean_version.log
E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855  tmp/fanout/r33_trade_lean/production_build_final.log
BF6DB82C6F80103B3ECD6E7BF32A72BCA1206A8B6E5B7D94769B612EBFFC27EB  tmp/fanout/r33_trade_lean/import_axiom_probe_final.log
134BA7C538F187054512AFE070D045DBF31E47D7B42EEF0DAC6403FC65C9AAB2  tmp/fanout/r33_trade_lean/trade_instantiation_probe_final.log
```

## Remaining graph-theoretic obligation

The finite descent and zero-defect bridge are complete only after the
concrete Gamma layer supplies the explicit realization fields. For a
positive-defect optimal coherent matching at a selected row state, it must
either coherently augment that matching or construct a graph-realized
simultaneous row change and a new coherent partial matching with fewer
unmatched obligations.

In R33 this is `deficientCollisionCut_lockExposureOrTrade`; its first open
internal lemma is `lockTrace_step`. That proof must validate the deduplicated
P1/P2/P3/P4/P5/common-blue relation, reservation exclusion, component labels,
old/new graph states, and the row-change witness. To reach canonical
collision feasibility, it must ultimately supply a state with the total
matching appearing on the right side of
`collisionDefect_eq_zero_iff_exists_total`.
