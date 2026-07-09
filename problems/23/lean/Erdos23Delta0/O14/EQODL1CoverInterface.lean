import Erdos23Delta0.ODLFull

/-!
# O14 EQ-ODL1 structural cover interface

This module is the small module-29 interface for the O14 chart cover.
It does not contain the 108 chart data and does not assert the structural
classifier theorem.  It records the exact shape the data/coverage layer must
fill:

* a classifier maps every structural EQ-ODL1 instance to one of `108` charts;
* an emitted payload marks every chart present;
* a chart-soundness provider proves the ODL core goal for any instance routed
  to a present chart.

The theorem `goal_of_checkEQODL1CoverCert` is the non-census glue from those
three ingredients to an arbitrary EQ-ODL1 instance.
-/

namespace Erdos23Delta0
namespace O14
namespace EQODL1CoverInterface

open ODLFull

/-- The O14 normalized EQ-ODL1 chart count. -/
abbrev ChartCount : Nat := 108

/-- Boolean less-than helper used by generated cover payloads. -/
def natLtB (a b : Nat) : Bool :=
  decide (a < b)

/-- Boolean equality helper used by generated cover payloads. -/
def natEqB (a b : Nat) : Bool :=
  decide (a = b)

theorem natLtB_sound {a b : Nat} (h : natLtB a b = true) : a < b := by
  exact of_decide_eq_true h

theorem natEqB_sound {a b : Nat} (h : natEqB a b = true) : a = b := by
  exact of_decide_eq_true h

/-- A structural classifier for EQ-ODL1 instances.  The hard coverage theorem
is the construction of such a classifier from the row descriptor space, not this
interface. -/
structure EQODL1Classifier (Inst : Type*) where
  chartOf : Inst → Nat
  chartOf_lt : ∀ I, chartOf I < ChartCount

/-- Emitted all-or-nothing O14 cover payload.  Data modules fill `present` from
the 108 exact chart certificates. -/
structure EQODL1CoverPayload where
  present : Nat → Bool

/-- The payload checker: all chart slots `0,...,107` must be present. -/
def checkEQODL1CoverCert (P : EQODL1CoverPayload) : Bool :=
  (List.range ChartCount).all P.present

theorem present_of_checkEQODL1CoverCert {P : EQODL1CoverPayload}
    (hcheck : checkEQODL1CoverCert P = true) {i : Nat} (hi : i < ChartCount) :
    P.present i = true := by
  unfold checkEQODL1CoverCert at hcheck
  exact (List.all_eq_true.mp hcheck) i (List.mem_range.mpr hi)

/-- Per-chart soundness provider.  This is the point where each emitted chart
certificate is connected to the ODL goal of every instance structurally routed
to that chart. -/
structure EQODL1ChartSound (Inst : Type*) (Goal : Inst → Prop)
    (C : EQODL1Classifier Inst) (P : EQODL1CoverPayload) : Prop where
  sound :
    ∀ i, i < ChartCount → P.present i = true →
      ∀ I, C.chartOf I = i → Goal I

/-- O14 cover glue: a total structural classifier, an all-present 108-slot
payload, and per-chart soundness prove the goal for every EQ-ODL1 instance. -/
theorem goal_of_checkEQODL1CoverCert
    {Inst : Type*} {Goal : Inst → Prop}
    (C : EQODL1Classifier Inst) (P : EQODL1CoverPayload)
    (H : EQODL1ChartSound Inst Goal C P)
    (hcheck : checkEQODL1CoverCert P = true) :
    ∀ I, Goal I := by
  intro I
  exact H.sound (C.chartOf I) (C.chartOf_lt I)
    (present_of_checkEQODL1CoverCert hcheck (C.chartOf_lt I)) I rfl

/-- ODL specialization of `goal_of_checkEQODL1CoverCert`. -/
theorem coreODLGoal_of_checkEQODL1CoverCert
    {G : CertGraph.GraphData} {c : CertGraph.CutData}
    {rows : CertGraph.RowDB} {Q : CertGraph.RowCert}
    {Inst : Type*} (coreOf : Inst → ODLCoreData G c rows Q)
    (C : EQODL1Classifier Inst) (P : EQODL1CoverPayload)
    (H : EQODL1ChartSound Inst (fun I => CoreODLGoal G c rows Q (coreOf I)) C P)
    (hcheck : checkEQODL1CoverCert P = true) :
    ∀ I, CoreODLGoal G c rows Q (coreOf I) :=
  goal_of_checkEQODL1CoverCert C P H hcheck

end EQODL1CoverInterface
end O14
end Erdos23Delta0
