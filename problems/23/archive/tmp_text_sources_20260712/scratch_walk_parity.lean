import Mathlib

namespace Erdos23Delta0
namespace ScratchWalkParity

open SimpleGraph

variable {V : Type*} [DecidableEq V] {G : SimpleGraph V}

 theorem even_countP_edges_iff_walk {u v : V} {p : G.Walk u v} (x : V) :
    Even (p.edges.countP fun e => x ∈ e) ↔ u ≠ v → x ≠ u ∧ x ≠ v := by
  induction p with
  | nil => simp
  | cons huv p ih =>
    simp only [List.countP_cons, Ne, SimpleGraph.Walk.edges_cons, Sym2.mem_iff]
    split_ifs with h
    · rw [decide_eq_true_eq] at h
      obtain (rfl | rfl) := h
      · rw [Nat.even_add_one, ih]
        simp only [huv.ne, imp_false, Ne, not_false_iff, true_and, not_forall,
          Classical.not_not, exists_prop, not_true, false_and,
          and_iff_right_iff_imp]
        rintro rfl rfl
        exact G.loopless _ huv
      · have := huv.ne
        grind
    · grind

 theorem even_countP_edges_closed {u : V} (p : G.Walk u u) (x : V) :
    Even (p.edges.countP fun e => x ∈ e) := by
  rw [even_countP_edges_iff_walk]
  intro h
  exact False.elim (h rfl)

#print axioms even_countP_edges_closed

end ScratchWalkParity
end Erdos23Delta0
