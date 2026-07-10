import Mathlib

/-!
# Bank-prime split-or-root induction

This module isolates the well-founded part of the proposed replacement for
broad root-locality.  A positive full-bank state need not itself be rooted if
it has a bank-conserving split into two lower-rank states whose combined
defect dominates the parent.  Repeating such splits reaches a rooted positive
state, provided every root witness is killed by the rooted theorem.

The graph-side work is exactly construction of `SplitOrRoot`; no graph claim
is asserted here.
-/

namespace Erdos23Delta0
namespace Wall
namespace BankPrime

/-- A proper bank-conserving split.  The bank and exchange bookkeeping is
summarized by `defect_le`; concrete providers must derive that inequality from
the checked closed-cut exchange identity and W1 discharge. -/
structure ProperSplit
    (State : Type*) (rank : State -> Nat) (defect : State -> ℚ)
    (parent : State) where
  left : State
  right : State
  left_rank : rank left < rank parent
  right_rank : rank right < rank parent
  defect_le : defect parent <= defect left + defect right

/-- Exact classifier obligation for the bank-prime route.  Every positive
state either has a rooted witness or has a proper bank-conserving split. -/
def SplitOrRoot
    (State RootWitness : Type*)
    (rank : State -> Nat) (defect : State -> ℚ)
    (rootAt : State -> RootWitness -> Prop) : Prop :=
  forall X, 0 < defect X ->
    Nonempty (ProperSplit State rank defect X) ∨ Exists (rootAt X)

/-- Positivity descends to at least one child of every proper split. -/
theorem ProperSplit.positive_child
    {State : Type*} {rank : State -> Nat} {defect : State -> ℚ}
    {parent : State} (S : ProperSplit State rank defect parent)
    (hpos : 0 < defect parent) :
    0 < defect S.left ∨ 0 < defect S.right := by
  by_contra h
  push_neg at h
  have hsum : defect S.left + defect S.right <= 0 := by linarith
  linarith [S.defect_le]

/-- The abstract bank-prime induction.  If rooted witnesses are impossible and
every positive state splits or is rooted, every state has nonpositive defect. -/
theorem defect_nonpos_of_split_or_root
    {State RootWitness : Type*}
    (rank : State -> Nat) (defect : State -> ℚ)
    (rootAt : State -> RootWitness -> Prop)
    (hclass : SplitOrRoot State RootWitness rank defect rootAt)
    (hroot : forall X r, rootAt X r -> False) :
    forall X, defect X <= 0 := by
  intro X
  apply (Nat.lt_wfRel.wf.onFun (f := rank)).induction X
  intro parent ih
  by_cases hpos : 0 < defect parent
  · rcases hclass parent hpos with hsplit | hrooted
    · obtain ⟨S⟩ := hsplit
      have hleft : defect S.left <= 0 := ih S.left S.left_rank
      have hright : defect S.right <= 0 := ih S.right S.right_rank
      calc
        defect parent <= defect S.left + defect S.right := S.defect_le
        _ <= 0 := by linarith
    · obtain ⟨r, hr⟩ := hrooted
      exact False.elim (hroot parent r hr)
  · exact le_of_not_gt hpos

end BankPrime
end Wall
end Erdos23Delta0
