import Erdos23Delta0.O14.EQODL1LeafProvider

/-!
# O14 chart cover to ODLFull

This is the module-30 glue theorem for EQ-ODL1 leaves.  It composes:

* the O14 checked-cover EQ leaf provider;
* the existing `Seed3ODLInternalLinks`;
* the existing semantic-tree checker;
* the root-represents-row bridge.

No chart data or structural classifier proof is introduced here.  Those remain
the module-29/data obligations feeding `EQODL1LeafCover`.
-/

namespace Erdos23Delta0
namespace O14
namespace ChartCoverToODLFull

open CertGraph
open CertGraph.Seed3RouteTree
open ODLFull
open EQODL1LeafProvider

/-- O14 EQ cover + semantic route-tree check gives the row-level ODL bound. -/
theorem rowODL_of_o14_eq_cover_semantic_tree
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} {sem : ODLNodeSemantics G c rows Q T}
    {root : Seed3Node} {Inst : Type*}
    (base : ConcreteODLLeafChecks G c rows Q T sem)
    (cover : EQODL1LeafCover G c rows Q T sem Inst)
    (links : Seed3ODLInternalLinks G c rows Q T sem)
    (hfind : findNode? T T.root = some root)
    (hcheck :
      checkSeed3ODLSemanticTree T sem
        (leafProviders_of_concreteChecksWithEQ
          (concreteChecksWithEQ_of_o14_cover base cover))
        links = true)
    (hrep : RootRepresentsRow G c rows Q (sem.coreOf root.id)) :
    rowSum G c rows Q ≤ (G.n : ℚ) + etaQ G c := by
  exact ODLFull_of_semantic_tree
    (leafProviders_of_concreteChecksWithEQ
      (concreteChecksWithEQ_of_o14_cover base cover))
    links hfind hcheck hrep

#print axioms rowODL_of_o14_eq_cover_semantic_tree

end ChartCoverToODLFull
end O14
end Erdos23Delta0
