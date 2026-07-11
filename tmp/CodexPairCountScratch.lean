import Erdos23Delta0.Gamma.ActiveScopedCoordinateTransport

namespace Erdos23Delta0.Gamma.ActiveScopedMinimumExchange

open CertGraph
open MinimumDemandRowSelection

theorem length_filter_ofFn_eq_card_filter
    {α : Type*} (n : Nat) (f : Fin n → α) (p : α → Prop)
    [DecidablePred p] :
    ((List.ofFn f).filter p).length =
      (Finset.univ.filter fun i : Fin n => p (f i)).card := by
  induction n with
  | zero => simp
  | succ n ih =>
      rw [List.ofFn_succ, Finset.card_eq_sum_ones, Finset.sum_filter,
        Fin.sum_univ_succ]
      by_cases h : p (f 0)
      · simp [h, ih, Nat.add_comm]
      · simp [h, ih]

theorem pairCount_eq_card_filter
    {bads : List BadEdgeData} (omega : RowChoice bads) (x y : Nat) :
    pairCount omega x y =
      (Finset.univ.filter fun i : Fin bads.length =>
        x ∈ ((bads.get i).rows.get (omega i)).verts ∧
        y ∈ ((bads.get i).rows.get (omega i)).verts).card := by
  unfold pairCount selectedRows
  rw [length_filter_ofFn_eq_card_filter]

theorem pairCount_replaceOne_of_owner_not_mem_changed
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (i : Fin bads.length)
    (replacement : Fin (bads.get i).rows.length)
    (owner other : Nat)
    (hownerOld : owner ∉ ((bads.get i).rows.get (omega i)).verts)
    (hownerNew : owner ∉ ((bads.get i).rows.get replacement).verts) :
    pairCount (replaceOne omega i replacement) owner other =
      pairCount omega owner other := by
  rw [pairCount_eq_card_filter, pairCount_eq_card_filter]
  congr 1
  ext j
  simp only [Finset.mem_filter, Finset.mem_univ, true_and]
  by_cases hji : j = i
  · subst j
    rw [replaceOne_apply_self]
    simp [hownerOld, hownerNew]
  · rw [replaceOne_apply_of_ne omega i j replacement hji]

end Erdos23Delta0.Gamma.ActiveScopedMinimumExchange
