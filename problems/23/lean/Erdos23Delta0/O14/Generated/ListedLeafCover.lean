import Erdos23Delta0.O14.EQODL1LeafProvider
import Erdos23Delta0.O14.Generated.ListedConcreteCover

/-!
# O14 listed leaf cover

This is the thin adapter from the listed v108 classifier layer to the existing
`EQODL1LeafCover` API consumed by `ChartCoverToODLFull`.

The module is intentionally structural-data-free: the caller must provide the
listed instance attached to each EQ leaf and the equality between that listed
instance's core and the semantic node core.
-/

namespace Erdos23Delta0
namespace O14
namespace Generated

open CertGraph
open CertGraph.Seed3RouteTree
open ODLFull
open EQODL1CoverInterface
open EQODL1LeafProvider

/-- Build the existing O14 EQ leaf cover from listed EQ-ODL1 instances and the
108-chart bridge registry. -/
def listedEQODL1LeafCover
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} {sem : ODLNodeSemantics G c rows Q T}
    (instOf : Seed3Node → PayloadRef → ListedShapeInst G c rows Q)
    (core_eq :
      ∀ n ref, n.kind = NodeKind.leaf LeafTag.EQ ref →
        sem.coreOf n.id = (instOf n ref).inst.core)
    (P : ChartBridgeInputs
      (fun I : ListedShapeInst G c rows Q => I.inst.core)
      (listedClassifier (G := G) (c := c) (rows := rows) (Q := Q))) :
    EQODL1LeafCover G c rows Q T sem (ListedShapeInst G c rows Q) where
  coreOf := fun I => I.inst.core
  instOf := instOf
  classifier := listedClassifier (G := G) (c := c) (rows := rows) (Q := Q)
  payload := v108Payload
  chartSound := chartSound_of_bridgeInputs P
  core_eq := core_eq

/-- Existing concrete checks plus the listed v108 chart bridge give an EQ-aware
leaf checker. -/
def concreteChecksWithListedEQ
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} {sem : ODLNodeSemantics G c rows Q T}
    (base : ConcreteODLLeafChecks G c rows Q T sem)
    (instOf : Seed3Node → PayloadRef → ListedShapeInst G c rows Q)
    (core_eq :
      ∀ n ref, n.kind = NodeKind.leaf LeafTag.EQ ref →
        sem.coreOf n.id = (instOf n ref).inst.core)
    (P : ChartBridgeInputs
      (fun I : ListedShapeInst G c rows Q => I.inst.core)
      (listedClassifier (G := G) (c := c) (rows := rows) (Q := Q))) :
    ConcreteODLLeafChecksWithEQ G c rows Q T sem :=
  concreteChecksWithEQ_of_o14_cover base
    (listedEQODL1LeafCover instOf core_eq P)

end Generated
end O14
end Erdos23Delta0
