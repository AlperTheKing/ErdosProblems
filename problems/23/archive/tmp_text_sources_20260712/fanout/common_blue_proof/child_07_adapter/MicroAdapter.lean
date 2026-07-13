import Erdos23Delta0.Gamma.CommonBlueExtendedMatching
import Erdos23Delta0.ResidualSourceTokenization
namespace Child07MicroAdapter
open Erdos23Delta0
open Erdos23Delta0.Gamma
open Erdos23Delta0.CertGraph
open Erdos23Delta0.Gamma.MinimumDemandRowSelection
open Erdos23Delta0.Gamma.CanonicalCollisionHall
open Erdos23Delta0.Gamma.ActiveScopedMinimumExchange
structure CollisionDebit (G : GraphData) (c : CutData) {bads : List BadEdgeData} (omega : RowChoice bads) where
  owner : Fin G.n
  other : Fin G.n
  copy : Fin (pairCount omega owner.1 other.1 - 1)
  active : ActiveOwner G c omega owner
def activeCollisionHalfEquiv (G : GraphData) (c : CutData) {bads : List BadEdgeData} (omega : RowChoice bads) :
    ActiveCollisionHalf G c omega ≃ CollisionDebit G c omega × Fin 2 where
  toFun d := (⟨d.1.owner, d.1.other, d.1.copy, d.2⟩, d.1.half)
  invFun d := ⟨⟨d.1.owner, d.1.other, d.1.copy, d.2⟩, d.1.active⟩
  left_inv d := by cases d with | mk d h => cases d; rfl
  right_inv d := by cases d with | mk d h => cases d; rfl
structure FreeCell (G : GraphData) {bads : List BadEdgeData} (omega : RowChoice bads) where
  sourceX : Fin G.n
  sourceY : Fin G.n
  distinct : sourceX ≠ sourceY
  free : pairCount omega sourceX.1 sourceY.1 = 0
def freeHalfEquiv (G : GraphData) {bads : List BadEdgeData} (omega : RowChoice bads) :
    FreeHalf G omega ≃ FreeCell G omega × Fin 2 where
  toFun s := (⟨s.sourceX, s.sourceY, s.distinct, s.free⟩, s.half)
  invFun s := ⟨s.1.sourceX, s.1.sourceY, s.2, s.1.distinct, s.1.free⟩
  left_inv s := by cases s; rfl
  right_inv s := by cases s with | mk s h => cases s; rfl
def rawSourceEmbedding {G : GraphData} {c : CutData} {bads : List BadEdgeData} {omega : RowChoice bads}
    (M : CommonBlueExtendedMatching.MicroMatching G c omega) :
    ((CollisionDebit G c omega × Fin 2) ⊕ (ActiveHitNeed G c omega × Fin 25)) ↪ (FreeCell G omega × Fin 2) :=
  (Equiv.sumCongr (activeCollisionHalfEquiv G c omega).symm (Equiv.refl _)).toEmbedding.trans
    ((⟨M.assign, M.injective⟩ : _ ↪ _).trans (freeHalfEquiv G omega).toEmbedding)
def ComponentPreserving {G : GraphData} {c : CutData} {bads : List BadEdgeData} {omega : RowChoice bads} {Comp : Type*}
    (M : CommonBlueExtendedMatching.MicroMatching G c omega) (vertexComp : Fin G.n → Comp)
    (debitComp : CollisionDebit G c omega → Comp) (sourceComp : FreeCell G omega → Comp) : Prop :=
  ∀ x, sourceComp (rawSourceEmbedding M x).1 =
    Sum.elim (fun d => debitComp d.1) (fun s => vertexComp s.1.1) x
def dataOfMicroMatching {G : GraphData} {c : CutData} {bads : List BadEdgeData} {omega : RowChoice bads} {Comp : Type*}
    (M : CommonBlueExtendedMatching.MicroMatching G c omega) (vertexComp : Fin G.n → Comp)
    (debitComp : CollisionDebit G c omega → Comp) (sourceComp : FreeCell G omega → Comp)
    (hcomp : ComponentPreserving M vertexComp debitComp sourceComp) (unit : ℚ) (unit_pos : 0 < unit) :
    ResidualSourceTokenization.Data (V := Fin G.n) (Source := FreeCell G omega)
      (Debit := CollisionDebit G c omega) (Slot := ActiveHitNeed G c omega) (Comp := Comp) where
  owner s := s.1
  source := rawSourceEmbedding M
  vertexComp := vertexComp
  debitComp := debitComp
  sourceComp := sourceComp
  source_component := hcomp
  unit := unit
  unit_pos := unit_pos
theorem r29_micro_cardinal_gate : (20025 : Nat) ≤ 20141 := by omega
#print axioms activeCollisionHalfEquiv
#print axioms freeHalfEquiv
#print axioms rawSourceEmbedding
#print axioms dataOfMicroMatching
#print axioms r29_micro_cardinal_gate
end Child07MicroAdapter




