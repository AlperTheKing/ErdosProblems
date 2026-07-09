import Mathlib

/-!
# Walk incidence parity

This module records the elementary parity fact that every vertex has even
incident edge-occurrence count in a closed walk. Mathlib has the corresponding
statement for trails; Gap#1 T6 needs the walk version because the closed walk is
formed by appending one geodesic to the reverse of another and may repeat edges.
-/

namespace Erdos23Delta0
namespace WalkParity

open SimpleGraph

variable {V : Type*} [DecidableEq V] {G : SimpleGraph V}

/-- For an arbitrary walk, the parity of the number of incident traversed edges
is controlled only by the endpoints. -/
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

/-- Every vertex has even incident edge-occurrence count in a closed walk. -/
theorem even_countP_edges_closed {u : V} (p : G.Walk u u) (x : V) :
    Even (p.edges.countP fun e => x ∈ e) := by
  rw [even_countP_edges_iff_walk]
  intro h
  exact False.elim (h rfl)

/-- If two non-loop unordered edges are the only possible contributors to an
even incidence count at every vertex, then they are the same edge. This is the
local Sym2 form used after canceling paired edge occurrences in a closed walk. -/
theorem sym2_eq_of_even_two_nonloop {a b c d : V}
    (hab : a ≠ b)
    (hpar : ∀ x : V,
      Even ((if x ∈ s(a,b) then 1 else 0) + (if x ∈ s(c,d) then 1 else 0))) :
    s(a,b) = s(c,d) := by
  have ha : a ∈ s(c,d) := by
    by_contra ha
    have h := hpar a
    simp [Sym2.mem_iff, hab, ha] at h
  have hb : b ∈ s(c,d) := by
    by_contra hb
    have h := hpar b
    simp [Sym2.mem_iff, hab.symm, hb] at h
  rw [Sym2.eq_iff]
  rw [Sym2.mem_iff] at ha hb
  grind

/-- For a nodup list, `countP` is the corresponding `0/1` sum over the
associated finset. -/
theorem List.countP_eq_sum_toFinset_of_nodup {α : Type*} [DecidableEq α]
    (l : List α) (P : α → Prop) [DecidablePred P] (hn : l.Nodup) :
    l.countP P = ∑ x ∈ l.toFinset, if P x then 1 else 0 := by
  induction l with
  | nil => simp
  | cons a t ih =>
    rw [List.nodup_cons] at hn
    have ht := hn.2
    have hnot : a ∉ t.toFinset := by simpa using hn.1
    rw [List.countP_cons, List.toFinset_cons, Finset.sum_insert hnot, ih ht]
    by_cases hP : P a <;> simp [hP] <;> omega


end WalkParity
end Erdos23Delta0
