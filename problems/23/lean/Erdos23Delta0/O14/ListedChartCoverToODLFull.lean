import Erdos23Delta0.O14.ChartCoverToODLFull
import Erdos23Delta0.O14.Generated.ListedLeafCover

/-!
# O14 listed chart cover to ODLFull

This is the semantic-dispatch adapter for the v108 listed chart registry.  It
keeps generated chart payloads separate from the route-tree proof: callers only
have to attach a listed EQ-ODL1 instance to each EQ leaf, prove the semantic core
equality for that attachment, and provide the chart-specific bridge inputs.
-/

namespace Erdos23Delta0
namespace O14
namespace ListedChartCoverToODLFull

open CertGraph
open CertGraph.Seed3RouteTree
open ODLFull
open EQODL1LeafProvider
open ChartCoverToODLFull

/-- Listed v108 chart data plus the semantic route-tree checker gives the
row-level ODL bound for EQ leaves. -/
theorem rowODL_of_listed_o14_eq_cover_semantic_tree
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} {sem : ODLNodeSemantics G c rows Q T}
    {root : Seed3Node}
    (base : ConcreteODLLeafChecks G c rows Q T sem)
    (instOf :
      Seed3Node → PayloadRef → Generated.ListedShapeInst G c rows Q)
    (core_eq :
      ∀ n ref, n.kind = NodeKind.leaf LeafTag.EQ ref →
        sem.coreOf n.id = (instOf n ref).inst.core)
    (bridge : Generated.ChartBridgeInputs
      (fun I : Generated.ListedShapeInst G c rows Q => I.inst.core)
      (Generated.listedClassifier (G := G) (c := c) (rows := rows) (Q := Q)))
    (links : Seed3ODLInternalLinks G c rows Q T sem)
    (hfind : findNode? T T.root = some root)
    (hcheck :
      checkSeed3ODLSemanticTree T sem
        (leafProviders_of_concreteChecksWithEQ
          (Generated.concreteChecksWithListedEQ base instOf core_eq bridge))
        links = true)
    (hrep : RootRepresentsRow G c rows Q (sem.coreOf root.id)) :
    rowSum G c rows Q ≤ (G.n : ℚ) + etaQ G c := by
  exact rowODL_of_o14_eq_cover_semantic_tree
    base
    (Generated.listedEQODL1LeafCover instOf core_eq bridge)
    links hfind
    (by
      simpa [Generated.concreteChecksWithListedEQ] using hcheck)
    hrep

/-- Semantic-shape version of the listed v108 O14 bridge.

The final assembly layer naturally extracts an `EQODL1ShapeInst` and proves
`EQODL1ShapeSound` for each EQ leaf.  This wrapper applies the generated
`ListedShapeCoverage` theorem internally, so callers do not have to prepackage
listed instances by hand. -/
theorem rowODL_of_listed_o14_eq_cover_semantic_tree_of_coverage
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} {sem : ODLNodeSemantics G c rows Q T}
    {root : Seed3Node}
    (base : ConcreteODLLeafChecks G c rows Q T sem)
    (hCover :
      Generated.ListedShapeCoverage (G := G) (c := c) (rows := rows) (Q := Q))
    (shapeInstOf :
      Seed3Node → PayloadRef → EQODL1ShapeInst G c rows Q)
    (shapeSound :
      ∀ n ref, EQODL1ShapeSound (shapeInstOf n ref))
    (core_eq :
      ∀ n ref, n.kind = NodeKind.leaf LeafTag.EQ ref →
        sem.coreOf n.id = (shapeInstOf n ref).core)
    (bridge : Generated.ChartBridgeInputs
      (fun I : Generated.ListedShapeInst G c rows Q => I.inst.core)
      (Generated.listedClassifier (G := G) (c := c) (rows := rows) (Q := Q)))
    (links : Seed3ODLInternalLinks G c rows Q T sem)
    (hfind : findNode? T T.root = some root)
    (hcheck :
      checkSeed3ODLSemanticTree T sem
        (leafProviders_of_concreteChecksWithEQ
          (Generated.concreteChecksWithListedEQ base
            (fun n ref =>
              Generated.listedInstOfCoverage hCover
                (shapeInstOf n ref)
                (shapeSound n ref))
            (fun n ref hkind => core_eq n ref hkind)
            bridge))
        links = true)
    (hrep : RootRepresentsRow G c rows Q (sem.coreOf root.id)) :
    rowSum G c rows Q ≤ (G.n : ℚ) + etaQ G c := by
  exact rowODL_of_listed_o14_eq_cover_semantic_tree
    base
    (fun n ref =>
      Generated.listedInstOfCoverage hCover
        (shapeInstOf n ref)
        (shapeSound n ref))
    (fun n ref hkind => core_eq n ref hkind)
    bridge
    links hfind hcheck hrep

end ListedChartCoverToODLFull
end O14
end Erdos23Delta0
