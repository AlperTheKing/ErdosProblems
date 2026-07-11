import Erdos23Delta0.ResidualSourceTokenization
import Erdos23Delta0.Gamma.MinimumDemandCollisionHall
import Erdos23Delta0.Gamma.TypedFullBankSources

/-!
# Checked full-bank micro flows

This module is the accounting interface for the R32 micro-flow model.  It
does not construct a row choice or assert that a feasible flow exists.
Instead, supplied finite data must contain

* an injective assignment of every collision half to a canonical free half;
* a typed Door, vertex-slack, or prune term for every one of the twenty-five
  microcopies of each retained hit need;
* component coherence and canonical source deduplication; and
* the exclusive free-source and bank-term reservation inequalities.

The soundness theorems expose the two downstream facts: a collision-only
`ResidualSourceTokenization.Data`, and a checked
`FullBankRelaxedCoverBundleView` paying the hit demand at exact 25x scale.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CheckedFullBankMicroFlow

open scoped BigOperators
open CanonicalCollisionHall
open FullBankToLengthSurplusCharge
open TypedFullBankSources

set_option linter.dupNamespace false
set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

/-- A canonical free-half key consists of its base key and one of two halves. -/
abbrev FreeHalfKey (FreeBase : Type*) := FreeBase × Fin 2

/-- The only bank sources licensed to fund retained hit needs.  Pattern-5
sources remain free-half sources; there is deliberately no `c5Base` case. -/
inductive HitBankSource (DoorKey VertexKey PruneKey : Type*) where
  | door (edge : DoorKey)
  | vertexSlack (vertex : VertexKey)
  | prune (key : PruneKey)
deriving DecidableEq, Repr

namespace HitBankSource

variable {DoorKey VertexKey PruneKey : Type*}

/-- Injection into the production typed-source vocabulary. -/
def toCapSource : HitBankSource DoorKey VertexKey PruneKey →
    CapSource DoorKey VertexKey Empty PruneKey
  | .door e => .door e
  | .vertexSlack v => .vertexSlack v
  | .prune r => .prune r

/-- The production full-bank capacity kind. -/
def kind : HitBankSource DoorKey VertexKey PruneKey → CapKind
  | .door _ => .door
  | .vertexSlack _ => .vertexSlack
  | .prune _ => .prune

@[simp] theorem kind_door (e : DoorKey) :
    kind (HitBankSource.door (VertexKey := VertexKey)
      (PruneKey := PruneKey) e) = CapKind.door := rfl

@[simp] theorem kind_vertexSlack (v : VertexKey) :
    kind (HitBankSource.vertexSlack (DoorKey := DoorKey)
      (PruneKey := PruneKey) v) = CapKind.vertexSlack := rfl

@[simp] theorem kind_prune (r : PruneKey) :
    kind (HitBankSource.prune (DoorKey := DoorKey)
      (VertexKey := VertexKey) r) = CapKind.prune := rfl

@[simp] theorem toCapSource_kind
    (s : HitBankSource DoorKey VertexKey PruneKey) :
    s.toCapSource.kind = s.kind := by
  cases s <;> rfl

end HitBankSource

/-- Raw finite micro-flow data.  `freeKey` is an embedding so provider tags
cannot manufacture duplicate copies of one canonical ordered half. -/
structure FullBankMicroFlowData
    (V FreeHalf FreeBase Debit Hit Comp DoorKey VertexKey PruneKey Term : Type*) where
  owner : Hit → V
  vertexComp : V → Comp
  debitComp : Debit → Comp
  defaultComp : Comp
  freeKey : FreeHalf ↪ FreeHalfKey FreeBase
  collisionSource : (Debit × Fin 2) ↪ FreeHalf
  collisionLegalB : (Debit × Fin 2) → FreeHalf → Bool
  reservedB : FreeHalf → Bool
  bankSource : Term → HitBankSource DoorKey VertexKey PruneKey
  bankComp : Term → Comp
  hitBank : Hit × Fin 25 → Term
  hitLegalB : Hit → HitBankSource DoorKey VertexKey PruneKey → Bool
  vertexSlackCapQ : VertexKey → ℚ
  pruneCapQ : PruneKey → ℚ
  unitQ : ℚ

namespace FullBankMicroFlowData

variable {V FreeHalf FreeBase Debit Hit Comp DoorKey VertexKey PruneKey Term : Type*}

variable (F : FullBankMicroFlowData V FreeHalf FreeBase Debit Hit Comp
  DoorKey VertexKey PruneKey Term)

/-- Collision assignment after canonical provider-key deduplication. -/
def collisionEmbedding : (Debit × Fin 2) ↪ FreeHalfKey FreeBase :=
  { toFun := fun x => F.freeKey (F.collisionSource x)
    inj' := by
      intro x y h
      apply F.collisionSource.injective
      exact F.freeKey.injective h }

/-- Component agreement for the two halves of one canonical free base. -/
def BaseKeyComponentCoherent : Prop :=
  ∀ x y : Debit × Fin 2,
    (collisionEmbedding F x).1 = (collisionEmbedding F y).1 →
      F.debitComp x.1 = F.debitComp y.1

/-- Official raw micro-capacity.  Every Door contributes exactly 25 units;
the other two capacities are exported explicitly by the supplied data. -/
def officialCapQ (t : Term) : ℚ :=
  match F.bankSource t with
  | .door _ => 25
  | .vertexSlack v => F.vertexSlackCapQ v
  | .prune r => F.pruneCapQ r

/-- One unit of spend for every collision half assigned to a free key. -/
def tokenizedSpendQ [Fintype Debit] [DecidableEq FreeHalf]
    (s : FreeHalf) : ℚ :=
  ∑ x : Debit × Fin 2, if F.collisionSource x = s then 1 else 0

/-- New bank spend is counted in exact micro-units. -/
def newSpendQ [Fintype Hit] [DecidableEq Term] (t : Term) : ℚ :=
  ∑ h : Hit × Fin 25, if F.hitBank h = t then 1 else 0

/-- The retained hit demand at micro scale. -/
def hitMicroDemandQ [Fintype Hit] : ℚ :=
  let _owner := F.owner
  Fintype.card (Hit × Fin 25)

theorem hitMicroDemandQ_eq_twentyFive [Fintype Hit] :
    hitMicroDemandQ F = 25 * (Fintype.card Hit : ℚ) := by
  simp [hitMicroDemandQ, Fintype.card_prod, Nat.cast_mul, mul_comm]

theorem newSpendQ_nonneg [Fintype Hit] [DecidableEq Term] (t : Term) :
    0 ≤ newSpendQ F t := by
  classical
  unfold newSpendQ
  apply Finset.sum_nonneg
  intro h _
  split <;> norm_num

theorem sum_newSpendQ [Fintype Hit] [Fintype Term] [DecidableEq Term] :
    (∑ t : Term, newSpendQ F t) = hitMicroDemandQ F := by
  classical
  calc
    (∑ t : Term, newSpendQ F t) =
        ∑ t : Term, ∑ h : Hit × Fin 25,
          if F.hitBank h = t then (1 : ℚ) else 0 := rfl
    _ = ∑ h : Hit × Fin 25, ∑ t : Term,
          if F.hitBank h = t then (1 : ℚ) else 0 := Finset.sum_comm
    _ = ∑ _h : Hit × Fin 25, (1 : ℚ) := by
      apply Finset.sum_congr rfl
      intro h _
      simp
    _ = hitMicroDemandQ F := by simp [hitMicroDemandQ]

end FullBankMicroFlowData

/-- Proof-facing checks on the finite flow itself.  In particular, Door
legality is checked on the retained hit object, and no graph switch is used to
create capacity. -/
structure CheckedFullBankMicroFlow
    {V FreeHalf FreeBase Debit Hit Comp DoorKey VertexKey PruneKey Term : Type*}
    (F : FullBankMicroFlowData V FreeHalf FreeBase Debit Hit Comp
      DoorKey VertexKey PruneKey Term) : Prop where
  collision_legal : ∀ x, F.collisionLegalB x (F.collisionSource x) = true
  base_component_coherent : F.BaseKeyComponentCoherent
  hit_legal : ∀ h : Hit × Fin 25,
    F.hitLegalB h.1 (F.bankSource (F.hitBank h)) = true
  hit_component : ∀ h : Hit × Fin 25,
    F.bankComp (F.hitBank h) = F.vertexComp (F.owner h.1)
  bank_source_unique : Function.Injective (fun t : Term =>
    (F.bankComp t, F.bankSource t))
  vertexSlackCapQ_nonneg : ∀ v, 0 ≤ F.vertexSlackCapQ v
  pruneCapQ_nonneg : ∀ r, 0 ≤ F.pruneCapQ r
  unitQ_pos : 0 < F.unitQ

/-- Prior use and local reservations are data, not capacity constructors. -/
structure MicroReservationLedgerData (FreeHalf Term : Type*) where
  rawFreeSpendQ : FreeHalf → ℚ
  priorSpendQ : Term → ℚ
  localReserveQ : Term → ℚ

namespace MicroReservationLedgerData

variable {V FreeHalf FreeBase Debit Hit Comp DoorKey VertexKey PruneKey Term : Type*}

variable (F : FullBankMicroFlowData V FreeHalf FreeBase Debit Hit Comp
  DoorKey VertexKey PruneKey Term)
variable (L : MicroReservationLedgerData FreeHalf Term)

/-- Capacity left after pre-existing spend and this component's reservation. -/
def residualCapQ (t : Term) : ℚ :=
  FullBankMicroFlowData.officialCapQ F t -
    L.priorSpendQ t - L.localReserveQ t

/-- Residual capacity grouped by the production full-bank kind. -/
def residualCapOfKindQ [Fintype Term] (k : CapKind) : ℚ :=
  ∑ t : Term, if (F.bankSource t).kind = k then L.residualCapQ F t else 0

/-- Exact FullBank-facing local view.  The `c5Base` column is zero because
Pattern-5 contributes canonical free halves rather than hit-bank capacity. -/
def fullBankView [Fintype Hit] [Fintype Term] :
    FullBankRelaxedCoverBundleView where
  demandQ := FullBankMicroFlowData.hitMicroDemandQ F
  doorCapQ := L.residualCapOfKindQ F CapKind.door
  vertexSlackCapQ := L.residualCapOfKindQ F CapKind.vertexSlack
  c5BaseCapQ := 0
  pruneCapQ := L.residualCapOfKindQ F CapKind.prune

end MicroReservationLedgerData

/-- The R32 exclusivity ledger.  Reserved free keys consume one raw unit;
bank terms include all prior use and local reservation before new flow. -/
structure CheckedMicroReservationLedger
    {V FreeHalf FreeBase Debit Hit Comp DoorKey VertexKey PruneKey Term : Type*}
    [Fintype Debit] [Fintype Hit] [DecidableEq FreeHalf] [DecidableEq Term]
    (F : FullBankMicroFlowData V FreeHalf FreeBase Debit Hit Comp
      DoorKey VertexKey PruneKey Term)
    (L : MicroReservationLedgerData FreeHalf Term) : Prop where
  rawFreeSpendQ_nonneg : ∀ s, 0 ≤ L.rawFreeSpendQ s
  priorSpendQ_nonneg : ∀ t, 0 ≤ L.priorSpendQ t
  localReserveQ_nonneg : ∀ t, 0 ≤ L.localReserveQ t
  reservation_recorded : ∀ s, F.reservedB s = true → 1 ≤ L.rawFreeSpendQ s
  free_exclusive : ∀ s,
    L.rawFreeSpendQ s + FullBankMicroFlowData.tokenizedSpendQ F s ≤ 1
  bank_exclusive : ∀ t,
    L.priorSpendQ t + L.localReserveQ t +
      FullBankMicroFlowData.newSpendQ F t ≤
        FullBankMicroFlowData.officialCapQ F t

section FiniteCheckers

variable {V FreeHalf FreeBase Debit Hit Comp DoorKey VertexKey PruneKey Term : Type*}
  [Fintype FreeHalf] [Fintype Debit] [Fintype Hit]
  [Fintype VertexKey] [Fintype PruneKey] [Fintype Term]
  [DecidableEq FreeHalf] [DecidableEq FreeBase] [DecidableEq Comp]
  [DecidableEq DoorKey] [DecidableEq VertexKey] [DecidableEq PruneKey]
  [DecidableEq Term]

variable (F : FullBankMicroFlowData V FreeHalf FreeBase Debit Hit Comp
  DoorKey VertexKey PruneKey Term)
variable (L : MicroReservationLedgerData FreeHalf Term)

/-- Kernel `decide` checker for supplied finite micro-flow data. -/
noncomputable def checkFullBankMicroFlow
    (F : FullBankMicroFlowData V FreeHalf FreeBase Debit Hit Comp
      DoorKey VertexKey PruneKey Term) : Bool := by
  classical
  exact decide (CheckedFullBankMicroFlow F)

theorem checkFullBankMicroFlow_eq_true_iff :
    checkFullBankMicroFlow F = true ↔ CheckedFullBankMicroFlow F := by
  simp [checkFullBankMicroFlow]

/-- Kernel `decide` checker for the two exclusivity inequalities. -/
noncomputable def checkMicroReservationLedger
    (F : FullBankMicroFlowData V FreeHalf FreeBase Debit Hit Comp
      DoorKey VertexKey PruneKey Term)
    (L : MicroReservationLedgerData FreeHalf Term) : Bool := by
  classical
  exact decide (CheckedMicroReservationLedger F L)

theorem checkMicroReservationLedger_eq_true_iff :
    checkMicroReservationLedger F L = true ↔
      CheckedMicroReservationLedger F L := by
  simp [checkMicroReservationLedger]

end FiniteCheckers

namespace Soundness

variable {V FreeHalf FreeBase Debit Hit Comp DoorKey VertexKey PruneKey Term : Type*}
  [Fintype V] [DecidableEq V]
  [Fintype FreeHalf] [DecidableEq FreeHalf]
  [Fintype FreeBase] [Fintype Debit]
  [Fintype Hit] [Fintype Term] [DecidableEq Term]

variable {F : FullBankMicroFlowData V FreeHalf FreeBase Debit Hit Comp
  DoorKey VertexKey PruneKey Term}
variable {L : MicroReservationLedgerData FreeHalf Term}

/-- Every used collision key contributes exactly one tokenized unit. -/
theorem tokenizedSpendQ_collisionSource (x : Debit × Fin 2) :
    FullBankMicroFlowData.tokenizedSpendQ F (F.collisionSource x) = 1 := by
  classical
  unfold FullBankMicroFlowData.tokenizedSpendQ
  simp [F.collisionSource.injective.eq_iff]

theorem collision_rawFreeSpendQ_eq_zero
    (hL : CheckedMicroReservationLedger F L) (x : Debit × Fin 2) :
    L.rawFreeSpendQ (F.collisionSource x) = 0 := by
  have hex := hL.free_exclusive (F.collisionSource x)
  rw [tokenizedSpendQ_collisionSource x] at hex
  linarith [hL.rawFreeSpendQ_nonneg (F.collisionSource x)]

/-- A collision assignment cannot reuse a key recorded as reserved. -/
theorem collisionSource_unreserved
    (hL : CheckedMicroReservationLedger F L) (x : Debit × Fin 2) :
    F.reservedB (F.collisionSource x) = false := by
  cases hres : F.reservedB (F.collisionSource x) with
  | false => rfl
  | true =>
      have hrecord := hL.reservation_recorded (F.collisionSource x) hres
      rw [collision_rawFreeSpendQ_eq_zero hL x] at hrecord
      norm_num at hrecord

/-- Component label of a canonical free base.  Coherence makes the chosen
collision witness irrelevant; unused bases receive `defaultComp`. -/
noncomputable def freeBaseComp
    (hF : CheckedFullBankMicroFlow F) (b : FreeBase) : Comp := by
  classical
  exact if h : ∃ x : Debit × Fin 2, (FullBankMicroFlowData.collisionEmbedding F x).1 = b then
    F.debitComp (Classical.choose h).1
  else F.defaultComp

theorem freeBaseComp_collision
    (hF : CheckedFullBankMicroFlow F) (x : Debit × Fin 2) :
    freeBaseComp hF (FullBankMicroFlowData.collisionEmbedding F x).1 =
      F.debitComp x.1 := by
  classical
  unfold freeBaseComp
  split
  · rename_i h
    have hc := hF.base_component_coherent
    unfold FullBankMicroFlowData.BaseKeyComponentCoherent at hc
    exact hc (Classical.choose h) x (Classical.choose_spec h)
  · rename_i h
    exact (h ⟨x, rfl⟩).elim

/-- The collision embedding with an impossible token-slot summand. -/
def residualCollisionEmbedding
    (F : FullBankMicroFlowData V FreeHalf FreeBase Debit Hit Comp
      DoorKey VertexKey PruneKey Term) :
    ((Debit × Fin 2) ⊕ (Empty × Fin 25)) ↪ (FreeBase × Fin 2) where
  toFun
    | .inl d => FullBankMicroFlowData.collisionEmbedding F d
    | .inr e => Empty.elim e.1
  inj' := by
    intro x y hxy
    cases x with
    | inl x =>
        cases y with
        | inl y =>
            exact congrArg Sum.inl
              ((FullBankMicroFlowData.collisionEmbedding F).injective hxy)
        | inr y => exact Empty.elim y.1
    | inr x => exact Empty.elim x.1

/-- Supplied collision data produces the existing residual-tokenization
object with no fabricated token slots. -/
noncomputable def toResidualSourceTokenization
    (hF : CheckedFullBankMicroFlow F) :
    ResidualSourceTokenization.Data
      (V := V) (Source := FreeBase) (Debit := Debit)
      (Slot := Empty) (Comp := Comp) where
  owner := fun e => Empty.elim e
  source := residualCollisionEmbedding F
  vertexComp := F.vertexComp
  debitComp := F.debitComp
  sourceComp := freeBaseComp hF
  source_component := by
    intro x
    cases x with
    | inl d => simpa using freeBaseComp_collision hF d
    | inr e => exact Empty.elim e.1
  unit := F.unitQ
  unit_pos := hF.unitQ_pos

/-- ResidualSourceTokenization-facing collision budget. -/
theorem collision_card_budget
    (hF : CheckedFullBankMicroFlow F) :
    2 * Fintype.card Debit ≤ 2 * Fintype.card FreeBase := by
  have h := (toResidualSourceTokenization hF).debit_add_token_card_le_source
  simpa using h

theorem newSpendQ_le_residualCapQ
    (hL : CheckedMicroReservationLedger F L) (t : Term) :
    FullBankMicroFlowData.newSpendQ F t ≤ L.residualCapQ F t := by
  have h := hL.bank_exclusive t
  unfold MicroReservationLedgerData.residualCapQ
  linarith

theorem residualCapQ_nonneg
    (hL : CheckedMicroReservationLedger F L) (t : Term) :
    0 ≤ L.residualCapQ F t :=
  le_trans (FullBankMicroFlowData.newSpendQ_nonneg F t)
    (newSpendQ_le_residualCapQ hL t)

theorem residualCapOfKindQ_nonneg
    (hL : CheckedMicroReservationLedger F L) (k : CapKind) :
    0 ≤ L.residualCapOfKindQ F k := by
  classical
  unfold MicroReservationLedgerData.residualCapOfKindQ
  apply Finset.sum_nonneg
  intro t _
  split
  · exact residualCapQ_nonneg hL t
  · exact le_rfl

theorem sum_residualCapQ_eq_typed_kinds :
    (∑ t : Term, L.residualCapQ F t) =
      L.residualCapOfKindQ F CapKind.door +
      L.residualCapOfKindQ F CapKind.vertexSlack +
      L.residualCapOfKindQ F CapKind.prune := by
  classical
  unfold MicroReservationLedgerData.residualCapOfKindQ
  rw [← Finset.sum_add_distrib, ← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro t _
  cases F.bankSource t <;> simp [HitBankSource.kind]

/-- Exact 25x hit demand is bounded by residual typed bank capacity. -/
theorem hitMicroDemand_le_typedResidualCap
    (hL : CheckedMicroReservationLedger F L) :
    FullBankMicroFlowData.hitMicroDemandQ F ≤
      L.residualCapOfKindQ F CapKind.door +
      L.residualCapOfKindQ F CapKind.vertexSlack +
      L.residualCapOfKindQ F CapKind.prune := by
  rw [← FullBankMicroFlowData.sum_newSpendQ F,
    ← sum_residualCapQ_eq_typed_kinds]
  exact Finset.sum_le_sum (fun t _ => newSpendQ_le_residualCapQ hL t)

/-- The supplied flow and exclusive ledger satisfy the production local
FullBank inequalities.  This is an implication from checked data, not a
feasibility or row-selection theorem. -/
theorem fullBankView_checked
    (hF : CheckedFullBankMicroFlow F)
    (hL : CheckedMicroReservationLedger F L) :
    (L.fullBankView F).Checked := by
  refine
    { demand_nonneg := ?_
      door_nonneg := residualCapOfKindQ_nonneg hL CapKind.door
      vertexSlack_nonneg := residualCapOfKindQ_nonneg hL CapKind.vertexSlack
      c5Base_nonneg := by
        change (0 : ℚ) ≤ 0
        norm_num
      prune_nonneg := residualCapOfKindQ_nonneg hL CapKind.prune
      demand_le_rhs := ?_ }
  · change (0 : ℚ) ≤ FullBankMicroFlowData.hitMicroDemandQ F
    simp [FullBankMicroFlowData.hitMicroDemandQ]
  · have h := hitMicroDemand_le_typedResidualCap hL
    simpa [MicroReservationLedgerData.fullBankView,
      FullBankRelaxedCoverBundleView.rhsQ, add_assoc] using h

end Soundness

/-! ## Production free-half key -/

/-- Forget proof fields and provider provenance from a production `FreeHalf`.
Injectivity ensures all source families are deduplicated by the literal
ordered pair and half bit before entering this module. -/
def canonicalFreeHalfKey
    {G : CertGraph.GraphData} {bads : List CertGraph.BadEdgeData}
    {omega : MinimumDemandRowSelection.RowChoice bads} :
    FreeHalf G omega ↪ FreeHalfKey (Fin G.n × Fin G.n) where
  toFun s := ((s.sourceX, s.sourceY), s.half)
  inj' := by
    intro s t h
    cases s
    cases t
    simp_all

#print axioms Soundness.toResidualSourceTokenization
#print axioms Soundness.collision_card_budget
#print axioms Soundness.collisionSource_unreserved
#print axioms Soundness.hitMicroDemand_le_typedResidualCap
#print axioms Soundness.fullBankView_checked

end CheckedFullBankMicroFlow
end Gamma
end Erdos23Delta0
