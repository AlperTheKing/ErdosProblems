import Mathlib

namespace Erdos23Delta0
namespace ScratchCountP

open Finset

variable {α : Type*} [DecidableEq α]

theorem List.countP_eq_sum_toFinset_of_nodup (l : List α) (P : α → Prop) [DecidablePred P]
    (hn : l.Nodup) :
    l.countP P = ∑ x ∈ l.toFinset, if P x then 1 else 0 := by
  induction l with
  | nil => simp
  | cons a t ih =>
    rw [List.nodup_cons] at hn
    have ht := hn.2
    have hnot : a ∉ t.toFinset := by simpa using hn.1
    rw [List.countP_cons, List.toFinset_cons, Finset.sum_insert hnot, ih ht]
    by_cases hP : P a <;> simp [hP] <;> omega

#print axioms List.countP_eq_sum_toFinset_of_nodup

end ScratchCountP
end Erdos23Delta0
