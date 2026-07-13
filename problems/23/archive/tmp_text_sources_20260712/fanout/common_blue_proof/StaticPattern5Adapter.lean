import Erdos23Delta0.Gamma.CommonBlueExtendedMatching
import Erdos23Delta0.ResidualSourceTokenization
import Erdos23Delta0.Gamma.TypedFullBankSources

namespace Erdos23Delta0
namespace Gamma
namespace StaticPattern5Adapter

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall
open ActiveScopedMinimumExchange
open CommonBlueExtendedMatching

/-- The sole reservation fact derived from static quiescence. -/
theorem not_scopedReserved_of_not_activeOwner
    {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} {omega : RowChoice bads}
    {s : FreeHalf G omega}
    (hquiet : Not (ActiveOwner G c omega s.sourceX)) :
    Not (ScopedReserved G c omega s) := by
  intro hreserved
  exact hquiet hreserved.2.2

/-- Collision data before its `Fin 2` half coordinate is attached. -/
structure CollisionDebit
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) where
  owner : Fin G.n
  other : Fin G.n
  copy : Fin (pairCount omega owner.1 other.1 - 1)
  active : ActiveOwner G c omega owner

def activeCollisionHalfEquiv
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) :
    Equiv (ActiveCollisionHalf G c omega)
      (CollisionDebit G c omega × Fin 2) where
  toFun d := (⟨d.1.owner, d.1.other, d.1.copy, d.2⟩, d.1.half)
  invFun d := ⟨⟨d.1.owner, d.1.other, d.1.copy, d.2⟩, d.1.active⟩
  left_inv d := by cases d with | mk d h => cases d; rfl
  right_inv d := by cases d with | mk d h => cases d; rfl

/-- A supplied static P5 relation. No switch or state transition is present.
The assignment domain itself enforces 25 micro-sources per HitNeed. -/
structure Provider
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (Comp BaseKey EdgeKey : Type*) where
  Source : Type*
  [sourceFintype : Fintype Source]
  literalHalf : (Source × Fin 2) ↪ FreeHalf G omega
  assignBase : MicroDemand G c omega ↪ (Source × Fin 2)
  staticAvailable : MicroDemand G c omega → FreeHalf G omega → Prop
  assigned_static : forall d, staticAvailable d (literalHalf (assignBase d))
  source_quiescent : forall d,
    Not (ActiveOwner G c omega (literalHalf (assignBase d)).sourceX)
  vertexComp : Fin G.n → Comp
  debitComp : CollisionDebit G c omega → Comp
  sourceComp : Source → Comp
  component_preserving : forall x,
    sourceComp
        (((Equiv.sumCongr (activeCollisionHalfEquiv G c omega).symm
          (Equiv.refl _)).toEmbedding.trans assignBase) x).1 =
      Sum.elim (fun d => debitComp d.1)
        (fun s => vertexComp s.1.1) x
  baseKey : Source → BaseKey
  baseKey_injective : Function.Injective baseKey
  newReservationEdges : Source → Finset EdgeKey
  reservation_free : forall source, newReservationEdges source = Finset.empty
  unit : ℚ
  unit_pos : 0 < unit

namespace Provider

variable {G : GraphData} {c : CutData}
variable {bads : List BadEdgeData} {omega : RowChoice bads}
variable {Comp BaseKey EdgeKey : Type*}

instance providerSourceFintype
    (P : Provider G c omega Comp BaseKey EdgeKey) : Fintype P.Source :=
  P.sourceFintype

def rawSource
    (P : Provider G c omega Comp BaseKey EdgeKey) :
    ((CollisionDebit G c omega × Fin 2) ⊕
      (ActiveHitNeed G c omega × Fin 25)) ↪ (P.Source × Fin 2) :=
  (Equiv.sumCongr (activeCollisionHalfEquiv G c omega).symm
    (Equiv.refl _)).toEmbedding.trans P.assignBase

def assignedLiteralHalf
    (P : Provider G c omega Comp BaseKey EdgeKey) :
    MicroDemand G c omega ↪ FreeHalf G omega :=
  P.assignBase.trans P.literalHalf

theorem assigned_not_scopedReserved
    (P : Provider G c omega Comp BaseKey EdgeKey)
    (d : MicroDemand G c omega) :
    Not (ScopedReserved G c omega (P.assignedLiteralHalf d)) := by
  apply not_scopedReserved_of_not_activeOwner
  exact P.source_quiescent d

/-- The 25 distinct images for one HitNeed are forced by the supplied global
micro-injection, not by the local P5 predicate. -/
theorem hitNeed_micro_sources_injective
    (P : Provider G c omega Comp BaseKey EdgeKey)
    (slot : ActiveHitNeed G c omega) :
    Function.Injective
      (fun i : Fin 25 => P.assignBase (Sum.inr (slot, i))) := by
  intro i j hij
  have hsum := P.assignBase.injective hij
  exact congrArg Prod.snd (Sum.inr.inj hsum)

def data
    (P : Provider G c omega Comp BaseKey EdgeKey) :
    ResidualSourceTokenization.Data
      (V := Fin G.n) (Source := P.Source)
      (Debit := CollisionDebit G c omega)
      (Slot := ActiveHitNeed G c omega) (Comp := Comp) where
  owner slot := slot.1
  source := P.rawSource
  vertexComp := P.vertexComp
  debitComp := P.debitComp
  sourceComp := P.sourceComp
  source_component := P.component_preserving
  unit := P.unit
  unit_pos := P.unit_pos

def typedC5BaseSource
    {ExitEdgeKey VertexKey PruneKey : Type*}
    (P : Provider G c omega Comp BaseKey EdgeKey) (source : P.Source) :
    TypedFullBankSources.CapSource
      ExitEdgeKey VertexKey BaseKey PruneKey :=
  .c5Base (P.baseKey source)

theorem typedC5BaseSource_injective
    {ExitEdgeKey VertexKey PruneKey : Type*}
    (P : Provider G c omega Comp BaseKey EdgeKey) :
    Function.Injective
      (P.typedC5BaseSource
        (ExitEdgeKey := ExitEdgeKey) (VertexKey := VertexKey)
        (PruneKey := PruneKey)) := by
  intro a b h
  apply P.baseKey_injective
  exact TypedFullBankSources.CapSource.c5Base.inj h

end Provider

/-- FullBank spending remains independent supplied data. Static P5
availability does not imply either spending condition. -/
structure FullBankSpendHypotheses
    (Local Token Comp BaseKey : Type*)
    [Fintype Local] [Fintype Token] where
  localComp : Local → Comp
  tokenComp : Token → Comp
  tokenBaseKey : Token → BaseKey
  tokenBaseKey_injective : Function.Injective tokenBaseKey
  spendQ : Local → Token → ℚ
  capQ : Token → ℚ
  spend_nonneg : forall l t, 0 ≤ spendQ l t
  no_double_spend : forall t,
    (Finset.univ.sum fun l => spendQ l t) ≤ capQ t
  no_cross_component_spend : forall l t,
    0 < spendQ l t → localComp l = tokenComp t

#print axioms not_scopedReserved_of_not_activeOwner
#print axioms Provider.assigned_not_scopedReserved
#print axioms Provider.hitNeed_micro_sources_injective
#print axioms Provider.data
#print axioms Provider.typedC5BaseSource_injective

end StaticPattern5Adapter
end Gamma
end Erdos23Delta0
