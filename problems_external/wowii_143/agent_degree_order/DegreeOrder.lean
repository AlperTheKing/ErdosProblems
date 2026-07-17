import FormalConjectures.Util.ProblemImports
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Degrees

/-! The degree-order bridge for WOWII Conjecture 143. -/

namespace AgentDegreeOrder

open Classical SimpleGraph

variable {α : Type*} [Fintype α] [Nontrivial α]

/-- In a nontrivial connected finite graph, second-smallest degree one forces two leaves. -/
lemma exists_distinct_degree_one_of_secondSmallestDegree_eq_one
    (G : SimpleGraph α) [DecidableRel G.Adj] (hG : G.Preconnected)
    (hσ : secondSmallestDegree G = 1) :
    ∃ x y : α, x ≠ y ∧ G.degree x = 1 ∧ G.degree y = 1 := by
  let ds := degreeSequence G
  have hlen : 2 ≤ ds.length := by
    simpa [ds, degreeSequence] using Fintype.one_lt_card (α := α)
  obtain ⟨a, b, tail, hds⟩ : ∃ a b tail, ds = a :: b :: tail := by
    cases h : ds with
    | nil => simp [h] at hlen
    | cons a rest =>
        cases hrest : rest with
        | nil => simp [h, hrest] at hlen
        | cons b tail => exact ⟨a, b, tail, rfl⟩
  have hb : b = 1 := by
    simpa [secondSmallestDegree, ds, hds] using hσ
  have hsorted : ds.Pairwise (· ≤ ·) := by
    simp [ds, degreeSequence]
  have hab : a ≤ b := by
    simpa [hds] using hsorted.rel_get_of_lt (a := ⟨0, by simp [hds]⟩)
      (b := ⟨1, by simp [hds]⟩) (by simp)
  have ha_mem : a ∈ ds := by simp [hds]
  have ha_pos : 0 < a := by
    have ha_map : a ∈ Finset.univ.val.map (fun v : α => G.degree v) := by
      simpa [ds, degreeSequence] using ha_mem
    obtain ⟨v, -, rfl⟩ := Multiset.mem_map.mp ha_map
    exact hG.degree_pos_of_nontrivial v
  have ha : a = 1 := by omega
  have hcount : 2 ≤ ds.count 1 := by simp [hds, ha, hb]
  have hcoeds : (↑ds : Multiset ℕ) =
      Finset.univ.val.map (fun v : α => G.degree v) := by
    simp [ds, degreeSequence]
  have hcountm : 2 ≤
      (Finset.univ.val.map (fun v : α => G.degree v)).count 1 := by
    rw [← hcoeds, Multiset.coe_count]
    exact hcount
  have hleaves : 2 ≤ (Finset.univ.filter fun v : α => G.degree v = 1).card := by
    rw [Multiset.count_map] at hcountm
    simpa only [← Finset.filter_val, eq_comm] using hcountm
  have htwo : 1 < (Finset.univ.filter fun v : α => G.degree v = 1).card := by omega
  obtain ⟨x, hx, y, hy, hxy⟩ := Finset.one_lt_card.mp htwo
  exact ⟨x, y, hxy, (Finset.mem_filter.mp hx).2, (Finset.mem_filter.mp hy).2⟩

end AgentDegreeOrder
