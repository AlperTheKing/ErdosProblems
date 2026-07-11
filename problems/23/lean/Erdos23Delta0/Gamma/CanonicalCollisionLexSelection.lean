import Erdos23Delta0.CertGraph
import Erdos23Delta0.Gamma.CheckedCollisionLexTrade

/-!
# Canonical finite collision selector

This module discharges the finite-choice part of the R35 wall.  It selects a
state minimizing collision defect and, among all defect minimizers, minimizing
the deterministic row code.  The remaining theorem is graph-geometric: a
positive-defect selected state must produce a coherent augmentation or an
explicit checked lex trade.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CanonicalCollisionLexSelection

open CertGraph
open CheckedCollisionDefectTrade
open CheckedCollisionLexTrade

universe uState uObligation uSource uComp uChange

variable {State : Type uState} {Obligation : Type uObligation}
variable {SourceBase : Type uSource} {Comp : Type uComp}
variable [DecidableEq Obligation]

/-- A finite state minimizing collision defect and then row code. -/
noncomputable def chooseLexMinimal
    [Fintype State] [Nonempty State]
    (D : Data State Obligation SourceBase Comp)
    (rowCode : State → Nat) :
    {state : State // LexMinimal D rowCode state} := by
  classical
  let defectChoice := chooseFiniteMinimizer D.collisionDefect
  let tieChoice := chooseFiniteFeasibleMinimizer
    (fun state : State =>
      D.collisionDefect state = D.collisionDefect defectChoice.1)
    ⟨defectChoice.1, rfl⟩ rowCode
  refine ⟨tieChoice.1, ?_, ?_⟩
  · intro other
    calc
      D.collisionDefect tieChoice.1 =
          D.collisionDefect defectChoice.1 := tieChoice.2.1
      _ ≤ D.collisionDefect other := defectChoice.2 other
  · intro other hdefect
    apply tieChoice.2.2 other
    exact hdefect.trans tieChoice.2.1

/-- The selected finite state itself. -/
noncomputable def canonicalState
    [Fintype State] [Nonempty State]
    (D : Data State Obligation SourceBase Comp)
    (rowCode : State → Nat) : State :=
  (chooseLexMinimal D rowCode).1

/-- The canonical state satisfies the exact two-level optimality contract. -/
theorem canonicalState_lexMinimal
    [Fintype State] [Nonempty State]
    (D : Data State Obligation SourceBase Comp)
    (rowCode : State → Nat) :
    LexMinimal D rowCode (canonicalState D rowCode) :=
  (chooseLexMinimal D rowCode).2

/-- No checked simultaneous trade can leave defect nonincreasing while
strictly lowering row code at the selected state. -/
theorem no_checked_trade_at_canonical
    [Fintype State] [Nonempty State]
    {D : Data State Obligation SourceBase Comp}
    {rowCode : State → Nat}
    {stateRealized : State → Prop}
    {ChangeWitness : Type uChange}
    {simultaneousRowChangeRealized :
      State → State → ChangeWitness → Prop}
    (T : Trade D rowCode stateRealized ChangeWitness
      simultaneousRowChangeRealized (canonicalState D rowCode)) : False :=
  false_of_lexMinimal (canonicalState_lexMinimal D rowCode) T

#print axioms chooseLexMinimal
#print axioms canonicalState_lexMinimal
#print axioms no_checked_trade_at_canonical

end CanonicalCollisionLexSelection
end Gamma
end Erdos23Delta0
