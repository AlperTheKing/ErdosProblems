# lean_bridge R29 synthesis

## Scope and goal state

`get_goal` returned `goal: null`; no active goal attachment was available. The lane used the repository-local `GOAL_LOOP.md`, `coordination/CODEX_ONBOARDING.md`, the newest R29 block at `coordination/CLAUDE_TO_CODEX.md:13979`, and `problems/23/writeup/WALL_ATTACK_R29_GPTPRO56.md`.

No production Lean file was edited by this lane. The user/another lane updated `ActiveScopedCoordinateTransport.lean` during the audit; its current source was re-read and rebuilt.

## Exact recommended interface

The compiling scratch is `GlobalDescentInterface.lean`. Its load-bearing declarations are:

```lean
def HallFailureHasScopedScoreGlobalDescent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  forall omega : RowChoice bads,
    ¬Nonempty (Matching G c omega) ->
      Exists fun eta : RowChoice bads =>
        scopedObligationScore G c eta < scopedObligationScore G c omega

def EveryScopedScoreMinimizerHasMatching
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  forall omega : RowChoice bads,
    (forall eta : RowChoice bads,
      scopedObligationScore G c omega <= scopedObligationScore G c eta) ->
    Nonempty (Matching G c omega)
```

The scratch proves:

```lean
theorem globalDescent_iff_everyMinimizerHasMatching :
  HallFailureHasScopedScoreGlobalDescent G c bads <->
    EveryScopedScoreMinimizerHasMatching G c bads

theorem minimumActiveScopedHall_of_globalDescent
    (hrows : RowsNonempty bads)
    (hdescent : HallFailureHasScopedScoreGlobalDescent G c bads) :
    MinimumActiveScopedHall G c bads hrows

theorem realMinimumActiveScopedHall_of_globalDescent
    ...
    (hdescent : RealHallFailureHasScopedScoreGlobalDescent G c bads) :
    MinimumActiveScopedHall G c bads hdb.rowsNonempty
```

This is the minimal reusable unbounded-descent interface. `eta` is an arbitrary valid `RowChoice`; it need not have a matching. `scopedCanonicalChoice` minimizes over all `RowChoice`, so any lower score is already contradictory. Adding Hamming distance, a replacement relation, reachability, or `Matching eta` is unnecessary and strictly strengthens the open graph theorem.

The pointwise equivalence itself does not require finiteness or nonemptiness. The concrete canonical wrapper requires `RowsNonempty bads`, already supplied by `CompleteShortestRowDB.rowsNonempty`.

## Existing compiled chain

1. `ActiveScopedMinimumExchange.lean:250-273` already constructs `minScopedChoice` with `chooseFiniteMinimizer`, defines `scopedCanonicalChoice`, and proves `scopedCanonicalChoice_optimal`.
2. `ActiveScopedMinimumExchange.lean:276-283,595-607,673-694` defines the now-falsified one-row witness/frontier and proves the canonical contradiction from that hypothesis.
3. `ActiveScopedOwnerHallReduction.lean:121-137` proves matching iff owner-shore Hall and matching failure iff an owner-shore defect exists.
4. `ActiveScopedVariationReduction.lean:159-199,399-436` turns negative total Hamming-one variation into one-row descent and then into the minimum Hall conclusion.
5. `ActiveScopedCoordinateTransport.lean` turns coordinate transports into negative Hamming-one variation. These implications remain logically compiled, but R29 prevents their universal graph hypotheses from being the final frontier.
6. Current CoordinateTransport persistence surface compiles: `newComponent_reachable_old_of_not_touchesChangedRows` at 346, `activeOwner_old_of_new_not_touchesChangedRows` at 370, `selectedLoad_replaceOne_of_owner_not_mem_changed` at 386, `activeDegree_new_le_old_of_not_touchesChangedRows` at 416, and `hitNeedUnits_new_le_old_of_not_touchesChangedRows` at 444.

Source rebuilds, all direct Lean 4.27.0, all with `RC=0` and no `error:` token:

| Module | Seconds |
|---|---:|
| ActiveScopedMinimumExchange | 26.35 |
| ActiveScopedVariationReduction | 25.44 |
| ActiveScopedCoordinateTransport, first/current confirmed | 33.16 / 23.87 |
| ActiveScopedOwnerHallReduction | 20.19 |

`GlobalDescentInterface.lean` rebuilt with `RC=0`. Token grep across it and the four audited production sources found zero `sorry`, `admit`, `native_decide`, or `sorryAx` matches. Separate axiom probes for all three new theorems printed exactly `[propext, Classical.choice, Quot.sound]`.

## Exact falsifiers and non-implications

1. R29 claims a 2,943-vertex Hall-failing tuple of score 30,811 for which all 459,004 Hamming-one changes have score at least 30,813. If independently gated, this falsifies `HallFailureHasScopedScoreOneRowDescent`, `HallFailureHasNegativeOneRowVariation`, and any universal transport premise that implies them on that instance.
2. R29 does not falsify global descent unless 30,811 is also globally minimal. A lower multi-row tuple would preserve the global interface. A verified Hall-failing global minimum would decisively falsify it.
3. One Hall-good minimizer does not imply the current opaque canonical minimizer is Hall-good. Exact two-state model: scores `(0,0)`, matching flags `(true,false)`, canonical selector chooses the second state. Therefore an existence-only theorem needs a new Hall-aware tie-break or a changed target.
4. `Relation.TransGen` or coordinated-step reachability is not required by the minimum contradiction and is unsupported after Hamming-one failure. It may be useful inside a future construction, but should not appear in the bridge contract.
5. The all-global-minimizers statement is stronger than the single opaque canonical target but is exactly equivalent to universal unbounded descent. This is the theorem-of-record requested after R29.

The R29 graph certificate itself remains ungated in this lane: the archive gives a prose SHA prefix only, not the full constructor/artifact. Its displayed arithmetic is consistent, but graph validity, max cut, row database, all deltas, and global landscape are separate obligations.

## Remaining mathematical gaps

1. Prove `RealHallFailureHasScopedScoreGlobalDescent`: from any Hall-failing `omega`, construct some arbitrary `eta` with strictly lower scoped score.
2. Gate the 2,943-vertex constructor and decide whether score 30,811 is global. This is the direct falsifier test for the new theorem.
3. Convert the new persistence lemmas into a simultaneous trade. The parallel `global_min_proof` lane isolates: coherent realization of coordinate choices, deficient-shore persistence, and terminal amortization of collision cost against component-splitting demand drop.
4. Choose production naming and location. The minimal module imports only `ActiveScopedMinimumExchange`; Variation and CoordinateTransport are not dependencies of the bridge.
5. Keep axiom probes out of final production sources. The parallel `GlobalScopedMinimum.lean` has equivalent declarations but embeds `#print axioms`; lean_bridge separates `AxiomProbe.lean`.

## Parallel reconciliation

`tmp/fanout/global_min_proof/lead/GlobalScopedMinimum.lean` independently proves the same equivalence and wrappers with different names. Its SHA256 is `5A6B8B41407061CAC35FA56A8A319A55C84DE670A04AA7B1F2E419FAD19CF03F`. There is no semantic disagreement between the two lanes.

## Source and artifact hashes

| Artifact | SHA256 |
|---|---|
| GOAL_LOOP.md | `E91A2F03BC6774D622D9610B24394A0B4338F6543D7BF19E4464FF5D450E014B` |
| coordination/CODEX_ONBOARDING.md | `E3012793ACCDE4E8F8FA3ED3E514A794A7D006A07E4BDC23E4239D14C9D61AD0` |
| coordination/CLAUDE_TO_CODEX.md | `B533191BAF54A2E3D53CE05E1F46269B78E6EEDBA90F08CB9B80B7FEAB6E9126` |
| WALL_ATTACK_R29_GPTPRO56.md | `FFF06D97F2E574FE2D66B9CEA4F3BC4244037A92EB8ED5BD363ECA73C8591B04` |
| ActiveScopedMinimumExchange.lean | `8F39D8443DDC26D38BB76DA10B9BED223F5F141546E6194C5177779F03174BC8` |
| ActiveScopedVariationReduction.lean | `F3FFD8B22EDD2DE55D53664F20B77651DF4B35033BA3E1ECB5D029AA11F8A921` |
| ActiveScopedCoordinateTransport.lean | `6B10458BEDD26B4D460FDD4AD034D55CB6B1DEE16A2691F22460E562941DC272` |
| ActiveScopedOwnerHallReduction.lean | `6A4D47533D10E4B04EB19CDA0D0554658ABD434C94C04566A01916708A90E8F0` |
| GlobalDescentInterface.lean | `90033FDFCF1BF7CE67781C67D0ED5C91EECF9DDEC1B062780EA61371E20996A6` |
| GlobalDescentInterface.olean | `A5908759339345EEBD4E2A4B534236AF91BBB3296468E4BF76FDD8A39918CD14` |
| axioms.log | `E8B2202B0A53F9532B36A9E54AB457C869C81E2FD9484F25C3762642177251C9` |

## Descendant ledger

Exactly nine descendants were launched, each on a distinct subproblem and forbidden to edit shared production files. All terminated. The copied CLI lacked sibling `codex-code-mode-host.exe`; seven descendants therefore returned blocker-only reports. `theorem_extraction` and `global_semantics` still returned useful theorem-level analyses from prompt context, both agreeing that arbitrary strict descent is sufficient and reachability is unjustified.

| Descendant | Outcome | report.md SHA256 |
|---|---|---|
| source_audit | host-blocked | `1C4BCB0E61A78140A9494F6C217C1C5C2A2863BF08E06E7DEF9E6B7E3BBE4043` |
| theorem_extraction | conceptual theorem extraction | `6C1BF8B668F6688E2688C841A0B8A4F9B918F6BFCF8834D5B912C46A162F0A4C` |
| finite_minimizer | host-blocked | `8BB35C091072BF3C57960E2D290440E40EBA14C80CC17632E6C073C4B31ADEA7` |
| global_semantics | conceptual semantics/falsifiers | `D76D686C65113563636F240F42C35A4088916AF2135DD9DBBCE8AA14AB5DAF0A` |
| matching_duality | host-blocked | `8E63EF3E1E37A0CBE438FBB8BEBE42960E25AFA0B3938607825E96DE2F2E28FB` |
| axiom_audit | host-blocked | `9A8AF5072218257A3906179056E20FC05B9A0F007C700787C462C61CA08FBFC6` |
| formalization_cost | host-blocked | `85895958139E4E42FEB2620AC345CBB776BF8C2158717BD361CA55F3CF5D1712` |
| falsifier_audit | host-blocked | `995C142D0D6D2FF53156988690148A71D628F0916C3D64AF0104B2F8D74414CF` |
| compile_probe | host-blocked | `E1D967875086CFFC73EDA10171697845BAFBDCDA0074D3B097489AA6D325DC51` |

The lead independently completed the blocked source, minimizer, matching, axiom, cost, falsifier, and compile audits. No floating-point computation was used as evidence or acceptance.
