import Mathlib

namespace Erdos23Delta0
namespace ScratchSdiff

open Finset

variable {α : Type*} [DecidableEq α]

 theorem sdiff_card_one_of_four_inter_three {A B : Finset α}
    (hA : A.card = 4) (hI : (A ∩ B).card = 3) :
    (A \ B).card = 1 := by
  have hEq : A \ B = A \ (A ∩ B) := by
    ext x
    simp
  have hInter : (A ∩ B) ∩ A = A ∩ B := by
    ext x
    simp [and_assoc, and_left_comm, and_comm]
  rw [hEq, Finset.card_sdiff, hInter]
  omega

#print axioms sdiff_card_one_of_four_inter_three

end ScratchSdiff
end Erdos23Delta0
