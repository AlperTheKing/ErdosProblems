import FormalConjectures.WrittenOnTheWallII.GraphConjecture314
import Mathlib.Combinatorics.SimpleGraph.ConcreteColorings
import Mathlib.Combinatorics.SimpleGraph.Metric

/-!
# Minimum odd closed walks

Scratch lemmas for the load-bearing `L1c` step of WOWII Conjecture 314.
-/

open Classical

namespace WOWII314.OddWalkSplitScratch

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} [DecidableRel G.Adj]

structure ShortestOddClosedWalk (G : SimpleGraph V) where
  vertex : V
  walk : G.Walk vertex vertex
  odd_length : Odd walk.length
  minimal : ∀ {u : V} (q : G.Walk u u), Odd q.length → walk.length ≤ q.length

private lemma odd_closed_walk_three_le_length {v : V} (w : G.Walk v v)
    (hw : Odd w.length) : 3 ≤ w.length := by
  match w with
  | .nil => simp at hw
  | .cons h .nil => simp at h
  | .cons _ (.cons _ .nil) => norm_num at hw
  | .cons _ (.cons _ (.cons _ _)) =>
      simp only [Walk.length_cons]
      omega

private lemma repeat_gives_shorter_odd
    (W : ShortestOddClosedWalk G) {i j : ℕ}
    (hi : 1 ≤ i) (hij : i < j) (hj : j ≤ W.walk.length)
    (heq : W.walk.getVert i = W.walk.getVert j) : False := by
  let d := j - i
  have hdpos : 0 < d := by simp [d, Nat.sub_pos_iff_lt, hij]
  have hdle : d ≤ W.walk.length - i := by omega
  have hqend : (W.walk.drop i).getVert d = W.walk.getVert i := by
    simp [d, Walk.drop_getVert, Nat.add_sub_of_le hij.le, heq]
  let q : G.Walk (W.walk.getVert i) (W.walk.getVert i) :=
    ((W.walk.drop i).take d).copy rfl hqend
  let r : G.Walk (W.walk.getVert i) (W.walk.getVert i) :=
    ((W.walk.drop j).append (W.walk.take i)).copy heq.symm rfl
  have hq_length : q.length = d := by
    simp [q, hdle]
  have hr_length : r.length = W.walk.length - d := by
    simp [r, d]
    omega
  have hsum : q.length + r.length = W.walk.length := by
    rw [hq_length, hr_length]
    omega
  have hq_lt : q.length < W.walk.length := by
    rw [hq_length]
    omega
  have hr_lt : r.length < W.walk.length := by
    rw [hr_length]
    omega
  by_cases hqodd : Odd q.length
  · exact (not_lt_of_ge (W.minimal q hqodd)) hq_lt
  · have hrodd : Odd r.length := by
      rw [← Nat.not_even_iff_odd]
      intro hreven
      have hqeven : Even q.length := Nat.not_odd_iff_even.mp hqodd
      have : Even W.walk.length := hsum ▸ hqeven.add hreven
      exact (Nat.not_even_iff_odd.mpr W.odd_length) this
    exact (not_lt_of_ge (W.minimal r hrodd)) hr_lt

private lemma shortest_getVert_injOn (W : ShortestOddClosedWalk G) :
    Set.InjOn W.walk.getVert {i | 1 ≤ i ∧ i ≤ W.walk.length} := by
  intro i hi j hj heq
  rcases Nat.lt_trichotomy i j with hij | rfl | hji
  · exact (repeat_gives_shorter_odd W hi.1 hij hj.2 heq).elim
  · rfl
  · exact (repeat_gives_shorter_odd W hj.1 hji hi.2 heq.symm).elim

private lemma shortest_tail_support_nodup (W : ShortestOddClosedWalk G) :
    W.walk.support.tail.Nodup := by
  rw [List.nodup_iff_injective_getElem]
  intro i j hij
  apply Fin.ext
  have hi : i.val + 1 ≤ W.walk.length := by
    simpa [Walk.length_support] using i.isLt
  have hj : j.val + 1 ≤ W.walk.length := by
    simpa [Walk.length_support] using j.isLt
  have hverts : W.walk.getVert (i.val + 1) = W.walk.getVert (j.val + 1) := by
    simpa [W.walk.getVert_eq_support_getElem hi,
      W.walk.getVert_eq_support_getElem hj] using hij
  have := shortest_getVert_injOn W (by simp; omega) (by simp; omega) hverts
  omega

private lemma isTrail_of_tail_nodup_of_three_le {v : V} (w : G.Walk v v)
    (htail : w.support.tail.Nodup) (hlen : 3 ≤ w.length) : w.IsTrail := by
  cases w with
  | nil => simp at hlen
  | @cons u v _ huv p =>
      have hpPath : p.IsPath := Walk.IsPath.mk' (by simpa using htail)
      rw [Walk.isTrail_cons]
      refine ⟨hpPath.isTrail, ?_⟩
      intro hedge
      have hvpen : v = p.penultimate :=
        hpPath.eq_penultimate_of_mem_edges hedge
      have hplen : 2 ≤ p.length := by
        simp only [Walk.length_cons] at hlen
        omega
      have hidx := hpPath.getVert_injOn
        (show 0 ≤ p.length by omega)
        (show p.length - 1 ≤ p.length by omega)
        (by simpa [Walk.penultimate] using hvpen)
      omega

lemma shortestOddClosedWalk_isCycle (W : ShortestOddClosedWalk G) :
    W.walk.IsCycle := by
  have htail := shortest_tail_support_nodup W
  have hlen := odd_closed_walk_three_le_length W.walk W.odd_length
  have hne : W.walk ≠ .nil := by
    intro h
    rw [h] at hlen
    simp at hlen
  rw [Walk.isCycle_def]
  exact ⟨isTrail_of_tail_nodup_of_three_le W.walk htail hlen, hne, htail⟩

end WOWII314.OddWalkSplitScratch
