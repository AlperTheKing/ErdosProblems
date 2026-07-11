import Erdos23Delta0.Gamma.CanonicalCollisionLexSelection

/-!
# Canonical collision progress contradiction

The graph-geometric endgame may produce one of three checked outcomes at the
canonical state: an augmentation in the same state, a strict defect trade, or
an explicitly rank-decreasing lex trade.  This module proves that any such
outcome contradicts finite canonicality.  It contains no graph-existence
assumption and does not assert that a progress outcome exists.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CanonicalCollisionProgress

open CheckedCollisionDefectTrade
open CheckedCollisionLexTrade
open CanonicalCollisionLexSelection

universe uState uObligation uSource uComp uChange

variable {State : Type uState} {Obligation : Type uObligation}
variable {SourceBase : Type uSource} {Comp : Type uComp}
variable [DecidableEq Obligation]

/-- A checked same-state augmentation below the honest minimum.  Constructing
one is impossible; the point is that a graph trace may expose it explicitly. -/
structure CheckedCoherentAugmentation
    (D : Data State Obligation SourceBase Comp) (state : State) where
  matching : CoherentPartialMatching D state
  unmatched_lt_defect :
    matching.unmatchedCount < D.collisionDefect state

theorem false_of_checkedCoherentAugmentation
    {D : Data State Obligation SourceBase Comp} {state : State}
    (A : CheckedCoherentAugmentation D state) : False := by
  exact (Nat.not_lt_of_ge
    (D.collisionDefect_le_unmatchedCount A.matching))
    A.unmatched_lt_defect

/-- The exact three-way progress surface consumed by the canonical argument. -/
def ProgressAtCanonical
    [Fintype State] [Nonempty State]
    (D : Data State Obligation SourceBase Comp)
    (rowCode : State → Nat)
    (stateRealized : State → Prop)
    (ChangeWitness : Type uChange)
    (simultaneousRowChangeRealized :
      State → State → ChangeWitness → Prop) : Prop :=
  let state := canonicalState D rowCode
  0 < D.collisionDefect state →
    Nonempty (CheckedCoherentAugmentation D state) ∨
      Nonempty (CheckedCollisionDefectTrade D stateRealized ChangeWitness
        simultaneousRowChangeRealized state) ∨
      Nonempty (Trade D rowCode stateRealized ChangeWitness
        simultaneousRowChangeRealized state)

/-- Any checked progress theorem at the canonical state forces zero defect. -/
theorem canonical_defect_eq_zero_of_progress
    [Fintype State] [Nonempty State]
    {D : Data State Obligation SourceBase Comp}
    {rowCode : State → Nat}
    {stateRealized : State → Prop}
    {ChangeWitness : Type uChange}
    {simultaneousRowChangeRealized :
      State → State → ChangeWitness → Prop}
    (hprogress : ProgressAtCanonical D rowCode stateRealized ChangeWitness
      simultaneousRowChangeRealized) :
    D.collisionDefect (canonicalState D rowCode) = 0 := by
  by_contra hnonzero
  have hpos : 0 < D.collisionDefect (canonicalState D rowCode) :=
    Nat.pos_of_ne_zero hnonzero
  rcases hprogress hpos with haugment | htrade
  · rcases haugment with ⟨A⟩
    exact false_of_checkedCoherentAugmentation A
  · rcases htrade with hstrict | hlex
    · rcases hstrict with ⟨T⟩
      have hlt := defect_lt T
      have hmin :=
        (canonicalState_lexMinimal D rowCode).1 T.newState
      exact (Nat.not_lt_of_ge hmin) hlt
    · rcases hlex with ⟨T⟩
      exact false_of_lexMinimal (canonicalState_lexMinimal D rowCode) T

#print axioms false_of_checkedCoherentAugmentation
#print axioms canonical_defect_eq_zero_of_progress

end CanonicalCollisionProgress
end Gamma
end Erdos23Delta0
