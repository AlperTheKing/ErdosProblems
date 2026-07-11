import Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge

/-!
# Kind-indexed full-bank source keys

The legacy global ledger stores only `sourceId : Nat`.  That aggregate key is
insufficient to recover legal own-Door incidence.  This module supplies the
typed replacement requested by the R13 audit: the source constructor itself
determines the capacity kind, and a Door source carries the exact extractor
exit-edge key.

The finite checker below proves own-Door legality and injectivity from source
equality.  Connecting these typed tokens to the existing wall `Sink` type is a
separate adapter obligation; no such adapter is assumed here.
-/

namespace Erdos23Delta0
namespace Gamma
namespace TypedFullBankSources

open FullBankToLengthSurplusCharge

/-- A source key whose payload type is determined by its bank kind. -/
inductive CapSource
    (ExitEdgeKey VertexKey BaseKey PruneKey : Type*) where
  | door (edge : ExitEdgeKey)
  | vertexSlack (vertex : VertexKey)
  | c5Base (base : BaseKey)
  | prune (prune : PruneKey)
  deriving DecidableEq, Repr

namespace CapSource

variable {ExitEdgeKey VertexKey BaseKey PruneKey : Type*}

/-- The capacity kind is determined, rather than redundantly serialized. -/
def kind : CapSource ExitEdgeKey VertexKey BaseKey PruneKey → CapKind
  | .door _ => .door
  | .vertexSlack _ => .vertexSlack
  | .c5Base _ => .c5Base
  | .prune _ => .prune

@[simp] theorem kind_door (e : ExitEdgeKey) :
    kind (CapSource.door (VertexKey := VertexKey) (BaseKey := BaseKey)
      (PruneKey := PruneKey) e) = CapKind.door := rfl

@[simp] theorem kind_vertexSlack (v : VertexKey) :
    kind (CapSource.vertexSlack (ExitEdgeKey := ExitEdgeKey)
      (BaseKey := BaseKey) (PruneKey := PruneKey) v) = CapKind.vertexSlack := rfl

@[simp] theorem kind_c5Base (b : BaseKey) :
    kind (CapSource.c5Base (ExitEdgeKey := ExitEdgeKey)
      (VertexKey := VertexKey) (PruneKey := PruneKey) b) = CapKind.c5Base := rfl

@[simp] theorem kind_prune (r : PruneKey) :
    kind (CapSource.prune (ExitEdgeKey := ExitEdgeKey)
      (VertexKey := VertexKey) (BaseKey := BaseKey) r) = CapKind.prune := rfl

end CapSource

/-- One globally named typed capacity token. -/
structure TypedLedgerToken (componentCount : Nat)
    (ExitEdgeKey VertexKey BaseKey PruneKey : Type*) where
  comp : Fin componentCount
  source : CapSource ExitEdgeKey VertexKey BaseKey PruneKey
  capQ : ℚ
  deriving Repr

namespace TypedLedgerToken

variable {componentCount : Nat}
variable {ExitEdgeKey VertexKey BaseKey PruneKey : Type*}

def kind
    (t : TypedLedgerToken componentCount ExitEdgeKey VertexKey BaseKey PruneKey) :
    CapKind :=
  t.source.kind

end TypedLedgerToken

/-- A finite typed ledger with uniqueness on `(component, source)`.  Because
`source.kind` is definitional, this is exactly uniqueness on
`(component, kind, source-payload)`. -/
structure TypedGlobalLedgerData (componentCount tokenCount : Nat)
    (ExitEdgeKey VertexKey BaseKey PruneKey : Type*) where
  token : Fin tokenCount →
    TypedLedgerToken componentCount ExitEdgeKey VertexKey BaseKey PruneKey
  source_injective : Function.Injective (fun t : Fin tokenCount =>
    ((token t).comp, (token t).source))

/-- Raw finite data used by the own-edge Door checker. -/
structure OwnEdgeDoorSourceData
    (Port ExitEdgeKey VertexKey BaseKey PruneKey : Type*)
    (componentCount tokenCount : Nat) where
  portEdge : Port → ExitEdgeKey
  token : Fin tokenCount →
    TypedLedgerToken componentCount ExitEdgeKey VertexKey BaseKey PruneKey
  doorOf : Port → Fin tokenCount

namespace OwnEdgeDoorSourceData

variable {Port ExitEdgeKey VertexKey BaseKey PruneKey : Type*}
variable {componentCount tokenCount : Nat}

variable (D : OwnEdgeDoorSourceData Port ExitEdgeKey VertexKey BaseKey PruneKey
  componentCount tokenCount)

/-- The proof-facing proposition recomputed by `checkOwnEdgeDoors`. -/
def Checked : Prop :=
  Function.Injective D.portEdge ∧
    (∀ p, (D.token (D.doorOf p)).source = CapSource.door (D.portEdge p)) ∧
    (∀ p, 25 ≤ (D.token (D.doorOf p)).capQ)

/-- Kernel-decidable finite checker for typed own-edge Door sources. -/
noncomputable def checkOwnEdgeDoors
    [Fintype Port] [DecidableEq Port]
    [DecidableEq ExitEdgeKey] [DecidableEq VertexKey]
    [DecidableEq BaseKey] [DecidableEq PruneKey] : Bool := by
  classical
  exact decide D.Checked

theorem checkOwnEdgeDoors_eq_true_iff
    [Fintype Port] [DecidableEq Port]
    [DecidableEq ExitEdgeKey] [DecidableEq VertexKey]
    [DecidableEq BaseKey] [DecidableEq PruneKey] :
    D.checkOwnEdgeDoors = true ↔ D.Checked := by
  classical
  simp [checkOwnEdgeDoors]

/-- Legal Door incidence generated directly from typed source equality. -/
def doorLegal (p : Port) (t : Fin tokenCount) : Prop :=
  (D.token t).source = CapSource.door (D.portEdge p)

theorem doorOf_legal (h : D.Checked) (p : Port) :
    D.doorLegal p (D.doorOf p) :=
  h.2.1 p

/-- The own-Door map is injective because two equal token indices have one
typed Door source, and exit-edge keys identify ports. -/
theorem doorOf_injective (h : D.Checked) : Function.Injective D.doorOf := by
  intro p q hpq
  apply h.1
  have hp := h.2.1 p
  have hq := h.2.1 q
  rw [hpq] at hp
  have hsrc :
      CapSource.door (D.portEdge p) = CapSource.door (D.portEdge q) :=
    hp.symm.trans hq
  exact CapSource.door.inj hsrc

/-- Hall-scale capacity of a typed token. -/
def hallCapQ (t : Fin tokenCount) : ℚ :=
  (D.token t).capQ / 25

theorem one_le_door_hallCapQ (h : D.Checked) (p : Port) :
    1 ≤ D.hallCapQ (D.doorOf p) := by
  unfold hallCapQ
  exact (le_div_iff₀ (by norm_num : (0 : ℚ) < 25)).2 (by
    simpa using h.2.2 p)

theorem doorOf_source_kind (h : D.Checked) (p : Port) :
    (D.token (D.doorOf p)).kind = CapKind.door := by
  rw [TypedLedgerToken.kind, h.2.1 p]
  rfl

end OwnEdgeDoorSourceData

#print axioms OwnEdgeDoorSourceData.checkOwnEdgeDoors_eq_true_iff
#print axioms OwnEdgeDoorSourceData.doorOf_legal
#print axioms OwnEdgeDoorSourceData.doorOf_injective
#print axioms OwnEdgeDoorSourceData.one_le_door_hallCapQ
#print axioms OwnEdgeDoorSourceData.doorOf_source_kind

end TypedFullBankSources
end Gamma
end Erdos23Delta0
