import OddWalkSplitScratch
import StructureCandidates

/-!
# From a shortest odd closed walk to an induced five-cycle

This scratch file joins the compiled parity/minimum-walk route in
`StructureCandidates` to the compiled cycle theorem in `OddWalkSplitScratch`.
It proves the load-bearing `L1d` and `L1e` steps without modifying the target.
-/

open Classical

namespace WOWII314.OddCycleInducedScratch

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} [DecidableRel G.Adj]

abbrev ShortestOddClosedWalk :=
  WOWII314.OddWalkSplitScratch.ShortestOddClosedWalk

/-- A chord between two cyclically nonconsecutive indexed vertices of a
minimum odd closed walk would split it into two strictly shorter closed walks,
one of odd length. -/
lemma shortestOddClosedWalk_no_chord
    (W : ShortestOddClosedWalk G) {i j : ℕ}
    (hij : i < j) (hj : j ≤ W.walk.length)
    (hsep : 2 ≤ j - i) (hcomp : j - i ≤ W.walk.length - 2) :
    ¬ G.Adj (W.walk.getVert i) (W.walk.getVert j) := by
  intro hchord
  let d := j - i
  have hi : i ≤ W.walk.length := hij.le.trans hj
  have hdle : d ≤ W.walk.length - i := by
    simp only [d]
    omega
  have hsegEnd : (W.walk.drop i).getVert d = W.walk.getVert j := by
    simp [d, Walk.drop_getVert, Nat.add_sub_of_le hij.le]
  let seg : G.Walk (W.walk.getVert i) (W.walk.getVert j) :=
    ((W.walk.drop i).take d).copy rfl hsegEnd
  let q : G.Walk (W.walk.getVert i) (W.walk.getVert i) :=
    seg.concat hchord.symm
  let r : G.Walk (W.walk.getVert i) (W.walk.getVert i) :=
    Walk.cons hchord ((W.walk.drop j).append (W.walk.take i))
  have hq_length : q.length = d + 1 := by
    simp [q, seg, hdle]
  have hr_length : r.length = W.walk.length - d + 1 := by
    simp [r, d]
    omega
  have hsum : q.length + r.length = W.walk.length + 2 := by
    rw [hq_length, hr_length]
    omega
  have hq_lt : q.length < W.walk.length := by
    rw [hq_length]
    simp only [d] at hsep hcomp ⊢
    omega
  have hr_lt : r.length < W.walk.length := by
    rw [hr_length]
    simp only [d] at hsep hcomp ⊢
    omega
  by_cases hqodd : Odd q.length
  · exact (not_lt_of_ge (W.minimal q hqodd)) hq_lt
  · have hrodd : Odd r.length := by
      rw [← Nat.not_even_iff_odd]
      intro hreven
      have hqeven : Even q.length := Nat.not_odd_iff_even.mp hqodd
      have hsumEven : Even (W.walk.length + 2) :=
        hsum ▸ hqeven.add hreven
      have hnEven : Even W.walk.length := by
        simpa [Nat.even_add] using hsumEven
      exact (Nat.not_even_iff_odd.mpr W.odd_length) hnEven
    exact (not_lt_of_ge (W.minimal r hrodd)) hr_lt

/-- The already compiled shortest-walk cycle theorem combines with the
triangle-free bridge from `StructureCandidates` to give the lower bound five. -/
lemma five_le_shortestOddClosedWalk_length
    (W : ShortestOddClosedWalk G)
    (hTriFree : ∀ a b c : V, G.Adj a b → G.Adj b c → G.Adj c a → False) :
    5 ≤ W.walk.length :=
  WOWII314.StructureCandidates.five_le_length_of_odd_cycle_triangle_free
    hTriFree (WOWII314.OddWalkSplitScratch.shortestOddClosedWalk_isCycle W)
    W.odd_length

/-- If the graph has no induced `P5`, a shortest odd closed walk has at most
five edges.  If it had at least seven, its first five vertices, with all
nonconsecutive pairs excluded by `shortestOddClosedWalk_no_chord`, would give
an induced copy of `pathGraph 5`. -/
lemma shortestOddClosedWalk_length_le_five_of_no_inducedP5
    (W : ShortestOddClosedWalk G)
    (hNoP5 : ¬ SimpleGraph.IsIndContained (pathGraph 5) G) :
    W.walk.length ≤ 5 := by
  by_contra hle
  obtain ⟨k, hk⟩ := W.odd_length
  have hlong : 7 ≤ W.walk.length := by omega
  have hcycle :=
    WOWII314.OddWalkSplitScratch.shortestOddClosedWalk_isCycle W
  have h01 : G.Adj (W.walk.getVert 0) (W.walk.getVert 1) :=
    W.walk.adj_getVert_succ (by omega)
  have h12 : G.Adj (W.walk.getVert 1) (W.walk.getVert 2) :=
    W.walk.adj_getVert_succ (by omega)
  have h23 : G.Adj (W.walk.getVert 2) (W.walk.getVert 3) :=
    W.walk.adj_getVert_succ (by omega)
  have h34 : G.Adj (W.walk.getVert 3) (W.walk.getVert 4) :=
    W.walk.adj_getVert_succ (by omega)
  have h02 : ¬ G.Adj (W.walk.getVert 0) (W.walk.getVert 2) :=
    shortestOddClosedWalk_no_chord W (by omega) (by omega) (by omega) (by omega)
  have h03 : ¬ G.Adj (W.walk.getVert 0) (W.walk.getVert 3) :=
    shortestOddClosedWalk_no_chord W (by omega) (by omega) (by omega) (by omega)
  have h04 : ¬ G.Adj (W.walk.getVert 0) (W.walk.getVert 4) :=
    shortestOddClosedWalk_no_chord W (by omega) (by omega) (by omega) (by omega)
  have h13 : ¬ G.Adj (W.walk.getVert 1) (W.walk.getVert 3) :=
    shortestOddClosedWalk_no_chord W (by omega) (by omega) (by omega) (by omega)
  have h14 : ¬ G.Adj (W.walk.getVert 1) (W.walk.getVert 4) :=
    shortestOddClosedWalk_no_chord W (by omega) (by omega) (by omega) (by omega)
  have h24 : ¬ G.Adj (W.walk.getVert 2) (W.walk.getVert 4) :=
    shortestOddClosedWalk_no_chord W (by omega) (by omega) (by omega) (by omega)
  have hinj : Function.Injective
      (fun t : Fin 5 ↦ W.walk.getVert t.val) := by
    intro a b hab
    apply Fin.ext
    exact hcycle.getVert_injOn'
      (by simp only [Set.mem_setOf_eq]; omega)
      (by simp only [Set.mem_setOf_eq]; omega) hab
  let e : pathGraph 5 ↪g G where
    toFun t := W.walk.getVert t.val
    inj' := hinj
    map_rel_iff' := by
      intro a b
      fin_cases a <;> fin_cases b <;>
        simp [pathGraph_adj, h01, h12, h23, h34,
          h02, h03, h04, h13, h14, h24, adj_comm]
  exact hNoP5 ⟨e⟩

/-- `L1e`: in a triangle-free induced-`P5`-free graph, every minimum odd
closed walk is a five-cycle, and by `shortestOddClosedWalk_no_chord` it is an
induced five-cycle. -/
lemma shortestOddClosedWalk_length_eq_five
    (W : ShortestOddClosedWalk G)
    (hTriFree : ∀ a b c : V, G.Adj a b → G.Adj b c → G.Adj c a → False)
    (hNoP5 : ¬ SimpleGraph.IsIndContained (pathGraph 5) G) :
    W.walk.length = 5 := by
  exact Nat.le_antisymm
    (shortestOddClosedWalk_length_le_five_of_no_inducedP5 W hNoP5)
    (five_le_shortestOddClosedWalk_length W hTriFree)

/-- Integration point: the minimum odd walk supplied by
`StructureCandidates` is repackaged for `OddWalkSplitScratch`, then `L1c`--`L1e`
produce an induced cycle of length five. -/
lemma not_bipartite_exists_induced_five_cycle
    (hNotBipartite : ¬ G.IsBipartite)
    (hTriFree : ∀ a b c : V, G.Adj a b → G.Adj b c → G.Adj c a → False)
    (hNoP5 : ¬ SimpleGraph.IsIndContained (pathGraph 5) G) :
    ∃ W : ShortestOddClosedWalk G,
      W.walk.IsCycle ∧ W.walk.length = 5 := by
  obtain ⟨v, w, hodd, hminimal⟩ :=
    WOWII314.StructureCandidates.exists_shortest_odd_closed_walk hNotBipartite
  let W : ShortestOddClosedWalk G := ⟨v, w, hodd, hminimal⟩
  exact ⟨W,
    WOWII314.OddWalkSplitScratch.shortestOddClosedWalk_isCycle W,
    shortestOddClosedWalk_length_eq_five W hTriFree hNoP5⟩

end WOWII314.OddCycleInducedScratch
