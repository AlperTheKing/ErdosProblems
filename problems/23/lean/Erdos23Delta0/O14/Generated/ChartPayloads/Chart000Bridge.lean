import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000Cone

/-!
# Chart 000 bridge

This module connects the accepted generated `Chart000Cone` witness factory to
the ODL core goal.  It deliberately does not claim the full 108-chart cover:
the caller must still supply the instance-specific `env`, slack
nonnegativity, combo equality, and target/core-defect equality.
-/

namespace Erdos23Delta0
namespace O14
namespace Generated
namespace ChartPayloads
namespace Chart000Bridge

open ODLFull
open PolyCert

/-- The accepted Chart000 chunked cone witness proves the corresponding ODL
core goal once the structural/core binding layer supplies its semantic inputs.
-/
theorem coreODLGoal_of_chart000Cone
    {G : CertGraph.GraphData} {c : CertGraph.CutData}
    {rows : CertGraph.RowDB} {Q : CertGraph.RowCert}
    (core : ODLCoreData G c rows Q) (env : Var → ℚ)
    (hvars : ∀ v, 0 ≤ env v)
    (hslacks :
      ∀ s ∈ Chart000Cone.Main.slacks, 0 ≤ NF.eval env s)
    (hcombo :
      NF.eval env ((Chart000Cone.Main.pairs.map Prod.snd).flatten) =
        NF.eval env
          (comboNF Chart000Cone.Main.base Chart000Cone.Main.mults
            Chart000Cone.Main.slacks))
    (htarget :
      NF.eval env ((Chart000Cone.Main.pairs.map Prod.fst).flatten) =
        coreDefect core) :
    CoreODLGoal G c rows Q core := by
  exact
    (Chart000Cone.Main.chart000Witness core env hvars hslacks hcombo
      htarget).sound

#print axioms coreODLGoal_of_chart000Cone

end Chart000Bridge
end ChartPayloads
end Generated
end O14
end Erdos23Delta0
