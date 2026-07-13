import Erdos23Delta0.ResidualSourceTokenization
import Erdos23Delta0.Gamma.TypedFullBankSources
namespace Child07ReservationAwareAdapterV3
open Erdos23Delta0 Erdos23Delta0.Gamma
structure ReservationLedger (Base Edge Half Demand : Type*)
    [Fintype Base] [DecidableEq Base] [Fintype Edge] [DecidableEq Edge]
    [Fintype Half] [DecidableEq Half] [Fintype Demand] where
  baseOf : Demand → Base
  assign : Demand → Half
  reservedEdges : Base → Finset Edge
  oldFreeHalfDeducted : Edge → Finset Half
  assign_injective : Function.Injective assign
  assignment_image_disjoint_deductions : Disjoint (Finset.univ.image assign)
    ((Finset.univ.image baseOf).biUnion fun b => (reservedEdges b).biUnion oldFreeHalfDeducted)
namespace ReservationLedger
variable {Base Edge Half Demand : Type*}
variable [Fintype Base] [DecidableEq Base] [Fintype Edge] [DecidableEq Edge]
variable [Fintype Half] [DecidableEq Half] [Fintype Demand]
def usedBases (L : ReservationLedger Base Edge Half Demand) := Finset.univ.image L.baseOf
def deductedOldKeys (L : ReservationLedger Base Edge Half Demand) :=
  L.usedBases.biUnion fun b => (L.reservedEdges b).biUnion L.oldFreeHalfDeducted
def assignedNewKeys (L : ReservationLedger Base Edge Half Demand) := Finset.univ.image L.assign
def usableNetCapacity (L : ReservationLedger Base Edge Half Demand) : Nat :=
  L.assignedNewKeys.card - L.deductedOldKeys.card
theorem assignedNewKeys_card (L : ReservationLedger Base Edge Half Demand) :
    L.assignedNewKeys.card = Fintype.card Demand := by
  classical
  rw [assignedNewKeys, Finset.card_image_of_injective Finset.univ L.assign_injective]
  exact Finset.card_univ
theorem usableNetCapacity_eq (L : ReservationLedger Base Edge Half Demand) :
    L.usableNetCapacity = Fintype.card Demand - L.deductedOldKeys.card := by
  rw [usableNetCapacity, L.assignedNewKeys_card]
structure Exclusive (L : ReservationLedger Base Edge Half Demand) : Prop where
  reservations_pairwise_disjoint : (L.usedBases : Set Base).PairwiseDisjoint L.reservedEdges
  edge_deductions_pairwise_disjoint : (Set.univ : Set Edge).PairwiseDisjoint L.oldFreeHalfDeducted
end ReservationLedger

def tinyIgnoringDeduction : ReservationLedger (Fin 1) (Fin 1) (Fin 2) (Fin 1) where
  baseOf := id; assign _ := 0; reservedEdges _ := {0}; oldFreeHalfDeducted _ := {1}
  assign_injective := by intro a b _; exact Subsingleton.elim a b
  assignment_image_disjoint_deductions := by simp
theorem tiny_raw_matching_exists : Function.Injective tinyIgnoringDeduction.assign := tinyIgnoringDeduction.assign_injective
theorem tiny_net_zero : tinyIgnoringDeduction.usableNetCapacity = 0 := by decide

structure SuppliedMicroMatching (CollisionDebit Slot FreeCell : Type*) where
  assign : ((CollisionDebit × Fin 2) ⊕ (Slot × Fin 25)) → (FreeCell × Fin 2)
  injective : Function.Injective assign
def conjugatedAssignment {ActiveCollisionHalf CollisionDebit Slot FreeHalf FreeCell : Type*}
    (collision : ActiveCollisionHalf ≃ CollisionDebit × Fin 2) (free : FreeHalf ≃ FreeCell × Fin 2)
    (raw : (ActiveCollisionHalf ⊕ (Slot × Fin 25)) ↪ FreeHalf) :
    ((CollisionDebit × Fin 2) ⊕ (Slot × Fin 25)) ↪ (FreeCell × Fin 2) :=
  (Equiv.sumCongr collision.symm (Equiv.refl _)).toEmbedding.trans (raw.trans free.toEmbedding)
def suppliedOfRaw {ActiveCollisionHalf CollisionDebit Slot FreeHalf FreeCell : Type*}
    (collision : ActiveCollisionHalf ≃ CollisionDebit × Fin 2) (free : FreeHalf ≃ FreeCell × Fin 2)
    (raw : (ActiveCollisionHalf ⊕ (Slot × Fin 25)) ↪ FreeHalf) : SuppliedMicroMatching CollisionDebit Slot FreeCell :=
  ⟨conjugatedAssignment collision free raw, (conjugatedAssignment collision free raw).injective⟩
def ComponentPreserving {V CollisionDebit Slot FreeCell Comp : Type*} (owner : Slot → V)
    (M : SuppliedMicroMatching CollisionDebit Slot FreeCell) (vertexComp : V → Comp)
    (debitComp : CollisionDebit → Comp) (sourceComp : FreeCell → Comp) : Prop :=
  ∀ x, sourceComp (M.assign x).1 = Sum.elim (fun d => debitComp d.1) (fun s => vertexComp (owner s.1)) x
def dataOfSupplied {V CollisionDebit Slot FreeCell Comp : Type*}
    [Fintype V] [DecidableEq V] [Fintype CollisionDebit] [Fintype Slot] [DecidableEq Slot] [Fintype FreeCell]
    (owner : Slot → V) (M : SuppliedMicroMatching CollisionDebit Slot FreeCell)
    (vertexComp : V → Comp) (debitComp : CollisionDebit → Comp) (sourceComp : FreeCell → Comp)
    (hcomp : ComponentPreserving owner M vertexComp debitComp sourceComp) (unit : ℚ) (unit_pos : 0 < unit) :
    ResidualSourceTokenization.Data (V := V) (Source := FreeCell) (Debit := CollisionDebit) (Slot := Slot) (Comp := Comp) where
  owner := owner; source := ⟨M.assign, M.injective⟩
  vertexComp := vertexComp; debitComp := debitComp; sourceComp := sourceComp
  source_component := hcomp; unit := unit; unit_pos := unit_pos

structure Pattern5C5BaseProvider (BaseKey Comp ExitEdgeKey VertexKey PruneKey : Type*) where
  Key : Type*
  [keyFintype : Fintype Key]
  baseKey : Key → BaseKey
  baseKey_injective : Function.Injective baseKey
  keyComp : Key → Comp
  baseComp : BaseKey → Comp
  component_identity : ∀ k, baseComp (baseKey k) = keyComp k
  reservationDeductions : Finset Key
  no_reservation_deductions : reservationDeductions = ∅
namespace Pattern5C5BaseProvider
instance {B C E V P} (X : Pattern5C5BaseProvider B C E V P) : Fintype X.Key := X.keyFintype
def source {B C E V P} (X : Pattern5C5BaseProvider B C E V P) (k : X.Key) :
    TypedFullBankSources.CapSource E V B P := .c5Base (X.baseKey k)
theorem source_injective {B C E V P} (X : Pattern5C5BaseProvider B C E V P) : Function.Injective X.source := by
  intro a b h
  apply X.baseKey_injective
  exact TypedFullBankSources.CapSource.c5Base.inj h
end Pattern5C5BaseProvider
#print axioms ReservationLedger.assignedNewKeys_card
#print axioms ReservationLedger.usableNetCapacity_eq
#print axioms tiny_net_zero
#print axioms conjugatedAssignment
#print axioms dataOfSupplied
#print axioms Pattern5C5BaseProvider.source_injective
end Child07ReservationAwareAdapterV3

