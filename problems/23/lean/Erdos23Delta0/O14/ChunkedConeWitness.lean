import Erdos23Delta0.O14.ConeEvalBridge
import Erdos23Delta0.O14.EQODL1CoverInterface

/-!
# Generator-facing chunked cone witnesses

`ConeEvalBridge` proves the value-level theorem used by generated O14 payloads.
This module packages the generated data into a small proof object and exposes the
exact chart-soundness shape required by `EQODL1CoverInterface`.

The production emitter should generate one `ChunkedConeWitness` per routed chart
case (or a dispatcher returning one).  This keeps the generated chart files
chunked while avoiding a single giant `PolyCert.ConeCert.hid` reduction.
-/

namespace Erdos23Delta0
namespace O14
namespace ChunkedCone

open PolyCert
open ODLFull
open ConeEvalBridge
open EQODL1CoverInterface

universe u

/-- A chunked cone certificate for one emitted O14 core.

The fields mirror `coreODLGoal_of_chunkedConeEval`; generated chart modules fill
them with sharded NF equalities and exact rational nonnegativity lemmas.
-/
structure Witness
    {G : CertGraph.GraphData} {c : CertGraph.CutData}
    {rows : CertGraph.RowDB} {Q : CertGraph.RowCert}
    (core : ODLCoreData G c rows Q) : Type where
  pairs : List (NF × NF)
  base : NF
  mults : List NF
  slacks : List NF
  env : Var → ℚ
  hvars : ∀ v, 0 ≤ env v
  hbase : base.allCoeffNonneg = true
  hmults : mults.all NF.allCoeffNonneg = true
  hslacks : ∀ s ∈ slacks, 0 ≤ NF.eval env s
  hchunks : checkEqPairs pairs = true
  hcombo :
    NF.eval env ((pairs.map Prod.snd).flatten) =
      NF.eval env (comboNF base mults slacks)
  htarget :
    NF.eval env ((pairs.map Prod.fst).flatten) = coreDefect core

/-- Soundness of a generated chunked cone witness. -/
theorem Witness.sound
    {G : CertGraph.GraphData} {c : CertGraph.CutData}
    {rows : CertGraph.RowDB} {Q : CertGraph.RowCert}
    {core : ODLCoreData G c rows Q}
    (W : Witness core) :
    CoreODLGoal G c rows Q core := by
  exact coreODLGoal_of_chunkedConeEval core W.pairs W.base W.mults W.slacks
    W.env W.hvars W.hbase W.hmults W.hslacks W.hchunks W.hcombo W.htarget

/-- Per-chart generated chunked witnesses.  This is the generator-facing
counterpart of `EQODL1ChartSound`: every instance routed to a present chart has
an exact chunked cone witness for its emitted ODL core.
-/
structure ChartWitnesses
    {G : CertGraph.GraphData} {c : CertGraph.CutData}
    {rows : CertGraph.RowDB} {Q : CertGraph.RowCert}
    {Inst : Type u}
    (coreOf : Inst → ODLCoreData G c rows Q)
    (C : EQODL1Classifier Inst) (P : EQODL1CoverPayload) : Type (u + 1) where
  witness :
    ∀ i, i < ChartCount → P.present i = true →
      ∀ I, C.chartOf I = i → Witness (coreOf I)

/-- Turn generated chunked witnesses into the chart-soundness provider consumed
by the O14 cover interface.
-/
theorem chartSound_of_chartWitnesses
    {G : CertGraph.GraphData} {c : CertGraph.CutData}
    {rows : CertGraph.RowDB} {Q : CertGraph.RowCert}
    {Inst : Type u}
    {coreOf : Inst → ODLCoreData G c rows Q}
    {C : EQODL1Classifier Inst} {P : EQODL1CoverPayload}
    (W : ChartWitnesses coreOf C P) :
    EQODL1ChartSound Inst
      (fun I => CoreODLGoal G c rows Q (coreOf I)) C P where
  sound := by
    intro i hi hp I hchart
    exact (W.witness i hi hp I hchart).sound

end ChunkedCone
end O14
end Erdos23Delta0


