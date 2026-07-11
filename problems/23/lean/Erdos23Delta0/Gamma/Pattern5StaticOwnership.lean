import Erdos23Delta0.ResidualSourceTokenization

/-!
# Static ownership for Pattern-5 source halves

Pattern 5 is used here only as a static source relation.  A residual source has
one component label per ordered-pair base key, while the two half bits are
matched separately.  Injectivity on full half keys is therefore insufficient:
assignments using the same base key must agree on their destination component.

This module deliberately exports no graph-local relation-level uniqueness
claim.  Such a claim is false; coherence is an obligation on the selected
global matching.
-/

namespace Erdos23Delta0
namespace Gamma
namespace Pattern5StaticOwnership

variable {Source Comp Domain : Type*}

/-- Component agreement whenever two assigned micro-obligations use the two
halves of the same ordered-pair base key. -/
def BaseKeyComponentCoherent
    (assign : Domain ↪ (Source × Fin 2)) (component : Domain → Comp) : Prop :=
  ∀ x y, (assign x).1 = (assign y).1 → component x = component y

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
`sourceComp` field, rather than merely a sufficient local rule. -/
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

/-- Collision-debit halves and twenty-five microcopies of each need slot. -/
abbrev MicroObligation (Debit Slot : Type*) :=
  (Debit × Fin 2) ⊕ (Slot × Fin 25)

def obligationComponent
    (owner : Slot → V) (vertexComp : V → Comp) (debitComp : Debit → Comp) :
    MicroObligation Debit Slot → Comp
  | Sum.inl d => debitComp d.1
  | Sum.inr s => vertexComp (owner s.1)

/-- The weakest static data that converts an exact micro-matching into
`ResidualSourceTokenization.Data`.  Pattern-5 eligibility is proved when the
global assignment is constructed; this adapter needs only base-key coherence.
-/
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
The existing interface then supplies source uniqueness, component
preservation, and the exact twenty-five-microcopy scale. -/
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

end Pattern5StaticOwnership
end Gamma
end Erdos23Delta0
