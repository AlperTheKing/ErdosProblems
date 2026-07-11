import Erdos23Delta0.Gamma.LiveDetourEndpointSource

/-!
# Arithmetic core of the cut-tight active-star lemma

For the blue-neighbour star of a cut-tight owner, the maximum-cut switch
inequality gives `2 * degree <= ownerLoss + sum neighbourLoss`.  This file
proves the exact pigeonhole step used to select a second blue neighbour whose
two-vertex loss with the chosen active neighbour is at least two.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CutTightStarPigeonhole

variable {Vertex : Type*} [DecidableEq Vertex]

theorem exists_other_with_two_le_loss_sum
    (neighbours : Finset Vertex) (activeNeighbour : Vertex)
    (loss : Vertex → Nat) (ownerLoss : Nat)
    (hdegree : 2 ≤ neighbours.card)
    (htight : ownerLoss ≤ 1)
    (hstar : 2 * neighbours.card ≤
      ownerLoss + ∑ z ∈ neighbours, loss z) :
    ∃ supportNeighbour ∈ neighbours,
      supportNeighbour ≠ activeNeighbour ∧
        2 ≤ loss activeNeighbour + loss supportNeighbour := by
  by_contra hnone
  push_neg at hnone
  obtain ⟨other, hotherMem, hotherNe⟩ :=
    neighbours.exists_mem_ne (by omega) activeNeighbour
  have hactiveLoss : loss activeNeighbour ≤ 1 := by
    have hlt := hnone other hotherMem hotherNe
    omega
  have hall : ∀ z ∈ neighbours, loss z ≤ 1 := by
    intro z hz
    by_cases hza : z = activeNeighbour
    · simpa [hza] using hactiveLoss
    · have hlt := hnone z hz hza
      omega
  have hsum : (∑ z ∈ neighbours, loss z) ≤ neighbours.card := by
    calc
      (∑ z ∈ neighbours, loss z) ≤ ∑ z ∈ neighbours, 1 := by
        exact Finset.sum_le_sum fun z hz => hall z hz
      _ = neighbours.card := by simp
  omega

#print axioms exists_other_with_two_le_loss_sum

end CutTightStarPigeonhole
end Gamma
end Erdos23Delta0
