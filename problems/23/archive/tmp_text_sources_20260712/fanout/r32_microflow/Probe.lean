import Erdos23Delta0.Gamma.CheckedFullBankMicroFlow

namespace R32MicroFlowProbe

open Erdos23Delta0.Gamma
open Erdos23Delta0.Gamma.CheckedFullBankMicroFlow
open Erdos23Delta0.Gamma.CheckedFullBankMicroFlow.Soundness

abbrev V := Unit
abbrev FreeHalfT := Unit × Fin 2
abbrev FreeBase := Unit
abbrev Debit := Unit
abbrev Hit := Unit
abbrev Comp := Unit
abbrev DoorKey := Unit
abbrev VertexKey := Empty
abbrev PruneKey := Empty
abbrev Term := Unit

def identityEmbedding (α : Type*) : α ↪ α where
  toFun := id
  inj' := fun _ _ h => h

/-- One collision debit uses the two free halves; one retained hit uses the
single typed Door exactly twenty-five times. -/
def flow : FullBankMicroFlowData V FreeHalfT FreeBase Debit Hit Comp
    DoorKey VertexKey PruneKey Term where
  owner := fun _ => ()
  vertexComp := fun _ => ()
  debitComp := fun _ => ()
  defaultComp := ()
  freeKey := identityEmbedding FreeHalfT
  collisionSource := identityEmbedding (Debit × Fin 2)
  collisionLegalB := fun _ _ => true
  reservedB := fun _ => false
  bankSource := fun _ => .door ()
  bankComp := fun _ => ()
  hitBank := fun _ => ()
  hitLegalB := fun _ _ => true
  vertexSlackCapQ := fun v => Empty.elim v
  pruneCapQ := fun r => Empty.elim r
  unitQ := 1 / 50

def ledger : MicroReservationLedgerData FreeHalfT Term where
  rawFreeSpendQ := fun _ => 0
  priorSpendQ := fun _ => 0
  localReserveQ := fun _ => 0

theorem flow_checked : CheckedFullBankMicroFlow flow := by
  refine
    { collision_legal := by intro x; rfl
      base_component_coherent := by intro x y h; rfl
      hit_legal := by intro h; rfl
      hit_component := by intro h; rfl
      bank_source_unique := by
        intro x y h
        exact Subsingleton.elim x y
      vertexSlackCapQ_nonneg := by intro v; exact Empty.elim v
      pruneCapQ_nonneg := by intro r; exact Empty.elim r
      unitQ_pos := by norm_num [flow] }

theorem ledger_checked : CheckedMicroReservationLedger flow ledger := by
  refine
    { rawFreeSpendQ_nonneg := by intro s; norm_num [ledger]
      priorSpendQ_nonneg := by intro t; norm_num [ledger]
      localReserveQ_nonneg := by intro t; norm_num [ledger]
      reservation_recorded := by intro s h; simp [flow] at h
      free_exclusive := ?_
      bank_exclusive := ?_ }
  · intro s
    have hs := tokenizedSpendQ_collisionSource (F := flow) s
    change ledger.rawFreeSpendQ s +
      FullBankMicroFlowData.tokenizedSpendQ flow
        (flow.collisionSource s) ≤ 1
    rw [hs]
    norm_num [ledger]
  · intro t
    cases t
    norm_num [ledger, flow, FullBankMicroFlowData.newSpendQ,
      FullBankMicroFlowData.officialCapQ]

theorem flow_check_eq_true : checkFullBankMicroFlow flow = true :=
  (checkFullBankMicroFlow_eq_true_iff flow).2 flow_checked

theorem ledger_check_eq_true :
    checkMicroReservationLedger flow ledger = true :=
  (checkMicroReservationLedger_eq_true_iff flow ledger).2 ledger_checked

noncomputable def residualData :=
  toResidualSourceTokenization flow_checked

theorem collision_budget :
    2 * Fintype.card Debit ≤ 2 * Fintype.card FreeBase :=
  collision_card_budget flow_checked

theorem collision_unreserved (x : Debit × Fin 2) :
    flow.reservedB (flow.collisionSource x) = false :=
  collisionSource_unreserved ledger_checked x

theorem hit_demand_eq_twentyFive :
    FullBankMicroFlowData.hitMicroDemandQ flow = 25 := by
  rw [FullBankMicroFlowData.hitMicroDemandQ_eq_twentyFive]
  norm_num

theorem hit_paid_by_typed_residual :
    FullBankMicroFlowData.hitMicroDemandQ flow ≤
      ledger.residualCapOfKindQ flow FullBankToLengthSurplusCharge.CapKind.door +
      ledger.residualCapOfKindQ flow
        FullBankToLengthSurplusCharge.CapKind.vertexSlack +
      ledger.residualCapOfKindQ flow FullBankToLengthSurplusCharge.CapKind.prune :=
  hitMicroDemand_le_typedResidualCap ledger_checked

theorem fullBank_view_checked :
    (ledger.fullBankView flow).Checked :=
  fullBankView_checked flow_checked ledger_checked

theorem fullBank_view_exact :
    (ledger.fullBankView flow).demandQ = 25 ∧
      (ledger.fullBankView flow).doorCapQ = 25 ∧
      (ledger.fullBankView flow).vertexSlackCapQ = 0 ∧
      (ledger.fullBankView flow).c5BaseCapQ = 0 ∧
      (ledger.fullBankView flow).pruneCapQ = 0 := by
  norm_num [MicroReservationLedgerData.fullBankView,
    MicroReservationLedgerData.residualCapOfKindQ,
    MicroReservationLedgerData.residualCapQ,
    FullBankMicroFlowData.hitMicroDemandQ,
    FullBankMicroFlowData.officialCapQ, flow, ledger,
    HitBankSource.kind]
  all_goals decide

#print axioms flow_checked
#print axioms ledger_checked
#print axioms flow_check_eq_true
#print axioms ledger_check_eq_true
#print axioms residualData
#print axioms collision_budget
#print axioms collision_unreserved
#print axioms hit_paid_by_typed_residual
#print axioms fullBank_view_checked
#print axioms fullBank_view_exact

end R32MicroFlowProbe
