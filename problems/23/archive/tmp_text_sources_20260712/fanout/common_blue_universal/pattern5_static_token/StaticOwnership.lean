import Erdos23Delta0.ResidualSourceTokenization

/-!
# Static ownership for Pattern-5 source halves

No cut is flipped here.  The exact issue is that a residual source has one
component label per ordered-pair base key, while its two half bits are matched
separately.  Thus injectivity on full half keys is insufficient: assignments
using the same base key must agree on their destination component.
-/

namespace CodexTmp.CommonBlueUniversal.Pattern5StaticToken

open Erdos23Delta0

variable {Source Comp Domain : Type*}

/-- Component agreement whenever two assigned micro-obligations use the two
halves of the same ordered-pair base key. -/
def BaseKeyComponentCoherent
    (assign : Domain ↪ (Source × Fin 2)) (component : Domain → Comp) : Prop :=
  ∀ x y, (assign x).1 = (assign y).1 → component x = component y

/-- Relation-level graph obligation sufficient for every matching using that
relation: one base key may be eligible in at most one destination component. -/
def RelationBaseComponentUnique
    (available : Domain → (Source × Fin 2) → Prop)
    (component : Domain → Comp) : Prop :=
  ∀ x y sx sy, available x sx → available y sy →
    sx.1 = sy.1 → component x = component y

theorem baseKeyComponentCoherent_of_relationUnique
    (available : Domain → (Source × Fin 2) → Prop)
    (component : Domain → Comp) (assign : Domain ↪ (Source × Fin 2))
    (havailable : ∀ x, available x (assign x))
    (hunique : RelationBaseComponentUnique available component) :
    BaseKeyComponentCoherent assign component := by
  intro x y hbase
  exact hunique x y (assign x) (assign y)
    (havailable x) (havailable y) hbase

/-- Destination-label every used base key.  Unused keys receive an arbitrary
default component and carry no capacity. -/
noncomputable def sourceComponentOf
    (defaultComp : Comp) (assign : Domain ↪ (Source × Fin 2))
    (component : Domain → Comp) (source : Source) : Comp := by
  classical
  exact if h : ∃ x, (assign x).1 = source then component (Classical.choose h)
    else defaultComp

theorem sourceComponentOf_assigned
    (defaultComp : Comp) (assign : Domain ↪ (Source × Fin 2))
    (component : Domain → Comp)
    (hcoherent : BaseKeyComponentCoherent assign component) (x : Domain) :
    sourceComponentOf defaultComp assign component (assign x).1 = component x := by
  classical
  unfold sourceComponentOf
  split
  · rename_i h
    exact hcoherent (Classical.choose h) x (Classical.choose_spec h)
  · rename_i h
    exact (h ⟨x, rfl⟩).elim

/-- Base-key coherence is exactly the condition needed to construct the
`sourceComp` field, not merely a convenient sufficient condition. -/
theorem exists_sourceComponent_iff_baseKeyComponentCoherent
    (defaultComp : Comp) (assign : Domain ↪ (Source × Fin 2))
    (component : Domain → Comp) :
    (∃ sourceComp : Source → Comp,
      ∀ x, sourceComp (assign x).1 = component x) ↔
      BaseKeyComponentCoherent assign component := by
  constructor
  · rintro ⟨sourceComp, hsource⟩ x y hbase
    rw [← hsource x, ← hsource y, hbase]
  · intro hcoherent
    exact ⟨sourceComponentOf defaultComp assign component,
      sourceComponentOf_assigned defaultComp assign component hcoherent⟩

section ResidualAdapter

variable {V Source Debit Slot Comp : Type*}
  [Fintype V] [DecidableEq V]
  [Fintype Source] [Fintype Debit]
  [Fintype Slot] [DecidableEq Slot]

abbrev MicroObligation (Debit Slot : Type*) :=
  (Debit × Fin 2) ⊕ (Slot × Fin 25)

def obligationComponent
    (owner : Slot → V) (vertexComp : V → Comp) (debitComp : Debit → Comp) :
    MicroObligation Debit Slot → Comp
  | Sum.inl d => debitComp d.1
  | Sum.inr s => vertexComp (owner s.1)

/-- The weakest static data that converts an exact micro-matching into
`ResidualSourceTokenization.Data`.  Pattern-5 graph eligibility belongs in the
proof that `source` is an allowed matching; the adapter itself needs only
base-key component coherence and never reuses a flipped row state. -/
structure CoherentMicroAssignment where
  owner : Slot → V
  source : MicroObligation Debit Slot ↪ (Source × Fin 2)
  vertexComp : V → Comp
  debitComp : Debit → Comp
  defaultComp : Comp
  base_coherent :
    BaseKeyComponentCoherent source
      (obligationComponent owner vertexComp debitComp)
  unit : ℚ
  unit_pos : 0 < unit

namespace CoherentMicroAssignment

variable (A : CoherentMicroAssignment
  (V := V) (Source := Source) (Debit := Debit) (Slot := Slot) (Comp := Comp))

noncomputable def sourceComp : Source → Comp :=
  sourceComponentOf A.defaultComp A.source
    (obligationComponent A.owner A.vertexComp A.debitComp)

theorem source_component (x : MicroObligation Debit Slot) :
    A.sourceComp (A.source x).1 =
      obligationComponent A.owner A.vertexComp A.debitComp x := by
  exact sourceComponentOf_assigned A.defaultComp A.source
    (obligationComponent A.owner A.vertexComp A.debitComp)
    A.base_coherent x

/-- Static conversion to the compiled residual-source tokenization interface.
This proves source uniqueness, component preservation, and the 25-microcopy
scale through that existing module; it does not construct a checked FullBank
package or its still-absent legal port incidence. -/
noncomputable def toResidualData :
    ResidualSourceTokenization.Data
      (V := V) (Source := Source) (Debit := Debit) (Slot := Slot) (Comp := Comp) where
  owner := A.owner
  source := A.source
  vertexComp := A.vertexComp
  debitComp := A.debitComp
  sourceComp := A.sourceComp
  source_component := by
    intro x
    cases x with
    | inl d =>
        simpa [obligationComponent] using A.source_component (Sum.inl d)
    | inr s =>
        simpa [obligationComponent] using A.source_component (Sum.inr s)
  unit := A.unit
  unit_pos := A.unit_pos

end CoherentMicroAssignment
end ResidualAdapter

/-! ## Exact two-half obstruction

An injective micro-assignment can send the two halves of one base key to two
different components.  No `Source → Comp` function can then satisfy the
compiled component-preservation field.
-/

def splitHalfAssignment : Bool ↪ (Unit × Fin 2) where
  toFun b := ((), if b then 1 else 0)
  inj' := by
    intro x y h
    cases x <;> cases y <;> simp_all

def splitComponent (b : Bool) : Bool := b

theorem splitHalfAssignment_not_baseKeyCoherent :
    ¬BaseKeyComponentCoherent splitHalfAssignment splitComponent := by
  intro h
  have hfalse := h false true rfl
  simp [splitComponent] at hfalse

theorem splitHalfAssignment_has_no_sourceComponent :
    ¬∃ sourceComp : Unit → Bool,
      ∀ x, sourceComp (splitHalfAssignment x).1 = splitComponent x := by
  intro h
  have hcoherent :=
    (exists_sourceComponent_iff_baseKeyComponentCoherent false
      splitHalfAssignment splitComponent).1 h
  exact splitHalfAssignment_not_baseKeyCoherent hcoherent

end CodexTmp.CommonBlueUniversal.Pattern5StaticToken

#print axioms CodexTmp.CommonBlueUniversal.Pattern5StaticToken.exists_sourceComponent_iff_baseKeyComponentCoherent
#print axioms CodexTmp.CommonBlueUniversal.Pattern5StaticToken.baseKeyComponentCoherent_of_relationUnique
#print axioms CodexTmp.CommonBlueUniversal.Pattern5StaticToken.CoherentMicroAssignment.toResidualData
#print axioms CodexTmp.CommonBlueUniversal.Pattern5StaticToken.splitHalfAssignment_has_no_sourceComponent
