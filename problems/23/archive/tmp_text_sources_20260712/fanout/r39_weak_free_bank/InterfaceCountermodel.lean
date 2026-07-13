import Erdos23Delta0.Gamma.CheckedFullBankMicroFlow

namespace Erdos23Delta0.Gamma.R39WeakFreeBank

open CheckedFullBankMicroFlow

def freeKey : Fin 2 ↪ FreeHalfKey Unit where
  toFun h := ((), h)
  inj' := fun _ _ h => congrArg Prod.snd h

def collisionSource : (Unit × Fin 2) ↪ Fin 2 where
  toFun := Prod.snd
  inj' := by
    rintro ⟨⟨⟩, a⟩ ⟨⟨⟩, b⟩ h
    simpa using h

def flow : FullBankMicroFlowData
    Unit (Fin 2) Unit Unit Empty Unit Empty Empty Empty Empty where
  owner := Empty.elim
  vertexComp := fun _ => ()
  debitComp := fun _ => ()
  defaultComp := ()
  freeKey := freeKey
  collisionSource := collisionSource
  collisionLegalB := fun _ _ => true
  reservedB := fun _ => false
  bankSource := Empty.elim
  bankComp := Empty.elim
  hitBank := fun h => Empty.elim h.1
  hitLegalB := fun h => Empty.elim h
  vertexSlackCapQ := Empty.elim
  pruneCapQ := Empty.elim
  unitQ := 1

theorem flow_checked : CheckedFullBankMicroFlow flow where
  collision_legal := by intro x; rfl
  base_component_coherent := by intro x y h; rfl
  hit_legal := by intro h; exact Empty.elim h.1
  hit_component := by intro h; exact Empty.elim h.1
  bank_source_unique := by intro t; exact Empty.elim t
  vertexSlackCapQ_nonneg := by intro v; exact Empty.elim v
  pruneCapQ_nonneg := by intro r; exact Empty.elim r
  unitQ_pos := by norm_num [flow]

def ledger : MicroReservationLedgerData (Fin 2) Empty where
  rawFreeSpendQ := fun _ => 0
  priorSpendQ := Empty.elim
  localReserveQ := Empty.elim

theorem each_free_half_has_one_raw_unit (h : Fin 2) :
    FullBankMicroFlowData.tokenizedSpendQ flow h = 1 := by
  simpa [flow, collisionSource] using
    (Soundness.tokenizedSpendQ_collisionSource
      (F := flow) (x := ((), h)))

theorem ledger_checked : CheckedMicroReservationLedger flow ledger where
  rawFreeSpendQ_nonneg := by intro s; norm_num [ledger]
  priorSpendQ_nonneg := by intro t; exact Empty.elim t
  localReserveQ_nonneg := by intro t; exact Empty.elim t
  reservation_recorded := by intro s h; simp [flow] at h
  free_exclusive := by
    intro s
    rw [each_free_half_has_one_raw_unit]
    norm_num [ledger]
  bank_exclusive := by intro t; exact Empty.elim t

theorem two_free_micro_units : Fintype.card (Unit × Fin 2) = 2 := by
  decide

theorem no_hit_bank_source
    (s : HitBankSource Empty Empty Empty) : False := by
  cases s <;> contradiction

theorem bank_columns_are_zero :
    let view := ledger.fullBankView flow
    view.doorCapQ = 0 ∧ view.vertexSlackCapQ = 0 ∧
      view.c5BaseCapQ = 0 ∧ view.pruneCapQ = 0 := by
  simp [MicroReservationLedgerData.fullBankView,
    MicroReservationLedgerData.residualCapOfKindQ]

#print axioms flow_checked
#print axioms ledger_checked
#print axioms each_free_half_has_one_raw_unit
#print axioms bank_columns_are_zero

end Erdos23Delta0.Gamma.R39WeakFreeBank
