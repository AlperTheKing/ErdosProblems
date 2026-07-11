import Erdos23Delta0.Gamma.CheckedCollisionDefectTrade

/-!
# Checked lexicographic collision trades

The R33 selector minimizes collision defect and then a deterministic row code.
Consequently a checked simultaneous row change need not strictly lower defect:
transporting an old optimal matching with no more unmatched obligations and
strictly lowering the row code is already impossible at the canonical state.

This is the finite target for the R34 closed-cycle branch.  The graph theorem
that constructs such a reversible cycle exchange remains explicit and open.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CheckedCollisionLexTrade

open CheckedCollisionDefectTrade

universe uState uObligation uSource uComp uChange

variable {State : Type uState} {Obligation : Type uObligation}
variable {SourceBase : Type uSource} {Comp : Type uComp}
variable [DecidableEq Obligation]

/-- Exact two-level optimality used by the canonical selector. -/
def LexMinimal
    (D : Data State Obligation SourceBase Comp)
    (rowCode : State → Nat) (state : State) : Prop :=
  (∀ other, D.collisionDefect state ≤ D.collisionDefect other) ∧
    (∀ other, D.collisionDefect other = D.collisionDefect state →
      rowCode state ≤ rowCode other)

/-- A checked simultaneous row change that preserves enough of an old exact
matching to avoid increasing its unmatched count, while strictly decreasing
the deterministic row code.  The new matching need not be optimal. -/
structure Trade
    (D : Data State Obligation SourceBase Comp)
    (rowCode : State → Nat)
    (stateRealized : State → Prop)
    (ChangeWitness : Type uChange)
    (simultaneousRowChangeRealized :
      State → State → ChangeWitness → Prop)
    (oldState : State) where
  old_state_realized : stateRealized oldState
  newState : State
  new_state_realized : stateRealized newState
  rowChange : ChangeWitness
  row_change_realized :
    simultaneousRowChangeRealized oldState newState rowChange
  oldMatching : CoherentPartialMatching D oldState
  old_defect_eq_unmatched :
    D.collisionDefect oldState = oldMatching.unmatchedCount
  newMatching : CoherentPartialMatching D newState
  unmatched_nonincreasing :
    newMatching.unmatchedCount ≤ oldMatching.unmatchedCount
  rowCode_lt : rowCode newState < rowCode oldState

/-- Every checked lex trade improves the honest objective: either its true
defect is already smaller, or the true defects are equal and row code drops. -/
theorem defect_lt_or_eq_and_rowCode_lt
    {D : Data State Obligation SourceBase Comp}
    {rowCode : State → Nat}
    {stateRealized : State → Prop}
    {ChangeWitness : Type uChange}
    {simultaneousRowChangeRealized :
      State → State → ChangeWitness → Prop}
    {oldState : State}
    (T : Trade D rowCode stateRealized ChangeWitness
      simultaneousRowChangeRealized oldState) :
    D.collisionDefect T.newState < D.collisionDefect oldState ∨
      (D.collisionDefect T.newState = D.collisionDefect oldState ∧
        rowCode T.newState < rowCode oldState) := by
  have hle : D.collisionDefect T.newState ≤
      D.collisionDefect oldState := by
    calc
      D.collisionDefect T.newState ≤ T.newMatching.unmatchedCount :=
        D.collisionDefect_le_unmatchedCount T.newMatching
      _ ≤ T.oldMatching.unmatchedCount := T.unmatched_nonincreasing
      _ = D.collisionDefect oldState := T.old_defect_eq_unmatched.symm
  rcases lt_or_eq_of_le hle with hlt | heq
  · exact Or.inl hlt
  · exact Or.inr ⟨heq, T.rowCode_lt⟩

/-- A lex-minimal canonical state admits no checked nonincreasing-defect row
rotation with smaller row code. -/
theorem false_of_lexMinimal
    {D : Data State Obligation SourceBase Comp}
    {rowCode : State → Nat}
    {stateRealized : State → Prop}
    {ChangeWitness : Type uChange}
    {simultaneousRowChangeRealized :
      State → State → ChangeWitness → Prop}
    {oldState : State}
    (hminimal : LexMinimal D rowCode oldState)
    (T : Trade D rowCode stateRealized ChangeWitness
      simultaneousRowChangeRealized oldState) : False := by
  rcases defect_lt_or_eq_and_rowCode_lt T with hlt | heq
  · exact (Nat.not_lt_of_ge (hminimal.1 T.newState)) hlt
  · exact (Nat.not_lt_of_ge (hminimal.2 T.newState heq.1)) heq.2

#print axioms defect_lt_or_eq_and_rowCode_lt
#print axioms false_of_lexMinimal

end CheckedCollisionLexTrade
end Gamma
end Erdos23Delta0
