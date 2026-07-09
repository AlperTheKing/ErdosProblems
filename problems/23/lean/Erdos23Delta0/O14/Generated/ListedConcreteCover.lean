import Erdos23Delta0.O14.Generated.BridgeRegistry
import Erdos23Delta0.O14.Generated.ListedClassifier

/-!
# O14 listed concrete cover

This module composes the source-only listed classifier with the generated
108-chart bridge registry.  It deliberately proves the cover only for
`ListedShapeInst`; the structural extraction layer must still prove that real
EQ-ODL1 instances have one of the listed v108 shapes and supply the per-chart
semantic bindings.
-/

namespace Erdos23Delta0
namespace O14
namespace Generated

open ODLFull
open EQODL1CoverInterface

/-- The v108 bridge registry proves the ODL core goal for every listed
EQ-ODL1 instance, once the semantic layer supplies the chart-specific
environment/slack/combo/target bindings. -/
theorem listedCoreODLGoals_of_bridgeInputs
    {G : CertGraph.GraphData} {c : CertGraph.CutData}
    {rows : CertGraph.RowDB} {Q : CertGraph.RowCert}
    (P : ChartBridgeInputs
      (fun I : ListedShapeInst G c rows Q => I.inst.core)
      (listedClassifier (G := G) (c := c) (rows := rows) (Q := Q))) :
    ∀ I : ListedShapeInst G c rows Q,
      CoreODLGoal G c rows Q I.inst.core := by
  exact coreODLGoal_of_checkEQODL1CoverCert
    (fun I : ListedShapeInst G c rows Q => I.inst.core)
    (listedClassifier (G := G) (c := c) (rows := rows) (Q := Q))
    v108Payload
    (chartSound_of_bridgeInputs P)
    v108Payload_check

/-- The remaining structural coverage obligation for the listed classifier:
every semantically sound EQ-ODL1 shape must land in one of the 108 certified
ledger pairs. -/
def ListedShapeCoverage
    {G : CertGraph.GraphData} {c : CertGraph.CutData}
    {rows : CertGraph.RowDB} {Q : CertGraph.RowCert} : Prop :=
  ∀ I : EQODL1ShapeInst G c rows Q, EQODL1ShapeSound I → ListedShape I.shape

/-- Package a semantically covered EQ-ODL1 instance as a listed instance. -/
def listedInstOfCoverage
    {G : CertGraph.GraphData} {c : CertGraph.CutData}
    {rows : CertGraph.RowDB} {Q : CertGraph.RowCert}
    (hCover : ListedShapeCoverage (G := G) (c := c) (rows := rows) (Q := Q))
    (I : EQODL1ShapeInst G c rows Q) (hSound : EQODL1ShapeSound I) :
    ListedShapeInst G c rows Q := {
  inst := I
  listed := hCover I hSound
}

/-- Final listed-cover bridge in the form expected by the structural extraction
layer: once it proves `ListedShapeCoverage` and supplies the chart-specific
semantic bindings, each semantically sound EQ-ODL1 instance obtains its ODL
core goal. -/
theorem coreODLGoal_of_listedCoverage
    {G : CertGraph.GraphData} {c : CertGraph.CutData}
    {rows : CertGraph.RowDB} {Q : CertGraph.RowCert}
    (hCover : ListedShapeCoverage (G := G) (c := c) (rows := rows) (Q := Q))
    (P : ChartBridgeInputs
      (fun I : ListedShapeInst G c rows Q => I.inst.core)
      (listedClassifier (G := G) (c := c) (rows := rows) (Q := Q)))
    (I : EQODL1ShapeInst G c rows Q) (hSound : EQODL1ShapeSound I) :
    CoreODLGoal G c rows Q I.core := by
  exact listedCoreODLGoals_of_bridgeInputs P
    (listedInstOfCoverage hCover I hSound)

end Generated
end O14
end Erdos23Delta0
