import Erdos23Delta0.O14.EQODL1CoverInterface

/-!
# O14 EQ leaf provider

`ODLFull.leafProviders_of_concreteChecks` intentionally leaves the EQ/SIB tags
closed until the O14 cover exists.  This module adds the EQ half of that bridge:
a checked O14 EQ-ODL1 cover resolves every route-tree EQ leaf whose emitted core
is identified with the structural EQ instance routed by the classifier.

The module remains data-free.  The emitter still has to provide:

* the structural instance attached to each EQ leaf payload;
* the equality between that instance's core and the semantic node core;
* the classifier, 108-slot cover payload, and per-chart soundness.
-/

namespace Erdos23Delta0
namespace O14
namespace EQODL1LeafProvider

open CertGraph
open CertGraph.Seed3RouteTree
open ODLFull
open EQODL1CoverInterface

/-- Existing concrete leaf checks plus an EQ checker.  Non-EQ tags are delegated
to the already compiled `ConcreteODLLeafChecks` dispatcher. -/
structure ConcreteODLLeafChecksWithEQ
    (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert)
    (T : Seed3RouteTreeData) (sem : ODLNodeSemantics G c rows Q T) : Type where
  base : ConcreteODLLeafChecks G c rows Q T sem
  checkEQ : Seed3Node → PayloadRef → Bool
  soundEQ : ∀ n ref, n.kind = NodeKind.leaf LeafTag.EQ ref → checkEQ n ref = true →
    resolvedODL G c rows Q T sem n

/-- Per-leaf-tag dispatch with O14 EQ support. -/
def checkODLLeafDispatchWithEQ
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} {sem : ODLNodeSemantics G c rows Q T}
    (P : ConcreteODLLeafChecksWithEQ G c rows Q T sem) (n : Seed3Node) : Bool :=
  match n.kind with
  | NodeKind.leaf LeafTag.EQ ref => P.checkEQ n ref
  | _ => checkODLLeafDispatch P.base n

/-- Build the route-tree leaf provider from concrete checks plus O14 EQ support. -/
def leafProviders_of_concreteChecksWithEQ
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} {sem : ODLNodeSemantics G c rows Q T}
    (P : ConcreteODLLeafChecksWithEQ G c rows Q T sem) :
    Seed3ODLLeafProviders G c rows Q T sem where
  checkLeaf := checkODLLeafDispatchWithEQ P
  sound := by
    intro n _hleaf hcheck
    cases hk : n.kind with
    | internal tag payload =>
        simp [checkODLLeafDispatchWithEQ, checkODLLeafDispatch, hk] at hcheck
    | leaf tag ref =>
        cases tag with
        | EQ =>
            exact P.soundEQ n ref hk (by simpa [checkODLLeafDispatchWithEQ, hk] using hcheck)
        | SIB =>
            have hbase := (leafProviders_of_concreteChecks P.base).sound n (by simp [hk, isLeafKind])
              (by simpa [checkODLLeafDispatchWithEQ, hk] using hcheck)
            exact hbase
        | NO_OVERFULL =>
            have hbase := (leafProviders_of_concreteChecks P.base).sound n (by simp [hk, isLeafKind])
              (by simpa [checkODLLeafDispatchWithEQ, hk] using hcheck)
            exact hbase
        | NEG_SWITCH =>
            have hbase := (leafProviders_of_concreteChecks P.base).sound n (by simp [hk, isLeafKind])
              (by simpa [checkODLLeafDispatchWithEQ, hk] using hcheck)
            exact hbase
        | PRUNABLE =>
            have hbase := (leafProviders_of_concreteChecks P.base).sound n (by simp [hk, isLeafKind])
              (by simpa [checkODLLeafDispatchWithEQ, hk] using hcheck)
            exact hbase
        | NOT_SATURATED =>
            have hbase := (leafProviders_of_concreteChecks P.base).sound n (by simp [hk, isLeafKind])
              (by simpa [checkODLLeafDispatchWithEQ, hk] using hcheck)
            exact hbase
        | FOUR_DOOR =>
            have hbase := (leafProviders_of_concreteChecks P.base).sound n (by simp [hk, isLeafKind])
              (by simpa [checkODLLeafDispatchWithEQ, hk] using hcheck)
            exact hbase
        | CONE =>
            have hbase := (leafProviders_of_concreteChecks P.base).sound n (by simp [hk, isLeafKind])
              (by simpa [checkODLLeafDispatchWithEQ, hk] using hcheck)
            exact hbase
        | BANK_BLOCK =>
            have hbase := (leafProviders_of_concreteChecks P.base).sound n (by simp [hk, isLeafKind])
              (by simpa [checkODLLeafDispatchWithEQ, hk] using hcheck)
            exact hbase
        | LENS_GATE =>
            have hbase := (leafProviders_of_concreteChecks P.base).sound n (by simp [hk, isLeafKind])
              (by simpa [checkODLLeafDispatchWithEQ, hk] using hcheck)
            exact hbase
        | SEED10 =>
            have hbase := (leafProviders_of_concreteChecks P.base).sound n (by simp [hk, isLeafKind])
              (by simpa [checkODLLeafDispatchWithEQ, hk] using hcheck)
            exact hbase

/-- Data needed to turn the global O14 cover into an EQ leaf checker. -/
structure EQODL1LeafCover
    (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert)
    (T : Seed3RouteTreeData) (sem : ODLNodeSemantics G c rows Q T)
    (Inst : Type*) where
  coreOf : Inst → ODLCoreData G c rows Q
  instOf : Seed3Node → PayloadRef → Inst
  classifier : EQODL1Classifier Inst
  payload : EQODL1CoverPayload
  chartSound :
    EQODL1ChartSound Inst (fun I => CoreODLGoal G c rows Q (coreOf I)) classifier payload
  core_eq :
    ∀ n ref, n.kind = NodeKind.leaf LeafTag.EQ ref →
      sem.coreOf n.id = coreOf (instOf n ref)

/-- A checked O14 cover resolves any EQ leaf described by `EQODL1LeafCover`. -/
theorem resolvedODL_eq_leaf_of_o14_cover
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} {sem : ODLNodeSemantics G c rows Q T}
    {Inst : Type*} (P : EQODL1LeafCover G c rows Q T sem Inst)
    {n : Seed3Node} {ref : PayloadRef}
    (hkind : n.kind = NodeKind.leaf LeafTag.EQ ref)
    (hcheck : checkEQODL1CoverCert P.payload = true) :
    resolvedODL G c rows Q T sem n := by
  unfold resolvedODL
  rw [P.core_eq n ref hkind]
  exact coreODLGoal_of_checkEQODL1CoverCert P.coreOf P.classifier P.payload
    P.chartSound hcheck (P.instOf n ref)

/-- Add O14 EQ support to an existing concrete leaf-check bundle. -/
def concreteChecksWithEQ_of_o14_cover
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} {sem : ODLNodeSemantics G c rows Q T}
    {Inst : Type*}
    (base : ConcreteODLLeafChecks G c rows Q T sem)
    (P : EQODL1LeafCover G c rows Q T sem Inst) :
    ConcreteODLLeafChecksWithEQ G c rows Q T sem where
  base := base
  checkEQ := fun _ _ => checkEQODL1CoverCert P.payload
  soundEQ := by
    intro n ref hkind hcheck
    exact resolvedODL_eq_leaf_of_o14_cover P hkind hcheck

end EQODL1LeafProvider
end O14
end Erdos23Delta0
