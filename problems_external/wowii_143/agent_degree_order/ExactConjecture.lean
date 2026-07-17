import Mathlib
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Degrees
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree

/-! Exact assembly of the three cases in WOWII Conjecture 143. -/

namespace AgentExactConjecture

open Classical SimpleGraph

variable {α : Type*} [Fintype α] [DecidableEq α] [Nontrivial α]

theorem conjecture143_exact (G : SimpleGraph α) [DecidableRel G.Adj]
    (hG : G.Connected) (hσ : 0 < secondSmallestDegree G) :
    (G.girth : ℝ) + 1 ≤
      (largestInducedTreeSize G : ℝ) * (secondSmallestDegree G : ℝ) := by
  have hnat : G.girth + 1 ≤
      largestInducedTreeSize G * secondSmallestDegree G := by
    by_cases hacyc : G.IsAcyclic
    · have htpos : 0 < largestInducedTreeSize G := one_le_largestInducedTreeSize G
      rw [hacyc.girth_eq_zero]
      exact Nat.mul_pos htpos hσ
    · have hgirth : 3 ≤ G.girth := G.three_le_girth hacyc
      by_cases hσ1 : secondSmallestDegree G = 1
      · obtain ⟨x, y, hxy, hx, hy⟩ :=
          exists_distinct_degree_one_of_secondSmallestDegree_eq_one G
            hG.preconnected hσ1
        simpa [hσ1] using
          girth_add_one_le_largestInducedTreeSize_of_two_leaves
            G hG hacyc hxy hx hy
      · have hσ2 : 2 ≤ secondSmallestDegree G := by omega
        have htreebound : G.girth - 1 ≤ largestInducedTreeSize G :=
          girth_sub_one_le_largestInducedTreeSize G hacyc
        calc
          G.girth + 1 ≤ 2 * (G.girth - 1) := by omega
          _ ≤ 2 * largestInducedTreeSize G :=
            Nat.mul_le_mul_left 2 htreebound
          _ = largestInducedTreeSize G * 2 := by omega
          _ ≤ largestInducedTreeSize G * secondSmallestDegree G :=
            Nat.mul_le_mul_left _ hσ2
  exact_mod_cast hnat

end AgentExactConjecture
