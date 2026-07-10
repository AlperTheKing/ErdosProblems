import Erdos23Delta0.HornClosedShoreSplitChecker
import Erdos23Delta0.DisjointPetalHalfSqueezeChecker

/-!
# Combined directed-Horn split or half-layer gate

This is the exact operational target for the current wall classifier.  A
payload may close the instance either by supplying two valid Horn-closed
children or by supplying a disjoint-petal positive-alpha TwoCover.  The module
proves soundness of the disjunction but deliberately does not assert that a
real extractor always emits one branch.
-/

namespace Erdos23Delta0
namespace HornSplitOrHalfLayerChecker

open Wall
open Wall.ClosedShore
open DisjointPetalHalfSqueezeChecker

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {I : BankedWallLP} {q : Nat}

/-- Combined Boolean gate for one supplied split candidate and one supplied
half-layer candidate. -/
noncomputable def check
    [DecidableEq I.Sink]
    (S : HornEscapeSurface I) (parent : Finset I.Port)
    (leftU rightU : Finset S.QComp)
    (H : Candidate V I q) (d : Dual I) : Bool :=
  checkHornClosedSplitCandidate S parent leftU rightU ||
    (checkCandidate H && checkPositiveAlphaTwoCover H d)

/-- Kernel soundness of the combined finite gate. -/
theorem sound [DecidableEq I.Sink]
    (S : HornEscapeSurface I) (L : I.Port → ℚ)
    (parent : Finset I.Port) (leftU rightU : Finset S.QComp)
    (H : Candidate V I q) (d : Dual I) (hd : d.Checked)
    (hcheck : check S parent leftU rightU H d = true) :
    Nonempty (ProperClosedBankSplit S.toQ L parent) ∨ ¬ d.StrictGap := by
  rw [check, Bool.or_eq_true, Bool.and_eq_true] at hcheck
  rcases hcheck with hsplit | ⟨hgeom, htwo⟩
  · exact Or.inl
      (nonempty_properClosedBankSplit_of_checkHornClosedSplitCandidate
        S L parent leftU rightU hsplit)
  · exact Or.inr (noStrictDual_of_checks H d hd hgeom htwo)

#print axioms sound

end HornSplitOrHalfLayerChecker
end Erdos23Delta0
